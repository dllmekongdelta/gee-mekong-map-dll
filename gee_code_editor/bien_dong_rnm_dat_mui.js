/**
 * ============================================================================
 *  BIẾN ĐỘNG RỪNG NGẬP MẶN 2020-2025 -- VÙNG MẪU ĐẤT MŨI (CÀ MAU)
 *  Bản hoàn chỉnh cho GEE Code Editor: dán toàn bộ file, bấm Run.
 *
 *  Kết quả:
 *    - 1 bản đồ biến động 3 lớp: ổn định / mất rừng / rừng mới
 *    - Bảng diện tích (ha) + biểu đồ
 *    - Độ chính xác so với Global Mangrove Watch (OA, Producer's, User's, Kappa)
 *    - Xuất GeoTIFF + CSV ra Google Drive (tab Tasks)
 *
 *  Phương pháp giống pipeline Python của repo (GEN03/GEN04):
 *    ảnh ghép median cả năm -> NDVI -> ngưỡng (Sentinel-2: 0.25) -> so 2 năm.
 *  Công thức rừng ngập mặn:  NDVI > ngưỡng  VÀ  nằm trong dải ven biển (ROI).
 *  ROI thay cho việc code Python vẽ tay AOI dọc bờ biển: NDVI không phân biệt được
 *  rừng ngập mặn với lúa / cây trồng, nên phải giới hạn không gian.
 *  Khác một điểm cần chú ý: bật mặt nạ mây theo điểm ảnh (band SCL). Nếu chỉ
 *  lọc theo % mây của cả cảnh, năm 2025 còn 4 cảnh và ảnh vẫn nhiều mây,
 *  làm kết quả biến động bị nhiễu (xem mục 3.5 của hướng dẫn).
 *
 *  Chỉ cần sửa khối "0. THAM SỐ". Hướng dẫn chi tiết:
 *  docs/HUONG_DAN_GEE_BIEN_DONG_RNM.md
 * ============================================================================
 */

// ---------------------------------------------------------------------------
// 0. THAM SỐ (chỉ sửa phần này)
// ---------------------------------------------------------------------------
var AOI = ee.Geometry.Rectangle([104.72, 8.56, 104.92, 8.74]);  // [Tây, Nam, Đông, Bắc]
var YEAR_A = 2020;          // năm đầu (GMW v3 chỉ có đến 2020 để kiểm chứng)
var YEAR_B = 2025;          // năm sau
var NDVI_THRESHOLD = 0.25;  // ngưỡng Sentinel-2 của repo (GEN04)

// VÙNG LỌC (ROI): chỉ tính rừng ngập mặn trong dải ven biển, để không lẫn
// lúa, cây trồng, vườn cây ở phía đất liền (NDVI không phân biệt được các loại cây xanh).
// Ưu tiên 1: ROI_POLYGON = đa giác bạn tự vẽ dọc dải rừng (giống AOI vẽ tay của code Python).
//            Vẽ bằng công cụ Geometry, đặt tên vungLoc, rồi viết: var ROI_POLYGON = vungLoc;
// Ưu tiên 2: MAX_DIST_SEA_KM = chỉ lấy vùng cách biển tối đa bằng ngần này km (tự động).
//            Đặt 0 để tắt (dùng cả khung AOI). Xem mục 4.5 của hướng dẫn để chọn giá trị.
var ROI_POLYGON = null;
var MAX_DIST_SEA_KM = 5;

var USE_SCL_MASK = true;    // true = loại mây theo điểm ảnh; false = chỉ lọc theo % mây (như repo)
var RUN_SWEEP = false;      // true = quét ngưỡng NDVI 0.10-0.35 so với GMW (thêm ~1 phút)
var SCALE = 30;             // mét, dùng chung cho mọi phép tính diện tích / độ chính xác

// ---------------------------------------------------------------------------
// 1. HÀM
// ---------------------------------------------------------------------------

// Loại điểm ảnh hỏng / bóng mây / mây / mây ti (SCL: 1, 3, 8, 9, 10)
function maskS2(img) {
  var scl = img.select('SCL');
  var bad = scl.eq(1).or(scl.eq(3)).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10));
  return img.updateMask(bad.not());
}

