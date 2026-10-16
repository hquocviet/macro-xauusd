# Macro XAUUSD calendar

Lịch dữ liệu vĩ mô ảnh hưởng tới XAUUSD, giờ Việt Nam, chia mức ảnh hưởng, kèm link kiểm tra dữ liệu.
File `macro_xauusd.ics` được cập nhật tự động hai tầng:
- **GitHub Actions, hàng ngày 17:00 VN:** đọc feed JSON lịch Fed, thêm phát biểu của Chủ tịch / Phó Chủ tịch / Thống đốc Fed
  trong 21 ngày tới, lưu snapshot các trang lịch chính thức vào `sources/`.
- **Routine Claude Code, thứ Sáu 18:00 VN:** xác nhận lại các ngày "(?)", tìm sự kiện bất thường (điều trần, hạn chót
  ngân sách/thuế quan), bổ sung kỳ công bố mới.

| File | Mục đích |
|---|---|
| `macro_xauusd.ics` | **File lịch để subscribe** (URL cố định bên dưới). Nhắc trước 1h; sự kiện 🔴 thêm nhắc 15' |
| `LICH_VI_MO_XAUUSD.md` | Bảng lịch đọc nhanh theo giờ VN, có link kiểm tra dữ liệu |
| `events_q4_2026.py` | Sự kiện có lịch cố định (sửa tay) |
| `events_dynamic.json` | Sự kiện routine tự thêm hàng tuần (Fed speakers, sự kiện bất thường) |
| `build_ics.py` | Sinh lại `.ics` + `.md`: `python3 build_ics.py` |
| `fetch_sources.py` | Tải feed Fed + snapshot trang lịch (GitHub Actions chạy hàng ngày) |
| `sources/` | Bản text các trang lịch chính thức, để routine đọc offline |
| `.github/workflows/update.yml` | Lịch chạy GitHub Actions |
| `ROUTINE.md` | Quy trình routine hàng tuần thực hiện |

## Subscribe bằng tài khoản Google riêng (tự động đồng bộ, không cần import tay)

URL lịch:

```
https://raw.githubusercontent.com/hquocviet/macro-xauusd/main/macro_xauusd.ics
```

1. Trên máy tính, đăng nhập Google Calendar bằng tài khoản muốn dùng.
2. Bên trái, cạnh **Other calendars** bấm **+** → **From URL** → dán URL trên → **Add calendar**.
3. Vào **Settings** (⚙) → chọn lịch vừa thêm (tên `Macro XAUUSD`) → **Event notifications** → Add notification → `1 hour` (Notification).
   **Bước này bắt buộc**: Google bỏ qua reminder trong file .ics của lịch subscribe, chỉ dùng thông báo mặc định của lịch.
   Muốn thêm nhắc 15' thì thêm notification thứ hai `15 minutes`.
4. Trên điện thoại: app Google Calendar → Settings → chọn tài khoản → bật hiển thị lịch `Macro XAUUSD`;
   Settings → General → bật *Notifications*. iOS: cho phép thông báo của app Google Calendar.

Google làm mới lịch subscribe khoảng 12–24 giờ một lần, nên routine chạy thứ Sáu thì muộn nhất thứ Bảy lịch tuần sau đã có.
Không thể ép Google làm mới sớm hơn; nếu cần gấp, tải file `.ics` và import tay vào một lịch khác.

## Chạy thủ công

```bash
python3 build_ics.py                 # sinh lại .ics + .md
python3 build_ics.py --no-extra-alarm   # chỉ nhắc 1h
python3 build_ics.py --no-info          # bỏ ngày nghỉ lễ/đổi giờ
```

Mức ảnh hưởng: 🔴 CAO (FOMC, NFP, CPI, PCE lõi, GDP sơ bộ, ISM, PPI, bán lẻ, bầu cử),
🟠 TRUNG BÌNH (claims, ADP, JOLTS, Michigan, CB, ECI, biên bản FOMC, ECB/BoJ/BoE, PBoC gold),
🟡 cửa sổ nhiều ngày cần cảnh giác (Fed speakers), ⚪ thông tin (nghỉ lễ, đổi giờ).
# macro-xauusd
