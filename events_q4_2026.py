# -*- coding: utf-8 -*-
"""
Danh sách sự kiện vĩ mô ảnh hưởng XAUUSD, Q4/2026 (16/10 -> 31/12/2026).
Giờ ghi theo múi giờ GỐC của nơi công bố; script build_ics.py sẽ tự quy đổi sang giờ VN
(và xử lý việc Mỹ đổi giờ mùa đông ngày 01/11/2026, châu Âu ngày 25/10/2026).

impact: "CAO" | "TB" (trung bình) | "INFO" (không phải dữ liệu, chỉ để biết: nghỉ lễ, đổi giờ...)
verified: True = lấy từ lịch chính thức của cơ quan công bố; False = theo quy luật/ lịch bên thứ 3, cần kiểm tra lại.
"""

NY = "America/New_York"
FRA = "Europe/Berlin"
LON = "Europe/London"
TYO = "Asia/Tokyo"
SHA = "Asia/Shanghai"

L = {
    "fomc_cal": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "fomc_inv": "https://www.investing.com/economic-calendar/interest-rate-decision-168",
    "fomc_min_inv": "https://www.investing.com/economic-calendar/fomc-meeting-minutes-108",
    "fedwatch": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html",
    "nfp_bls": "https://www.bls.gov/news.release/empsit.nr0.htm",
    "nfp_inv": "https://www.investing.com/economic-calendar/nonfarm-payrolls-227",
    "cpi_bls": "https://www.bls.gov/news.release/cpi.nr0.htm",
    "cpi_inv": "https://www.investing.com/economic-calendar/cpi-69",
    "corecpi_inv": "https://www.investing.com/economic-calendar/core-cpi-56",
    "ppi_bls": "https://www.bls.gov/news.release/ppi.nr0.htm",
    "ppi_inv": "https://www.investing.com/economic-calendar/ppi-238",
    "pce_bea": "https://www.bea.gov/data/income-saving/personal-income",
    "pce_inv": "https://www.investing.com/economic-calendar/core-pce-price-index-61",
    "gdp_bea": "https://www.bea.gov/data/gdp/gross-domestic-product",
    "gdp_inv": "https://www.investing.com/economic-calendar/gdp-375",
    "retail_census": "https://www.census.gov/retail/sales.html",
    "retail_inv": "https://www.investing.com/economic-calendar/retail-sales-256",
    "ism_site": "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/",
    "ism_mfg_inv": "https://www.investing.com/economic-calendar/ism-manufacturing-pmi-173",
    "ism_svc_inv": "https://www.investing.com/economic-calendar/ism-non-manufacturing-pmi-176",
    "claims_dol": "https://www.dol.gov/ui/data.pdf",
    "claims_inv": "https://www.investing.com/economic-calendar/initial-jobless-claims-294",
    "jolts_bls": "https://www.bls.gov/news.release/jolts.nr0.htm",
    "jolts_inv": "https://www.investing.com/economic-calendar/jolts-job-openings-1057",
    "adp_site": "https://adpemploymentreport.com/",
    "adp_inv": "https://www.investing.com/economic-calendar/adp-nonfarm-employment-change-1",
    "umich_site": "https://www.sca.isr.umich.edu/",
    "umich_inv": "https://www.investing.com/economic-calendar/michigan-consumer-sentiment-320",
    "cb_site": "https://www.conference-board.org/research/consumer-confidence",
    "cb_inv": "https://www.investing.com/economic-calendar/cb-consumer-confidence-48",
    "eci_bls": "https://www.bls.gov/news.release/eci.nr0.htm",
    "ecb_pr": "https://www.ecb.europa.eu/press/pr/date/html/index.en.html",
    "ecb_inv": "https://www.investing.com/economic-calendar/interest-rate-decision-164",
    "boj_pr": "https://www.boj.or.jp/en/mopo/mpmdeci/index.htm",
    "boe_pr": "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes",
    "pboc_safe": "https://www.safe.gov.cn/en/OfficialReserveAssets/index.html",
    "ff": "https://www.forexfactory.com/calendar",
    "treasury_ref": "https://home.treasury.gov/policy-issues/financing-the-government/quarterly-refunding",
    "fed_calendar": "https://www.federalreserve.gov/newsevents/calendar.htm",
    "fed_speeches_rss": "https://www.federalreserve.gov/feeds/speeches.xml",
    "nyse": "https://www.nyse.com/markets/hours-calendars",
}

