# Hướng dẫn làm bản đồ biến động rừng ngập mặn bằng Google Earth Engine (JavaScript)

**Dành cho:** người chưa từng dùng Google Earth Engine (GEE), làm việc hoàn toàn trên trình duyệt (Code Editor), không cần cài Python.
**Kết quả cuối:** 1 bản đồ biến động rừng ngập mặn (mất / mới / ổn định) cho một vùng nhỏ ở Đồng bằng sông Cửu Long (mũi Cà Mau), kèm bảng diện tích và bảng độ chính xác.
**Thời gian:** khoảng 3–4 giờ nếu làm lần đầu.
**Căn cứ:** quy trình Python của repo này (`GEN01`–`GEN04`, `MAP03`, `MAP05`) được viết lại bằng JavaScript. Script hoàn chỉnh cho vùng mẫu: [gee_code_editor/bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js). Bản JavaScript đầy đủ cho toàn bộ ĐBSCL nằm ở [gee_code_editor/mangrove_analysis.js](../gee_code_editor/mangrove_analysis.js).

---

## Lộ trình 6 mục

| #   | Mục                                              | Bạn làm được gì sau mục này                                                                  |
| --- | ------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| 1   | Tìm hiểu GEE                                     | Đăng nhập Code Editor, hiểu các khái niệm cốt lõi, chạy được script đầu tiên                 |
| 2   | Import và lấy dữ liệu liên quan                  | Tìm dataset, gọi ảnh Landsat / Sentinel-2 / GMW, vẽ vùng nghiên cứu (AOI), tải shapefile lên |
| 3   | Tiền xử lý: lọc mây và ảnh ghép theo năm         | Có 1 ảnh sạch đại diện cho mỗi năm                                                           |
| 4   | Tính NDVI và phân loại rừng ngập mặn             | Có mặt nạ rừng ngập mặn (0/1) cho mỗi năm, hiểu cách chọn ngưỡng                             |
| 5   | Phát hiện biến động và tính diện tích            | Có lớp mất / mới / ổn định, bảng ha, biểu đồ, chú giải                                       |
| 6   | Làm hoàn chỉnh vùng mẫu và đánh giá độ chính xác | Có sản phẩm cuối: bản đồ + bảng diện tích + Overall Accuracy / Kappa                         |

Luồng xử lý tổng quát:

```
Vẽ AOI → Lấy ảnh vệ tinh theo năm → Lọc mây → Ảnh ghép median → Tính NDVI
      → Ngưỡng NDVI = mặt nạ rừng → So 2 năm = mất / mới / ổn định
      → Tính diện tích (ha) → Kiểm chứng (GMW + điểm tham chiếu) → Xuất bản đồ
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
| **Assets**               | Dữ liệu của bạn tải lên (shapefile, raster)                        |
| **Thanh tìm kiếm**       | Tìm dataset trong Data Catalog, ví dụ gõ `Landsat 8 Level 2`       |
| **Console**              | Nơi hiện kết quả của lệnh `print()` và thông báo lỗi (màu đỏ)      |
| **Inspector**            | Bấm vào bản đồ để xem giá trị điểm ảnh ở từng lớp                  |
| **Tasks**                | Nơi bấm **Run** để xuất file ra Google Drive (mục 5–6)             |
| **Layers** (trên bản đồ) | Bật / tắt / chỉnh độ trong suốt từng lớp `Map.addLayer()`          |

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
| ------------------------------------- | --------------------------------------------- | --------------------- |
| `ee.Image`                            | 1 ảnh, gồm nhiều **band** (kênh phổ)          | 1 cảnh Sentinel-2     |
| `ee.ImageCollection`                  | Bộ sưu tập nhiều ảnh                          | Tất cả ảnh Landsat 8  |
| `ee.Geometry`                         | Hình học: điểm, đường, đa giác                | Vùng nghiên cứu (AOI) |
| `ee.Feature` / `ee.FeatureCollection` | Hình học kèm bảng thuộc tính                  | Ranh giới các xã      |
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

### 5.1 Logic: so sánh hai mặt nạ

Với mặt nạ năm đầu **A** và năm sau **B** (1 = rừng), mỗi điểm ảnh rơi vào 1 trong 4 trường hợp:

| A   | B   | Ý nghĩa                       | Phép tính (JS)           |
| --- | --- | ----------------------------- | ------------------------ |
| 1   | 0   | **Mất rừng** (loss)           | `maskA.and(maskB.not())` |
| 0   | 1   | **Rừng mới** (gain)           | `maskB.and(maskA.not())` |
| 1   | 1   | **Ổn định** (rừng cả hai năm) | `maskA.and(maskB)`       |
| 0   | 0   | Không phải rừng               | (bỏ qua)                 |

Đây là đúng logic của [MAP01](../MAP01_Mangrove_LOSS.ipynb) và [MAP02](../MAP02_Mangrove_GAIN.ipynb) trong repo.

> Các đoạn code ở mục 5 dùng biến `AOI`, `YEAR_A`, `YEAR_B`, `maskA`, `maskB` (mặt nạ rừng của hai năm, tạo theo mục 3–4). Chúng được ghép sẵn thành một script chạy được ở mục 6.2, bạn có thể đọc mục 5 để hiểu rồi chạy thẳng mục 6.

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

print("Rừng năm A (ha):", areaHa(maskA));
print("Mất rừng (ha):", areaHa(loss));
print("Rừng mới (ha):", areaHa(gain));
```

