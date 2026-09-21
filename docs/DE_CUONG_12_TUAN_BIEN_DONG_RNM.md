# Đề cương 12 tuần: Bản đồ biến động rừng ngập mặn vùng ven biển Đồng bằng sông Cửu Long bằng Google Earth Engine

**Dùng cho:** người hướng dẫn kèm một bạn chưa biết gì về GEE / viễn thám, làm việc bán thời gian (khoảng 12–15 giờ mỗi tuần), hoàn thành trong 12 tuần.
**Tài liệu đi kèm trong repo:**
- [HUONG_DAN_GEE_BIEN_DONG_RNM.md](HUONG_DAN_GEE_BIEN_DONG_RNM.md): hướng dẫn kỹ thuật 6 mục (gọi tắt là "Hướng dẫn").
- [bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js): script phương pháp nền cho vùng tập Đất Mũi.
- [mangrove_analysis.js](../gee_code_editor/mangrove_analysis.js): bản JavaScript đa năm cho toàn vùng (dùng để tham khảo cách gộp nhiều mốc).
- `shapefile_commune/VungNghiencuu.*`: ranh giới 109 xã của dự án.

---

## 1. Thông tin đề tài

**Tên đề tài:** Đánh giá biến động rừng ngập mặn vùng ven biển Đồng bằng sông Cửu Long (109 xã) giai đoạn 2020–2025 bằng ảnh Sentinel-2 trên Google Earth Engine.

**Câu hỏi nghiên cứu:**
1. Diện tích rừng ngập mặn toàn vùng, và theo từng tỉnh, tăng hay giảm giữa 2020 và 2025, bao nhiêu ha?
2. Phần rừng bị mất chuyển thành loại đất nào (nuôi trồng thuỷ sản, nông nghiệp, đô thị, mặt nước)?
3. Những xã nào biến động mạnh nhất (điểm nóng)?
4. Cách phân loại có giám sát (Random Forest) cải thiện độ chính xác bao nhiêu so với cách ngưỡng NDVI có giới hạn vùng?

**Phạm vi:**
- **Vùng nghiên cứu:** 109 xã ven biển ĐBSCL trong `shapefile_commune/VungNghiencuu` (khoảng 10.490 km², 5 mã tỉnh trong shapefile).
- **Mốc thời gian:** 2020 và 2025, cùng dùng Sentinel-2.
- **Vùng tập (sandbox):** khung Đất Mũi `[104.72, 8.56, 104.92, 8.74]` (khoảng 22 × 20 km). Dùng ở tuần 1–3 để học nhanh vì chạy trong vài chục giây, sau đó mới chạy toàn vùng.
- **Tuỳ chọn nếu dư thời gian:** mốc 2015 (Landsat 8); các năm khác trong chuỗi 1988–2026 của repo.

**Sản phẩm cuối (8 thứ):**

| # | Sản phẩm | Định dạng |
|---|----------|-----------|
| 1 | Bản đồ biến động rừng ngập mặn 2020–2025 toàn vùng (ổn định / mất / mới), có chú giải, hướng bắc, tỷ lệ, nguồn dữ liệu | PNG + GeoTIFF |
| 2 | Bản đồ phân loại lớp phủ 2020 và 2025 (5 lớp) | GeoTIFF (chia theo tỉnh) |
| 3 | Bảng diện tích (ha) toàn vùng, theo tỉnh và theo xã; ma trận chuyển đổi 5 × 5 | CSV |
| 4 | Danh sách xã điểm nóng (mất hoặc tăng mạnh nhất) | CSV + hình |
| 5 | Bảng độ chính xác: OA, Kappa, Producer's / User's, F1 lớp rừng; theo tỉnh; so sánh với Global Mangrove Watch (GMW) | CSV + trong báo cáo |
| 6 | Bộ điểm mẫu đã gán nhãn cho hai năm và luật gán nhãn | CSV / GEE Asset |
| 7 | Toàn bộ script GEE, chạy lại được từ đầu | `.js` |
| 8 | Báo cáo (15–20 trang) và slide bảo vệ | Word / PDF |

**Kết quả tối thiểu chấp nhận được** (nếu chậm, xem mục 7): phương pháp nền (NDVI + vùng lọc) cho toàn vùng, kèm đánh giá độ chính xác và báo cáo trung thực về hạn chế; Random Forest chỉ ở một số tỉnh trọng điểm.

---

## 2. Vì sao phạm vi ĐBSCL làm đề tài khó hơn

Tôi đã đo một số con số trên dữ liệu thật (ngày 21/09/2026) để bạn biết trước điều gì sẽ xảy ra:

| Phép đo | Kết quả | Ý nghĩa cho đề tài |
|---------|---------|--------------------|
| Diện tích "rừng" khi chỉ dùng NDVI > 0,25 trên cả 109 xã (2020, đã loại mây theo điểm ảnh, đo ở độ phân giải 100 m) | Khoảng **655.000 ha** | GMW 2020 trong cùng vùng chỉ khoảng **101.000 ha**. NDVI đơn thuần cho gấp hơn 6 lần: **không dùng được** nếu không giới hạn vùng hoặc không phân loại có giám sát |
| Đa giác dải ven biển vẽ tay của repo (974 đỉnh) | 10.413 km²; chứa khoảng 34.200 ha rừng GMW | Đây là cách mà code Python trước đây tránh lẫn nông nghiệp |
| Phần đa giác dải nằm trong 109 xã | Chứa khoảng 31.800 ha rừng GMW, chỉ khoảng **31%** rừng GMW của 109 xã | Đa giác dải bỏ sót phần lớn rừng nằm ngoài dải. Nếu dùng làm vùng lọc thì phải nêu rõ điều này |
| Số cảnh Sentinel-2 mỗi năm phủ vùng, mây < 60% | Khoảng 320–360 cảnh (đo trên 109 xã và trên đa giác dải, năm 2020 và 2025) | Khối lượng lớn hơn nhiều so với vùng tập (29–33 cảnh) |
| Tính diện tích tương tác toàn vùng ở 100 m | Chạy được trong khoảng 14 giây | Tính ở độ phân giải 30 m toàn vùng **chưa thử**: dự kiến phải chia theo tỉnh hoặc xuất (Export) |

**Hệ quả cho kế hoạch:**
1. **Nhánh B (Random Forest) trở thành trung tâm**, không còn là phần nâng cao. Với vùng có cả rừng, ao tôm, lúa, đô thị, phân loại đa lớp là cách tách chúng có cơ sở nhất.
2. Nhánh A (NDVI + vùng lọc) vẫn cần làm: là mốc so sánh, là phương án dự phòng, và giúp người mới hiểu dữ liệu. Nhưng **vùng lọc phải được chọn có bằng chứng** (tuần 4).
3. **Mẫu phải rải khắp các tỉnh**, không chỉ ở một nơi, và kiểm tra độ chính xác theo tỉnh.
4. **Khối lượng tính toán** cần được quản lý: chia theo tỉnh, dùng `tileScale`, xuất kết quả trung gian.

---

## 3. Phương pháp tổng quát

```
NHÁNH A (nền, tuần 2–4)                 NHÁNH B (chính, tuần 5–10)
Ảnh Sentinel-2 sạch mây                 Ảnh Sentinel-2 sạch mây + chỉ số + độ cao
        │                                        │
   NDVI > 0,25                           Điểm mẫu tự gán nhãn (5 lớp), rải khắp các tỉnh
   VÀ trong vùng lọc (ROI)                       │
        │                                Random Forest (train / test tách theo khối)
   Bản đồ rừng / không rừng                      │
        │                                Bản đồ 5 lớp cho 2020 và 2025
        └────────────── So sánh + kiểm chứng (GMW, điểm mẫu) ──────────────┘
                                   │
            Biến động + ma trận chuyển đổi + thống kê theo tỉnh / xã + báo cáo
```

**Các quyết định thiết kế (đã cân nhắc, không tự ý đổi giữa chừng):**
- **Cùng cảm biến Sentinel-2 cho cả hai năm**, để tránh biến động giả do đổi vệ tinh.
- **Bắt buộc loại mây theo điểm ảnh (band SCL).** Ở vùng tập Đất Mũi, chỉ lọc % mây thì 2025 còn 4 cảnh còn mây và cho ra mức giảm rừng giả (−2.069 ha, so với −484 ha khi ảnh sạch).
- **Vùng lọc của nhánh A chọn bằng bằng chứng**, không chọn tuỳ ý (tuần 4).
- **Mẫu gán nhãn cho cả hai năm tại cùng các điểm**, để vừa huấn luyện, vừa kiểm tra độ chính xác của lớp biến động.
- **Tách mẫu huấn luyện / kiểm tra theo khối không gian** (lưới 10 × 10 km), không tách ngẫu nhiên từng điểm, vì điểm gần nhau giống nhau và làm độ chính xác bị thổi phồng.
- **Chỉnh tham số bằng sai số out-of-bag của Random Forest**, không dùng tập kiểm tra để chỉnh.
- **Thống kê theo xã** dùng ranh giới 109 xã (giống phần 3 của `MAP05_Validation_RecentChange.ipynb` trong repo).

---

## 4. Dữ liệu và công cụ

| Loại | Chi tiết |
|------|----------|
| Nền tảng | Google Earth Engine Code Editor (JavaScript), tài khoản Google, Cloud project phi thương mại |
| Ảnh chính | `COPERNICUS/S2_SR_HARMONIZED` (Sentinel-2, 10 m) |
| Ảnh phụ (tuỳ chọn) | `LANDSAT/LC08/C02/T1_L2` cho mốc 2015 |
| Tham chiếu độc lập | `projects/sat-io/open-datasets/GMW/extent/GMW_V3` (Global Mangrove Watch, đến 2020) |
| Ranh giới vùng | `shapefile_commune/VungNghiencuu.*` (tải lên GEE Assets, xem Hướng dẫn mục 2.5) |
| Biến phụ trợ | Nước lâu năm `JRC/GSW1_4/GlobalSurfaceWater`; độ cao `JAXA/ALOS/AW3D30/V3_2` (nếu không có, dùng `V2_2`) |
| Ảnh nền để gán nhãn | Bản đồ "Satellite" của Code Editor, Sentinel-2 màu thật của từng năm |
| Đọc / ghi | VS Code (soạn script và báo cáo), Google Sheets hoặc CSV (nhật ký, mẫu) |
| Quản lý bản | Git hoặc lưu file có ngày trong tên; nhật ký tuần bằng Markdown |

Cấu trúc thư mục bạn đề nghị người thực hiện dùng:

```
du_an/
  nhat_ky/           tuan_01.md ... tuan_12.md
  scripts/           T01_hello.js ... (đánh số theo tuần)
  mau_diem/          luat_gan_nhan.md, diem_mau.csv
  ket_qua/           bản đồ, bảng CSV, hình
  bao_cao/           bao_cao.docx, slide.pptx
```

**Mentor cần chuẩn bị trước tuần 1** (tuần 0, khoảng 4–6 giờ):
1. Tài khoản Earth Engine + Cloud project đã kích hoạt cho người thực hiện.
2. Thư mục repo, chia sẻ quyền truy cập, tạo cấu trúc thư mục ở trên.
3. Tải shapefile 109 xã lên GEE Assets của người thực hiện (hoặc chia sẻ asset của bạn).
4. Ba công cụ mà **repo hiện chưa có** (cần cho tuần 3, 5, 7). Nếu cần, nhờ tôi viết:
   - Script nền chạy toàn vùng: nhận ranh giới 109 xã làm AOI, có mặt nạ mây SCL, lựa chọn vùng lọc, thống kê theo tỉnh và xã, và chia nhỏ để không quá tải.
   - Script sinh điểm ngẫu nhiên phân tầng (theo bản đồ nền và theo tỉnh).
   - Script mẫu Random Forest đã sửa các lỗi thường gặp (chồng lấn tập, band nhiễu, `scale` sai), có xuất kết quả theo tỉnh.
5. Chốt giờ họp cố định mỗi tuần (45 phút) và kênh hỏi nhanh.

---

## 5. Kế hoạch 12 tuần

### Tổng quan

| Tuần | Chủ đề | Sản phẩm chính cuối tuần | Mốc |
|------|--------|--------------------------|-----|
| 1 | Làm quen GEE và JavaScript (vùng tập) | Script Hello + 5 bài tập | |
| 2 | Dữ liệu ảnh và loại mây (vùng tập) | Bảng so sánh 3 cách lọc mây | |
| 3 | NDVI, phương pháp nền: vùng tập rồi toàn vùng | Bản đồ nền vùng tập + số liệu toàn vùng | |
| 4 | Chọn vùng lọc, đánh giá phương pháp nền, đọc tài liệu | Báo cáo ngắn 2 trang | **Mốc 1** |
| 5 | Thiết kế hệ phân loại, học gán nhãn | Luật gán nhãn + 30 điểm mẫu thử | |
| 6 | Lập bộ điểm mẫu (khoảng 800 điểm, rải khắp các tỉnh) | Bộ điểm mẫu hoàn chỉnh | |
| 7 | Random Forest cho 2020 | Bản đồ 5 lớp 2020 + độ chính xác | |
| 8 | Random Forest cho 2025, so sánh hai nhánh | Bản đồ 2025 + bảng so sánh | **Mốc 2** |
| 9 | Biến động, ma trận chuyển đổi, thống kê theo tỉnh và xã | Bản đồ biến động cuối + xã điểm nóng | |
| 10 | Đánh giá độ chính xác cuối (kể cả theo tỉnh) | Bảng độ chính xác + thảo luận sai số | |
| 11 | Bản đồ chuẩn và bản nháp báo cáo | Bản nháp đầy đủ | |
| 12 | Hoàn thiện, kiểm tra tái lập, bảo vệ thử | Gói nộp cuối | **Mốc 3** |

Cách đọc mỗi tuần dưới đây: **Mục tiêu** (cần đạt), **Việc làm**, **Nộp cuối tuần**, **Đạt khi** (tiêu chí nghiệm thu), **Hỏi kiểm tra hiểu** (2 câu bạn hỏi để biết người thực hiện hiểu hay chỉ chép code).

---

### Tuần 1. Làm quen GEE và JavaScript

**Mục tiêu:** đăng nhập, chạy được script đầu tiên, hiểu các khái niệm cốt lõi.

**Việc làm:**
- Đọc Hướng dẫn **Mục 1** và **Mục 2**.
- Chạy script "Hello GEE" (mục 1.6 của Hướng dẫn), quan sát ảnh và danh sách band.
- Làm 5 bài tập nhỏ, mỗi bài một script ngắn:
  1. In số cảnh Sentinel-2 phủ vùng tập trong năm 2025.
  2. Đổi vùng sang một nơi khác trong ĐBSCL, đổi năm.
  3. Hiển thị ảnh Landsat 8 màu thật cùng năm.
  4. Vẽ AOI bằng công cụ Geometry, rồi thay bằng toạ độ gõ tay.
  5. Hiển thị lớp NDVI với bảng màu.
- Bắt đầu nhật ký tuần.
- Tài liệu bổ trợ (kiểm tra lại đường dẫn còn dùng được): <https://developers.google.com/earth-engine/guides> và khoá học miễn phí "End-to-End Google Earth Engine" của Spatial Thoughts.

**Nộp cuối tuần:** 5 script, ảnh chụp màn hình, nhật ký tuần 1.

**Đạt khi:** tự chạy lại được không cần nhìn hướng dẫn; đọc được thông báo lỗi đỏ trong Console và sửa được ít nhất 2 lỗi.

**Hỏi kiểm tra hiểu:** "`ee.Number` khác số JavaScript ở điểm nào?" và "Vì sao `print` hiện `Object` chứ không hiện giá trị ngay?"

---

### Tuần 2. Dữ liệu ảnh và loại mây

**Mục tiêu:** tạo được ảnh ghép sạch mây cho từng năm, và hiểu vì sao mây quyết định chất lượng cả đề tài.