// Vùng lọc (ROI) dạng ảnh 0/1. Cố định theo thời gian (không đổi giữa các năm)
// nên hai năm luôn được so sánh trên cùng một vùng.
function buildRoi() {
  if (ROI_POLYGON !== null) {
    return ee.Image.constant(1).clip(ROI_POLYGON).unmask(0).clip(AOI).rename('roi');
  }
  if (MAX_DIST_SEA_KM <= 0) {
    return ee.Image.constant(1).clip(AOI).rename('roi');
  }
  // "Biển" = nước tồn tại lâu năm (JRC Global Surface Water), rồi bỏ các vùng nước hẹp
  // (sông, kênh, ao tôm) bằng co rồi nở 400 m, chỉ còn biển và cửa sông lớn.
  var water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence')
      .gt(50).unmask(0).clip(AOI.buffer(15000));
  var sea = water.focalMin(400, 'circle', 'meters')
      .focalMax(400, 'circle', 'meters')
      .selfMask();
  var distM = sea.fastDistanceTransform(300, 'pixels', 'squared_euclidean')
      .sqrt()
      .multiply(30);                                   // pixel 30 m -> mét
  return distM.lt(MAX_DIST_SEA_KM * 1000).unmask(0).clip(AOI).rename('roi');
}

// Ảnh ghép median cả năm + NDVI + mặt nạ rừng (NDVI > ngưỡng VÀ nằm trong ROI) cho 1 năm
function buildYear(year) {
  var cloudMax = USE_SCL_MASK ? 60 : 20;
  var col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
      .filterBounds(AOI)
      .filterDate(year + '-01-01', (year + 1) + '-01-01')
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloudMax));
  if (USE_SCL_MASK) {
    col = col.map(maskS2);
  }
  print('Số cảnh Sentinel-2 năm ' + year + ':', col.size());  // quá ít cảnh = kết quả kém tin cậy
  var img = col.median().clip(AOI);
  var ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return {
    img: img,
    ndvi: ndvi,
    mask: ndvi.gt(NDVI_THRESHOLD).and(ROI).rename('mangrove')
  };
}

// Diện tích (ha) của các điểm ảnh = 1
function areaHa(binary) {
  var tong = binary.multiply(ee.Image.pixelArea()).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: AOI,
    scale: SCALE,
    maxPixels: 1e13,
    bestEffort: true
  });
  return ee.Number(tong.values().get(0)).divide(10000);
}

// Độ chính xác của mặt nạ pred so với mặt nạ tham chiếu ref (đều là 0/1),
// chỉ tính trong ROI (nơi phương pháp được áp dụng)
function accuracy(pred, ref) {
  var combo = pred.toInt().multiply(2).add(ref.toInt()).updateMask(ROI).rename('combo');
  var hist = ee.Dictionary(combo.reduceRegion({
    reducer: ee.Reducer.frequencyHistogram(),
    geometry: AOI,
    scale: SCALE,
    maxPixels: 1e13,
    bestEffort: true
  }).get('combo'));
  // combo: 0 = cả hai không rừng (TN) | 1 = chỉ tham chiếu có rừng (bỏ sót, FN)
  //        2 = chỉ mình có rừng (thừa, FP) | 3 = cả hai có rừng (TP)
  var tn = ee.Number(hist.get('0', 0));
  var fn = ee.Number(hist.get('1', 0));
  var fp = ee.Number(hist.get('2', 0));
  var tp = ee.Number(hist.get('3', 0));
  var total = tn.add(fn).add(fp).add(tp);
  var oa = tp.add(tn).divide(total);
  var pa = tp.divide(tp.add(fn));   // Producer's Accuracy
  var ua = tp.divide(tp.add(fp));   // User's Accuracy
  var pe = tp.add(fp).multiply(tp.add(fn))
      .add(fn.add(tn).multiply(fp.add(tn)))
      .divide(total.multiply(total));
  var kappa = oa.subtract(pe).divide(ee.Number(1).subtract(pe));
  return ee.Dictionary({
    OverallAccuracy: oa.format('%.3f'),
    ProducerAccuracy: pa.format('%.3f'),
    UserAccuracy: ua.format('%.3f'),
    Kappa: kappa.format('%.3f')
  });
}

