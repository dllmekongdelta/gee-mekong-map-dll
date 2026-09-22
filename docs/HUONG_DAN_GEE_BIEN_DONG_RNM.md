# Hướng dẫn làm bản đồ biến động rừng ngập mặn bằng Google Earth Engine (JavaScript)

**Dành cho:** người chưa từng dùng Google Earth Engine (GEE), làm việc hoàn toàn trên trình duyệt (Code Editor), không cần cài Python.
**Kết quả cuối:** một chuỗi bản đồ biến động rừng ngập mặn qua các mốc năm **1988, 1992, 1997, 2001, 2005, 2010, 2015, 2020, nay** cho một vùng nhỏ ở Đồng bằng sông Cửu Long (mũi Cà Mau) — mỗi giai đoạn giữa hai mốc liên tiếp chỉ **1 bản đồ gộp 3 lớp** (ổn định / mất / mới), không phải 3 bản đồ tách rời (Coverage / Loss / Gain như 3 file HTML gốc của repo) — kèm bảng diện tích theo mốc năm, bảng tốc độ biến động theo giai đoạn, so sánh giai đoạn gần nhất với lịch sử, và bảng độ chính xác. Mục 7 (mở rộng) hướng dẫn thêm cách tự thu thập mẫu trên bản đồ, dùng khi muốn đi xa hơn ngưỡng NDVI (ví dụ phân loại có giám sát nhiều lớp, xem đề cương 12 tuần).
**Thời gian:** khoảng 4–6 giờ cho Mục 1–6 nếu làm lần đầu (nhiều mốc năm hơn bản chỉ so 2 năm); Mục 7 tốn thêm nhiều giờ tuỳ số điểm mẫu cần thu thập.
**Căn cứ:** quy trình Python của repo này (`GEN01`–`GEN04`, `MAP03`, `MAP05`) được viết lại bằng JavaScript. Script hoàn chỉnh cho vùng mẫu, chạy toàn bộ 9 mốc năm: [gee_code_editor/bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js). Bản JavaScript đầy đủ cho toàn bộ ĐBSCL (cùng 9 mốc năm nhưng chưa có vùng lọc ROI, còn theo bảng màu Loss/Gain 9 sắc cũ) nằm ở [gee_code_editor/mangrove_analysis.js](../gee_code_editor/mangrove_analysis.js). Tài liệu này khớp với [docs/DE_CUONG_12_TUAN_BIEN_DONG_RNM.md](DE_CUONG_12_TUAN_BIEN_DONG_RNM.md) — Mục 1–6 ở đây là "nhánh A" (nền) của đề cương, Mục 7 phục vụ "nhánh B" (phân loại có giám sát) ở tuần 5 trở đi.

---

## Lộ trình 6 mục (+ Mục 7 mở rộng)

| #   | Mục                                              | Bạn làm được gì sau mục này                                                                  |
| --- | ------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| 1   | Tìm hiểu GEE                                     | Đăng nhập Code Editor, hiểu các khái niệm cốt lõi, chạy được script đầu tiên                 |
| 2   | Import và lấy dữ liệu liên quan                  | Tìm dataset, gọi ảnh Landsat / Sentinel-2 / GMW, vẽ vùng nghiên cứu (AOI), tải shapefile lên |
| 3   | Tiền xử lý: lọc mây và ảnh ghép theo năm         | Có 1 ảnh sạch đại diện cho mỗi mốc năm                                                       |
| 4   | Tính NDVI và phân loại rừng ngập mặn             | Có mặt nạ rừng ngập mặn (0/1) cho mỗi mốc năm, hiểu cách chọn ngưỡng                         |
| 5   | Phát hiện biến động và tính diện tích            | Có 1 bản đồ gộp 3 lớp cho MỖI giai đoạn, bảng ha, tỷ lệ %, tốc độ ha/năm, so sánh giai đoạn  |
| 6   | Làm hoàn chỉnh vùng mẫu và đánh giá độ chính xác | Có sản phẩm cuối: chuỗi bản đồ theo giai đoạn + các bảng trên + Overall Accuracy / Kappa     |
| 7   | (Mở rộng) Thu thập mẫu trên bản đồ               | Biết cách tự tạo điểm mẫu (thủ công hoặc ngẫu nhiên phân tầng) để kiểm chứng hoặc huấn luyện |

Luồng xử lý tổng quát:

```
Vẽ AOI → Với MỖI mốc năm (1988...nay): lấy ảnh vệ tinh → lọc mây → ảnh ghép median
       → tính NDVI → ngưỡng NDVI VÀ vùng lọc (ROI) = mặt nạ rừng của mốc đó
      → Với MỖI giai đoạn (2 mốc liên tiếp): so 2 mặt nạ = 1 bản đồ gộp 3 lớp
        (ổn định / mất / mới) -- không tách thành bản đồ Coverage/Loss/Gain riêng
      → Tính diện tích, tỷ lệ %, tốc độ ha/năm mỗi giai đoạn → so giai đoạn gần
        nhất với trung bình các giai đoạn lịch sử
      → Kiểm chứng (GMW + điểm tham chiếu) → Xuất bản đồ
      → (Mở rộng, Mục 7) Tự thu thập mẫu trên bản đồ → dùng cho kiểm chứng
        2 lớp hoặc huấn luyện phân loại nhiều lớp
```

---

## Mục 1. Tìm hiểu Google Earth Engine

### 1.1 GEE là gì?

GEE là nền tảng của Google để xử lý ảnh vệ tinh **ngay trên máy chủ của Google**. Bạn không tải ảnh về máy: bạn viết vài chục dòng lệnh, Google chạy tính toán trên toàn bộ kho ảnh (Landsat từ 1984, Sentinel-2 từ 2015…) rồi trả kết quả về bản đồ. Việc này rất hợp với bài toán biến động rừng, vì cần so nhiều năm ảnh trên một vùng rộng.

Có hai cách dùng GEE, cùng một hệ thống phía sau:

|                | Code Editor (web, JavaScript)             | Python API (geemap / Jupyter)                           |
| -------------- | ----------------------------------------- | ------------------------------------------------------- |
| Cách dùng      | Mở trình duyệt, gõ code, bấm Run          | Cài Python, đăng nhập bằng `ee.Authenticate()`          |
| Phù hợp        | Người mới, thử nhanh, xem kết quả tức thì | Tự động hoá, xuất HTML, chạy theo lịch (GitHub Actions) |
| Trong repo này | `gee_code_editor/mangrove_analysis.js`    | `GEN01`–`GEN06`, `MAP01`–`MAP05`                        |

Hướng dẫn này dùng **Code Editor**.

### 1.2 Đăng ký và mở Code Editor

1. Dùng tài khoản Google, vào <https://code.earthengine.google.com>.
2. Nếu chưa có quyền, đăng ký tại <https://earthengine.google.com/signup> (chọn mục dùng phi thương mại / nghiên cứu, học thuật).
3. GEE hiện yêu cầu gắn với một **Google Cloud project** (miễn phí cho phi thương mại). Làm theo hướng dẫn trên màn hình để tạo hoặc chọn project, đồng thời bật Earth Engine API. Repo Python dùng project `gee-mekong-map`, bạn có thể dùng project của riêng mình.
4. Mở lại Code Editor. Nếu thấy giao diện 4 khung như bên dưới là xong.

> Giao diện đăng ký của Google thay đổi theo thời gian. Nếu tên nút khác với mô tả, hãy làm theo hướng dẫn chính thức tại <https://developers.google.com/earth-engine/guides/access>.

### 1.3 Làm quen giao diện

```
┌──────────────┬──────────────────────────────────┬────────────────┐
│ Scripts      │  Thanh tìm kiếm (search dataset) │ Inspector      │
│ Docs         ├──────────────────────────────────┤ Console        │
│ Assets       │  Khung soạn code  [Run] [Save]   │ Tasks          │
│              ├──────────────────────────────────┴────────────────┤
│              │  BẢN ĐỒ (Layers ở góc phải trên, Map/Satellite)    │
└──────────────┴───────────────────────────────────────────────────┘
```

| Khung                    | Dùng để                                                            |
| ------------------------ | ------------------------------------------------------------------ |
| **Scripts**              | Lưu / mở script (New → File). Bấm **Save** hay Ctrl+S thường xuyên |
| **Docs**                 | Tra cứu hàm (gõ tên hàm, ví dụ `normalizedDifference`)             |
| **Assets**               | Dữ liệu của bạn tải lên (shapefile, raster, mẫu điểm)              |
| **Thanh tìm kiếm**       | Tìm dataset trong Data Catalog, ví dụ gõ `Landsat 8 Level 2`       |
| **Console**              | Nơi hiện kết quả của lệnh `print()` và thông báo lỗi (màu đỏ)      |
| **Inspector**            | Bấm vào bản đồ để xem giá trị điểm ảnh ở từng lớp                  |
| **Tasks**                | Nơi bấm **Run** để xuất file ra Google Drive (mục 5–6)             |
| **Layers** (trên bản đồ) | Bật / tắt / chỉnh độ trong suốt từng lớp `Map.addLayer()`          |
| **Geometry** (góc trên-trái bản đồ) | Vẽ điểm / đường / đa giác trực tiếp trên ảnh (dùng ở Mục 7) |

### 1.4 JavaScript tối thiểu bạn cần

Bạn chỉ cần biết 5 điều:

```javascript
var ten = "Cà Mau"; // var: khai báo biến
var nam = 2020; // số
var danhSach = [2015, 2020, 2025]; // mảng
var thamSo = { min: 0, max: 3000 }; // đối tượng (dictionary)
function binhPhuong(x) {
  return x * x;
} // hàm
// dòng bắt đầu bằng // là chú thích
```

Ghi chú khi đối chiếu với code Python trong repo:

| Python (repo)                                            | JavaScript (Code Editor)                |
| -------------------------------------------------------- | --------------------------------------- |
| `import ee` + `ee.Authenticate()` + `ee.Initialize(...)` | Không cần, Code Editor đã đăng nhập sẵn |
| `# chú thích`                                            | `// chú thích`                          |
| `def f(x):`                                              | `function f(x) {` … `}`                 |
| `f"{year}-01-01"`                                        | `year + '-01-01'`                       |
| `True / False / None`                                    | `true / false / null`                   |
| `mask_a.And(mask_b.Not())`                               | `maskA.and(maskB.not())` (chữ thường)   |
| `x.getInfo()`                                            | Không dùng, chỉ cần `print(x)`          |
| `geemap.Map().add_layer(...)`                            | `Map.addLayer(...)`                     |
| `df.to_csv(...)`                                         | `Export.table.toDrive(...)`             |
| Vòng `for` trên list                                     | `list.forEach(function (item) { ... })` |

> Nên viết theo kiểu JavaScript cũ (`var`, `function`), không dùng `let`, `const`, mũi tên `=>`, template string, vì Code Editor hỗ trợ tốt nhất kiểu này.

### 1.5 Các khái niệm cốt lõi của GEE