**Việc làm:**
- Đọc Hướng dẫn **Mục 3**.
- Trên vùng tập, tạo ảnh ghép median 2020 và 2025 theo **ba cách**: (a) không lọc, (b) lọc `CLOUDY_PIXEL_PERCENTAGE` < 20, (c) lọc < 60 và mặt nạ SCL.
- In số cảnh của từng cách và từng năm, chụp ảnh màu thật để so sánh.
- Thử chuyển cách (c) sang toàn vùng (dùng ranh giới 109 xã, tải lên Assets) và xem số cảnh; ghi lại thời gian chạy.
- (Tuỳ chọn) làm ảnh ghép Landsat 8 cho 2015.

**Nộp cuối tuần:** bảng số cảnh 3 cách × 2 năm; 6 ảnh so sánh; một đoạn 5–7 câu giải thích vì sao chọn cách (c).

**Đạt khi:** giải thích được vì sao 2025 với cách (b) chỉ còn ít cảnh và ảnh còn mây. Số cảnh vùng tập gần với số tham chiếu (Hướng dẫn mục 3.3: 16 / 4 cho cách b, 33 / 29 cho cách c).

**Hỏi kiểm tra hiểu:** "Vì sao dùng median thay cho trung bình?" và "Lọc `filterDate` ngày kết thúc có được tính không?"

---

### Tuần 3. NDVI, phương pháp nền: vùng tập rồi toàn vùng

**Mục tiêu:** ra bản đồ biến động đầu tiên, và thấy tận mắt vì sao NDVI đơn thuần không đủ khi vùng rộng.

**Việc làm:**
- Đọc Hướng dẫn **Mục 4** (NDVI, ngưỡng) và **Mục 5** (mất / mới / ổn định).
- **Vùng tập (khoảng 2 ngày):** chạy [bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js) nguyên bản, đọc từng phần, chú thích tiếng Việt vào file của mình. Tự viết lại phần "mất / mới / ổn định" từ đầu (không nhìn file).
- **Toàn vùng (khoảng 2 ngày, mentor chạy cùng):** đổi AOI sang 109 xã, chạy NDVI > 0,25 cho 2020. So diện tích với GMW 2020 và **ghi lại con số** (tham chiếu: khoảng 655.000 ha so với khoảng 101.000 ha, đo ở 100 m). Chụp ảnh những nơi "rừng" thực ra là ruộng hoặc vườn.
- Ghi lại thời gian chạy và các lỗi hạn mức, nếu có.

**Nộp cuối tuần:** bản đồ nền vùng tập, bảng diện tích, script tự viết, bảng "NDVI toàn vùng so với GMW" kèm ảnh minh hoạ ít nhất 3 nơi nhầm.

**Đạt khi:** số liệu vùng tập gần với Hướng dẫn mục 6.3 (cho phép lệch nhỏ vì dữ liệu GEE cập nhật); giải thích được vì sao diện tích toàn vùng gấp nhiều lần GMW.

**Hỏi kiểm tra hiểu:** "Điểm ảnh nào được tô màu tím hồng, vì sao?" và "NDVI cao ở ruộng lúa khác NDVI cao ở rừng ngập mặn thế nào, hay chúng giống nhau?"

---

### Tuần 4. Chọn vùng lọc và đánh giá phương pháp nền (Mốc 1)

**Mục tiêu:** có vùng lọc chọn bằng bằng chứng, và biết phương pháp nền đúng đến đâu, sai ở đâu.

**Việc làm:**
- Đọc Hướng dẫn **mục 4.5** và **mục 6.3–6.4**.
- So sánh các **ứng viên vùng lọc** cho toàn vùng, theo hai tiêu chí: **Kappa trong vùng lọc** và **rừng GMW nằm ngoài vùng lọc (ha)**:
  1. Đa giác dải ven biển của repo (`aoi` trong `mangrove_analysis.js`).
  2. Khoảng cách tới biển 5, 8, 10 km (tham số `MAX_DIST_SEA_KM`; phương pháp này mới thử ở vùng tập, cần kiểm tra lại ở toàn vùng).
  3. Đa giác vẽ tay mở rộng (nếu cần).
- Bật `RUN_SWEEP` để xem Kappa theo ngưỡng NDVI.
- Tính diện tích rừng nền theo tỉnh cho 2020 và 2025.
- Đọc 2 tài liệu (mục 9, phần tài liệu tham khảo) và tóm tắt mỗi bài 5 dòng.
- **Ngày dự phòng:** dùng để bù nếu tuần 1–3 còn dở.

**Nộp cuối tuần:** báo cáo ngắn 2 trang "Phương pháp nền: vùng lọc đã chọn và vì sao, kết quả, độ chính xác, hạn chế".

**Mốc 1 (họp 60 phút):** xem báo cáo và demo bản đồ nền toàn vùng.

**Đạt khi:** có bảng so sánh các ứng viên vùng lọc và lựa chọn có lý do rõ ràng; giải thích được vì sao con số Kappa chưa phải "sự thật thực địa" (GMW cũng là bản đồ suy ra từ vệ tinh). Ở vùng tập, tham chiếu tôi đo được là Kappa 0,656 (dải 5 km); **với toàn vùng chưa có số tham chiếu**, mục tiêu của tuần này là lập ra số đó.

**Hỏi kiểm tra hiểu:** "Tăng vùng lọc thì được gì, mất gì?" và "Kappa 0,65 nghĩa là gì bằng lời thường?"