// Một hàng chú giải: ô màu + chữ
function hangChuGiai(mau, chu) {
  var o = ui.Label('', {backgroundColor: mau, padding: '8px', margin: '0 6px 4px 0'});
  var t = ui.Label(chu, {margin: '0 0 4px 0', fontSize: '12px'});
  return ui.Panel([o, t], ui.Panel.Layout.Flow('horizontal'));
}

// ---------------------------------------------------------------------------
// 2. MẶT NẠ RỪNG 2 NĂM
// ---------------------------------------------------------------------------
var ROI = buildRoi();
var A = buildYear(YEAR_A);
var B = buildYear(YEAR_B);
var maskA = A.mask;
var maskB = B.mask;

// ---------------------------------------------------------------------------
// 3. PHÁT HIỆN BIẾN ĐỘNG
// ---------------------------------------------------------------------------
var loss = maskA.and(maskB.not());      // có rừng năm A, mất năm B
var gain = maskB.and(maskA.not());      // không có năm A, có rừng năm B
var stable = maskA.and(maskB);          // rừng cả hai năm

// Gộp thành 1 ảnh: 1 = ổn định, 2 = mất, 3 = mới
var bienDong = ee.Image(0)
    .where(stable, 1)
    .where(loss, 2)
    .where(gain, 3)
    .rename('change');
bienDong = bienDong.updateMask(bienDong.gt(0));

// ---------------------------------------------------------------------------
// 4. HIỂN THỊ BẢN ĐỒ
// ---------------------------------------------------------------------------
var COLOR_STABLE = '#1a9850';
var COLOR_LOSS = '#c51b8a';
var COLOR_GAIN = '#ffd92f';
var RGB_VIS = {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000};

Map.setOptions('SATELLITE');
Map.centerObject(AOI, 11);
Map.addLayer(ROI.updateMask(ROI), {palette: ['ffffff']}, 'Vùng lọc (ROI)', false, 0.3);
Map.addLayer(A.img, RGB_VIS, 'Ảnh ' + YEAR_A, false);
Map.addLayer(B.img, RGB_VIS, 'Ảnh ' + YEAR_B, false);
Map.addLayer(maskA.updateMask(maskA), {palette: [COLOR_STABLE]}, 'Rừng ' + YEAR_A, false);
Map.addLayer(maskB.updateMask(maskB), {palette: [COLOR_STABLE]}, 'Rừng ' + YEAR_B, false);
Map.addLayer(bienDong, {min: 1, max: 3, palette: [COLOR_STABLE, COLOR_LOSS, COLOR_GAIN]},
    'BIẾN ĐỘNG ' + YEAR_A + '-' + YEAR_B);

var chuGiai = ui.Panel({style: {position: 'bottom-right', padding: '8px 12px'}});
chuGiai.add(ui.Label('Biến động RNM ' + YEAR_A + '-' + YEAR_B, {fontWeight: 'bold'}));
chuGiai.add(hangChuGiai(COLOR_STABLE, 'Ổn định'));
chuGiai.add(hangChuGiai(COLOR_LOSS, 'Mất rừng'));
chuGiai.add(hangChuGiai(COLOR_GAIN, 'Rừng mới'));
Map.add(chuGiai);

// ---------------------------------------------------------------------------
// 5. BẢNG DIỆN TÍCH + BIỂU ĐỒ
// ---------------------------------------------------------------------------
var lossHa = areaHa(loss);
var gainHa = areaHa(gain);
var bang = ee.FeatureCollection([
  ee.Feature(null, {nhan: 'Rừng ' + YEAR_A, ha: areaHa(maskA)}),
  ee.Feature(null, {nhan: 'Rừng ' + YEAR_B, ha: areaHa(maskB)}),
  ee.Feature(null, {nhan: 'Mất', ha: lossHa}),
  ee.Feature(null, {nhan: 'Mới', ha: gainHa}),
  ee.Feature(null, {nhan: 'Ròng (mới - mất)', ha: gainHa.subtract(lossHa)})
]);
print('BẢNG DIỆN TÍCH (ha)', bang);
print(ui.Chart.feature.byFeature(bang, 'nhan', 'ha')
    .setChartType('ColumnChart')
    .setOptions({title: 'Diện tích rừng ngập mặn (ha)', legend: {position: 'none'}}));