| Khái niệm                             | Hiểu đơn giản                                 | Ví dụ                 |
| -------------------------------------- | --------------------------------------------- | --------------------- |
| `ee.Image`                            | 1 ảnh, gồm nhiều **band** (kênh phổ)          | 1 cảnh Sentinel-2     |
| `ee.ImageCollection`                  | Bộ sưu tập nhiều ảnh                          | Tất cả ảnh Landsat 8  |
| `ee.Geometry`                         | Hình học: điểm, đường, đa giác                | Vùng nghiên cứu (AOI) |
| `ee.Feature` / `ee.FeatureCollection` | Hình học kèm bảng thuộc tính                  | Ranh giới các xã, điểm mẫu |
| `ee.Reducer`                          | Phép gộp: tổng, trung bình, median, histogram | Tổng diện tích rừng   |
| `scale`                               | Kích thước 1 điểm ảnh (mét) khi tính          | 30 m cho Landsat      |

**Điều dễ nhầm nhất: phía server và phía client.**
Mọi đối tượng bắt đầu bằng `ee.` nằm trên **máy chủ Google**, không phải trong trình duyệt của bạn. Vì vậy:

- Muốn xem giá trị, dùng `print(x)`, đừng dùng `if (x > 5)` với `x` là `ee.Number` (sẽ không chạy như mong đợi).
- Phép tính phải dùng hàm của GEE: `a.add(b)` chứ không phải `a + b` khi `a` là `ee.Number`.
- Nối chuỗi với số phía client (`'Năm ' + 2020`) thì bình thường.

### 1.6 Script đầu tiên (chạy thử ngay)

Tạo script mới (Scripts → New → File), dán, bấm **Run**:

```javascript
// Hello GEE: xem vùng Đất Mũi (Cà Mau) bằng ảnh Sentinel-2 năm 2020
var aoi = ee.Geometry.Rectangle([104.72, 8.56, 104.92, 8.74]);  // [Tây, Nam, Đông, Bắc]

// Loại điểm ảnh bị mây / bóng mây bằng band SCL (giải thích ở mục 3.5)
function boMay(img) {
  var scl = img.select('SCL');
  var xau = scl.eq(1).or(scl.eq(3)).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10));
  return img.updateMask(xau.not());
}

var anh = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate('2020-01-01', '2021-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
    .map(boMay)
    .median()
    .clip(aoi);

Map.centerObject(aoi, 11);
Map.addLayer(anh, {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000}, 'Sentinel-2 2020 (màu thật)');
print('Các band của ảnh:', anh.bandNames());
```

> **Nếu ảnh của bạn trắng xoá:** đó là mây. Vùng ven biển ĐBSCL nhiều mây quanh năm, nên gộp **toàn bộ** ảnh của năm (73 cảnh trong ví dụ này) mà không loại mây thì ảnh ghép vẫn trắng. Hai dòng `filter(...)` và `map(boMay)` ở trên chính là phần loại mây. Bạn có thể xoá chúng đi rồi Run lại để thấy sự khác biệt.

Nếu thấy bản đồ hiện ảnh vệ tinh mũi Cà Mau và Console in danh sách band, bạn đã sẵn sàng cho mục 2.

Nếu gặp lỗi, xem bảng xử lý lỗi cuối tài liệu.

---

## Mục 2. Cách import và lấy dữ liệu liên quan

### 2.1 Các dữ liệu cần cho bài toán này

Đây là đúng các nguồn mà pipeline Python của repo đang dùng:

| Mục đích                | Dataset ID                                        | Thời gian                  | Band dùng                | Ghi chú                                                 |
| ----------------------- | ------------------------------------------------- | -------------------------- | ------------------------ | ------------------------------------------------------- |
| Ảnh 1988–2010           | `LANDSAT/LT05/C02/T1_L2` (Landsat 5)              | 1984–2012                  | NIR `SR_B4`, Red `SR_B3` | Repo dùng cho 1988, 1992, 1997                          |
| Ảnh 2001–2010           | `LANDSAT/LE07/C02/T1_L2` (Landsat 7)              | 1999–2022                  | NIR `SR_B4`, Red `SR_B3` | Từ 2003 ảnh bị sọc (SLC-off), ảnh ghép median giúp giảm |
| Ảnh 2013 trở đi         | `LANDSAT/LC08/C02/T1_L2` (Landsat 8)              | 2013–                      | NIR `SR_B5`, Red `SR_B4` | Repo dùng cho 2015                                      |
| Ảnh 2017 trở đi         | `COPERNICUS/S2_SR_HARMONIZED` (Sentinel-2)        | ~2017–                     | NIR `B8`, Red `B4`       | Độ phân giải 10 m. Repo dùng cho 2020, 2025, 2026       |
| Kiểm chứng độc lập      | `projects/sat-io/open-datasets/GMW/extent/GMW_V3` | 1996, 2007–2010, 2015–2020 | `b1`                     | Global Mangrove Watch v3. **Không có** năm 2025/2026    |
| Ranh giới xã (tuỳ chọn) | `shapefile_commune/VungNghiencuu.*` trong repo    |                            |                          | Phải tự tải lên Assets (mục 2.5)                        |

Vì sao Landsat cho quá khứ và Sentinel-2 cho hiện tại: Landsat có lưu trữ từ thập niên 1980 nhưng chỉ 30 m; Sentinel-2 sắc nét hơn (10 m) nhưng mới có từ 2015–2017.

### 2.2 Tìm dataset trong Data Catalog

1. Gõ vào **thanh tìm kiếm** trên cùng, ví dụ `Sentinel-2 Level-2A`.
2. Chọn kết quả (biểu tượng ảnh). Một cửa sổ mô tả hiện ra, gồm: **Dataset Availability** (năm có dữ liệu), **Bands** (tên và ý nghĩa từng band), **Properties** (thuộc tính, ví dụ `CLOUDY_PIXEL_PERCENTAGE`), **Example Code**.
3. Bấm **Import** để chèn 1 dòng `var imageCollection = ee.ImageCollection(...)` vào đầu script.

Cách nên dùng hơn: **tự gõ ID** như ví dụ sau. Script sẽ tự đầy đủ, người khác chạy lại được ngay, không phụ thuộc vào các "import" ẩn ở đầu file.

```javascript
var l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2");
var s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED");
```

### 2.3 Xem bên trong một dataset

Thói quen quan trọng: **luôn kiểm tra dữ liệu trước khi dùng**.

```javascript
var s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED");
print("Tổng số ảnh:", s2.size());
print("Ảnh đầu tiên:", s2.first()); // mở ra xem band và thuộc tính
print("Tên band:", s2.first().bandNames());
```

Bấm mũi tên trong Console để mở rộng đối tượng. Chú ý các thuộc tính dùng để lọc mây: Landsat có `CLOUD_COVER`, Sentinel-2 có `CLOUDY_PIXEL_PERCENTAGE`.

### 2.4 Xác định vùng nghiên cứu (AOI)

**Cách A. Gõ toạ độ (nên dùng, tái lập được):**

```javascript
// Hình chữ nhật [Tây, Nam, Đông, Bắc], toạ độ kinh độ / vĩ độ (WGS84)
var AOI = ee.Geometry.Rectangle([104.72, 8.56, 104.92, 8.74]);
```

**Cách B. Vẽ tay:** dùng công cụ ở góc trên bên trái bản đồ (biểu tượng đa giác / chữ nhật), vẽ vùng, script sẽ tự có biến `geometry`. Đổi tên thành `AOI` bằng cách bấm vào tên biến trong khung code.

**Cách C. Đa giác chi tiết ĐBSCL:** repo có sẵn đa giác 974 đỉnh ở đầu file [gee_code_editor/mangrove_analysis.js](../gee_code_editor/mangrove_analysis.js) (biến `aoi`), sao chép nguyên khối vào script nếu muốn làm toàn vùng.

> **Lời khuyên chọn AOI rất quan trọng cho độ chính xác:** NDVI chỉ cho biết "có thực vật xanh", chứ không phân biệt được rừng ngập mặn với lúa, cây trồng, bờ ao tôm có cây… Vì vậy AOI nên là **dải ven biển có rừng ngập mặn chiếm ưu thế**, đừng lấy khung quá rộng vào sâu nội địa. Mục 6 có số liệu chứng minh điều này.

### 2.5 Tải shapefile lên Assets (tuỳ chọn: ranh giới xã)

Code Editor không đọc được file `.shp` trên máy bạn. Phải tải lên trước:

1. Khung **Assets** → **NEW** → **Shape files**.
2. Chọn cùng lúc các file `.shp`, `.shx`, `.dbf`, `.prj` (và `.cpg` nếu có) trong `shapefile_commune/`.
3. Đặt tên asset (ví dụ `VungNghiencuu`), bấm **Upload**, theo dõi ở tab **Tasks** đến khi xong.
4. Bấm vào asset → sao chép **Asset ID** (dạng `projects/<project-của-bạn>/assets/VungNghiencuu`; tài khoản cũ có thể là `users/<tên>/VungNghiencuu`).

```javascript
var xa = ee.FeatureCollection(
  "projects/<project-của-bạn>/assets/VungNghiencuu"
);
print("Số đối tượng:", xa.size());
print(xa.first()); // xem tên cột: ma_xa, ten_xa, ten_huyen, ten_tinh...
Map.addLayer(
  xa.style({ color: "008B8B", fillColor: "00000000", width: 2 }),
  {},
  "Ranh giới xã"
);
```

Nên lọc theo cột mã `ma_xa` (chỉ có số) thay vì tên tiếng Việt, vì tên có dấu trong dbf dễ bị lỗi mã hoá. Ví dụ, ranh giới xã Đất Mũi (mã `34017`, kiểm tra kiểu dữ liệu của cột bằng `print(xa.first())` để biết dùng số hay chuỗi):

```javascript
var datMui = xa.filter(ee.Filter.eq("ma_xa", "34017"));
```

### 2.6 Lọc dữ liệu: cú pháp chung

Mọi lần gọi ảnh đều theo cùng khuôn:

```javascript
var col = ee
  .ImageCollection("<ID dataset>")
  .filterBounds(AOI) // chỉ ảnh phủ vùng của bạn
  .filterDate("2020-01-01", "2021-01-01") // ngày cuối KHÔNG được tính
  .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)); // bỏ ảnh nhiều mây
```

> Ngày kết thúc của `filterDate` là **loại trừ**. Muốn lấy cả năm 2020 phải viết đến `2021-01-01`. (Python của repo dùng `2020-12-31` nên bỏ sót đúng ngày 31/12, ảnh hưởng không đáng kể, nhưng cách viết ở đây chính xác hơn.)

---

## Mục 3. Tiền xử lý: lọc mây và ảnh ghép theo năm

Vùng ven biển ĐBSCL nhiều mây, đặc biệt mùa mưa (tháng 5–11), và cây ngập mặn liên tục bị thuỷ triều che. Một ảnh đơn lẻ hiếm khi đủ dùng, nên ta gộp cả năm thành **1 ảnh ghép** (composite).

### 3.1 Ý tưởng