---

### Tuần 5. Thiết kế hệ phân loại và học gán nhãn

**Mục tiêu:** thống nhất hệ lớp và luật gán nhãn; người thực hiện gán nhãn ổn định.

**Việc làm:**
- Viết **luật gán nhãn 1 trang** cho 5 lớp:
  1. Rừng ngập mặn
  2. Mặt nước (sông, biển, kênh)
  3. Nuôi trồng thuỷ sản (ao tôm)
  4. Nông nghiệp và cây trồng khác
  5. Đô thị và đất trống
- Với mỗi lớp: mô tả ảnh màu thật trông thế nào, ví dụ điển hình và trường hợp "khó" (rừng xen ao tôm; đất ngập nước nông; bờ đê có cây). Quy ước xử lý điểm lai: **không lấy** điểm nằm ở ranh giới hoặc lai lẫn.
- Thiết kế mẫu: sinh điểm ngẫu nhiên **phân tầng theo tỉnh và theo bản đồ nền** (rừng ổn định, mất, mới, không rừng ổn định) bằng script mentor cung cấp. Mỗi tỉnh phải có điểm.
- Gán nhãn thử 30 điểm cho cả hai năm; mentor gán lại cùng 30 điểm độc lập.

**Nộp cuối tuần:** luật gán nhãn; 30 điểm đã gán nhãn kèm nhận xét khó khăn.

**Đạt khi:** mức đồng thuận giữa hai người gán nhãn trên 30 điểm thử tốt (mục tiêu: đồng ý trên 80% số điểm). Phần không đồng ý được dùng để sửa luật.

**Hỏi kiểm tra hiểu:** "Vì sao không lấy điểm ở ranh giới?" và "Vì sao mẫu phải rải khắp các tỉnh thay vì lấy nơi dễ nhận ra?"

---

### Tuần 6. Lập bộ điểm mẫu

**Mục tiêu:** hoàn thành khoảng **800 điểm** gán nhãn cho **cả hai năm** (2020 và 2025), rải khắp các tỉnh.

**Việc làm:**
- Gán nhãn theo lô nhỏ (50–100 điểm mỗi lần) để không mệt và giữ chất lượng. Ước tính khoảng 1,5 phút mỗi điểm cho hai năm, tổng khoảng 20 giờ; vì vậy tuần này cần khoảng 15 giờ và tuần 5 đã gán phần đầu.
- Mục tiêu số điểm: **mỗi lớp khoảng 150 điểm** (để tập kiểm tra có khoảng 45–50 điểm mỗi lớp). Lớp nào thiếu thì bổ sung điểm thủ công.
- Mentor kiểm tra lại 10% điểm ngẫu nhiên (khoảng 80 điểm).
- Lưu vào CSV (`id, lon, lat, tinh, nhan_2020, nhan_2025, ghi_chu`) và tải lên GEE Assets.

**Nộp cuối tuần:** `diem_mau.csv`, asset đã tải lên, bảng thống kê số điểm mỗi lớp, mỗi năm và mỗi tỉnh, kết quả kiểm tra 10% của mentor.

**Đạt khi:** đủ số điểm mỗi lớp; tỷ lệ đồng ý khi kiểm tra lại khoảng 85% trở lên; mỗi tỉnh có điểm.

**Hỏi kiểm tra hiểu:** "Điểm nào bạn ít chắc chắn nhất và vì sao?" và "Nếu lớp Nuôi trồng thuỷ sản chỉ có 15 điểm thì ảnh hưởng gì đến mô hình?"

---

### Tuần 7. Random Forest cho 2020

**Mục tiêu:** huấn luyện và chạy Random Forest, đọc được kết quả.

**Việc làm:**
- Đọc lại phần Random Forest trong code mẫu (mentor cung cấp).
- Chuẩn bị biến đầu vào: `B2, B3, B4, B8` (Sentinel-2: xanh dương, xanh lá, đỏ, cận hồng ngoại), `B11`, `NDVI`, `NDMI` (độ ẩm), độ cao, độ dốc. **Không** đưa band chất lượng hay góc chụp vào.
- Tách mẫu huấn luyện / kiểm tra **theo khối 10 × 10 km** (khoảng 70 / 30). Tập kiểm tra để dành, chưa đụng đến.
- Huấn luyện, xem tầm quan trọng của biến (`explain()`), chỉnh số cây bằng sai số out-of-bag. Đặt `seed` để chạy lại ra cùng kết quả.
- **Phân loại toàn vùng theo từng tỉnh** và xuất từng tỉnh ra Assets hoặc Drive, thay vì tính một lần cho cả vùng.

**Nộp cuối tuần:** bản đồ 5 lớp 2020, biểu đồ tầm quan trọng của biến, độ chính xác trên tập kiểm tra.

**Đạt khi:** chạy lại hai lần ra cùng bản đồ (nhờ `seed`); giải thích được vì sao tập kiểm tra tách theo khối.

**Hỏi kiểm tra hiểu:** "Random Forest là gì, vì sao gọi 'rừng'?" và "Nếu tách mẫu ngẫu nhiên từng điểm thì độ chính xác báo cáo sẽ thế nào và vì sao?"

---

### Tuần 8. Random Forest cho 2025 và so sánh hai nhánh (Mốc 2)

**Mục tiêu:** có bản đồ 2025 và biết Random Forest hơn / kém phương pháp nền ở đâu.

