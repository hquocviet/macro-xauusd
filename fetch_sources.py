#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chạy hàng ngày bởi GitHub Actions (có internet đầy đủ). Hai việc:
1. Tải feed JSON lịch Fed (https://www.federalreserve.gov/json/calendar.json), lọc phát biểu / thảo luận /
   điều trần của Chủ tịch, Phó Chủ tịch, Thống đốc Fed trong WINDOW_DAYS ngày tới và ghi vào
   events_dynamic.json (các mục có "source": "fed_json"; mục do người/Claude thêm được giữ nguyên).
2. Lưu bản text của vài trang lịch chính thức vào sources/ để routine Claude đọc offline.

Chạy tay:  python3 fetch_sources.py   (rồi python3 build_ics.py)
"""
import json, re, html, sys, os
from datetime import date, datetime, timedelta
from urllib.request import Request, urlopen

WINDOW_DAYS = 21
FED_JSON = "https://www.federalreserve.gov/json/calendar.json"
FED_CAL_URL = "https://www.federalreserve.gov/newsevents/calendar.htm"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
SNAPSHOTS = {
    "bea_schedule.txt": "https://www.bea.gov/news/schedule",
    "treasury_refunding.txt": "https://home.treasury.gov/policy-issues/financing-the-government/quarterly-refunding",
    "umich_home.txt": "https://www.sca.isr.umich.edu/",
    "fed_fomc_calendar.txt": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
}

KIND_VI = {"Speech": "Phát biểu", "Discussion": "Thảo luận (có hỏi đáp)", "Testimony": "Điều trần Quốc hội",
           "Remarks": "Phát biểu", "Welcoming Remarks": "Phát biểu khai mạc", "Opening Remarks": "Phát biểu khai mạc"}


def get(url, timeout=40):
    with urlopen(Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def clean(s):
    s = html.unescape(html.unescape(s or ""))
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def to_24h(t):
    """'11:30 p.m.' -> '23:30'; '' -> None"""
    m = re.match(r"\s*(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?", (t or "").lower())
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if ap == "p" and h != 12:
        h += 12
    if ap == "a" and h == 12:
        h = 0
    return f"{h:02d}:{mi:02d}"


def role_vi(person):
    p = person
    if re.search(r"\bChair(man|woman)?\b(?! for)", p) and "Vice" not in p:
        return "CAO", "Chủ tịch Fed " + re.sub(r"^Chair(man|woman)?\s+", "", p)
    if "Vice Chair for Supervision" in p:
        return "TB", "Phó Chủ tịch Fed (Giám sát) " + p.replace("Vice Chair for Supervision", "").strip()
    if "Vice Chair" in p:
        return "TB", "Phó Chủ tịch Fed " + p.replace("Vice Chair", "").strip()
    if p.startswith("Governor"):
        return "TB", "Thống đốc Fed " + p.replace("Governor", "").strip()
    return "TB", p


def fed_events(today):
    raw = get(FED_JSON).decode("utf-8-sig")
    data = json.loads(raw)
    out = []
    end = today + timedelta(days=WINDOW_DAYS)
    for e in data.get("events", []):
        if e.get("type") not in ("Speeches", "Testimony"):
            continue
        month = e.get("month") or ""
        if not re.match(r"\d{4}-\d{2}$", month):
            continue
        for d in [x.strip() for x in str(e.get("days") or "").split(",") if x.strip()]:
            try:
                dt = date(int(month[:4]), int(month[5:7]), int(d))
            except ValueError:
                continue
            if not (today <= dt <= end):
                continue
            title = clean(e.get("title"))
            kind, _, person = title.partition(" - ")
            if not person:
                person = title
            impact, who = role_vi(person.strip())
            if e.get("type") == "Testimony" and "Chủ tịch Fed" in who:
                impact = "CAO"
            kind_vi = KIND_VI.get(kind.strip(), kind.strip())
            topic = clean(e.get("description"))
            loc = clean(e.get("location"))
            t = to_24h(e.get("time"))
            name = f"Fed: {who} — {kind_vi}" + (f": {topic}" if topic else "")
            note = (loc + ". " if loc else "") + ("Giờ gốc ET theo lịch Fed." if t else "Fed chưa công bố giờ.")
            links = [FED_CAL_URL]
            if e.get("live"):
                links.append(e["live"].strip())
            out.append({"date": dt.isoformat(), "time": t, "tz": "America/New_York", "impact": impact,
                        "title": name, "note": note, "links": links, "verified": True, "source": "fed_json"})
    return out


def merge(new, today):
    path = "events_dynamic.json"
    old = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
    keep = [x for x in old if x.get("source") != "fed_json"
            and date.fromisoformat(x["date"]) >= today - timedelta(days=7)]
    merged = keep + new
    merged.sort(key=lambda x: (x["date"], x.get("time") or ""))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    return len(keep), len(new)


def snapshots():
    os.makedirs("sources", exist_ok=True)
    ok, bad = [], []
    for name, url in SNAPSHOTS.items():
        try:
            txt = get(url).decode("utf-8", "ignore")
            txt = re.sub(r"(?is)<(script|style|noscript|svg).*?</\1>", " ", txt)
            txt = clean(txt)
            with open(os.path.join("sources", name), "w", encoding="utf-8") as f:
                f.write(f"SOURCE: {url}\nFETCHED: {datetime.utcnow():%Y-%m-%d %H:%M} UTC\n\n{txt}\n")
            ok.append(name)
        except Exception as ex:  # noqa
            bad.append(f"{name}: {ex}")
    return ok, bad


if __name__ == "__main__":
    today = date.today()
    try:
        new = fed_events(today)
    except Exception as ex:
        print(f"ERROR fed calendar: {ex}", file=sys.stderr)
        new = None
    if new is not None:
        kept, added = merge(new, today)
        print(f"fed_json: {added} sự kiện Fed trong {WINDOW_DAYS} ngày tới; giữ {kept} mục khác")
        for x in new:
            print(f"  {x['date']} {x['time'] or 'cả ngày'} ET  {x['impact']}  {x['title'][:90]}")
    ok, bad = snapshots()
    print(f"snapshots ok: {', '.join(ok)}")
    if bad:
        print("snapshots failed: " + "; ".join(bad), file=sys.stderr)