Vì sao `scale: 30`: đủ mịn cho Landsat, và dùng chung 30 m cho cả Sentinel-2 cho phép so sánh công bằng giữa các năm (giống `SCALE_M = 30` ở MAP05).

### 5.3 Biến động ròng và tốc độ hằng năm

```
Ròng (ha)      = Gain − Loss
Tốc độ (ha/năm) = Ròng / số năm giữa hai mốc
```

Tốc độ theo năm giúp so sánh hai giai đoạn dài khác nhau (giống cột `annual_rate_ha_yr` trong MAP05).

### 5.4 Biểu đồ nhanh

```javascript
var bang = ee.FeatureCollection([
  ee.Feature(null, { nhan: "Rừng " + YEAR_A, ha: areaHa(maskA) }),
  ee.Feature(null, { nhan: "Rừng " + YEAR_B, ha: areaHa(maskB) }),
  ee.Feature(null, { nhan: "Mất", ha: areaHa(loss) }),
  ee.Feature(null, { nhan: "Mới", ha: areaHa(gain) }),
]);
print(bang);
print(
  ui.Chart.feature
    .byFeature(bang, "nhan", "ha")
    .setChartType("ColumnChart")
    .setOptions({
      title: "Diện tích rừng ngập mặn (ha)",
      legend: { position: "none" },
    })
);
```

### 5.5 Kiểm tra độ bền của kết quả (đừng bỏ qua)

Trước khi kết luận "rừng giảm X ha", tự hỏi:

1. Hai ảnh ghép có **số cảnh** tương đương không (mục 3.3)?
2. Đổi ngưỡng NDVI ±0,05 hoặc bật mặt nạ mây (mục 3.5), xu hướng (tăng / giảm) có **giữ nguyên** không?
3. Chênh lệch ròng có **lớn hơn** mức dao động do 1 và 2 gây ra không?

Nếu không, kết luận chỉ là "chưa chắc chắn". Đây là tinh thần của phần kiểm tra độ bền ngưỡng NDVI được mô tả trong README của repo.

### 5.6 Chú giải bản đồ

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

---

## Mục 6. Hoàn thành vùng mẫu ĐBSCL và tính độ chính xác

### 6.1 Vùng mẫu

**Đất Mũi, Cà Mau** (mũi cực Nam), hình chữ nhật `[104.72, 8.56, 104.92, 8.74]`, khoảng 22 × 20 km. Vùng này được chọn vì rừng ngập mặn chiếm ưu thế ven biển, có dữ liệu GMW để đối chiếu, và đủ nhỏ để mọi phép tính chạy trong vài chục giây. Đa giác Đất Mũi trong shapefile xã của repo (`ma_xa` = 34017) có khung bao `[104.71, 8.56, 104.92, 8.73]`, gần như trùng với hình chữ nhật này.

Sản phẩm cần có sau mục này:

- [ ] 1 bản đồ biến động 3 lớp (ổn định / mất / mới), giai đoạn 2020 → 2025, có chú giải
- [ ] Bảng diện tích (ha): rừng 2 năm, mất, mới, ròng
- [ ] Bảng độ chính xác: Overall Accuracy, Producer's / User's Accuracy, Kappa
- [ ] File GeoTIFF xuất ra Google Drive

Toàn bộ do một file làm ra: [gee_code_editor/bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js).

### 6.2 Script hoàn chỉnh