**Việc làm:**
- Áp dụng **cùng cấu hình, cùng mẫu (nhãn 2025)** để phân loại 2025.
- Lập bảng so sánh nhánh A và nhánh B trên cùng tập điểm kiểm tra: Kappa, User's và Producer's của lớp rừng, diện tích rừng; theo từng tỉnh.
- Xem trên bản đồ những nơi hai nhánh khác nhau và chụp lại; tìm nguyên nhân.

**Nộp cuối tuần:** bản đồ 2025, bảng so sánh, ba hình ví dụ vùng bất đồng.

**Mốc 2 (họp 60 phút):** duyệt bảng so sánh; **quyết định tiếp tục hay thu hẹp phạm vi** (mục 7).

**Đạt khi:** có kết luận có bằng chứng "nhánh nào tốt hơn, ở đâu, vì sao". Không đòi hỏi Random Forest phải thắng; kết quả trung thực mới là mục tiêu.

**Hỏi kiểm tra hiểu:** "Nếu hai bản đồ 2020 và 2025 phân loại độc lập, 'biến động' nào có thể là giả?" và "Nhánh nào cho ước lượng diện tích rừng lớn hơn, vì sao?"

---

### Tuần 9. Biến động, ma trận chuyển đổi, thống kê theo tỉnh và xã

**Mục tiêu:** ra bản đồ biến động cuối, biết rừng mất chuyển thành gì, và xã nào là điểm nóng.

**Việc làm:**
- So sánh hai bản đồ phân loại (post-classification comparison): tạo ma trận 5 × 5 (diện tích chuyển từ lớp i sang lớp j), toàn vùng và theo tỉnh.
- Rút ra bản đồ **rừng ổn định / mất / mới** và bản đồ **hướng chuyển đổi** của phần rừng mất.
- Thống kê theo 109 xã (`reduceRegions`, giống phần 3 của MAP05): tốc độ biến động ròng (ha/năm) mỗi xã, xếp hạng điểm nóng.
- **Kiểm tra độ bền:** chạy lại với (a) seed khác, (b) bỏ độ cao và độ dốc, (c) tắt mặt nạ SCL, (d) đổi vùng lọc của nhánh A. Xem kết luận (tăng hay giảm) có đổi chiều không.

**Nộp cuối tuần:** ma trận chuyển đổi (CSV), bản đồ biến động cuối, bảng xã điểm nóng, bảng kiểm tra độ bền.

**Đạt khi:** trả lời được "chênh lệch ròng có lớn hơn mức dao động khi đổi cách làm không?" Nếu không lớn hơn, kết luận phải ghi là "chưa chắc chắn". Với xã có diện tích rừng nhỏ, kết quả phải ghi chú là dễ nhiễu.

**Hỏi kiểm tra hiểu:** "Mất và mới cùng khoảng 1.650 ha nhưng ròng chỉ +31 ha (ở vùng tập): ta kết luận gì?" và "Vì sao ma trận chuyển đổi nhiều thông tin hơn một con số ròng?"

---

### Tuần 10. Đánh giá độ chính xác cuối

**Mục tiêu:** có bảng độ chính xác đầy đủ và biết đọc nó đúng.

**Việc làm:**
- Trên **tập kiểm tra chưa từng dùng**: ma trận nhầm lẫn, OA, Kappa, Producer's, User's, F1 của lớp rừng, cho 2020 và 2025; **theo từng tỉnh**.
- Độ chính xác của lớp biến động: dùng các điểm có nhãn hai năm (điểm nào thật sự mất / mới).
- Đối chiếu với GMW cho 2020.
- Đọc mục về ước lượng diện tích có hiệu chỉnh sai số (Olofsson và cộng sự, 2014); **làm phiên bản đơn giản nếu kịp, hoặc ghi rõ đây là hạn chế chưa làm**.
- Viết phần thảo luận sai số: nguồn gốc (mây, lai lẫn, ranh giới, mẫu ít, khác nhau giữa các tỉnh) và ảnh hưởng.

**Nộp cuối tuần:** bảng độ chính xác, một trang thảo luận sai số.

**Đạt khi:** không có số nào lấy từ tập đã dùng để huấn luyện hoặc chỉnh tham số; nêu được ít nhất 3 nguồn sai số cụ thể của đề tài; chỉ ra tỉnh nào độ chính xác thấp nhất và vì sao.

**Hỏi kiểm tra hiểu:** "Producer's Accuracy thấp của lớp rừng nghĩa là gì trên bản đồ?" và "Vì sao độ chính xác lớp biến động thấp hơn độ chính xác từng năm?"

---

### Tuần 11. Bản đồ chuẩn và bản nháp báo cáo

**Mục tiêu:** có sản phẩm trình bày được.

**Việc làm:**
- Làm bản đồ chuẩn: chú giải, hướng bắc, tỷ lệ, nguồn dữ liệu, tên và ngày tạo. Xuất GeoTIFF và PNG (toàn vùng và các khu phóng to).
- Biểu đồ: diện tích theo lớp, năm và tỉnh; ma trận chuyển đổi (dạng bảng nhiệt); so sánh hai nhánh; xếp hạng xã điểm nóng.
- Viết bản nháp báo cáo theo khung: Mở đầu → Vùng nghiên cứu và dữ liệu → Phương pháp → Kết quả → Thảo luận (hạn chế) → Kết luận.