1. **Lọc cảnh:** giữ các cảnh có % mây thấp (Landsat: `CLOUD_COVER` < 30; Sentinel-2: `CLOUDY_PIXEL_PERCENTAGE` < 20 theo repo).
2. **Median theo từng điểm ảnh:** với mỗi vị trí, lấy giá trị **trung vị** qua tất cả các cảnh trong năm. Điểm ảnh bị mây / bóng mây ở vài cảnh sẽ bị loại nhờ trung vị.
3. **Cắt theo AOI** (`clip`) để tính nhanh hơn và bản đồ gọn.

Đây chính là hai hàm `get_landsat_composite` / `get_sentinel_composite` trong [GEN03_helper_functions.py](../GEN03_helper_functions.py).

### 3.2 Code

```javascript
function landsatComposite(collectionId, year, geom) {
  return ee
    .ImageCollection(collectionId)
    .filterBounds(geom)
    .filterDate(year + "-01-01", year + 1 + "-01-01")
    .filter(ee.Filter.lt("CLOUD_COVER", 30))
    .median()
    .clip(geom);
}

function sentinelComposite(collectionId, year, geom) {
  return ee
    .ImageCollection(collectionId)
    .filterBounds(geom)
    .filterDate(year + "-01-01", year + 1 + "-01-01")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    .median()
    .clip(geom);
}

var img2020 = sentinelComposite("COPERNICUS/S2_SR_HARMONIZED", 2020, AOI);
Map.centerObject(AOI, 11);
Map.addLayer(
  img2020,
  { bands: ["B4", "B3", "B2"], min: 0, max: 3000 },
  "Sentinel-2 2020"
);
```

Màu thật cho từng loại ảnh (dùng để kiểm tra bằng mắt):

| Ảnh         | `bands`                     | `min` | `max` |
| ----------- | --------------------------- | ----- | ----- |
| Sentinel-2  | `['B4','B3','B2']`          | 0     | 3000  |
| Landsat 5/7 | `['SR_B3','SR_B2','SR_B1']` | 7000  | 16000 |
| Landsat 8   | `['SR_B4','SR_B3','SR_B2']` | 7000  | 16000 |

### 3.3 Bắt buộc: đếm số cảnh trong ảnh ghép

```javascript
var soCanh = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(AOI)
    .filterDate('2025-01-01', '2026-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .size();
print('Số cảnh năm 2025:', soCanh);
```

Ảnh ghép chỉ tin cậy khi có đủ cảnh **và** đã loại mây. Khi chạy thử trên vùng mũi Cà Mau (ngày 21/09/2026), số cảnh Sentinel-2 phụ thuộc rất nhiều vào cách lọc:

| Cách làm                                      | Số cảnh 2020 | Số cảnh 2025 | Ảnh ghép                               |
| --------------------------------------------- | ------------ | ------------ | -------------------------------------- |
| Không lọc gì                                  | 73           | (rất nhiều)  | Trắng xoá vì mây                       |
| Chỉ lọc `CLOUDY_PIXEL_PERCENTAGE` < 20 (repo) | 16           | **4**        | 2020 khá sạch, 2025 còn nhiều mảng mây |
| Lọc < 60 và loại mây từng điểm ảnh (SCL)      | 33           | 29           | Sạch ở cả hai năm                      |

Ảnh ghép 2025 chỉ có 4 cảnh còn mây, nên khi so với 2020 sẽ tạo ra "biến động giả" (mục 3.5 có số liệu). Hãy luôn kiểm tra số cảnh và xem ảnh màu thật của từng năm trước khi tin vào bản đồ biến động.

### 3.4 Chọn năm

- Dùng ảnh **cả năm** (như trên), không chọn tuỳ tiện 1 tháng, để năm nào cũng có cùng "mùa" đại diện.
- Khi có thể, so sánh hai năm **cùng cảm biến** (ví dụ Sentinel-2 2020 với Sentinel-2 2025). Đổi cảm biến giữa hai năm (Landsat → Sentinel-2) có thể tạo chênh lệch do độ phân giải khác nhau (30 m so với 10 m). Repo Python cũng nêu nguyên tắc này khi so sánh 2020 → 2025.

### 3.5 Mặt nạ mây theo điểm ảnh (Sentinel-2): nên bật

Lọc theo % mây của **cả cảnh** là chưa đủ: cảnh 15% mây vẫn có mây ngay trên vùng của bạn, còn cảnh 30% mây có thể hoàn toàn sạch ở vùng đó. Cách tốt hơn là nới ngưỡng mây lên 60% (để có nhiều cảnh) và loại **từng điểm ảnh** bị mây, bóng mây bằng band phân loại `SCL`:

```javascript
function maskS2(img) {
  var scl = img.select('SCL');
  // 1 = hỏng/bão hoà, 3 = bóng mây, 8-9 = mây, 10 = mây ti
  var bad = scl.eq(1).or(scl.eq(3)).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10));
  return img.updateMask(bad.not());
}

var s2Sach = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(AOI)
    .filterDate('2025-01-01', '2026-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
    .map(maskS2)
    .median()
    .clip(AOI);
```

**Vì sao quan trọng:** trên vùng mẫu, cùng thuật toán và cùng ngưỡng NDVI 0,25, chỉ khác cách loại mây, kết quả biến động 2020 → 2025 khác hẳn:

| Cách loại mây                        | Rừng 2025 (ha) | Mất (ha) | Mới (ha) | Ròng (ha)        |
| ------------------------------------ | -------------- | -------- | -------- | ---------------- |
| Chỉ lọc % mây < 20 (4 cảnh, còn mây) | 23.051         | 4.329    | 2.260    | **−2.069** (−8%) |
| Mặt nạ SCL (29 cảnh, ảnh sạch)       | 24.708         | 2.932    | 2.448    | **−484** (−1,9%) |

Phần lớn mức "giảm 2.069 ha" ở dòng đầu là do mây trong ảnh 2025, không phải rừng mất thật. Script ở mục 6 bật `USE_SCL_MASK = true` theo mặc định.

---

## Mục 4. Tính NDVI và phân loại rừng ngập mặn

### 4.1 NDVI là gì?

Cây xanh hấp thụ ánh sáng đỏ (để quang hợp) và phản xạ mạnh cận hồng ngoại (NIR). Chỉ số thực vật NDVI khai thác điều đó:

```
NDVI = (NIR − Red) / (NIR + Red)      giá trị từ −1 đến +1
```

Nước → âm; đất trống / bùn → gần 0; thực vật xanh → dương, càng rậm càng cao.

Band khác nhau theo cảm biến (đúng như hàm `add_ndvi` trong [GEN03](../GEN03_helper_functions.py)):

| Cảm biến     | NIR     | Red     |
| ------------ | ------- | ------- |
| Landsat 5, 7 | `SR_B4` | `SR_B3` |
| Landsat 8, 9 | `SR_B5` | `SR_B4` |
| Sentinel-2   | `B8`    | `B4`    |

```javascript
function addNdvi(image, sensor) {
  var ndvi;
  if (sensor === "L5" || sensor === "L7") {
    ndvi = image.normalizedDifference(["SR_B4", "SR_B3"]);
  } else if (sensor === "L8" || sensor === "L9") {
    ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]);
  } else if (sensor === "S2") {
    ndvi = image.normalizedDifference(["B8", "B4"]);
  } else {
    throw new Error("Cảm biến không hợp lệ: " + sensor);
  }
  return image.addBands(ndvi.rename("NDVI"));
}

var img2020n = addNdvi(img2020, "S2");
Map.addLayer(
  img2020n.select("NDVI"),
  { min: -0.2, max: 0.8, palette: ["0000ff", "ffffcc", "78c679", "006837"] },
  "NDVI 2020"
);
```

### 4.2 Từ NDVI thành mặt nạ rừng: ngưỡng

Rừng ngập mặn = điểm ảnh có NDVI **lớn hơn ngưỡng**:

```javascript
var rung2020 = img2020n.select("NDVI").gt(0.25); // 1 = rừng, 0 = không phải rừng
Map.addLayer(
  rung2020.updateMask(rung2020),
  { palette: ["1a9850"] },
  "Rừng ngập mặn 2020"
);
```

`updateMask(rung)` làm trong suốt các điểm ảnh bằng 0, nên chỉ thấy phần rừng.

### 4.3 Chọn ngưỡng: đừng đoán, hãy kiểm chứng

Repo dùng **hai ngưỡng khác nhau theo cảm biến**:

```javascript
var NDVI_THRESHOLD_LANDSAT = 0.1;
var NDVI_THRESHOLD_SENTINEL = 0.25;
```

Lý do (nêu trong [GEN04](../GEN04_mangrove_layers.py) và file `_threshold_sweep.csv`): nhóm tác giả thử 7 mức ngưỡng từ 0,10 đến 0,30 và so với Global Mangrove Watch (GMW) cho các năm trùng nhau. Kết quả:

- **Landsat:** Kappa cao nhất ở 0,10 và giảm đều khi tăng ngưỡng (ví dụ 2010: 0,787 ở 0,10 so với 0,479 ở 0,30). Giữ 0,10.
- **Sentinel-2:** Kappa gần như phẳng trong khoảng 0,10–0,30 (0,745–0,748), nên nâng ngưỡng lên 0,25 giảm được lỗi "thừa" mà không mất Kappa.

Bài học: **ngưỡng phụ thuộc cảm biến và vùng**, phải đối chiếu với một nguồn tham chiếu. Mục 6.4 có đoạn code chạy đúng phép quét ngưỡng này cho vùng của bạn.

> **Lưu ý kỹ thuật quan trọng:** repo dùng trực tiếp giá trị số nguyên của ảnh Landsat `_L2` (chưa nhân hệ số 0,0000275 và trừ 0,2). Các ngưỡng 0,10 / 0,25 được chỉnh với cách tính đó. **Không** trộn với cách nhân hệ số, vì giá trị NDVI sẽ khác và ngưỡng phải quét lại.

### 4.4 Giới hạn của phương pháp (nên nói rõ khi báo cáo)

- NDVI không phân biệt rừng ngập mặn với thực vật khác (lúa, cây ăn trái, bờ ao). Cách giảm lỗi này nằm ở mục 4.5 (giới hạn không gian), không nằm ở việc đổi công thức chỉ số.
- Không dùng dữ liệu thực địa. Tham chiếu GMW cũng là bản đồ suy ra từ vệ tinh, có sai số riêng.
- Thuỷ triều, mùa vụ, mây làm NDVI dao động giữa các năm.

### 4.5 Công thức đúng hơn: NDVI kết hợp giới hạn không gian (ROI)

**Vấn đề:** ở vùng có cả đất liền (như khung Đất Mũi), NDVI > ngưỡng cũng bắt lúa, vườn cây, cây trồng. Code Python của repo tránh được vì AOI là dải ven biển vẽ tay, chỉ chứa rừng ngập mặn và ít cây khác.

**Công thức dùng trong script:**

```
Rừng ngập mặn (năm t) = NDVI(t) > ngưỡng   VÀ   điểm ảnh nằm trong vùng lọc (ROI)
```