Script hoàn chỉnh nằm trong một file riêng, đã kiểm tra cú pháp: [gee_code_editor/bien_dong_rnm_dat_mui.js](../gee_code_editor/bien_dong_rnm_dat_mui.js).

1. Mở file trong VS Code, chọn hết (Ctrl+A), sao chép (Ctrl+C).
2. Trong Code Editor: **Scripts → NEW → File**, đặt tên, dán vào khung code.
3. Bấm **Run**. Chỉ cần sửa khối `0. THAM SỐ` ở đầu file (AOI, hai năm, ngưỡng NDVI, công tắc mặt nạ mây).

File gồm 9 phần, khớp với các mục 3–6 của hướng dẫn:

| Phần | Nội dung                                                   | Mục hướng dẫn |
| ---- | ---------------------------------------------------------- | ------------- |
| 0    | Tham số (gồm ROI: `ROI_POLYGON`, `MAX_DIST_SEA_KM`)         | 4.5, 6.1      |
| 1    | Hàm: ROI, mặt nạ mây, ảnh ghép + NDVI, diện tích, độ chính xác | 3, 4, 5   |
| 2–3  | Mặt nạ rừng 2 năm, phát hiện mất / mới / ổn định           | 4, 5.1        |
| 4    | Bản đồ 3 lớp + chú giải                                    | 5.1, 5.6      |
| 5    | Bảng diện tích + biểu đồ                                   | 5.2, 5.4      |
| 6    | Độ chính xác so với GMW                                    | 6.3           |
| 7    | Quét ngưỡng NDVI (tuỳ chọn, `RUN_SWEEP = true`)            | 6.4           |
| 8    | Điểm tham chiếu tự chọn (tuỳ chọn, bỏ dấu chú thích)       | 6.5           |
| 9    | Xuất GeoTIFF và CSV ra Google Drive                        | 6.2           |

> **Lưu ý khi dán code:** nếu VS Code tự định dạng file bằng Prettier, hãy dùng file `.prettierrc` ở gốc repo (đã có). Cấu hình mặc định của Prettier 3 thêm dấu phẩy thừa sau tham số cuối của lời gọi hàm (dạng `Map.addLayer(a, b, "tên",` rồi xuống dòng `);`), và Code Editor không chấp nhận cú pháp đó.

Sau khi bấm **Run**:

1. **Console** hiện số cảnh từng năm, bảng diện tích, biểu đồ, và độ chính xác so với GMW. Đợi vài chục giây nếu kết quả chưa hiện.
2. **Bản đồ** hiện lớp "BIẾN ĐỘNG 2020-2025". Bật thêm các lớp khác ở góc phải trên (Layers).
3. Bấm vào bản đồ, xem tab **Inspector** để đối chiếu giá trị từng lớp tại điểm đó.
4. Tab **Tasks** hiện 2 việc xuất file (ảnh và CSV): bấm **Run** ở từng dòng → xác nhận → file xuất hiện trong Google Drive của bạn.

### 6.3 Số liệu tham chiếu để bạn đối chiếu

Kết quả khi tôi chạy cùng logic với cấu hình mặc định của file (`USE_SCL_MASK = true`, ngưỡng 0,25, `MAX_DIST_SEA_KM = 5`) bằng Python API ngày 21/09/2026. Dữ liệu GEE có thể được cập nhật nên số của bạn có thể lệch nhẹ; nếu lệch nhiều là dấu hiệu bạn đã làm khác đi.

| Chỉ tiêu                             | 2020   | 2025   |
| ------------------------------------ | ------ | ------ |
| Số cảnh trong ảnh ghép               | 33     | 29     |
| Diện tích rừng trong ROI (ha)        | 18.610 | 18.640 |

ROI rộng 34.909 ha. Rừng GMW 2020 nằm trong ROI: 17.270 ha, nằm ngoài ROI: 5.595 ha.

Biến động 2020 → 2025 trong ROI: ổn định **16.969 ha**, mất **1.641 ha**, mới **1.672 ha**, ròng **+31 ha** (gần như không đổi).

Độ chính xác năm 2020 so với GMW, chỉ tính trong ROI (điểm ảnh 30 m):

| Overall Accuracy | Producer's | User's | Kappa |
| ---------------- | ---------- | ------ | ----- |
| 0,828            | 0,865      | 0,803  | 0,656 |