**Nộp cuối tuần:** bản nháp báo cáo đầy đủ, các hình và bảng.

**Đạt khi:** mỗi con số trong báo cáo truy được về một script và một bảng trong thư mục kết quả.

**Hỏi kiểm tra hiểu:** "Hình nào là bằng chứng chính cho kết luận chính của bạn?" và "Bạn tin kết luận nào nhất, tin kết luận nào ít nhất?"

---

### Tuần 12. Hoàn thiện, kiểm tra tái lập, bảo vệ thử (Mốc 3)

**Mục tiêu:** đóng gói và bảo vệ được.

**Việc làm:**
- Sửa báo cáo theo nhận xét của mentor.
- **Kiểm tra tái lập:** một người khác chạy lại các script chính từ đầu trên tài khoản của họ, ra được các con số chính (phần chạy nặng có thể kiểm tra trên một tỉnh).
- Làm slide 12–15 trang; bảo vệ thử 15 phút và trả lời câu hỏi.
- Đóng gói: script, mẫu, kết quả, báo cáo, nhật ký.

**Nộp cuối tuần:** gói nộp cuối (8 sản phẩm ở mục 1), slide, nhật ký đầy đủ.

**Mốc 3:** bảo vệ thử và nghiệm thu.

**Đạt khi:** theo bảng chấm ở mục 6.

---

## 6. Tiêu chí nghiệm thu và bảng chấm

| Tiêu chí | Điểm | Đạt tốt khi |
|----------|------|-------------|
| Tái lập được | 25 | Người khác chạy script từ đầu ra được số chính; có `seed`; không có hằng số "ma thuật" chưa giải thích |
| Độ chính xác và kiểm chứng | 25 | Tập kiểm tra tách theo khối và không dùng để chỉnh; báo cáo đủ OA, Kappa, Producer's, User's, có theo tỉnh; có so GMW |
| Hiểu và giải thích | 20 | Trả lời được câu hỏi kiểm tra hiểu ở các tuần; giải thích được vì sao không dùng cách khác |
| Báo cáo và sản phẩm | 20 | Bản đồ chuẩn; bảng, hình khớp với văn bản; nêu hạn chế trung thực |
| Nhật ký và chủ động | 10 | Nhật ký đều mỗi tuần; ghi lỗi, cách sửa; tự thử trước khi hỏi |

**Mục tiêu độ chính xác tham khảo** (chưa được kiểm chứng cho ĐBSCL, đặt ra để có đích nhắm, không phải cam kết): OA trên tập kiểm tra khoảng 0,80 trở lên và User's / Producer's của lớp rừng khoảng 0,75 trở lên. Nếu không đạt, không được chỉnh mẫu hay tập kiểm tra để "ép" đạt; thay vào đó phân tích nguyên nhân trong báo cáo.

---

## 7. Rủi ro và phương án dự phòng

| Rủi ro | Dấu hiệu | Xử lý |
|--------|----------|-------|
| **Vượt hạn mức tính toán của GEE** (khả năng cao ở phạm vi này) | Lỗi "memory limit", quá thời gian, tác vụ Export lâu | Chia theo tỉnh; tăng `tileScale`; tính ở 100 m khi thử nghiệm, chỉ tính 30 m khi xuất cuối; xuất kết quả trung gian ra Assets |
| Chậm tiến độ ở tuần 1–3 | Sang tuần 4 vẫn chưa ra bản đồ nền | Dùng ngày dự phòng tuần 4; rút phần bài tập tuần 1; mentor chạy cùng ở tuần 3 |
| Gán nhãn quá lâu | Tuần 6 chưa đạt 400 điểm | Giảm xuống 500 điểm, gộp lớp 4 và 5 thành một lớp "Khác"; mentor gán giúp một phần |
| Random Forest không tốt hơn phương pháp nền | Mốc 2 cho thấy chênh lệch nhỏ | Vẫn hoàn thành; kết luận trung thực "không cải thiện đáng kể" là kết quả hợp lệ |
| Vùng lọc bỏ sót nhiều rừng thật | Rừng GMW nằm ngoài vùng lọc lớn (đa giác dải repo bỏ sót khoảng 69% rừng GMW của 109 xã) | Chọn vùng lọc rộng hơn theo bằng chứng ở tuần 4; nêu rõ trong báo cáo |
| Mây làm ảnh 2025 kém | Số cảnh ít, ảnh còn mảng mây | Bật SCL, nới ngưỡng mây; nếu vẫn kém, dùng ảnh ghép hai năm (2024–2025) và ghi rõ |
| Lớp thiếu mẫu, tỉnh thiếu mẫu | Lớp hoặc tỉnh có dưới 40 điểm | Bổ sung điểm thủ công; nếu không được, gộp lớp hoặc ghi chú độ chính xác tỉnh đó không đáng tin |
| Hai người gán nhãn bất đồng nhiều | Đồng thuận dưới 80% ở tuần 5 | Viết lại luật, thêm ví dụ minh hoạ, gán lại 30 điểm thử |
| Kết quả mâu thuẫn với GMW | Chênh lệch lớn ở một số tỉnh | Xem lại vùng lọc; ghi rõ GMW cũng có sai số; không tự động coi GMW là đúng |

