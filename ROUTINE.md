# Routine hàng tuần (thứ Sáu 18:00 VN = 11:00 UTC)

Mục tiêu: cập nhật `macro_xauusd.ics` cho 14 ngày tới mà không cần người dùng kiểm tra tay.

1. Đọc `events_q4_2026.py` và `events_dynamic.json` để biết những gì đã có.
2. **Fed speakers (ưu tiên cao nhất):** lấy lịch tại https://www.federalreserve.gov/newsevents/calendar.htm
   (và trang tháng kế tiếp nếu gần cuối tháng). Thêm vào `events_dynamic.json` mọi phát biểu / điều trần /
   họp báo của Chủ tịch Fed (CAO) và các Thống đốc Fed (TB) trong 14 ngày tới, có ngày giờ ET.
   Bỏ qua: sự kiện không có giờ, sự kiện kỹ thuật (open board meeting về quy định, lễ trao giải...).
   Nếu có phát biểu của Chủ tịch regional Fed có quyền bỏ phiếu FOMC năm nay thì thêm mức TB.
3. **Sự kiện bất thường khác** trong 14 ngày tới liên quan USD/vàng: điều trần Quốc hội của Chủ tịch Fed hoặc
   Bộ trưởng Tài chính, hạn chót ngân sách/đóng cửa chính phủ Mỹ, hạn chót thuế quan, kỳ họp bất thường.
   Nguồn: web search (từ khoá "week ahead", "economic calendar next week", "Fed speakers next week").
4. **Xác nhận lại ngày "(?)"** rơi vào 14 ngày tới (ADP, Michigan, Conference Board, JOLTS, biên bản FOMC):
   kiểm tra trang chính thức; nếu khác thì sửa ngày trong `events_q4_2026.py` và đặt `verified=True`.
   Nếu BLS/BEA đã đăng lịch tháng/quý mới chưa có trong file (ví dụ tháng 1/2027) thì thêm.
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