Cách đọc: Kappa 0,66 nghĩa là mức đồng thuận **khá**. User's 0,80 nghĩa là khoảng 20% "rừng" tìm được không phải rừng theo GMW. Phần "thừa" còn lại có thể đến từ bờ đê có cây, rừng trồng xen kẽ ao tôm (chỉ số quang phổ không tách được), và cả sai số của chính GMW.

**So sánh cùng dữ liệu khi không dùng ROI** (`MAX_DIST_SEA_KM = 0`): Kappa 0,593; mất 2.932 ha; mới 2.448 ha; ròng −484 ha. Phần biến động bị loại nằm ở ngoài ROI (đất liền cách biển hơn 5 km); nhiều khả năng do cây trồng thay đổi theo mùa vụ, nhưng tôi chưa kiểm chứng trực tiếp trên ảnh.

Ba bài học từ thử nghiệm:

- **Giới hạn không gian:** xem mục 4.5. Cùng thuật toán, chỉ đổi cách giới hạn vùng, Kappa ở khung nhiều đất liền (vùng B) tăng từ 0,37 lên 0,53.
- **Mây:** kết quả biến động phụ thuộc mạnh vào việc loại mây (bảng ở mục 3.5). Độ chính xác 2020 gần như không đổi giữa hai cách loại mây (Kappa 0,594 và 0,593), nhưng số liệu biến động thì khác nhiều.
- Vì vậy, **độ chính xác của một năm không đủ để tin vào bản đồ biến động giữa hai năm**. Hãy kiểm tra thêm bằng điểm tham chiếu tự chọn (mục 6.5).

### 6.4 Độ chính xác (b): quét ngưỡng NDVI

Đặt `RUN_SWEEP = true` ở đầu script rồi Run lại. Script in độ chính xác của năm A với các ngưỡng 0,10–0,35 (giống `_threshold_sweep.csv` của repo). Kết quả tham chiếu dưới đây tính **khi không dùng ROI** (`MAX_DIST_SEA_KM = 0`), 2020, Sentinel-2, so với GMW. Tôi chưa chạy lại phép quét ngưỡng với ROI, nên hãy bật `RUN_SWEEP = true` với cấu hình của bạn để có bảng đúng cho vùng của mình:

| Ngưỡng NDVI | Overall | Producer's | User's | Kappa |
| ----------- | ------- | ---------- | ------ | ----- |
| 0,10        | 0,819   | 0,943      | 0,765  | 0,634 |
| 0,15        | 0,814   | 0,919      | 0,769  | 0,624 |
| 0,20        | 0,807   | 0,891      | 0,774  | 0,611 |
| **0,25**    | 0,798   | 0,858      | 0,778  | 0,593 |
| 0,30        | 0,787   | 0,821      | 0,782  | 0,573 |
| 0,35        | 0,775   | 0,780      | 0,786  | 0,548 |

Ở vùng này, Kappa giảm nhẹ khi tăng ngưỡng còn User's tăng nhẹ (thừa ít hơn, bỏ sót nhiều hơn). Chênh lệch giữa các ngưỡng không lớn, nên ngưỡng 0,25 của repo là hợp lý và giữ được tính nhất quán với bản đồ toàn ĐBSCL. Nếu bạn đổi ngưỡng cho năm A, **phải áp dụng cùng ngưỡng cho năm B**, nếu không phép so sánh không còn ý nghĩa.

### 6.5 Độ chính xác (c): điểm tham chiếu tự chọn (đặc biệt cho năm 2025)

GMW không có 2025, nên năm này cần tự lập điểm tham chiếu. Cách làm chuẩn của GEE:

1. Chuyển bản đồ sang **Satellite** để nhìn ảnh độ phân giải cao của Google.
2. Trong công cụ vẽ (góc trên trái bản đồ) bấm **Add a marker**, rồi bấm lên bản đồ để đặt điểm ở nơi bạn **chắc chắn là rừng ngập mặn**. Ghi ít nhất **50 điểm**, rải khắp AOI, cách nhau ≥ 100 m, đặt vào giữa các mảng rừng đồng nhất (tránh sát ranh giới).
3. Trong khung code, bấm biểu tượng bánh răng của layer vừa tạo:
   - Đổi tên thành `mangrovePts`
   - **Import as:** `FeatureCollection`
   - **Add property:** tên `ref`, giá trị `1`
4. Lặp lại cho các nơi **không phải rừng ngập mặn** (nước, bãi bùn, ao tôm, đất trống, rừng tràm, lúa…): layer `otherPts`, thuộc tính `ref = 0`, ít nhất 50 điểm.
5. Trong file script, ở phần `8.`, bỏ dấu `/*` và `*/` sau khi đã tạo 2 layer. Nội dung khối đó:

```javascript
/*
var refPts = mangrovePts.merge(otherPts);

var mau = maskB.rename('pred').toInt().sampleRegions({
  collection: refPts, properties: ['ref'], scale: 30
});
var cm = mau.errorMatrix('ref', 'pred');       // hàng = thực tế, cột = dự đoán (0 = không rừng, 1 = rừng)
print('Ma trận nhầm lẫn ' + YEAR_B, cm);
print('Overall Accuracy:', cm.accuracy());
print("Producer's Accuracy [không rừng, rừng]:", cm.producersAccuracy());
print("User's Accuracy [không rừng, rừng]:",     cm.consumersAccuracy());
print('Kappa:', cm.kappa());
*/
```

Lưu ý khi tự lập điểm tham chiếu:

- Ảnh nền vệ tinh có thể không đúng năm bạn đang kiểm chứng. Hãy chọn các điểm mà tình trạng (rừng / không rừng) chắc chắn không đổi, hoặc đối chiếu thêm bằng Timelapse.
- Số điểm ít (~100) cho ước lượng dao động khá lớn. Hãy nêu số điểm khi báo cáo.
- Chọn điểm thủ công dễ thiên về nơi "dễ nhìn". Nếu cần chặt chẽ hơn, hãy tạo điểm ngẫu nhiên bằng `ee.FeatureCollection.randomPoints(AOI, 100, 42)` rồi gán nhãn từng điểm.
- Độ chính xác của **bản đồ biến động** thấp hơn độ chính xác của từng năm, vì sai số hai năm cộng dồn. Hãy đọc con số mất / mới với sự thận trọng.

### 6.6 Kiểm tra cuối và cách trình bày sản phẩm

Trước khi coi là xong:

- [ ] Ảnh màu thật của cả hai năm không còn mảng mây lớn (bật lớp `Ảnh 2020`, `Ảnh 2025` để xem) và số cảnh hai năm không chênh nhau quá nhiều
- [ ] Bản đồ trông hợp lý so với ảnh nền (rừng ven biển được tô, biển và ao không bị tô)
- [ ] Đã bật lớp `Vùng lọc (ROI)`, kiểm tra ROI phủ hết dải rừng và không lấn vào ruộng / vườn; đã xem số `Rừng GMW nằm ngoài ROI`
- [ ] Đã có Overall Accuracy và Kappa (ít nhất so với GMW)
- [ ] Đã thử đổi ngưỡng / bật mặt nạ mây và xu hướng không đổi chiều (mục 5.5)
- [ ] Đã xuất GeoTIFF và CSV

Khi ghi vào báo cáo, nên nêu rõ:

> Bản đồ biến động rừng ngập mặn 2020–2025 vùng Đất Mũi được suy ra từ ngưỡng NDVI (0,25) của ảnh ghép median cả năm Sentinel-2 đã loại mây theo điểm ảnh (band SCL), giới hạn trong dải cách biển không quá 5 km để hạn chế lẫn với cây trồng. Độ chính xác so với Global Mangrove Watch năm 2020 trong vùng này: OA = 0,83; Kappa = 0,66. GMW không có năm 2025 nên kết quả 2025 chưa được kiểm chứng trực tiếp. Diện tích rừng gần như không đổi (ròng +31 ha), trong khi mất và mới đều khoảng 1.650 ha, mức thay đổi thuần thấp hơn sai số phân loại nên cần đọc thận trọng.

### 6.7 Mở rộng ra toàn ĐBSCL

Khi đã quen, chuyển sang bản đầy đủ [gee_code_editor/mangrove_analysis.js](../gee_code_editor/mangrove_analysis.js): đa giác AOI 974 đỉnh, 10 mốc năm (1988–2026), 9 giai đoạn mất / mới, bảng màu chú giải. Việc cần thêm để có độ tin cậy như MAP05:

- Tính diện tích từng năm và từng giai đoạn (mục 5.2) bằng `reduceRegion`; với vùng lớn, tăng `scale` hoặc chia nhỏ để không vượt giới hạn bộ nhớ.
- So sánh với GMW cho 1997 (dùng GMW 1996), 2010, 2015, 2020.
- Thống kê theo xã bằng `reduceRegions` trên tài sản shapefile xã (mục 2.5).