**Phương án thu hẹp** (quyết định ở Mốc 2, tuần 8, nếu tiến độ chậm), theo thứ tự ưu tiên:
1. Giữ phương pháp nền cho **toàn vùng**, chỉ làm Random Forest cho **2–3 tỉnh trọng điểm** (nơi có nhiều rừng ngập mặn nhất), báo cáo rõ phạm vi của từng phương pháp.
2. Giảm số điểm mẫu xuống 500 và gộp lớp thành 4 lớp.
3. Bỏ thống kê theo xã, giữ thống kê theo tỉnh.
4. Phương án tối thiểu: chỉ phương pháp nền + vùng lọc chọn bằng bằng chứng + điểm tham chiếu tự chọn cho 2025 (Hướng dẫn mục 6.5) + báo cáo hạn chế. Đây vẫn là một đề tài hoàn chỉnh.

---

## 8. Cách bạn kèm người mới

**Họp hàng tuần (45 phút):**
1. 10 phút: người thực hiện demo trực tiếp trên máy (không chỉ đưa ảnh chụp).
2. 10 phút: bạn hỏi 2 câu kiểm tra hiểu của tuần đó.
3. 10 phút: xem lỗi và điểm vướng.
4. 10 phút: giao việc tuần sau, nói rõ "đạt khi".
5. 5 phút: ghi biên bản ngắn vào nhật ký.

**Quy tắc giúp người mới tự đứng được:**
- **Tự thử 30 phút hoặc 3 lần** trước khi hỏi; khi hỏi phải kèm thông báo lỗi nguyên văn và đoạn code liên quan.
- Đọc thông báo lỗi đỏ trong Console trước; dùng bảng xử lý lỗi ở Phụ lục A của Hướng dẫn.
- **Không chép code mà không hiểu**: mỗi đoạn dán vào phải có chú thích tiếng Việt do chính mình viết.
- Ghi nhật ký mỗi tuần: làm gì, ra gì, lỗi gì, học được gì, chưa hiểu gì.
- Lưu script có ngày trong tên hoặc dùng Git; không sửa đè bản đã nộp.
- Khi chạy toàn vùng: thử trên một tỉnh nhỏ trước, rồi mới chạy cả vùng.

**Dấu hiệu người thực hiện chưa hiểu (cần chậm lại):** nói được "cách chạy" nhưng không nói được "vì sao"; kết quả đẹp nhưng không giải thích được nguồn gốc con số; không dám đổi tham số để thử.

**Ba lỗi rất thường gặp cần tự bắt:**
1. Dùng tập kiểm tra để chỉnh tham số, rồi báo độ chính xác trên chính tập đó.
2. Tin bản đồ biến động khi hai năm dùng cách loại mây khác nhau.
3. Bỏ qua vùng lọc hoặc phân loại có giám sát, nên biến động "giả" và diện tích rừng phình to ở đất nông nghiệp.

---

## 9. Phụ lục

### Thuật ngữ nhanh

| Thuật ngữ | Ý nghĩa |
|-----------|---------|
| AOI | Vùng nghiên cứu |
| ROI (vùng lọc) | Phần của AOI mà phương pháp nền được áp dụng (dải ven biển) |
| Ảnh ghép (composite) | Ảnh tổng hợp từ nhiều cảnh trong một năm, thường bằng median |
| NDVI | Chỉ số thực vật, (NIR − Red) / (NIR + Red) |
| Random Forest | Thuật toán phân loại gồm nhiều cây quyết định, bỏ phiếu lấy kết quả |
| OOB (out-of-bag) | Sai số ước lượng bằng phần mẫu mỗi cây "không thấy" khi huấn luyện |
| Ma trận nhầm lẫn | Bảng đối chiếu lớp dự đoán và lớp thật |
| Producer's / User's Accuracy | Tỷ lệ bỏ sót / tỷ lệ thừa của một lớp (đọc theo hướng "thật" hoặc "bản đồ") |
| Kappa | Độ đồng thuận đã trừ phần trùng ngẫu nhiên |
| Ma trận chuyển đổi | Bảng diện tích chuyển từ lớp này sang lớp khác giữa hai thời điểm |
| Tile scale | Tham số của GEE để chia nhỏ tính toán, giảm lỗi hết bộ nhớ |

### Tài liệu tham khảo gợi ý

Kiểm tra lại thông tin trích dẫn (tập, trang) trước khi đưa vào báo cáo.

1. Gorelick, N. và cộng sự (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27.
2. Bunting, P. và cộng sự (2022). Global Mangrove Extent Change 1996–2020: Global Mangrove Watch Version 3.0. *Remote Sensing*, 14(15), 3657.
3. Olofsson, P. và cộng sự (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42–57.
4. Breiman, L. (2001). Random Forests. *Machine Learning*, 45, 5–32.
5. Congalton, R. G. (1991). A review of assessing the accuracy of classifications of remotely sensed data. *Remote Sensing of Environment*, 37, 35–46.
6. Baloloy, A. B. và cộng sự (2020). Development and application of a new mangrove vegetation index (MVI) for rapid and accurate mangrove mapping. *ISPRS Journal of Photogrammetry and Remote Sensing*, 166, 95–117.

**Đọc trước ở tuần 4:** bài 2 (mục phương pháp) và bài 1 (phần tổng quan). **Đọc ở tuần 10:** bài 3.

### Nhật ký tuần (mẫu)

```
Tuần: __   Ngày: __   Số giờ làm: __
Đã làm:
Kết quả / con số chính:
Lỗi gặp và cách sửa:
Điều mới học được:
Điều chưa hiểu:
Kế hoạch tuần sau:
```
