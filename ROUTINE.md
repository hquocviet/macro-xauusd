# Quy trình cập nhật tự động

## Tầng 1 — GitHub Actions, hàng ngày 17:00 VN (không cần AI, không cần người)
`.github/workflows/update.yml` chạy `fetch_sources.py` rồi `build_ics.py` và commit nếu có thay đổi:
- Đọc feed JSON lịch Fed, thêm mọi phát biểu / thảo luận / điều trần của Chủ tịch (CAO), Phó Chủ tịch và
  Thống đốc Fed (TB) trong 21 ngày tới vào `events_dynamic.json` (mục `"source": "fed_json"`).
- Lưu bản text các trang lịch BEA, Treasury refunding, UMich, FOMC vào `sources/` cho tầng 2 đọc offline.
Chạy tay trên GitHub: tab Actions → "Update macro XAUUSD calendar" → Run workflow.

## Tầng 2 — Routine Claude Code, thứ Sáu 18:00 VN = 11:00 UTC
Sandbox của routine KHÔNG truy cập được federalreserve.gov / bls.gov / bea.gov (proxy chặn), nên routine
đọc `sources/*.txt` và `events_dynamic.json` do tầng 1 tạo, chỉ dùng WebSearch cho phần còn lại.

Mục tiêu: cập nhật `macro_xauusd.ics` cho 14 ngày tới mà không cần người dùng kiểm tra tay.

1. Đọc `events_q4_2026.py` và `events_dynamic.json` để biết những gì đã có.
2. **Fed speakers:** đã do tầng 1 tự thêm (`source: fed_json`), KHÔNG thêm lại. Chỉ bổ sung phát biểu của
   Chủ tịch regional Fed có quyền bỏ phiếu FOMC năm nay nếu WebSearch tìm được ngày giờ từ 2 nguồn khớp nhau (TB).
3. **Sự kiện bất thường khác** trong 14 ngày tới liên quan USD/vàng: điều trần Quốc hội của Chủ tịch Fed hoặc
   Bộ trưởng Tài chính, hạn chót ngân sách/đóng cửa chính phủ Mỹ, hạn chót thuế quan, kỳ họp bất thường.
   Nguồn: web search (từ khoá "week ahead", "economic calendar next week", "Fed speakers next week").
4. **Xác nhận lại ngày "(?)"** rơi vào 14 ngày tới (ADP, Michigan, Conference Board, JOLTS, biên bản FOMC,
   Treasury refunding): đọc `sources/umich_home.txt`, `sources/treasury_refunding.txt`, `sources/fed_fomc_calendar.txt`,
   `sources/bea_schedule.txt`; phần còn lại dùng WebSearch. Nếu xác nhận hoặc khác ngày thì sửa `events_q4_2026.py`
   và đặt `verified=True`. Nếu `sources/bea_schedule.txt` có kỳ công bố GDP/PCE mới chưa có trong file thì thêm.
5. Không trùng lặp: trước khi thêm, so sánh ngày + tiêu đề với sự kiện đã có. Xoá khỏi `events_dynamic.json`
   các sự kiện đã qua hơn 7 ngày.
6. Chạy `python3 build_ics.py`, kiểm tra in ra "OK:", rồi commit và push lên `main` với message dạng
   `weekly update YYYY-MM-DD: +N Fed speakers, +M other, K dates confirmed`.
7. Nếu một nguồn không truy cập được, ghi rõ trong commit message; không bịa ngày giờ.

Định dạng phần tử trong `events_dynamic.json`:
```json
{"date": "2026-11-05", "time": "13:00", "tz": "America/New_York", "impact": "CAO",
 "title": "Chủ tịch Fed Warsh phát biểu tại ... (chủ đề: triển vọng kinh tế)",
 "note": "Có hỏi đáp / không hỏi đáp", "links": ["https://www.federalreserve.gov/newsevents/calendar.htm"],
 "verified": true}
```
`impact` ∈ CAO | TB. `time` null = cả ngày. Giờ ghi theo múi giờ gốc trong `tz`, script tự đổi sang giờ VN.