// ---------------------------------------------------------------------------
// 6. ĐỘ CHÍNH XÁC (a): SO VỚI GLOBAL MANGROVE WATCH v3
//    GMW chỉ có 1996, 2007-2010, 2015-2020 => chỉ kiểm chứng được năm A (<= 2020).
//    Năm B (2025) không có tham chiếu: dùng điểm tham chiếu tự chọn ở mục 8.
// ---------------------------------------------------------------------------
var GMW = ee.ImageCollection('projects/sat-io/open-datasets/GMW/extent/GMW_V3');
var gmwA = GMW.filter(ee.Filter.eq('id_no', 'gmw_v3_' + YEAR_A)).first()
    .select('b1')
    .unmask(0)
    .gt(0)
    .rename('gmw')
    .clip(AOI);
print('ĐỘ CHÍNH XÁC ' + YEAR_A + ' so với GMW', accuracy(maskA, gmwA));
print('Diện tích rừng theo GMW ' + YEAR_A + ' (ha):', areaHa(gmwA));
// Rừng GMW nằm NGOÀI vùng lọc là phần bị loại bỏ. Nếu số này lớn, kiểm tra xem đó là rừng
// thật (tăng MAX_DIST_SEA_KM hoặc vẽ lại ROI_POLYGON) hay là cây trồng.
print('Rừng GMW nằm ngoài ROI (ha):', areaHa(gmwA.and(ROI.not())));
print('Diện tích ROI (ha):', areaHa(ROI));
Map.addLayer(gmwA.updateMask(gmwA), {palette: ['ff7f00']}, 'GMW ' + YEAR_A + ' (tham chiếu)', false);

// ---------------------------------------------------------------------------
// 7. (TUỲ CHỌN) QUÉT NGƯỠNG NDVI SO VỚI GMW -- đặt RUN_SWEEP = true ở trên
// ---------------------------------------------------------------------------
if (RUN_SWEEP) {
  [0.10, 0.15, 0.20, 0.25, 0.30, 0.35].forEach(function (t) {
    print('NDVI > ' + t, accuracy(A.ndvi.gt(t).and(ROI), gmwA));
  });
}

// ---------------------------------------------------------------------------
// 8. (TUỲ CHỌN) ĐỘ CHÍNH XÁC (b): ĐIỂM THAM CHIẾU TỰ CHỌN CHO NĂM B
//    Cách làm: xem mục 6.5 của hướng dẫn. Vẽ >= 50 điểm mỗi loại bằng công cụ
//    Geometry (góc trên trái bản đồ), đổi tên layer và import thành
//    FeatureCollection có property 'ref':
//      mangrovePts -> ref = 1 (chắc chắn là rừng ngập mặn)
//      otherPts    -> ref = 0 (nước, bùn, ao tôm, lúa, đất trống...)
//    Sau đó bỏ dấu /* và */ ở dưới đây.
// ---------------------------------------------------------------------------
/*
var refPts = mangrovePts.merge(otherPts);
var mau = maskB.rename('pred').toInt().sampleRegions({
  collection: refPts,
  properties: ['ref'],
  scale: SCALE
});
var cm = mau.errorMatrix('ref', 'pred');   // hàng = thực tế, cột = dự đoán (0 = không rừng, 1 = rừng)
print('Ma trận nhầm lẫn ' + YEAR_B, cm);
print('Overall Accuracy:', cm.accuracy());
print("Producer's Accuracy [không rừng, rừng]:", cm.producersAccuracy());
print("User's Accuracy [không rừng, rừng]:", cm.consumersAccuracy());
print('Kappa:', cm.kappa());
*/

// ---------------------------------------------------------------------------
// 9. XUẤT RA GOOGLE DRIVE (mở tab Tasks -> bấm Run ở từng dòng)
// ---------------------------------------------------------------------------
Export.image.toDrive({
  image: bienDong.unmask(0).toByte(),   // 0 = không rừng, 1 = ổn định, 2 = mất, 3 = mới
  description: 'RNM_bien_dong_' + YEAR_A + '_' + YEAR_B,
  region: AOI,
  scale: SCALE,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
Export.table.toDrive({
  collection: bang,
  description: 'RNM_bang_dien_tich_' + YEAR_A + '_' + YEAR_B,
  fileFormat: 'CSV'
});
