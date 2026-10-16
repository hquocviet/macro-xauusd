#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sinh file .ics (import vào Google Calendar) + bảng lịch Markdown theo giờ VN
từ dữ liệu trong events_q4_2026.py.

Chạy:  python3 build_ics.py
Tạo ra: macro_xauusd.ics  và  LICH_VI_MO_XAUUSD.md

Tuỳ chọn:
  --no-extra-alarm   : chỉ nhắc trước 1h (bỏ nhắc thêm 15' cho sự kiện CAO)
  --no-info          : bỏ các sự kiện INFO (nghỉ lễ, đổi giờ)
"""
import sys, uuid, hashlib, json, os
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo
from collections import defaultdict

from events_q4_2026 import EVENTS, WINDOWS, L

# Sự kiện động (routine hàng tuần thêm vào): events_dynamic.json
# [{"date":"2026-11-05","time":"13:00","tz":"America/New_York","impact":"CAO","title":"...",
#   "note":"...","links":["https://..."],"verified":true}]   (time=null => cả ngày)
DYN = []
if os.path.exists("events_dynamic.json"):
    with open("events_dynamic.json", encoding="utf-8") as f:
        for d in json.load(f):
            DYN.append((d["date"], d.get("time"), d.get("tz", "America/New_York"), d["impact"],
                        d["title"], d.get("note", ""), d.get("links", []), d.get("verified", True)))
ALL_EVENTS = list(EVENTS) + DYN


def link(k):
    """k là key trong L hoặc URL trực tiếp."""
    return k if k.startswith("http") else L[k]


VN = ZoneInfo("Asia/Ho_Chi_Minh")
EXTRA_ALARM = "--no-extra-alarm" not in sys.argv
KEEP_INFO = "--no-info" not in sys.argv

IMPACT_ORDER = {"CAO": 0, "TB": 1, "WINDOW": 2, "INFO": 3}
IMPACT_ICON = {"CAO": "🔴", "TB": "🟠", "WINDOW": "🟡", "INFO": "⚪"}
IMPACT_VI = {"CAO": "CAO", "TB": "Trung bình", "WINDOW": "Cửa sổ cần cảnh giác (nhiều ngày)", "INFO": "Thông tin"}
LABEL = {
    "fomc_cal": "Fed (lịch FOMC)", "fomc_inv": "Investing", "fomc_min_inv": "Investing", "fedwatch": "CME FedWatch",
    "nfp_bls": "BLS", "nfp_inv": "Investing", "cpi_bls": "BLS", "cpi_inv": "Investing CPI", "corecpi_inv": "Investing Core CPI",
    "ppi_bls": "BLS", "ppi_inv": "Investing", "pce_bea": "BEA PCE", "pce_inv": "Investing Core PCE",
    "gdp_bea": "BEA GDP", "gdp_inv": "Investing GDP", "retail_census": "Census", "retail_inv": "Investing",
    "ism_site": "ISM", "ism_mfg_inv": "Investing Mfg", "ism_svc_inv": "Investing Svc",
    "claims_dol": "DOL (PDF)", "claims_inv": "Investing", "jolts_bls": "BLS JOLTS", "jolts_inv": "Investing JOLTS",
    "adp_site": "ADP", "adp_inv": "Investing", "umich_site": "UMich", "umich_inv": "Investing",
    "cb_site": "Conference Board", "cb_inv": "Investing", "eci_bls": "BLS ECI", "ecb_pr": "ECB", "ecb_inv": "Investing",
    "boj_pr": "BoJ", "boe_pr": "BoE", "pboc_safe": "SAFE", "ff": "ForexFactory", "nyse": "NYSE",
    "treasury_ref": "US Treasury", "fed_calendar": "Lịch sự kiện Fed", "fed_speeches_rss": "RSS phát biểu Fed",
}
WD_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]


def to_vn(d, t, tz):
    """Trả về datetime giờ VN (timezone-aware) hoặc None nếu cả ngày."""
    if t is None:
        return None
    src = datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(tz))
    return src.astimezone(VN)


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    """RFC 5545: gấp dòng tối đa 75 octet."""
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > 73:
            out.append(cur)
            cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)


def duration_for(items):
    titles = " ".join(i[4] for i in items)
    if "FOMC: Quyết định" in titles or "ECB:" in titles:
        return timedelta(minutes=90)
    return timedelta(minutes=30)


# ---- gộp các sự kiện cùng thời điểm thành 1 event để không spam thông báo ----
groups = defaultdict(list)
for ev in ALL_EVENTS:
    d, t, tz, imp, *_ = ev
    if imp == "INFO" and not KEEP_INFO:
        continue
    key = (d, None) if t is None else (d, to_vn(d, t, tz).isoformat())
    groups[key].append(ev)

rows = []  # cho markdown
vevents = []
now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

for key in sorted(groups, key=lambda k: (k[0], k[1] or "")):
    items = sorted(groups[key], key=lambda e: IMPACT_ORDER[e[3]])
    d, iso = key
    impact = items[0][3]
    icon = IMPACT_ICON[impact]
    allday = iso is None
    dt_vn = None if allday else datetime.fromisoformat(iso)
    day = date.fromisoformat(d) if allday else dt_vn.date()
    verified_all = all(e[7] for e in items)

    # Tiêu đề
    if len(items) == 1:
        summary = f"{icon} {items[0][4]}"
    else:
        summary = f"{icon} " + " | ".join(e[4] for e in items)
    if not verified_all:
        summary += " (ngày cần xác nhận)"

    # Mô tả
    lines = [f"Mức ảnh hưởng tới XAUUSD: {IMPACT_VI[impact]}"]
    if allday:
        lines.append("Thời gian: cả ngày (không có giờ cố định)")
    else:
        lines.append(f"Giờ VN: {dt_vn.strftime('%H:%M')} {WD_VI[dt_vn.weekday()]} {dt_vn.strftime('%d/%m/%Y')}")
        src = items[0]
        lines.append(f"Giờ gốc: {src[1]} ({src[2]})")
    lines.append("")
    for e in items:
        lines.append(f"• {e[4]}")
        if e[5]:
            lines.append(f"  Ghi chú: {e[5]}")
        if not e[7]:
            lines.append("  ⚠ Ngày theo quy luật/lịch bên thứ 3 — kiểm tra lại trước 1 tuần.")
    lines.append("")
    lines.append("Link kiểm tra dữ liệu khi công bố:")
    seen = set()
    for e in items:
        for k in e[6]:
            if k not in seen:
                seen.add(k)
                lines.append(f"- {link(k)}")
    lines.append(f"- Lịch tổng hợp (ForexFactory): {L['ff']}")
    description = "\n".join(lines)

    uid = hashlib.md5(f"{d}-{iso}-{summary}".encode()).hexdigest() + "@macro-xauusd"

    v = ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{now}"]
    if allday:
        v.append(f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}")
        v.append(f"DTEND;VALUE=DATE:{(day + timedelta(days=1)).strftime('%Y%m%d')}")
    else:
        start_utc = dt_vn.astimezone(timezone.utc)
        end_utc = start_utc + duration_for(items)
        v.append(f"DTSTART:{start_utc.strftime('%Y%m%dT%H%M%SZ')}")
        v.append(f"DTEND:{end_utc.strftime('%Y%m%dT%H%M%SZ')}")
    v.append(f"SUMMARY:{esc(summary)}")
    v.append(f"DESCRIPTION:{esc(description)}")
    v.append(f"CATEGORIES:XAUUSD,{impact}")
    v.append("TRANSP:TRANSPARENT")  # không chiếm trạng thái "bận"
    if impact != "INFO":
        v += ["BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT1H",
              f"DESCRIPTION:{esc('Còn 1 giờ: ' + summary)}", "END:VALARM"]
        if EXTRA_ALARM and impact == "CAO" and not allday:
            v += ["BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT15M",
                  f"DESCRIPTION:{esc('Còn 15 phút: ' + summary)}", "END:VALARM"]
    v.append("END:VEVENT")
    vevents.append("\r\n".join(fold(x) for x in v))

    rows.append((day, dt_vn, impact, items, verified_all))

# ---- cửa sổ nhiều ngày ----
for ws, we, title, note, links in WINDOWS:
    sd, ed = date.fromisoformat(ws), date.fromisoformat(we)
    summary = f"🟡 {title}"
    lines = [f"Mức: {IMPACT_VI['WINDOW']}", f"Từ {sd.strftime('%d/%m/%Y')} đến hết {ed.strftime('%d/%m/%Y')}", "",
             f"• {title}", f"  Ghi chú: {note}", "", "Link theo dõi:"] + [f"- {L[k]}" for k in links]
    uid = hashlib.md5(f"{ws}-{we}-{title}".encode()).hexdigest() + "@macro-xauusd"
    v = ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{now}",
         f"DTSTART;VALUE=DATE:{sd.strftime('%Y%m%d')}",
         f"DTEND;VALUE=DATE:{(ed + timedelta(days=1)).strftime('%Y%m%d')}",
         f"SUMMARY:{esc(summary)}", f"DESCRIPTION:{esc(chr(10).join(lines))}",
         "CATEGORIES:XAUUSD,WINDOW", "TRANSP:TRANSPARENT",
         "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT1H",
         f"DESCRIPTION:{esc('Bắt đầu ' + summary)}", "END:VALARM", "END:VEVENT"]
    vevents.append("\r\n".join(fold(x) for x in v))
    fake = (ws, None, "America/New_York", "WINDOW",
            f"{title} — {sd.strftime('%d/%m')} → {ed.strftime('%d/%m/%Y')}", note, links, True)
    rows.append((sd, None, "WINDOW", [fake], True))
rows.sort(key=lambda r: (r[0], r[1].isoformat() if r[1] else ""))

cal = [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//macro-data//XAUUSD Macro Calendar Q4 2026//VI",
    "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
    "X-WR-CALNAME:Macro XAUUSD", "X-WR-TIMEZONE:Asia/Ho_Chi_Minh",
    "X-WR-CALDESC:Lịch dữ liệu vĩ mô ảnh hưởng XAUUSD - giờ Việt Nam - nhắc trước 1h",
]
ics = "\r\n".join(fold(x) for x in cal) + "\r\n" + "\r\n".join(vevents) + "\r\nEND:VCALENDAR\r\n"
with open("macro_xauusd.ics", "w", encoding="utf-8", newline="") as f:
    f.write(ics)

# ---------------- Markdown ----------------
md = []
md.append("# Lịch dữ liệu vĩ mô ảnh hưởng XAUUSD (giờ Việt Nam)\n")
md.append("Giờ **Việt Nam (UTC+7)**. 🔴 = ảnh hưởng CAO, 🟠 = TRUNG BÌNH, 🟡 = cửa sổ nhiều ngày cần cảnh giác (Fed speakers), ⚪ = thông tin (nghỉ lễ/đổi giờ). "
          "Dấu **(?)** = ngày theo quy luật hoặc lịch bên thứ 3, chưa có xác nhận chính thức.\n")
md.append("> **Lưu ý đổi giờ:** Mỹ hết giờ mùa hè từ **01/11/2026** → dữ liệu 08:30 ET dời từ **19:30** sang **20:30 VN**; "
          "10:00 ET từ 21:00 → 22:00 VN; FOMC 14:00 ET từ 01:00 → **02:00 VN sáng hôm sau**. Châu Âu đổi giờ từ 25/10/2026.\n")

cur_month = None
for day, dt_vn, impact, items, verified_all in rows:
    m = day.strftime("%m/%Y")
    if m != cur_month:
        cur_month = m
        md.append(f"\n## Tháng {m}\n")
        md.append("| Ngày (VN) | Giờ VN | Mức | Sự kiện | Ghi chú | Link kiểm tra |")
        md.append("|---|---|---|---|---|---|")
    dstr = f"{WD_VI[day.weekday()]} {day.strftime('%d/%m')}"
    tstr = "cả ngày" if dt_vn is None else dt_vn.strftime("%H:%M")
    if dt_vn is not None and dt_vn.date() != date.fromisoformat(items[0][0]):
        tstr += f" (đêm {date.fromisoformat(items[0][0]).strftime('%d/%m')} giờ Mỹ)"
    icon = IMPACT_ICON[impact] + (" (?)" if not verified_all else "")
    titles = "<br>".join(e[4] for e in items)
    notes = "<br>".join(e[5] for e in items if e[5])
    links, seen = [], set()
    for e in items:
        for k in e[6]:
            if k not in seen:
                seen.add(k)
                links.append(f"[{LABEL.get(k, 'link' if k.startswith('http') else k)}]({link(k)})")
    md.append(f"| {dstr} | {tstr} | {icon} | {titles} | {notes} | {' · '.join(links)} |")

md.append("\n## Link hữu ích chung\n")
md.append(f"- Lịch kinh tế tổng hợp (lọc USD, High/Medium): {L['ff']}")
md.append("- Investing.com Economic Calendar: https://www.investing.com/economic-calendar/")
md.append(f"- CME FedWatch (xác suất Fed tăng/giảm lãi suất): {L['fedwatch']}")
md.append(f"- Lịch họp FOMC chính thức: {L['fomc_cal']}")
md.append("- Lịch công bố BLS theo tháng: https://www.bls.gov/schedule/2026/11_sched_list.htm (đổi 11 → 12)")
md.append("- Lịch công bố BEA: https://www.bea.gov/news/schedule")
md.append("- Lịch Census (Retail Sales): https://www.census.gov/retail/release_schedule.html")
md.append("- Lịch ISM: https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/")
md.append("- Lợi suất TPCP Mỹ 10Y & DXY (theo dõi cùng vàng): https://www.cnbc.com/quotes/US10Y , https://www.marketwatch.com/investing/index/dxy")
with open("LICH_VI_MO_XAUUSD.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")

n_cao = sum(1 for r in rows if r[2] == "CAO")
n_tb = sum(1 for r in rows if r[2] == "TB")
n_info = sum(1 for r in rows if r[2] == "INFO")
n_win = sum(1 for r in rows if r[2] == "WINDOW")
print(f"OK: {len(vevents)} events -> macro_xauusd.ics  (CAO={n_cao}, TB={n_tb}, WINDOW={n_win}, INFO={n_info})")