ROI cố định theo thời gian (không đổi giữa hai năm), nên bản đồ biến động không bị "mất / mới" giả do ROI thay đổi. Có hai cách tạo ROI:

1. **Vẽ tay (chính xác nhất, giống code Python):** dùng công cụ Geometry vẽ đa giác dọc dải rừng, đặt tên `vungLoc`, rồi trong script viết `var ROI_POLYGON = vungLoc;`.
2. **Tự động theo khoảng cách tới biển:** đặt `MAX_DIST_SEA_KM = 5` (mặc định). Script lấy "biển" từ JRC Global Surface Water (nước tồn tại lâu năm), bỏ sông / kênh / ao hẹp, rồi giữ các điểm ảnh cách biển không quá 5 km.

**Tôi đã thử các công thức thay thế và đối chiếu GMW 2020.** Hai vùng thử: vùng chính Đất Mũi (A: `[104.72, 8.56, 104.92, 8.74]`) và một khung khác phía Đông Bắc, nhiều đất liền hơn (B: `[104.80, 8.70, 105.02, 8.86]`). Kappa toàn khung:

| Công thức                                                | Kappa vùng A | Kappa vùng B |
| -------------------------------------------------------- | ------------ | ------------ |
| NDVI > 0,25 (cả khung)                                   | **0,593**    | 0,370        |
| CMRI = NDVI − NDWI > 0,8                                 | 0,501        | 0,466        |
| MVI = (NIR − Green) / (SWIR1 − Green) > 3                | 0,524        | 0,399        |
| NDVI > 0,25 và NDMI (độ ẩm) > 0,3                        | 0,478        | 0,464        |
| NDVI thấp nhất trong năm (P10) > 0,2                     | 0,502        | 0,464        |
| NDVI > 0,25 và Dynamic World (cây + thực vật ngập) > 0,5 | 0,457        | 0,469        |
| NDVI > 0,25 và không phải đất nông nghiệp (ESA WorldCover) | 0,593      | 0,400        |
| **NDVI > 0,25 và cách biển ≤ 5 km**                      | 0,475        | **0,527**    |

Đọc kết quả:

- **Đổi chỉ số (CMRI, MVI, NDMI…) không phải lời giải.** Chúng cải thiện nhẹ ở vùng B nhưng làm kém đi ở vùng A. Thêm điều kiện độ ẩm hay NDVI chặt hơn lên trên ROI cũng chỉ thay đổi Kappa trong khoảng từ −0,04 đến +0,05. Lý do: rừng ngập mặn, ruộng lúa và vườn cây có phổ rất giống nhau ở ảnh cả năm.
- **Giới hạn không gian mới là yếu tố quyết định ở vùng nhiều đất liền** (vùng B: Kappa 0,37 → 0,53, User's 0,48 → 0,70–0,83).
- **Nhưng cắt càng hẹp càng mất rừng thật.** Ở vùng A, rừng ngập mặn (theo GMW) vào sâu ít nhất 8 km, nên Kappa toàn khung thấp hơn khi cắt ở 3–5 km:

| Khoảng cách tới biển | Vùng A: Kappa toàn khung | Vùng A: Kappa chỉ trong ROI | Vùng B: Kappa toàn khung |
| -------------------- | ------------------------ | --------------------------- | ------------------------ |
| Không giới hạn       | 0,593                    | 0,593                       | 0,370                    |
| ≤ 3 km               | 0,360                    | 0,724                       | 0,509                    |
| ≤ 5 km               | 0,475                    | 0,656                       | 0,527                    |
| ≤ 8 km               | 0,573                    | 0,608                       | 0,456                    |

"Kappa toàn khung" coi rừng GMW nằm ngoài ROI là bị bỏ sót. "Kappa chỉ trong ROI" chỉ tính trong vùng phương pháp được áp dụng, giống cách code Python của repo đánh giá (AOI = dải ven biển). Hai cách đều đúng, nhưng phải nói rõ khi báo cáo.

**Cách chọn khoảng cách:**

1. Chạy script, bật lớp **Vùng lọc (ROI)** trên nền ảnh vệ tinh và kiểm tra bằng mắt: ROI có phủ hết dải rừng thật không? Có lấn vào ruộng, vườn không?
2. Xem dòng **Rừng GMW nằm ngoài ROI (ha)** ở Console. Con số lớn nghĩa là ROI đang loại cả rừng thật, hãy tăng `MAX_DIST_SEA_KM` (Đất Mũi có rừng quốc gia nên có thể cần 8 km) hoặc vẽ tay `ROI_POLYGON`.
3. Với vùng chỉ có dải rừng hẹp ven biển, `ROI_POLYGON` vẽ tay bám sát dải rừng luôn tốt hơn khoảng cách cố định.

> Khoảng cách tới biển chỉ là ước lượng thô, dựa vào ranh giới nước của JRC. Mục đích là loại bỏ vùng đất liền sâu, không phải xác định chính xác ranh giới rừng.

---

## Mục 5. Phát hiện biến động và tính diện tích

### 5.1 Logic: so sánh hai mặt nạ (áp dụng cho MỖI giai đoạn)

Với mặt nạ mốc trước **A** và mốc sau **B** (1 = rừng), mỗi điểm ảnh rơi vào 1 trong 4 trường hợp:

| A   | B   | Ý nghĩa                       | Phép tính (JS)           |
| --- | --- | ------------------------------ | ------------------------ |
| 1   | 0   | **Mất rừng** (loss)           | `maskA.and(maskB.not())` |
| 0   | 1   | **Rừng mới** (gain)           | `maskB.and(maskA.not())` |
| 1   | 1   | **Ổn định** (rừng cả hai mốc) | `maskA.and(maskB)`       |
| 0   | 0   | Không phải rừng               | (bỏ qua)                 |

Đây là đúng logic của [MAP01](../MAP01_Mangrove_LOSS.ipynb) và [MAP02](../MAP02_Mangrove_GAIN.ipynb) trong repo, áp dụng cho **mỗi cặp mốc năm liên tiếp**: với 9 mốc (1988, 1992, 1997, 2001, 2005, 2010, 2015, 2020, nay) thì có 8 giai đoạn, tức lặp lại đúng phép tính dưới đây 8 lần.

> **Khác với repo Python gốc** (3 sản phẩm tách rời: `Mangrove_COVERAGE_map.html`, `Mangrove_LOSS_map.html`, `Mangrove_GAIN_map.html`, mỗi loại 1 bảng màu 9 sắc riêng cho 9 giai đoạn): ở đây mỗi giai đoạn chỉ có **1 bản đồ**, gộp mất và mới vào cùng 3 lớp. Vì luôn chỉ có 3 lớp (Ổn định / Mất / Mới) bất kể giai đoạn nào, **1 chú giải duy nhất dùng chung cho mọi giai đoạn** — không cần đổi màu theo giai đoạn như bảng ramp 9 sắc cũ.

> Các đoạn code ở mục 5 dùng biến `AOI`, `maskA`, `maskB` (mặt nạ rừng của 2 mốc liên tiếp, tạo theo mục 3–4). Trong script hoàn chỉnh ở mục 6.2, các biến này được thay bằng một vòng lặp qua toàn bộ 8 giai đoạn; đọc mục 5 để hiểu logic của 1 giai đoạn, rồi xem mục 6 để biết cách lặp cho cả chuỗi.

```javascript
var loss = maskA.and(maskB.not());
var gain = maskB.and(maskA.not());
var stable = maskA.and(maskB);

// Gộp 3 lớp thành 1 ảnh để làm 1 bản đồ duy nhất: 1 = ổn định, 2 = mất, 3 = mới
var bienDong = ee
  .Image(0)
  .where(stable, 1)
  .where(loss, 2)
  .where(gain, 3)
  .rename("change");
bienDong = bienDong.updateMask(bienDong.gt(0));

Map.addLayer(
  bienDong,
  { min: 1, max: 3, palette: ["1a9850", "c51b8a", "ffd92f"] },
  "Biến động rừng ngập mặn"
);
```

Màu chọn: xanh lá = ổn định, tím hồng = mất (cùng hệ màu tím của lớp LOSS trong repo), vàng = mới. Ba màu này nổi trên nền ảnh vệ tinh và phân biệt được nhau.

**Lặp cho toàn bộ 8 giai đoạn:** thay vì viết tay 8 lần, script ở mục 6.2 dùng một vòng `for` chạy qua mảng các mốc năm đã tính mặt nạ, tạo ra 8 ảnh `bienDong` (1 cho mỗi giai đoạn) và thêm mỗi ảnh làm 1 lớp riêng trên bản đồ — chỉ giai đoạn gần nhất hiện sẵn, các giai đoạn khác tự bật ở khung Layers.

### 5.2 Tính diện tích (ha)

`ee.Image.pixelArea()` cho diện tích mỗi điểm ảnh (m²). Nhân với mặt nạ rồi cộng lại:

```javascript
function areaHa(binary) {
  var tong = binary.multiply(ee.Image.pixelArea()).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: AOI,
    scale: 30, // mét; dùng cùng 1 scale cho mọi phép tính
    maxPixels: 1e13,
    bestEffort: true,
  });
  return ee.Number(tong.values().get(0)).divide(10000); // m² → ha
}

print("Rừng mốc A (ha):", areaHa(maskA));
print("Mất rừng (ha):", areaHa(loss));
print("Rừng mới (ha):", areaHa(gain));
```

Vì sao `scale: 30`: đủ mịn cho Landsat, và dùng chung 30 m cho cả Sentinel-2 cho phép so sánh công bằng giữa các mốc năm (giống `SCALE_M = 30` ở MAP05). Gọi hàm này cho **cả 9 mốc năm**, không chỉ 2 mốc, để có bảng diện tích đầy đủ (mục 6.2, phần 5 của script).

### 5.3 Biến động ròng, tỷ lệ % và tốc độ hằng năm (để SO SÁNH giữa các giai đoạn)

Một mình số ha "mất" hay "ròng" không nói lên giai đoạn nào biến động mạnh hơn: các giai đoạn dài khác nhau (4–6 năm) và diện tích rừng đầu kỳ khác nhau. Cần chuẩn hoá bằng hai cách:

```
Ròng (ha)         = Mới − Mất
Tỷ lệ mất (%)     = Mất / Rừng đầu kỳ × 100
Tỷ lệ mới (%)     = Mới / Rừng đầu kỳ × 100
Tốc độ (ha/năm)   = Ròng / số năm giữa hai mốc
```

- **Tỷ lệ %** chuẩn hoá theo diện tích rừng ban đầu: mất 500 ha trên nền 15.000 ha (3,3%) đáng lo hơn nhiều so với mất 500 ha trên nền 100.000 ha (0,5%), dù cùng số ha.
- **Tốc độ ha/năm** chuẩn hoá theo thời gian: giai đoạn 6 năm (2020 → nay) và giai đoạn 4 năm (2001-2005) không thể so trực tiếp số ròng, phải chia cho số năm (giống cột `annual_rate_ha_yr` trong MAP05).

Script ở mục 6.2 tính cả 3 chỉ số này cho **mỗi giai đoạn**, gộp vào 1 bảng để so sánh trực quan giai đoạn nào biến động mạnh nhất.

```javascript
var bang = ee.FeatureCollection([
  ee.Feature(null, {
    giai_doan: "A-B",
    mat_ha: areaHa(loss),
    moi_ha: areaHa(gain),
    ty_le_mat_pct: areaHa(loss).divide(areaHa(maskA)).multiply(100),
    ty_le_moi_pct: areaHa(gain).divide(areaHa(maskA)).multiply(100),
  }),
]);
print(bang);
```

### 5.4 So sánh nhiều giai đoạn: bảng biến động và z-score so với lịch sử

Sau khi có bảng biến động của cả 8 giai đoạn, câu hỏi tiếp theo là: **giai đoạn gần nhất có gì khác thường so với lịch sử?** Cách đơn giản (đơn giản hoá từ Phần 2 của `MAP05_Validation_RecentChange.ipynb`): so tốc độ ha/năm của giai đoạn gần nhất với **trung bình và độ lệch chuẩn** của tốc độ các giai đoạn trước đó.

```javascript
// rates = mảng tốc độ ha/năm của TỪNG giai đoạn, theo đúng thứ tự thời gian
var historicalRates = ee.List(rates).slice(0, rates.length - 1); // bỏ giai đoạn cuối
var recentRate = ee.List(rates).get(rates.length - 1); // giai đoạn cuối = gần nhất

var histMean = ee.Number(historicalRates.reduce(ee.Reducer.mean()));
var histStd = ee.Number(ee.List(historicalRates).reduce(ee.Reducer.stdDev()));
var zScore = ee.Number(recentRate).subtract(histMean).divide(histStd);
```

Đọc `zScore`: |z| ≥ 2 nghĩa là tốc độ gần đây lệch khá xa so với biến thiên lịch sử, đáng nêu trong báo cáo; |z| < 2 nghĩa là còn trong biên độ dao động bình thường. Với chỉ 7 giai đoạn lịch sử làm mẫu (như ở vùng tập), đây là chỉ số **mô tả/khám phá**, không phải kiểm định giả thuyết chặt chẽ — đúng như cách MAP05 tự giới hạn kết luận của nó.

### 5.5 Kiểm tra độ bền của kết quả (đừng bỏ qua, cho MỖI giai đoạn)

Trước khi kết luận "giai đoạn X mất Y ha", tự hỏi:

1. Hai ảnh ghép của giai đoạn đó có **số cảnh** tương đương không (mục 3.3)? Các mốc Landsat cũ (1988–2010) thường có ít cảnh hơn Sentinel-2 nhiều.
2. Đổi ngưỡng NDVI ±0,05 hoặc bật mặt nạ mây (mục 3.5), xu hướng (tăng / giảm) của giai đoạn đó có **giữ nguyên** không?
3. Chênh lệch ròng có **lớn hơn** mức dao động do 1 và 2 gây ra không?

Nếu không, kết luận chỉ là "chưa chắc chắn" cho giai đoạn đó — không cần loại cả giai đoạn khỏi bảng, chỉ cần ghi chú rõ trong báo cáo. Đây là tinh thần của phần kiểm tra độ bền ngưỡng NDVI được mô tả trong README của repo.

### 5.6 Chú giải bản đồ (1 chú giải, dùng chung cho mọi giai đoạn)

```javascript
function hangChuGiai(mau, chu) {
  var o = ui.Label("", {
    backgroundColor: mau,
    padding: "8px",
    margin: "0 6px 4px 0",
  });
  var t = ui.Label(chu, { margin: "0 0 4px 0", fontSize: "12px" });
  return ui.Panel([o, t], ui.Panel.Layout.Flow("horizontal"));
}
var chuGiai = ui.Panel({
  style: { position: "bottom-right", padding: "8px 12px" },
});
chuGiai.add(ui.Label("Biến động rừng ngập mặn", { fontWeight: "bold" }));
chuGiai.add(hangChuGiai("#1a9850", "Ổn định"));
chuGiai.add(hangChuGiai("#c51b8a", "Mất rừng"));
chuGiai.add(hangChuGiai("#ffd92f", "Rừng mới"));
Map.add(chuGiai);
```

Vì chỉ có 3 lớp và dùng chung cho mọi giai đoạn, chú giải này không cần vẽ lại khi bạn bật lớp biến động của giai đoạn khác trong khung Layers — nó luôn đúng cho bất kỳ giai đoạn nào đang hiện.

---

## Mục 6. Hoàn thành vùng mẫu ĐBSCL và tính độ chính xác

### 6.1 Vùng mẫu

**Đất Mũi, Cà Mau** (mũi cực Nam), hình chữ nhật `[104.72, 8.56, 104.92, 8.74]`, khoảng 22 × 20 km. Vùng này được chọn vì rừng ngập mặn chiếm ưu thế ven biển, có dữ liệu GMW để đối chiếu, và đủ nhỏ để mọi phép tính chạy trong vài phút. Đa giác Đất Mũi trong shapefile xã của repo (`ma_xa` = 34017) có khung bao `[104.71, 8.56, 104.92, 8.73]`, gần như trùng với hình chữ nhật này.

Sản phẩm cần có sau mục này:

- [ ] 8 bản đồ biến động 3 lớp (ổn định / mất / mới), 1 cho mỗi giai đoạn giữa 9 mốc năm 1988→nay, dùng chung 1 chú giải
- [ ] Bảng diện tích (ha) theo từng mốc năm
- [ ] Bảng biến động theo giai đoạn: mất / mới / ròng (ha), tỷ lệ % (so với rừng đầu kỳ), tốc độ ha/năm
- [ ] So sánh giai đoạn gần nhất với trung bình các giai đoạn lịch sử (z-score)
- [ ] Bảng độ chính xác so với GMW cho các mốc có tham chiếu (1997≈1996, 2010, 2015, 2020): Overall Accuracy, Producer's / User's Accuracy, Kappa
- [ ] File GeoTIFF (1 mỗi giai đoạn) + CSV xuất ra Google Drive

Toàn bộ do một file làm ra: [gee_code_editor/bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js).

### 6.2 Script hoàn chỉnh

Script hoàn chỉnh nằm trong một file riêng, đã kiểm tra cú pháp: [gee_code_editor/bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js).

1. Mở file trong VS Code, chọn hết (Ctrl+A), sao chép (Ctrl+C).
2. Trong Code Editor: **Scripts → NEW → File**, đặt tên, dán vào khung code.
3. Bấm **Run**. Chỉ cần sửa khối `0. THAM SỐ` ở đầu file (AOI, danh sách mốc năm `MILESTONES`, ngưỡng NDVI mỗi mốc, ROI, công tắc mặt nạ mây).
4. **Chạy khoảng 2–5 phút** (9 mốc năm × nhiều phép tính), lâu hơn hẳn bản chỉ so 2 năm — đây là bình thường, không phải lỗi.

File gồm 11 phần:

| Phần | Nội dung                                                       | Mục hướng dẫn |
| ---- | ---------------------------------------------------------------- | ------------- |
| 0    | Tham số: `MILESTONES` (9 mốc năm), `ROI_POLYGON`/`MAX_DIST_SEA_KM` | 4.5, 6.1    |
| 1    | Hàm: ROI, mặt nạ mây, ảnh ghép + NDVI theo cảm biến, diện tích, độ chính xác | 3, 4  |
| 2    | Mặt nạ rừng cho TỪNG mốc năm (vòng lặp qua `MILESTONES`)          | 4, 5.1        |
| 3    | Phát hiện biến động cho TỪNG giai đoạn (vòng lặp qua các cặp mốc liên tiếp) | 5.1     |
| 4    | Bản đồ: 1 lớp biến động/giai đoạn + 1 chú giải chung              | 5.1, 5.6      |
| 5    | Bảng diện tích theo mốc năm                                       | 5.2           |
| 6    | Bảng biến động theo giai đoạn (mất/mới/ròng/%/tốc độ) + z-score so lịch sử | 5.3, 5.4 |
| 7    | Độ chính xác so với GMW cho các mốc trùng                         | 6.3           |
| 8    | Quét ngưỡng NDVI (tuỳ chọn, `RUN_SWEEP = true`)                   | 6.4           |
| 9    | Điểm tham chiếu tự chọn cho mốc 'nay' (tuỳ chọn, bỏ dấu chú thích) | 6.5, Mục 7   |
| 10   | Xuất GeoTIFF (mỗi giai đoạn) và CSV ra Google Drive                | 6.2           |

> **Lưu ý khi dán code:** nếu VS Code tự định dạng file bằng Prettier, hãy dùng file `.prettierrc` ở gốc repo (đã có). Cấu hình mặc định của Prettier 3 thêm dấu phẩy thừa sau tham số cuối của lời gọi hàm (dạng `Map.addLayer(a, b, "tên",` rồi xuống dòng `);`), và Code Editor không chấp nhận cú pháp đó.

Sau khi bấm **Run**:

1. **Console** hiện số cảnh từng mốc năm, bảng diện tích theo mốc, bảng biến động theo giai đoạn, z-score, và độ chính xác so với GMW. Đợi vài phút nếu kết quả chưa hiện hết.
2. **Bản đồ** hiện lớp "BIẾN ĐỘNG 2020 - nay" (giai đoạn gần nhất). Bật thêm các giai đoạn khác ở góc phải trên (Layers) — mỗi giai đoạn là 1 lớp riêng, dùng chung 1 chú giải.
3. Bấm vào bản đồ, xem tab **Inspector** để đối chiếu giá trị từng lớp tại điểm đó.
4. Tab **Tasks** hiện 10 việc xuất file (8 GeoTIFF, 1 mỗi giai đoạn, + 2 CSV): bấm **Run** ở từng dòng → xác nhận → file xuất hiện trong Google Drive của bạn.

### 6.3 Số liệu tham chiếu để bạn đối chiếu

Kết quả khi tôi chạy cùng logic (`USE_SCL_MASK = true`, `MAX_DIST_SEA_KM = 5`, ngưỡng 0,10 cho Landsat / 0,25 cho Sentinel-2) bằng Python API ngày 22/09/2026. Dữ liệu GEE có thể được cập nhật nên số của bạn có thể lệch nhẹ; nếu lệch nhiều là dấu hiệu bạn đã làm khác đi. ROI (cách biển ≤ 5 km) rộng **34.909 ha**.

**Diện tích rừng theo mốc năm (trong ROI):**

| Mốc năm                | 1988   | 1992   | 1997   | 2001   | 2005   | 2010   | 2015   | 2020   | nay (2026) |
| ----------------------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ---------- |
| Số cảnh trong ảnh ghép  | 12     | 9      | 18     | 8      | 20     | 9      | 24     | 33     | 34         |
| Diện tích rừng (ha)     | 16.823 | 13.139 | 15.849 | 18.494 | 15.698 | 17.526 | 19.968 | 18.623 | 18.147     |

**Cảnh báo ngay từ bảng này:** các mốc Landsat (1988–2015) có **rất ít cảnh** (8–24) so với Sentinel-2 (33–34). Hai mốc 1992 (9 cảnh) và 2001 (8 cảnh) đặc biệt ít — đây chính là 2 mốc "lõm/nhọn" bất thường trong bảng diện tích. Cần nghi ngờ đây một phần là composite nhiễu do thiếu ảnh sạch, không hẳn là biến động thật (xem mục 5.5).

**Bảng biến động theo giai đoạn:**

| Giai đoạn       | Mất (ha) | Mới (ha) | Ròng (ha) | Tốc độ (ha/năm) | % mất | % mới |
| --------------- | -------- | -------- | --------- | ---------------- | ----- | ----- |
| 1988–1992       | 4.170    | 485      | −3.685    | **−921,2**       | 24,8% | 2,9%  |
| 1992–1997       | 1.368    | 4.078    | +2.710    | **+542,0**       | 10,4% | 31,0% |
| 1997–2001       | 858      | 3.503    | +2.645    | **+661,2**       | 5,4%  | 22,1% |
| 2001–2005       | 3.481    | 685      | −2.796    | **−698,9**       | 18,8% | 3,7%  |
| 2005–2010       | 1.381    | 3.210    | +1.828    | **+365,6**       | 8,8%  | 20,4% |
| 2010–2015       | 515      | 2.957    | +2.442    | **+488,4**       | 2,9%  | 16,9% |
| 2015–2020       | 2.275    | 930      | −1.345    | **−269,0**       | 11,4% | 4,7%  |
| 2020–nay (2026) | 2.146    | 1.670    | −476      | **−79,4**        | 11,5% | 9,0%  |

**So sánh giai đoạn gần nhất với lịch sử (mục 5.4):** trung bình tốc độ 7 giai đoạn lịch sử (1988–2020) là **+24,0 ha/năm**, độ lệch chuẩn **646,6 ha/năm** — biến thiên rất lớn giữa các giai đoạn lịch sử. Tốc độ giai đoạn gần nhất (2020 → nay) là **−79,4 ha/năm**, cho z-score ≈ **−0,16**. Đọc kết quả: |z| < 2 nên **giai đoạn gần đây KHÔNG khác thường** so với biến động lịch sử của chính vùng này — biên độ dao động lịch sử (có giai đoạn tới ±900 ha/năm) còn lớn hơn nhiều mức giảm hiện tại.

**Độ chính xác so với GMW cho các mốc trùng (trong ROI):**

| Mốc (so với GMW)             | Overall Accuracy | Producer's | User's | Kappa |
| ----------------------------- | ----------------- | ---------- | ------ | ----- |
| 1997 vs GMW 1996 (lệch 1 năm) | 0,811              | 0,779      | 0,814  | 0,620 |
| 2010 vs GMW 2010              | 0,846              | 0,859      | 0,829  | 0,692 |
| 2015 vs GMW 2015              | 0,863              | 0,938      | 0,815  | 0,727 |
| 2020 vs GMW 2020              | 0,828              | 0,865      | 0,803  | 0,657 |

Cách đọc: Kappa 0,62–0,73 (trung bình đến khá) qua cả 4 mốc kiểm chứng được — phương pháp có mức tin cậy tương đối ổn định theo thời gian, không riêng năm 2020. Kappa cao nhất ở 2015 (0,727), thấp nhất ở 1997 (0,620, cũng là mốc so khớp gần đúng lệch 1 năm nên tự nhiên kém chính xác hơn).

Bốn bài học từ thử nghiệm:

- **Giới hạn không gian (ROI) vẫn cần thiết cho mọi mốc năm, không chỉ 2020/2025:** xem mục 4.5.
- **Độ tin cậy không đều theo thời gian:** các mốc Landsat cũ (đặc biệt 1992, 2001) có ít cảnh, nên số liệu các giai đoạn liền kề chúng (1988–1992, 1992–1997, 1997–2001, 2001–2005) kém tin cậy hơn các giai đoạn Sentinel-2 gần đây.
- **Biến thiên lịch sử tự nhiên đã rất lớn** (độ lệch chuẩn 646,6 ha/năm): một giai đoạn "giảm" không tự động là bất thường, phải so với z-score.
- Vì vậy, **độ chính xác so với GMW của một mốc không đủ để tin vào bản đồ biến động của một giai đoạn** — luôn kiểm tra số cảnh (mục 3.3) và độ bền theo ngưỡng/mặt nạ mây (mục 5.5) cho từng giai đoạn cụ thể bạn đang diễn giải.

### 6.4 Độ chính xác (b): quét ngưỡng NDVI

Đặt `RUN_SWEEP = true` và `SWEEP_YEAR = 2020` ở đầu script rồi Run lại. Script in độ chính xác của mốc đó với các ngưỡng 0,10–0,35 (giống `_threshold_sweep.csv` của repo). Kết quả tham chiếu dưới đây tính **khi không dùng ROI** (`MAX_DIST_SEA_KM = 0`), 2020, Sentinel-2, so với GMW — tôi chưa chạy lại phép quét với ROI, hãy bật `RUN_SWEEP = true` với cấu hình của bạn để có bảng đúng cho vùng của mình:

| Ngưỡng NDVI | Overall | Producer's | User's | Kappa |
| ----------- | ------- | ---------- | ------ | ----- |
| 0,10        | 0,819   | 0,943      | 0,765  | 0,634 |
| 0,15        | 0,814   | 0,919      | 0,769  | 0,624 |
| 0,20        | 0,807   | 0,891      | 0,774  | 0,611 |
| **0,25**    | 0,798   | 0,858      | 0,778  | 0,593 |
| 0,30        | 0,787   | 0,821      | 0,782  | 0,573 |
| 0,35        | 0,775   | 0,780      | 0,786  | 0,548 |

Ở vùng này, Kappa giảm nhẹ khi tăng ngưỡng còn User's tăng nhẹ (thừa ít hơn, bỏ sót nhiều hơn). Chênh lệch giữa các ngưỡng không lớn, nên ngưỡng 0,25 của repo là hợp lý và giữ được tính nhất quán với bản đồ toàn ĐBSCL. **Ngưỡng phải giữ cố định cho mọi mốc năm cùng cảm biến** — đổi ngưỡng cho một mốc mà không đổi mốc kia làm mọi phép so sánh giữa các giai đoạn mất ý nghĩa.

### 6.5 Độ chính xác (c): điểm tham chiếu tự chọn (đặc biệt cho mốc 'nay')

GMW không có năm 2026, nên mốc 'nay' cần tự lập điểm tham chiếu. Cách làm ở đây chỉ là bản tóm tắt nhanh dùng ngay cho script mục 6.2 — cách làm đầy đủ (kể cả khi dùng cho **mẫu huấn luyện** phân loại nhiều lớp, không chỉ điểm kiểm chứng 2 lớp) nằm ở **Mục 7** ngay sau đây.

1. Chuyển bản đồ sang **Satellite** để nhìn ảnh độ phân giải cao của Google.
2. Trong công cụ vẽ (góc trên trái bản đồ) bấm **Add a marker**, rồi bấm lên bản đồ để đặt điểm ở nơi bạn **chắc chắn là rừng ngập mặn**. Ghi ít nhất **50 điểm**, rải khắp AOI, cách nhau ≥ 100 m, đặt vào giữa các mảng rừng đồng nhất (tránh sát ranh giới).
3. Trong khung code, bấm biểu tượng bánh răng của layer vừa tạo:
   - Đổi tên thành `mangrovePts`
   - **Import as:** `FeatureCollection`
   - **Add property:** tên `ref`, giá trị `1`
4. Lặp lại cho các nơi **không phải rừng ngập mặn** (nước, bãi bùn, ao tôm, đất trống, rừng tràm, lúa…): layer `otherPts`, thuộc tính `ref = 0`, ít nhất 50 điểm.
5. Trong file script, ở phần `9.`, bỏ dấu `/*` và `*/` sau khi đã tạo 2 layer. Nội dung khối đó:

```javascript
/*
var refPts = mangrovePts.merge(otherPts);
var maskNay = maskByYear[LAST_YEAR];
var mau = maskNay.rename('pred').toInt().sampleRegions({
  collection: refPts, properties: ['ref'], scale: SCALE
});
var cm = mau.errorMatrix('ref', 'pred');   // hàng = thực tế, cột = dự đoán (0 = không rừng, 1 = rừng)
print('Ma trận nhầm lẫn mốc nay', cm);
print('Overall Accuracy:', cm.accuracy());
print("Producer's Accuracy [không rừng, rừng]:", cm.producersAccuracy());
print("User's Accuracy [không rừng, rừng]:",     cm.consumersAccuracy());
print('Kappa:', cm.kappa());
*/
```

Lưu ý khi tự lập điểm tham chiếu:

- Ảnh nền vệ tinh có thể không đúng năm bạn đang kiểm chứng. Hãy chọn các điểm mà tình trạng (rừng / không rừng) chắc chắn không đổi, hoặc đối chiếu thêm bằng Timelapse.
- Số điểm ít (~100) cho ước lượng dao động khá lớn. Hãy nêu số điểm khi báo cáo.
- Chọn điểm thủ công dễ thiên về nơi "dễ nhìn". Nếu cần chặt chẽ hơn, hãy tạo điểm ngẫu nhiên bằng `ee.FeatureCollection.randomPoints(AOI, 100, 42)` rồi gán nhãn từng điểm (xem Mục 7.3).
- Độ chính xác của **bản đồ biến động** thấp hơn độ chính xác của từng mốc, vì sai số hai mốc cộng dồn. Hãy đọc con số mất / mới với sự thận trọng.

### 6.6 Kiểm tra cuối và cách trình bày sản phẩm

Trước khi coi là xong:

- [ ] Ảnh màu thật của các mốc năm không còn mảng mây lớn (bật lớp `Ảnh <mốc>` để xem); mốc nào ít cảnh (mục 6.3) đã được ghi chú độ tin cậy thấp hơn
- [ ] Bản đồ trông hợp lý so với ảnh nền (rừng ven biển được tô, biển và ao không bị tô) ở giai đoạn gần nhất và ít nhất 1 giai đoạn cũ
- [ ] Đã bật lớp `Vùng lọc (ROI)`, kiểm tra ROI phủ hết dải rừng và không lấn vào ruộng / vườn; đã xem số `Rừng GMW nằm ngoài ROI`
- [ ] Đã có Overall Accuracy và Kappa so với GMW cho ít nhất 2 mốc
- [ ] Đã xem z-score của giai đoạn gần nhất so với lịch sử (mục 5.4) và giải thích được ý nghĩa
- [ ] Đã thử đổi ngưỡng / bật mặt nạ mây và xu hướng của giai đoạn gần nhất không đổi chiều (mục 5.5)
- [ ] Đã xuất GeoTIFF (từng giai đoạn) và CSV

Khi ghi vào báo cáo, nên nêu rõ:

> Chuỗi bản đồ biến động rừng ngập mặn 1988–nay vùng Đất Mũi được suy ra từ ngưỡng NDVI theo cảm biến (0,10 Landsat / 0,25 Sentinel-2) của ảnh ghép median cả năm, giới hạn trong dải cách biển không quá 5 km để hạn chế lẫn với cây trồng. Độ chính xác so với Global Mangrove Watch dao động Kappa 0,62–0,73 qua 4 mốc kiểm chứng được (1997, 2010, 2015, 2020). Tốc độ biến động ròng giai đoạn gần nhất (2020 → nay, −79,4 ha/năm) nằm trong biên độ dao động bình thường so với 7 giai đoạn lịch sử (trung bình +24,0, độ lệch chuẩn 646,6 ha/năm; z ≈ −0,16). Các mốc Landsat có ít cảnh (đặc biệt 1992 và 2001) khiến số liệu quanh chúng kém tin cậy hơn giai đoạn Sentinel-2 gần đây; GMW không có năm 2026 nên mốc 'nay' chưa được kiểm chứng trực tiếp bằng GMW (xem điểm tham chiếu tự chọn, mục 6.5/Mục 7).

### 6.7 Mở rộng ra toàn ĐBSCL

Khi đã quen, chuyển sang bản đầy đủ [gee_code_editor/mangrove_analysis.js](../gee_code_editor/mangrove_analysis.js): đa giác AOI 974 đỉnh, 9 mốc năm (1988–2026), 8 giai đoạn. Việc cần thêm để có độ tin cậy như MAP05 **và** khớp với cách gộp 3 lớp + ROI của mục 5–6:

- File này hiện **chưa có ROI riêng** — đa giác 974 đỉnh đã tự đóng vai trò như một `ROI_POLYGON` vẽ tay rất chi tiết cho toàn ĐBSCL, nên có thể giữ nguyên logic đó, chỉ cần thêm mặt nạ mây SCL (mục 3.5) cho Sentinel-2.
- Vẫn dùng bảng màu Loss/Gain 9 sắc riêng (2 lớp mỗi giai đoạn) thay vì 1 bản đồ gộp 3 lớp/giai đoạn. Muốn khớp với cách làm ở mục 5–6, đổi sang đúng logic `ee.Image(0).where(...)` như mục 5.1, dùng lại 1 chú giải 3 màu cho toàn bộ 8 giai đoạn.
- Tính diện tích từng mốc và từng giai đoạn (mục 5.2–5.4) bằng `reduceRegion`; với vùng lớn, tăng `scale` hoặc chia nhỏ theo tỉnh để không vượt giới hạn bộ nhớ.
- So sánh với GMW cho 1997 (dùng GMW 1996), 2010, 2015, 2020 (mục 6.3).
- Thống kê theo xã bằng `reduceRegions` trên tài sản shapefile xã (mục 2.5).
- Đây chính là "nhánh A" của [đề cương 12 tuần](DE_CUONG_12_TUAN_BIEN_DONG_RNM.md) khi mở rộng sang toàn vùng 109 xã. Nhánh B (phân loại nhiều lớp) cần mẫu — xem Mục 7.

---

## Mục 7 (Mở rộng). Thu thập mẫu để kiểm chứng hoặc huấn luyện

Mục 1–6 chỉ dùng ngưỡng NDVI, **không cần mẫu** (chỉ cần đối chiếu với GMW, một bộ dữ liệu công khai). Nhưng GMW có 2 hạn chế lớn:

1. Chỉ là bản đồ **rừng / không rừng** (raster), không có điểm mẫu cho bạn, và không phân biệt được nuôi trồng thuỷ sản / nông nghiệp / đô thị — nếu muốn tách các lớp này (như nhánh phân loại có giám sát của [đề cương 12 tuần](DE_CUONG_12_TUAN_BIEN_DONG_RNM.md), tuần 5–8), phải có mẫu của **từng lớp**.
2. Không có năm 2025/2026 — mốc 'nay' không kiểm chứng được bằng GMW, phải tự tạo điểm tham chiếu (đã nêu tóm tắt ở mục 6.5).

Vì vậy: **có, mẫu phải tự thu thập** — và **có, cách chuẩn để làm là chọn điểm ngay trên bản đồ GEE**, nhìn ảnh vệ tinh trực tiếp trong Code Editor. Đây đúng là cách đoạn code Random Forest tham khảo (vùng Cần Giờ) đã làm: các biến `Green_Forest`, `Water_body`, `Salt_Agric`, `Crop_Land`, `Urban` trong ví dụ đó chính là các FeatureCollection được tạo ra từ việc vẽ điểm/đa giác trực tiếp trên bản đồ.

### 7.1 Trước khi vẽ điểm: xác định 2 điều

1. **Mẫu để làm gì?**
   - (a) Chỉ **kiểm chứng** mặt nạ NDVI 2 lớp (rừng / không rừng) — đã đủ dùng cách ở mục 6.5, không cần đọc hết mục này.
   - (b) **Huấn luyện** một bộ phân loại nhiều lớp (ví dụ Random Forest) — cần nhiều mẫu hơn, đủ mỗi lớp, và cần tách tập huấn luyện / kiểm tra (mục 7.4).
2. **Bao nhiêu lớp?** Khớp với luật gán nhãn ở tuần 5 của đề cương 12 tuần — ví dụ 5 lớp: **Rừng ngập mặn / Mặt nước / Nuôi trồng thuỷ sản (ao tôm) / Nông nghiệp và cây trồng khác / Đô thị và đất trống**. Viết ra ví dụ điển hình và trường hợp "khó" (rừng xen ao tôm, đất ngập nước nông, bờ đê có cây) cho mỗi lớp trước khi vẽ điểm — nếu không, bạn sẽ gán nhãn không nhất quán giữa các lô làm khác ngày.

### 7.2 Cách 1: Chọn điểm thủ công ngay trên bản đồ (nhìn ảnh, tự quyết định)

Làm được ngay trong Code Editor, không cần công cụ nào khác.

1. Chuyển bản đồ sang **Satellite**, hoặc bật lớp ảnh màu thật của đúng năm cần lấy mẫu (mục 3.2) — **nhãn phải khớp với ảnh của năm đó**, không dùng ảnh nền hiện tại để gán nhãn cho năm 1997.
2. Phóng to (zoom) tới khu vực bạn **chắc chắn** thuộc 1 lớp, đồng nhất, không lẫn loại khác.
3. Dùng công cụ **Geometry** (góc trên-trái bản đồ) → chọn kiểu **Point** (hoặc **Marker**) → bấm từng điểm lên bản đồ.
4. Khi xong 1 lớp, bấm biểu tượng bánh răng của layer geometry vừa vẽ:
   - Đổi tên (ví dụ `rung2020`)
   - **Import as:** `FeatureCollection`
   - **Add property:** đặt tên cột (ví dụ `lop`), giá trị số cho lớp đó (ví dụ `0` = rừng ngập mặn)
5. Lặp lại, **mỗi lớp một layer riêng** (dễ kiểm tra, dễ sửa nếu lỡ tay), ví dụ `nuoc2020` (`lop = 1`), `aoTom2020` (`lop = 2`), `nongNghiep2020` (`lop = 3`), `doThi2020` (`lop = 4`).
6. Gộp (merge) tất cả thành 1 bộ mẫu:

```javascript
var mau2020 = rung2020
  .merge(nuoc2020)
  .merge(aoTom2020)
  .merge(nongNghiep2020)
  .merge(doThi2020);
print('Số điểm mỗi lớp:', mau2020.aggregate_histogram('lop'));
```

7. **Xuất mẫu ra Asset** để dùng lại nhiều lần (không phải vẽ lại mỗi lần Run script):

```javascript
Export.table.toAsset({
  collection: mau2020,
  description: 'mau_2020',
  assetId: 'mau_2020'
});
```

Sau khi tác vụ Export chạy xong (tab Tasks), nạp lại ở script khác bằng:

```javascript
var mau2020 = ee.FeatureCollection('projects/<project-của-bạn>/assets/mau_2020');
```

**Quy tắc khi bấm điểm thủ công** (khớp với luật gán nhãn ở đề cương, tuần 5):

- Đặt điểm vào **giữa** vùng đồng nhất, cách ranh giới với lớp khác ít nhất 1–2 điểm ảnh (≥ 20–30 m với Sentinel-2, ≥ 60–90 m với Landsat).
- Các điểm cùng lớp nên cách nhau ≥ 100 m, để không lấy nhiều điểm cùng mô tả 1 vị trí (tự tương quan không gian).
- **Không lấy** điểm ở nơi bạn còn nghi ngờ hoặc ở ranh giới lai giữa 2 lớp — bỏ qua, không cố đoán.
- Ghi lại luật này thành văn bản (1 trang) trước khi bắt đầu, đặc biệt nếu có nhiều người cùng gán nhãn.

**Ưu điểm:** nhìn ảnh thật nên chọn đúng, kiểm soát tốt loại đất, làm nhanh cho các lớp hiếm (ví dụ ao tôm nhỏ, khó rơi vào mẫu ngẫu nhiên).
**Nhược điểm:** tốn thời gian; **dễ thiên vị** chọn "nơi dễ nhìn, điển hình" — bộ mẫu có thể không đại diện hết sự đa dạng của vùng, làm độ chính xác đo được lạc quan hơn thực tế.

### 7.3 Cách 2: Vị trí ngẫu nhiên (hoặc ngẫu nhiên phân tầng), vẫn tự gán nhãn bằng mắt

Không có cách nào tự động gán nhãn — bạn luôn phải tự nhìn và quyết định lớp. Điều thay đổi ở đây là **vị trí điểm do máy chọn ngẫu nhiên**, không phải do bạn chọn "nơi dễ nhìn", để mẫu đại diện tốt hơn cho toàn vùng.

**Ngẫu nhiên đơn giản trong AOI:**

```javascript
var diemNgauNhien = ee.FeatureCollection.randomPoints({
  region: AOI,
  points: 200,
  seed: 42   // cố định seed để chạy lại ra đúng các điểm này
});
Map.addLayer(diemNgauNhien, {color: 'ff0000'}, 'Điểm ngẫu nhiên (chưa gán nhãn)');
```

Sau đó bấm vào từng điểm (hoặc phóng to quanh nó), tự quyết định lớp, rồi gán bằng tay — ví dụ mở bảng thuộc tính từng feature hoặc dùng lại cách "vẽ marker trùng vị trí rồi gán property" ở mục 7.2.

**Ngẫu nhiên phân tầng theo bản đồ nền (tốt hơn, khớp với đề cương tuần 5):** rải điểm đều theo từng "vùng" của bản đồ biến động (mục 5), để không bị dồn hết vào vùng rộng nhất (ví dụ "ổn định") và bỏ sót vùng hiếm (ví dụ "mới"):

```javascript
var vung = bienDong.unmask(0);  // 0 = không rừng, 1 = ổn định, 2 = mất, 3 = mới
var diemPhanTang = vung.stratifiedSample({
  numPoints: 50,        // 50 điểm cho MỖI giá trị (0, 1, 2, 3)
  classBand: 'change',
  region: AOI,
  scale: 30,
  seed: 42,
  geometries: true
});
Map.addLayer(diemPhanTang, {color: 'ff0000'}, 'Điểm phân tầng theo vùng biến động');
```

Với mỗi điểm trong `diemPhanTang`, bạn vẫn phải tự xem ảnh và gán **nhãn thật** (lớp trong 5 lớp của tuần 5), không dùng luôn giá trị `change` của nó — `stratifiedSample` chỉ giúp chọn **vị trí** rải đều, không thay được việc tự nhìn và gán nhãn.

**So sánh hai cách:**

| Tiêu chí         | Thủ công tự chọn vị trí (7.2)       | Ngẫu nhiên / ngẫu nhiên phân tầng (7.3) |
| ----------------- | ------------------------------------- | ----------------------------------------- |
| Tốc độ            | Nhanh hơn (chỉ chọn nơi rõ ràng)     | Chậm hơn (phải xử lý cả điểm mơ hồ, phải bỏ và vẽ lại điểm khác nếu rơi vào ranh giới) |
| Đại diện cho vùng | Kém — thiên về nơi "dễ nhìn"          | Tốt hơn                                    |
| Phù hợp nhất cho  | Điểm kiểm chứng nhanh (mục 6.5), bổ sung cho lớp hiếm | Mẫu huấn luyện chính, đánh giá độ chính xác khách quan |

**Khuyến nghị:** dùng **ngẫu nhiên phân tầng làm khung chính**, rồi bổ sung một ít điểm thủ công cho lớp còn thiếu (ví dụ ao tôm nhỏ, rải rác, ít rơi vào mẫu ngẫu nhiên).

### 7.4 Tách tập huấn luyện / kiểm tra theo KHỐI không gian

Nếu mẫu dùng để **huấn luyện** (không chỉ kiểm chứng), phải để riêng một phần **không đụng tới** khi huấn luyện, dùng để kiểm tra độ chính xác sau cùng. Tách theo **từng điểm** (`ee.FeatureCollection.randomColumn()` rồi lọc theo tỉ lệ) là sai vì các điểm gần nhau thường giống nhau (tự tương quan không gian) — huấn luyện và kiểm tra bằng những điểm "gần như trùng vị trí" làm độ chính xác đo được lạc quan giả.

Cách đúng: gán mỗi điểm vào 1 **khối** (ví dụ lưới 10 × 10 km) theo toạ độ, rồi chia khối (không chia điểm) thành huấn luyện / kiểm tra:

```javascript
function ganKhoi(feature) {
  var lon = feature.geometry().coordinates().get(0);
  var lat = feature.geometry().coordinates().get(1);
  var khoi = ee.Number(lon).multiply(10).floor().format('%d')
      .cat('_')
      .cat(ee.Number(lat).multiply(10).floor().format('%d'));  // ~11 km mỗi khối
  return feature.set('khoi', khoi);
}

var mauCoKhoi = mau2020.map(ganKhoi);
var khoiNgauNhien = ee.FeatureCollection(mauCoKhoi.aggregate_array('khoi').distinct()
    .map(function (k) { return ee.Feature(null, {khoi: k, r: Math.random()}); }));
// Lọc mauCoKhoi theo danh sách khoi có r < 0.7 (huấn luyện) hoặc >= 0.7 (kiểm tra)
```

> Đoạn `Math.random()` phía client chỉ minh hoạ ý tưởng; trong script thật nên dùng `ee.FeatureCollection.randomColumn()` áp trên danh sách **khối** (không áp trên danh sách điểm) để giữ tính tái lập bằng `seed`.

### 7.5 Sau khi có mẫu: dùng để làm gì tiếp

- **Kiểm chứng 2 lớp** (rừng / không rừng): dùng thẳng ở mục 6.5 — không cần 5 lớp, không cần tách khối cầu kỳ như 7.4 (mẫu ít, chỉ để kiểm tra, không huấn luyện).
- **Huấn luyện phân loại nhiều lớp** (Random Forest 5 lớp, như nhánh B của [đề cương 12 tuần](DE_CUONG_12_TUAN_BIEN_DONG_RNM.md), tuần 7–8): cần đủ mẫu mỗi lớp (đề cương đặt mục tiêu khoảng 150 điểm/lớp), tách khối (mục 7.4), rồi đưa vào `ee.Classifier.smileRandomForest(...)`. Phần này cần một script riêng (huấn luyện, chỉnh tham số, xuất bản đồ 5 lớp) — **chưa nằm trong 6 mục nền của hướng dẫn này**; xem đề cương hoặc hỏi thêm nếu cần viết script đó.

---

## Phụ lục A. Xử lý lỗi thường gặp

| Thông báo / triệu chứng                                          | Nguyên nhân và cách sửa                                                                                               |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `ReferenceError: xxx is not defined`                              | Sai tên biến hoặc dùng biến trước khi khai báo. Kiểm tra chính tả (JS phân biệt hoa / thường)                         |
| `Band pattern 'B8' did not match any bands` (hoặc tên band khác)  | Ảnh không có band đó. Ví dụ dùng band Sentinel-2 cho ảnh Landsat, hoặc mốc năm dùng nhầm `cfg` của cảm biến khác. In `image.bandNames()` để xem tên band thật |
| `Collection query aborted after accumulating over 5000 elements` | Thao tác trên collection quá lớn (thường do thiếu `filterBounds` / `filterDate`). Lọc hẹp lại                         |
| `User memory limit exceeded` / `Computation timed out`            | AOI quá lớn, `scale` quá nhỏ, hoặc quá nhiều mốc năm/giai đoạn tính cùng lúc. Tăng `scale` (ví dụ 60), thu nhỏ AOI, giảm số mốc năm khi thử nghiệm, hoặc dùng `Export` để tính ngầm |
| Bản đồ trắng / không hiện lớp                                     | Chưa bật lớp trong **Layers**, hoặc lớp `updateMask` không còn điểm nào (mặt nạ toàn 0). Kiểm tra `filterDate` và AOI |
| Console chỉ hiện `Object`, không thấy số                          | Bấm mũi tên mở rộng. Với `ee.Number` cần đợi vài giây để server tính                                                  |
| `null` / `Cannot read property ... of null` ở phần GMW            | Năm không có trong GMW v3. Xem danh sách năm bằng `print(GMW.aggregate_array('id_no'))`                               |
| Diện tích ra `0`                                                  | Mặt nạ rỗng hoặc AOI ngoài vùng có ảnh. Thử `Map.addLayer(ndvi)` để xem NDVI của mốc đó                              |
| Composite có sọc đen (Landsat 7 sau 2003)                         | Lỗi SLC-off của Landsat 7. Median nhiều cảnh giảm bớt. Nếu mốc quan tâm chỉ có ít cảnh, cân nhắc dùng Landsat 5 / 8   |
| Kết quả mỗi lần Run hơi khác                                      | Ít gặp, do dữ liệu ảnh được cập nhật; với mốc 'nay' (chưa đủ mùa), ảnh ghép thay đổi theo ngày                       |
| `stratifiedSample` / `randomPoints` chạy rất lâu hoặc trả về ít điểm hơn `numPoints` | Vùng đó có ít điểm ảnh thuộc lớp cần lấy mẫu (ví dụ lớp "mới" rất nhỏ). Giảm `scale`, tăng vùng, hoặc bổ sung điểm thủ công |
| Vẽ điểm Geometry rồi mất khi Reload trang                          | Phải **Save** script trước khi rời trang; hoặc Export điểm ra Asset (mục 7.2, bước 7) ngay khi vừa vẽ xong           |

## Phụ lục B. Thuật ngữ

| Thuật ngữ             | Giải thích                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| AOI                   | Area Of Interest, vùng nghiên cứu                                                               |
| ROI (vùng lọc)        | Phần của AOI mà phương pháp NDVI được áp dụng (dải ven biển) — xem mục 4.5                       |
| Band                  | Một kênh phổ của ảnh (đỏ, cận hồng ngoại…)                                                      |
| Composite (ảnh ghép)  | Ảnh tổng hợp từ nhiều cảnh trong một khoảng thời gian, thường bằng median                       |
| Mốc năm               | Một năm cụ thể có tính mặt nạ rừng (ví dụ 1988, 1992, …, nay) — khác "giai đoạn" là khoảng giữa 2 mốc |
| Giai đoạn             | Khoảng giữa 2 mốc năm liên tiếp (ví dụ 2020–nay); mỗi giai đoạn có 1 bản đồ biến động 3 lớp riêng |
| NDVI                  | Chỉ số thực vật khác biệt chuẩn hoá                                                             |
| Mặt nạ (mask)         | Ảnh 0/1: 1 = đối tượng cần tìm                                                                  |
| Overall Accuracy (OA) | Tỷ lệ điểm ảnh phân loại đúng trên tổng số                                                      |
| Producer's Accuracy   | Trong số điểm ảnh **thật sự là rừng** (theo tham chiếu), bao nhiêu % được tìm ra. Thấp = bỏ sót |
| User's Accuracy       | Trong số điểm ảnh **mình gán là rừng**, bao nhiêu % đúng là rừng. Thấp = thừa                   |
| Kappa (κ)             | Mức đồng thuận đã trừ phần trùng hợp ngẫu nhiên. > 0,8 rất tốt; 0,6–0,8 tốt; 0,4–0,6 trung bình |
| z-score               | Độ lệch của giai đoạn gần nhất so với trung bình lịch sử, chia cho độ lệch chuẩn lịch sử — xem mục 5.4 |
| GMW                   | Global Mangrove Watch, bản đồ rừng ngập mặn toàn cầu độc lập (radar + quang học)                |
| Loss / Gain           | Mất rừng / rừng mới giữa hai mốc năm liên tiếp                                                  |
| Mẫu (sample)          | Điểm đã biết chắc thuộc lớp gì, tự thu thập trên bản đồ — dùng để kiểm chứng hoặc huấn luyện, xem Mục 7 |
| Ngẫu nhiên phân tầng (stratified sampling) | Rải điểm ngẫu nhiên đều theo từng vùng/lớp, để mẫu không dồn hết vào vùng rộng nhất — xem mục 7.3 |
| Tách theo khối (spatial block split) | Chia tập huấn luyện/kiểm tra theo vùng địa lý (không theo từng điểm), tránh điểm gần nhau lặp thông tin — xem mục 7.4 |

## Phụ lục C. Học thêm

- Tài liệu chính thức: <https://developers.google.com/earth-engine/guides> (mục Getting Started và Image / ImageCollection Overview)
- Data Catalog: <https://developers.google.com/earth-engine/datasets>
- Global Mangrove Watch: <https://www.globalmangrovewatch.org>
- Đối chiếu với code Python của dự án: [GEN03_helper_functions.py](../GEN03_helper_functions.py), [GEN04_mangrove_layers.py](../GEN04_mangrove_layers.py), [MAP05_Validation_RecentChange.ipynb](../MAP05_Validation_RecentChange.ipynb)
- Kế hoạch triển khai đầy đủ (12 tuần, gồm cả nhánh phân loại có giám sát): [docs/DE_CUONG_12_TUAN_BIEN_DONG_RNM.md](DE_CUONG_12_TUAN_BIEN_DONG_RNM.md)