---

## Phụ lục A. Xử lý lỗi thường gặp

| Thông báo / triệu chứng                                          | Nguyên nhân và cách sửa                                                                                               |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `ReferenceError: xxx is not defined`                             | Sai tên biến hoặc dùng biến trước khi khai báo. Kiểm tra chính tả (JS phân biệt hoa / thường)                         |
| `Band pattern 'B8' did not match any bands` (hoặc tên band khác) | Ảnh không có band đó. Ví dụ dùng band Sentinel-2 cho ảnh Landsat. In `image.bandNames()` để xem tên band thật         |
| `Collection query aborted after accumulating over 5000 elements` | Thao tác trên collection quá lớn (thường do thiếu `filterBounds` / `filterDate`). Lọc hẹp lại                         |
| `User memory limit exceeded` / `Computation timed out`           | AOI quá lớn hoặc `scale` quá nhỏ. Tăng `scale` (ví dụ 60), thu nhỏ AOI, hoặc dùng `Export` để tính ngầm               |
| Bản đồ trắng / không hiện lớp                                    | Chưa bật lớp trong **Layers**, hoặc lớp `updateMask` không còn điểm nào (mặt nạ toàn 0). Kiểm tra `filterDate` và AOI |
| Console chỉ hiện `Object`, không thấy số                         | Bấm mũi tên mở rộng. Với `ee.Number` cần đợi vài giây để server tính                                                  |
| `null` / `Cannot read property ... of null` ở phần GMW           | Năm không có trong GMW v3. Xem danh sách năm bằng `print(GMW.aggregate_array('id_no'))`                               |
| Diện tích ra `0`                                                 | Mặt nạ rỗng hoặc AOI ngoài vùng có ảnh. Thử `Map.addLayer(A.ndvi)` để xem NDVI                                        |
| Composite có sọc đen (Landsat 7 sau 2003)                        | Lỗi SLC-off của Landsat 7. Median nhiều cảnh giảm bớt. Nếu năm quan tâm chỉ có ít cảnh, cân nhắc dùng Landsat 5 / 8   |
| Kết quả mỗi lần Run hơi khác                                     | Ít gặp, do dữ liệu ảnh được cập nhật; với năm hiện tại (chưa đủ mùa), ảnh ghép thay đổi theo ngày                     |

## Phụ lục B. Thuật ngữ

| Thuật ngữ             | Giải thích                                                                                      |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| AOI                   | Area Of Interest, vùng nghiên cứu                                                               |
| Band                  | Một kênh phổ của ảnh (đỏ, cận hồng ngoại…)                                                      |
| Composite (ảnh ghép)  | Ảnh tổng hợp từ nhiều cảnh trong một khoảng thời gian, thường bằng median                       |
| NDVI                  | Chỉ số thực vật khác biệt chuẩn hoá                                                             |
| Mặt nạ (mask)         | Ảnh 0/1: 1 = đối tượng cần tìm                                                                  |
| Overall Accuracy (OA) | Tỷ lệ điểm ảnh phân loại đúng trên tổng số                                                      |
| Producer's Accuracy   | Trong số điểm ảnh **thật sự là rừng** (theo tham chiếu), bao nhiêu % được tìm ra. Thấp = bỏ sót |
| User's Accuracy       | Trong số điểm ảnh **mình gán là rừng**, bao nhiêu % đúng là rừng. Thấp = thừa                   |
| Kappa (κ)             | Mức đồng thuận đã trừ phần trùng hợp ngẫu nhiên. > 0,8 rất tốt; 0,6–0,8 tốt; 0,4–0,6 trung bình |
| GMW                   | Global Mangrove Watch, bản đồ rừng ngập mặn toàn cầu độc lập (radar + quang học)                |
| Loss / Gain           | Mất rừng / rừng mới giữa hai năm                                                                |

## Phụ lục C. Học thêm

- Tài liệu chính thức: <https://developers.google.com/earth-engine/guides> (mục Getting Started và Image / ImageCollection Overview)
- Data Catalog: <https://developers.google.com/earth-engine/datasets>
- Global Mangrove Watch: <https://www.globalmangrovewatch.org>
- Đối chiếu với code Python của dự án: [GEN03_helper_functions.py](../GEN03_helper_functions.py), [GEN04_mangrove_layers.py](../GEN04_mangrove_layers.py), [MAP05_Validation_RecentChange.ipynb](../MAP05_Validation_RecentChange.ipynb)