# Mỗi phần tử: (date, time|None, tz, impact, title, note, links, verified)
# time=None => sự kiện cả ngày.
EVENTS = [
    # ---------------- Tháng 10 ----------------
    ("2026-10-22", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)",
     "Hàng tuần. Mạnh hơn/yếu hơn dự báo tác động ngắn hạn tới USD & vàng.", ["claims_dol", "claims_inv"], True),
    ("2026-10-23", "10:00", NY, "TB", "Tâm lý tiêu dùng Michigan T10 (chính thức) + kỳ vọng lạm phát",
     "Chú ý kỳ vọng lạm phát 1 năm / 5 năm.", ["umich_site", "umich_inv"], True),
    ("2026-10-27", "10:00", NY, "TB", "Niềm tin tiêu dùng Conference Board T10 (Mỹ)",
     "Ngày theo quy luật thứ Ba cuối tháng, chưa có xác nhận chính thức.", ["cb_site", "cb_inv"], False),
    ("2026-10-28", "14:00", NY, "CAO", "FOMC: Quyết định lãi suất + Tuyên bố (14:00 ET) + Họp báo Chủ tịch Fed Warsh (14:30 ET)",
     "Sự kiện quan trọng nhất tháng với vàng. Không có dự báo kinh tế (SEP) kỳ này. "
     "Tuyên bố: federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm",
     ["fomc_cal", "fomc_inv", "fedwatch"], True),
    ("2026-10-29", "08:30", NY, "CAO", "GDP Q3/2026 (ước tính lần 1) + PCE lõi T9 (thước đo lạm phát ưa thích của Fed) + Đơn thất nghiệp",
     "BEA công bố cùng lúc GDP sơ bộ Q3 và Personal Income & Outlays T9 (gồm Core PCE).",
     ["gdp_bea", "pce_bea", "gdp_inv", "pce_inv", "claims_inv"], True),
    ("2026-10-29", "14:15", FRA, "TB", "ECB: Quyết định lãi suất (14:15 CET) + Họp báo Lagarde (14:45 CET)",
     "Ảnh hưởng gián tiếp qua EUR/USD -> DXY.", ["ecb_pr", "ecb_inv"], True),
    ("2026-10-30", "11:30", TYO, "TB", "BoJ: Quyết định chính sách tiền tệ + Báo cáo triển vọng (Outlook Report)",
     "BoJ không ấn định giờ; thường công bố 11:30–12:30 JST (≈ 09:30–10:30 VN). Họp báo Thống đốc 15:30 JST (13:30 VN).",
     ["boj_pr"], True),
    ("2026-10-30", "08:30", NY, "TB", "Chỉ số chi phí lao động ECI Q3/2026 (Mỹ)",
     "Thước đo tiền lương Fed theo dõi sát.", ["eci_bls"], True),

    # ---------------- Tháng 11 ----------------
    ("2026-11-01", None, NY, "INFO", "Mỹ kết thúc giờ mùa hè (DST) → dữ liệu 08:30 ET chuyển từ 19:30 sang 20:30 giờ VN",
     "Từ hôm nay: 08:30 ET = 20:30 VN, 10:00 ET = 22:00 VN, FOMC 14:00 ET = 02:00 VN sáng hôm sau.", [], True),
    ("2026-11-02", "10:00", NY, "CAO", "ISM PMI Sản xuất T10 (Mỹ)",
     "Chú ý chỉ số phụ Prices Paid (lạm phát) và Employment.", ["ism_site", "ism_mfg_inv"], True),
    ("2026-11-03", None, NY, "CAO", "BẦU CỬ GIỮA KỲ MỸ (Midterm Elections)",
     "Kết quả về rạng sáng 04/11 giờ VN. Biến động mạnh USD, lợi suất TPCP và vàng; rủi ro gap.", ["ff"], True),
    ("2026-11-03", "10:00", NY, "TB", "JOLTS: Cơ hội việc làm T9 (Mỹ)",
     "Ngày theo lịch bên thứ 3 dẫn nguồn BLS.", ["jolts_bls", "jolts_inv"], False),
    ("2026-11-04", "08:15", NY, "TB", "ADP: Việc làm khu vực tư nhân T10 (Mỹ)",
     "Ngày ước tính (thứ Tư trước NFP). ADP chưa đăng lịch công khai.", ["adp_site", "adp_inv"], False),
    ("2026-11-04", "08:30", NY, "TB", "Treasury Quarterly Refunding — kế hoạch phát hành TPCP Mỹ quý tới",
     "Quy mô phát hành trái phiếu dài hạn tăng → lợi suất tăng → bất lợi cho vàng. Thứ Tư đầu tiên của tháng 2/5/8/11, chưa xác nhận.",
     ["treasury_ref"], False),
    ("2026-11-04", "10:00", NY, "CAO", "ISM PMI Dịch vụ T10 (Mỹ)",
     "Chú ý Prices Paid.", ["ism_site", "ism_svc_inv"], True),
    ("2026-11-05", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)", "", ["claims_dol", "claims_inv"], True),
    ("2026-11-05", "12:00", LON, "TB", "BoE: Quyết định lãi suất + Báo cáo Chính sách tiền tệ T11",
     "Ảnh hưởng gián tiếp qua GBP/USD.", ["boe_pr"], True),
    ("2026-11-06", "08:30", NY, "CAO", "BẢNG LƯƠNG PHI NÔNG NGHIỆP (NFP) T10 + Tỷ lệ thất nghiệp + Thu nhập giờ (Mỹ)",
     "Dữ liệu việc làm quan trọng nhất tháng.", ["nfp_bls", "nfp_inv"], True),
    ("2026-11-07", None, SHA, "TB", "PBoC/SAFE: Dự trữ vàng Trung Quốc T10 (mua/bán vàng của NHTW TQ)",
     "Thường công bố ngày 7 hàng tháng, không có giờ cố định. Yếu tố cầu vàng dài hạn.", ["pboc_safe"], False),
    ("2026-11-10", "08:30", NY, "CAO", "CPI T10 (Mỹ) — lạm phát tiêu dùng + CPI lõi",
     "Cùng với NFP và FOMC là 3 sự kiện tác động mạnh nhất tới vàng.", ["cpi_bls", "cpi_inv", "corecpi_inv"], True),
    ("2026-11-12", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)", "", ["claims_dol", "claims_inv"], True),
    ("2026-11-13", "08:30", NY, "CAO", "PPI T10 (Mỹ) — lạm phát sản xuất", "", ["ppi_bls", "ppi_inv"], True),
    ("2026-11-13", "10:00", NY, "TB", "Tâm lý tiêu dùng Michigan T11 (sơ bộ) + kỳ vọng lạm phát",
     "Ngày ước tính theo quy luật thứ Sáu tuần 2; UMich chưa đăng lịch.", ["umich_site", "umich_inv"], False),
    ("2026-11-17", "08:30", NY, "CAO", "Doanh số bán lẻ T10 (Mỹ)", "", ["retail_census", "retail_inv"], True),
    ("2026-11-18", "14:00", NY, "TB", "Biên bản họp FOMC (cuộc họp 27–28/10)",
     "Ngày suy ra từ quy tắc '3 tuần sau quyết định' của Fed; Fed chưa niêm yết chính thức.",
     ["fomc_cal", "fomc_min_inv"], False),
    ("2026-11-19", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)", "", ["claims_dol", "claims_inv"], True),
    ("2026-11-24", "10:00", NY, "TB", "Niềm tin tiêu dùng Conference Board T11 (Mỹ)", "", ["cb_site", "cb_inv"], False),
    ("2026-11-25", "08:30", NY, "CAO", "GDP Q3/2026 (ước tính lần 2) + PCE lõi T10 + Đơn thất nghiệp (dời sớm do Lễ Tạ ơn)",
     "Dồn nhiều dữ liệu trước kỳ nghỉ, thanh khoản mỏng → biến động mạnh.",
     ["gdp_bea", "pce_bea", "pce_inv", "claims_inv"], True),
    ("2026-11-25", "10:00", NY, "TB", "Tâm lý tiêu dùng Michigan T11 (chính thức)",
     "Ngày ước tính (thường dời lên thứ Tư trước Lễ Tạ ơn).", ["umich_site", "umich_inv"], False),
    ("2026-11-26", None, NY, "INFO", "Mỹ nghỉ Lễ Tạ ơn — thị trường Mỹ đóng cửa, thanh khoản vàng rất mỏng", "", ["nyse"], True),
    ("2026-11-27", None, NY, "INFO", "Mỹ đóng cửa sớm 13:00 ET (01:00 VN 28/11) — Black Friday", "", ["nyse"], True),

    # ---------------- Tháng 12 ----------------
    ("2026-12-01", "10:00", NY, "CAO", "ISM PMI Sản xuất T11 + JOLTS T10 (Mỹ)", "", ["ism_site", "ism_mfg_inv", "jolts_bls", "jolts_inv"], True),
    ("2026-12-02", "08:15", NY, "TB", "ADP: Việc làm khu vực tư nhân T11 (Mỹ)", "Ngày ước tính.", ["adp_site", "adp_inv"], False),
    ("2026-12-03", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)", "", ["claims_dol", "claims_inv"], True),
    ("2026-12-03", "10:00", NY, "CAO", "ISM PMI Dịch vụ T11 (Mỹ)", "", ["ism_site", "ism_svc_inv"], True),
    ("2026-12-04", "08:30", NY, "CAO", "BẢNG LƯƠNG PHI NÔNG NGHIỆP (NFP) T11 + Tỷ lệ thất nghiệp + Thu nhập giờ (Mỹ)",
     "NFP cuối cùng trước FOMC 09/12.", ["nfp_bls", "nfp_inv"], True),
    ("2026-12-07", None, SHA, "TB", "PBoC/SAFE: Dự trữ vàng Trung Quốc T11", "Thường ngày 7 hàng tháng.", ["pboc_safe"], False),
    ("2026-12-09", "14:00", NY, "CAO", "FOMC: Quyết định lãi suất + Tuyên bố + DỰ BÁO KINH TẾ (SEP, dot plot) 14:00 ET + Họp báo Warsh 14:30 ET",
     "Kỳ họp có dot plot → thị trường định giá lại lộ trình lãi suất 2027. Biến động cực mạnh. "
     "Tuyên bố: federalreserve.gov/newsevents/pressreleases/monetary20261209a.htm",
     ["fomc_cal", "fomc_inv", "fedwatch"], True),
    ("2026-12-10", "08:30", NY, "CAO", "CPI T11 (Mỹ) + CPI lõi + Đơn thất nghiệp",
     "Ngay sau FOMC → củng cố hoặc đảo chiều phản ứng của vàng.", ["cpi_bls", "cpi_inv", "corecpi_inv", "claims_inv"], True),
    ("2026-12-11", "10:00", NY, "TB", "Tâm lý tiêu dùng Michigan T12 (sơ bộ)", "Ngày ước tính.", ["umich_site", "umich_inv"], False),
    ("2026-12-15", "08:30", NY, "CAO", "PPI T11 (Mỹ)", "", ["ppi_bls", "ppi_inv"], True),
    ("2026-12-16", "08:30", NY, "CAO", "Doanh số bán lẻ T11 (Mỹ)", "", ["retail_census", "retail_inv"], True),
    ("2026-12-17", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)", "", ["claims_dol", "claims_inv"], True),
    ("2026-12-17", "12:00", LON, "TB", "BoE: Quyết định lãi suất", "", ["boe_pr"], True),
    ("2026-12-17", "14:15", FRA, "TB", "ECB: Quyết định lãi suất (14:15 CET) + Họp báo 14:45 CET + Dự báo vĩ mô mới", "", ["ecb_pr", "ecb_inv"], True),
    ("2026-12-18", "11:30", TYO, "TB", "BoJ: Quyết định chính sách tiền tệ",
     "Thường 11:30–12:30 JST (≈ 09:30–10:30 VN). Họp báo 15:30 JST.", ["boj_pr"], True),
    ("2026-12-23", "08:30", NY, "CAO", "GDP Q3/2026 (ước tính lần 3) + PCE lõi T11 (Mỹ)",
     "Dữ liệu lớn cuối cùng của năm; thanh khoản mỏng dịp Giáng sinh.", ["gdp_bea", "pce_bea", "pce_inv"], True),
    ("2026-12-23", "10:00", NY, "TB", "Tâm lý tiêu dùng Michigan T12 (chính thức)", "Ngày ước tính.", ["umich_site", "umich_inv"], False),
    ("2026-12-24", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)",
     "Có thể dời sang 23/12 nếu Chính phủ Mỹ nghỉ 24/12. Thị trường Mỹ đóng cửa sớm 13:00 ET.", ["claims_dol", "claims_inv", "nyse"], False),
    ("2026-12-25", None, NY, "INFO", "Giáng sinh — thị trường Mỹ/Âu đóng cửa", "", ["nyse"], True),
    ("2026-12-29", "10:00", NY, "TB", "Niềm tin tiêu dùng Conference Board T12 (Mỹ)", "Ngày ước tính.", ["cb_site", "cb_inv"], False),
    ("2026-12-31", "08:30", NY, "TB", "Đơn xin trợ cấp thất nghiệp lần đầu (Mỹ)", "", ["claims_dol", "claims_inv"], True),
]

# Cửa sổ nhiều ngày (sự kiện cả ngày kéo dài): (start, end_inclusive, title, note, links)
# Quy tắc blackout của Fed: không phát biểu từ thứ Bảy thứ 2 trước họp FOMC đến hết thứ Năm sau họp.
WINDOWS = [
    ("2026-10-30", "2026-11-27", "CỬA SỔ FED SPEAKERS: quan chức Fed phát biểu dày đặc (sau FOMC 28/10, trước blackout 28/11)",
     "Đậm đặc nhất 7–10 ngày đầu. Kiểm tra lịch Fed mỗi thứ Sáu hoặc bật thông báo app Investing/ForexFactory (lọc USD, Fed speakers).",
     ["fed_calendar", "fed_speeches_rss", "ff"]),
    ("2026-12-11", "2027-01-15", "CỬA SỔ FED SPEAKERS: sau FOMC 09/12, đến trước blackout họp cuối tháng 1/2027",
     "Thanh khoản mỏng cuối năm → phát biểu Fed dễ gây biến động lớn hơn bình thường.",
     ["fed_calendar", "fed_speeches_rss", "ff"]),
]
