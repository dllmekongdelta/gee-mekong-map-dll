/**
 * ============================================================================
 *  BIẾN ĐỘNG RỪNG NGẬP MẶN NHIỀU MỐC NĂM (1988 -> nay) -- VÙNG MẪU ĐẤT MŨI (CÀ MAU)
 *  Bản hoàn chỉnh cho GEE Code Editor: dán toàn bộ file, bấm Run.
 *
 *  Ý TƯỞNG CHÍNH (khác bản chỉ so 2 năm):
 *  - Không làm 3 bản đồ tách rời (Coverage / Loss / Gain, như MAP01-03 của repo).
 *  - Mỗi GIAI ĐOẠN giữa 2 mốc năm liên tiếp (1988-1992, 1992-1997, ...) chỉ có
 *    ĐÚNG 1 bản đồ, gộp 3 lớp: Ổn định / Mất rừng / Rừng mới. Cùng 3 màu cho
 *    mọi giai đoạn (không cần bảng màu 9 sắc như trước), nên chỉ cần 1 chú giải.
 *  - Tính thêm TỶ LỆ biến động mỗi giai đoạn (mất, mới, ròng theo % rừng đầu kỳ,
 *    và tốc độ ha/năm) để SO SÁNH giai đoạn nào biến động mạnh hơn.
 *
 *  Kết quả:
 *    - N bản đồ biến động 3 lớp (N = số giai đoạn), chỉ giai đoạn gần nhất hiện
 *      sẵn, các giai đoạn khác tự bật ở khung Layers (góc phải trên bản đồ).
 *    - Bảng diện tích rừng theo từng mốc năm.
 *    - Bảng biến động theo từng giai đoạn: mất/mới/ròng (ha), tỷ lệ (%), tốc độ (ha/năm).
 *    - So sánh giai đoạn gần nhất với trung bình các giai đoạn trước (z-score).
 *    - Độ chính xác so với Global Mangrove Watch cho các năm có tham chiếu.
 *    - Xuất GeoTIFF (mỗi giai đoạn 1 file) + CSV ra Google Drive (tab Tasks).
 *
 *  Phương pháp giống pipeline Python của repo (GEN03/GEN04):
 *    ảnh ghép median cả năm -> NDVI -> ngưỡng theo cảm biến (Landsat: 0.10,
 *    Sentinel-2: 0.25) -> so hai mốc liên tiếp.
 *  Công thức rừng ngập mặn:  NDVI > ngưỡng  VÀ  nằm trong dải ven biển (ROI).
 *  ROI thay cho việc code Python vẽ tay AOI dọc bờ biển: NDVI không phân biệt được
 *  rừng ngập mặn với lúa / cây trồng, nên phải giới hạn không gian (mục 4.5 của
 *  Hướng dẫn). ROI cố định theo thời gian, dùng chung cho mọi mốc năm.
 *  Với Sentinel-2 (2020, nay), bật mặt nạ mây theo điểm ảnh (band SCL): chỉ lọc
 *  theo % mây của cả cảnh không đủ khi ảnh gần đây còn ít cảnh (mục 3.5).
 *
 *  Script này chạy khoảng 2-5 phút (9 mốc năm x nhiều phép tính). Bình thường.
 *  Chỉ cần sửa khối "0. THAM SỐ". Hướng dẫn chi tiết:
 *  docs/HUONG_DAN_GEE_BIEN_DONG_RNM.md
 * ============================================================================
 */

// ---------------------------------------------------------------------------
// 0. THAM SỐ (chỉ sửa phần này)
// ---------------------------------------------------------------------------
var AOI = ee.Geometry.Rectangle([104.72, 8.56, 104.92, 8.74]);  // [Tây, Nam, Đông, Bắc]

// Các mốc năm, giống chuỗi 1988-2026 của repo. Thêm collection/band/ngưỡng đúng
// với cảm biến của từng mốc (xem Hướng dẫn mục 4 để hiểu vì sao band khác nhau).
// Mốc cuối dùng nhãn 'nay' và lấy dữ liệu đến NGÀY HÔM NAY (không phải hết năm),
// vì năm hiện tại chưa có đủ ảnh cả năm.
var MILESTONES = [
  {year: 1988, label: '1988', collection: 'LANDSAT/LT05/C02/T1_L2', sensorName: 'Landsat 5',
   cloudProp: 'CLOUD_COVER', cloudMax: 30, nir: 'SR_B4', red: 'SR_B3', thr: 0.10, isS2: false},
  {year: 1992, label: '1992', collection: 'LANDSAT/LT05/C02/T1_L2', sensorName: 'Landsat 5',
   cloudProp: 'CLOUD_COVER', cloudMax: 30, nir: 'SR_B4', red: 'SR_B3', thr: 0.10, isS2: false},
  {year: 1997, label: '1997', collection: 'LANDSAT/LT05/C02/T1_L2', sensorName: 'Landsat 5',
   cloudProp: 'CLOUD_COVER', cloudMax: 30, nir: 'SR_B4', red: 'SR_B3', thr: 0.10, isS2: false},
  {year: 2001, label: '2001', collection: 'LANDSAT/LE07/C02/T1_L2', sensorName: 'Landsat 7',
   cloudProp: 'CLOUD_COVER', cloudMax: 30, nir: 'SR_B4', red: 'SR_B3', thr: 0.10, isS2: false},
  {year: 2005, label: '2005', collection: 'LANDSAT/LE07/C02/T1_L2', sensorName: 'Landsat 7',
   cloudProp: 'CLOUD_COVER', cloudMax: 30, nir: 'SR_B4', red: 'SR_B3', thr: 0.10, isS2: false},
  {year: 2010, label: '2010', collection: 'LANDSAT/LE07/C02/T1_L2', sensorName: 'Landsat 7',
   cloudProp: 'CLOUD_COVER', cloudMax: 30, nir: 'SR_B4', red: 'SR_B3', thr: 0.10, isS2: false},
  {year: 2015, label: '2015', collection: 'LANDSAT/LC08/C02/T1_L2', sensorName: 'Landsat 8',
   cloudProp: 'CLOUD_COVER', cloudMax: 30, nir: 'SR_B5', red: 'SR_B4', thr: 0.10, isS2: false},
  {year: 2020, label: '2020', collection: 'COPERNICUS/S2_SR_HARMONIZED', sensorName: 'Sentinel-2',
   cloudProp: 'CLOUDY_PIXEL_PERCENTAGE', cloudMax: 20, nir: 'B8', red: 'B4', thr: 0.25, isS2: true},
  {year: 2026, label: 'nay (2026)', collection: 'COPERNICUS/S2_SR_HARMONIZED', sensorName: 'Sentinel-2',
   cloudProp: 'CLOUDY_PIXEL_PERCENTAGE', cloudMax: 20, nir: 'B8', red: 'B4', thr: 0.25, isS2: true}
];
var LAST_YEAR = 2026;  // mốc cuối = mốc dùng nhãn 'nay' và lấy đến ngày hôm nay

// VÙNG LỌC (ROI): chỉ tính rừng ngập mặn trong dải ven biển, để không lẫn
// lúa, cây trồng, vườn cây ở phía đất liền (NDVI không phân biệt được các loại cây xanh).
// Ưu tiên 1: ROI_POLYGON = đa giác bạn tự vẽ dọc dải rừng (giống AOI vẽ tay của code Python).
//            Vẽ bằng công cụ Geometry, đặt tên vungLoc, rồi viết: var ROI_POLYGON = vungLoc;
// Ưu tiên 2: MAX_DIST_SEA_KM = chỉ lấy vùng cách biển tối đa bằng ngần này km (tự động).
//            Đặt 0 để tắt (dùng cả khung AOI). Xem mục 4.5 của hướng dẫn để chọn giá trị.
var ROI_POLYGON = null;
var MAX_DIST_SEA_KM = 5;

var USE_SCL_MASK = true;      // true = loại mây theo điểm ảnh (Sentinel-2); false = chỉ lọc % mây
var RUN_SWEEP = false;        // true = quét ngưỡng NDVI 0.10-0.35 cho năm SWEEP_YEAR so với GMW
var SWEEP_YEAR = 2020;
var SCALE = 30;                // mét, dùng chung cho mọi phép tính diện tích / độ chính xác
var SHOW_LAST_PERIOD_ONLY = true;  // true = chỉ hiện sẵn giai đoạn gần nhất, còn lại tự bật ở Layers

// ---------------------------------------------------------------------------
// 1. HÀM
// ---------------------------------------------------------------------------

// Loại điểm ảnh hỏng / bóng mây / mây / mây ti (SCL: 1, 3, 8, 9, 10) -- chỉ Sentinel-2
function maskS2(img) {
  var scl = img.select('SCL');
  var bad = scl.eq(1).or(scl.eq(3)).or(scl.eq(8)).or(scl.eq(9)).or(scl.eq(10));
  return img.updateMask(bad.not());
}

// Vùng lọc (ROI) dạng ảnh 0/1. Cố định theo thời gian (không đổi giữa các mốc)
// nên mọi mốc năm luôn được so sánh trên cùng một vùng.
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

// Ảnh ghép median + NDVI + mặt nạ rừng (NDVI > ngưỡng VÀ nằm trong ROI) cho 1 mốc năm.
// cfg là 1 phần tử của MILESTONES ở trên.
function buildMilestone(cfg) {
  var isLast = cfg.year === LAST_YEAR;
  var endDate = isLast ? NOW_STR : (cfg.year + 1) + '-01-01';   // mốc cuối: đến hôm nay
  var cloudMax = (cfg.isS2 && USE_SCL_MASK) ? 60 : cfg.cloudMax;
  var col = ee.ImageCollection(cfg.collection)
      .filterBounds(AOI)
      .filterDate(cfg.year + '-01-01', endDate)
      .filter(ee.Filter.lt(cfg.cloudProp, cloudMax));
  if (cfg.isS2 && USE_SCL_MASK) {
    col = col.map(maskS2);
  }
  print('So canh ' + cfg.label + ' (' + cfg.sensorName + '):', col.size());
  var img = col.median().clip(AOI);
  var ndvi = img.normalizedDifference([cfg.nir, cfg.red]).rename('NDVI');
  var mask = ndvi.gt(cfg.thr).and(ROI).rename('mangrove');
  return {year: cfg.year, label: cfg.label, cfg: cfg, img: img, ndvi: ndvi, mask: mask};
}

// Diện tích (ha) của các điểm ảnh = 1
function areaHa(binary) {
  var tong = binary.multiply(ee.Image.pixelArea()).reduceRegion({
    reducer: ee.Reducer.sum(), geometry: AOI, scale: SCALE, maxPixels: 1e13, bestEffort: true
  });
  return ee.Number(tong.values().get(0)).divide(10000);
}

// Độ chính xác của mặt nạ pred so với mặt nạ tham chiếu ref (đều 0/1), chỉ tính trong ROI
function accuracy(pred, ref) {
  var combo = pred.toInt().multiply(2).add(ref.toInt()).updateMask(ROI).rename('combo');
  var hist = ee.Dictionary(combo.reduceRegion({
    reducer: ee.Reducer.frequencyHistogram(), geometry: AOI, scale: SCALE,
    maxPixels: 1e13, bestEffort: true
  }).get('combo'));
  // combo: 0 = cả hai không rừng (TN) | 1 = chỉ tham chiếu có rừng (bỏ sót, FN)
  //        2 = chỉ mình có rừng (thừa, FP) | 3 = cả hai có rừng (TP)
  var tn = ee.Number(hist.get('0', 0));
  var fn = ee.Number(hist.get('1', 0));
  var fp = ee.Number(hist.get('2', 0));
  var tp = ee.Number(hist.get('3', 0));
  var total = tn.add(fn).add(fp).add(tp);
  var oa = tp.add(tn).divide(total);
  var pa = tp.divide(tp.add(fn));
  var ua = tp.divide(tp.add(fp));
  var pe = tp.add(fp).multiply(tp.add(fn))
      .add(fn.add(tn).multiply(fp.add(tn)))
      .divide(total.multiply(total));
  var kappa = oa.subtract(pe).divide(ee.Number(1).subtract(pe));
  return ee.Dictionary({
    OverallAccuracy: oa.format('%.3f'), ProducerAccuracy: pa.format('%.3f'),
    UserAccuracy: ua.format('%.3f'), Kappa: kappa.format('%.3f')
  });
}

// Một hàng chú giải: ô màu + chữ
function hangChuGiai(mau, chu) {
  var o = ui.Label('', {backgroundColor: mau, padding: '8px', margin: '0 6px 4px 0'});
  var t = ui.Label(chu, {margin: '0 0 4px 0', fontSize: '12px'});
  return ui.Panel([o, t], ui.Panel.Layout.Flow('horizontal'));
}

// ---------------------------------------------------------------------------
// 2. MẶT NẠ RỪNG CHO TỪNG MỐC NĂM
// ---------------------------------------------------------------------------
var NOW_STR = new Date().toISOString().slice(0, 10);  // ngày hôm nay, dạng 'YYYY-MM-DD'
var ROI = buildRoi();

var milestones = MILESTONES.map(buildMilestone);   // 1 phần tử / mốc năm, theo đúng thứ tự
var maskByYear = {};
milestones.forEach(function (m) { maskByYear[m.year] = m.mask; });

// ---------------------------------------------------------------------------
// 3. PHÁT HIỆN BIẾN ĐỘNG -- 1 BẢN ĐỒ GỘP 3 LỚP CHO MỖI GIAI ĐOẠN
// ---------------------------------------------------------------------------
var COLOR_STABLE = '#1a9850';   // xanh lá: rừng cả hai mốc
var COLOR_LOSS = '#c51b8a';     // tím hồng: mất rừng
var COLOR_GAIN = '#ffd92f';     // vàng: rừng mới

// Mỗi phần tử: {a, b, labelA, labelB, loss, gain, stable, bienDong}
var periods = [];
for (var i = 0; i < milestones.length - 1; i++) {
  var mA = milestones[i];
  var mB = milestones[i + 1];
  var loss = mA.mask.and(mB.mask.not());     // có rừng ở A, mất ở B
  var gain = mB.mask.and(mA.mask.not());     // không có ở A, có rừng ở B
  var stable = mA.mask.and(mB.mask);         // rừng cả hai mốc
  // Gộp thành 1 ảnh: 1 = ổn định, 2 = mất, 3 = mới (CHỈ 3 LỚP, dùng chung cho mọi giai đoạn)
  var bienDong = ee.Image(0).where(stable, 1).where(loss, 2).where(gain, 3).rename('change');
  bienDong = bienDong.updateMask(bienDong.gt(0));
  periods.push({
    a: mA.year, b: mB.year, labelA: mA.label, labelB: mB.label,
    loss: loss, gain: gain, stable: stable, bienDong: bienDong
  });
}

// ---------------------------------------------------------------------------
// 4. HIỂN THỊ BẢN ĐỒ
// ---------------------------------------------------------------------------
var RGB_VIS_S2 = {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000};
var RGB_VIS_L = {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 7000, max: 16000};

Map.setOptions('SATELLITE');
Map.centerObject(AOI, 11);
Map.addLayer(ROI.updateMask(ROI), {palette: ['ffffff']}, 'Vùng lọc (ROI)', false, 0.3);

// Ảnh màu thật + mặt nạ rừng từng mốc năm (ẩn theo mặc định, tự bật ở Layers để kiểm tra)
milestones.forEach(function (m) {
  var vis = m.cfg.isS2 ? RGB_VIS_S2 : RGB_VIS_L;
  Map.addLayer(m.img, vis, 'Ảnh ' + m.label, false);
  Map.addLayer(m.mask.updateMask(m.mask), {palette: [COLOR_STABLE]}, 'Rừng ' + m.label, false);
});

// 1 lớp bản đồ biến động cho mỗi giai đoạn -- CÙNG 3 màu, không cần đổi bảng màu theo giai đoạn
periods.forEach(function (p, idx) {
  var isLastPeriod = idx === periods.length - 1;
  var visibleByDefault = SHOW_LAST_PERIOD_ONLY ? isLastPeriod : true;
  Map.addLayer(p.bienDong, {min: 1, max: 3, palette: [COLOR_STABLE, COLOR_LOSS, COLOR_GAIN]},
      'BIẾN ĐỘNG ' + p.labelA + ' - ' + p.labelB, visibleByDefault);
});

// Chú giải DUY NHẤT, dùng chung cho mọi giai đoạn (đây là điểm khác so với bảng màu
// 9 sắc LOSS/GAIN của repo -- ở đây chỉ có 3 lớp, không phụ thuộc giai đoạn nào)
var chuGiai = ui.Panel({style: {position: 'bottom-right', padding: '8px 12px'}});
chuGiai.add(ui.Label('Biến động rừng ngập mặn', {fontWeight: 'bold'}));
chuGiai.add(ui.Label('(bật giai đoạn cần xem ở khung Layers)', {fontSize: '11px', color: '666666'}));
chuGiai.add(hangChuGiai(COLOR_STABLE, 'Ổn định'));
chuGiai.add(hangChuGiai(COLOR_LOSS, 'Mất rừng'));
chuGiai.add(hangChuGiai(COLOR_GAIN, 'Rừng mới'));
Map.add(chuGiai);

// ---------------------------------------------------------------------------
// 5. BẢNG DIỆN TÍCH THEO MỐC NĂM
// ---------------------------------------------------------------------------
var bangDienTich = ee.FeatureCollection(milestones.map(function (m) {
  return ee.Feature(null, {nam: m.label, ha: areaHa(m.mask)});
}));
print('BẢNG DIỆN TÍCH RỪNG THEO MỐC NĂM (ha)', bangDienTich);
print(ui.Chart.feature.byFeature(bangDienTich, 'nam', 'ha').setChartType('ColumnChart')
    .setOptions({title: 'Diện tích rừng ngập mặn theo mốc năm (ha)', legend: {position: 'none'}}));

// ---------------------------------------------------------------------------
// 6. BẢNG BIẾN ĐỘNG + TỶ LỆ THEO TỪNG GIAI ĐOẠN (đây là phần thay cho "3 bản đồ riêng")
// ---------------------------------------------------------------------------
var bangBienDong = ee.FeatureCollection(periods.map(function (p) {
  var lossHa = areaHa(p.loss);
  var gainHa = areaHa(p.gain);
  var startHa = areaHa(maskByYear[p.a]);
  var years = p.b - p.a;   // số năm giữa 2 mốc (mốc cuối tính theo năm lịch, dữ liệu có thể chưa đủ năm)
  var netHa = gainHa.subtract(lossHa);
  return ee.Feature(null, {
    giai_doan: p.labelA + '-' + p.labelB,
    mat_ha: lossHa, moi_ha: gainHa, rong_ha: netHa,
    ty_le_mat_pct: lossHa.divide(startHa).multiply(100),   // % rừng đầu kỳ bị mất
    ty_le_moi_pct: gainHa.divide(startHa).multiply(100),   // % rừng đầu kỳ có thêm (rừng mới)
    toc_do_ha_nam: netHa.divide(years)                      // tốc độ ròng, ha/năm
  });
}));
print('BẢNG BIẾN ĐỘNG THEO GIAI ĐOẠN (ha, %, ha/năm)', bangBienDong);
print(ui.Chart.feature.byFeature(bangBienDong, 'giai_doan', 'toc_do_ha_nam').setChartType('ColumnChart')
    .setOptions({title: 'Tốc độ biến động ròng theo giai đoạn (ha/năm)', legend: {position: 'none'}}));

// So sánh giai đoạn GẦN NHẤT với trung bình các giai đoạn LỊCH SỬ trước đó (kiểu z-score,
// giống Phần 2 của MAP05_Validation_RecentChange.ipynb, nhưng đơn giản hoá cho Code Editor).
var rates = bangBienDong.aggregate_array('toc_do_ha_nam');
var nPeriods = periods.length;
var historicalRates = ee.List(rates).slice(0, nPeriods - 1);   // bỏ giai đoạn cuối
var recentRate = ee.List(rates).get(nPeriods - 1);
var histMean = ee.Number(historicalRates.reduce(ee.Reducer.mean()));
var histStd = ee.Number(ee.List(historicalRates).reduce(ee.Reducer.stdDev()));
var zScore = ee.Number(recentRate).subtract(histMean).divide(histStd);
print('Tốc độ trung bình các giai đoạn lịch sử (ha/năm):', histMean);
print('Độ lệch chuẩn tốc độ lịch sử (ha/năm):', histStd);
print('Tốc độ giai đoạn gần nhất (ha/năm):', recentRate);
print('Standardized departure (z-score) của giai đoạn gần nhất so với lịch sử:', zScore);
print('Đọc z-score: |z| >= 2 là đáng chú ý (khác thường so với biến thiên lịch sử); ' +
    '|z| < 2 là nằm trong biên độ dao động bình thường. Với ít giai đoạn lịch sử (ở đây: ' +
    (nPeriods - 1) + '), đây là chỉ số mô tả/khám phá, không phải kiểm định giả thuyết chặt chẽ.');

// ---------------------------------------------------------------------------
// 7. ĐỘ CHÍNH XÁC SO VỚI GLOBAL MANGROVE WATCH v3
//    GMW chỉ có 1996, 2007-2010, 2015-2020: chỉ so được các mốc trùng hoặc gần trùng.
//    Mốc 'nay' (2026) không có tham chiếu: dùng điểm tham chiếu tự chọn ở mục 9.
// ---------------------------------------------------------------------------
var GMW = ee.ImageCollection('projects/sat-io/open-datasets/GMW/extent/GMW_V3');
var GMW_MATCHES = [
  {year: 1997, gmwYear: 1996, approx: true},    // lệch 1 năm, so khớp gần đúng
  {year: 2010, gmwYear: 2010, approx: false},
  {year: 2015, gmwYear: 2015, approx: false},
  {year: 2020, gmwYear: 2020, approx: false}
];
GMW_MATCHES.forEach(function (mObj) {
  var ref = GMW.filter(ee.Filter.eq('id_no', 'gmw_v3_' + mObj.gmwYear)).first()
      .select('b1').unmask(0).gt(0).rename('gmw').clip(AOI);
  var tag = mObj.approx ? ' (so khớp gần đúng, lệch 1 năm)' : '';
  print('ĐỘ CHÍNH XÁC ' + mObj.year + ' so với GMW ' + mObj.gmwYear + tag,
      accuracy(maskByYear[mObj.year], ref));
  if (mObj.year === 2020) {
    print('Rừng GMW ' + mObj.gmwYear + ' nằm ngoài ROI (ha):', areaHa(ref.and(ROI.not())));
  }
});
print('Diện tích ROI (ha):', areaHa(ROI));

// ---------------------------------------------------------------------------
// 8. (TUỲ CHỌN) QUÉT NGƯỠNG NDVI SO VỚI GMW CHO 1 NĂM -- đặt RUN_SWEEP = true ở trên
// ---------------------------------------------------------------------------
if (RUN_SWEEP) {
  var sweepM = milestones.filter(function (m) { return m.year === SWEEP_YEAR; })[0];
  var sweepMatch = GMW_MATCHES.filter(function (g) { return g.year === SWEEP_YEAR; })[0];
  if (sweepM && sweepMatch) {
    var sweepRef = GMW.filter(ee.Filter.eq('id_no', 'gmw_v3_' + sweepMatch.gmwYear)).first()
        .select('b1').unmask(0).gt(0).rename('gmw').clip(AOI);
    [0.10, 0.15, 0.20, 0.25, 0.30, 0.35].forEach(function (t) {
      print('NDVI(' + SWEEP_YEAR + ') > ' + t, accuracy(sweepM.ndvi.gt(t).and(ROI), sweepRef));
    });
  } else {
    print('RUN_SWEEP: SWEEP_YEAR không có trong MILESTONES hoặc GMW_MATCHES.');
  }
}

// ---------------------------------------------------------------------------
// 9. (TUỲ CHỌN) ĐỘ CHÍNH XÁC: ĐIỂM THAM CHIẾU TỰ CHỌN CHO MỐC 'NAY' (không có GMW)
//    Cách làm: xem mục 6.5 của Hướng dẫn. Vẽ >= 50 điểm mỗi loại bằng công cụ
//    Geometry (góc trên trái bản đồ), đổi tên layer và import thành
//    FeatureCollection có property 'ref':
//      mangrovePts -> ref = 1 (chắc chắn là rừng ngập mặn)
//      otherPts    -> ref = 0 (nước, bùn, ao tôm, lúa, đất trống...)
//    Sau đó bỏ dấu /* và */ ở dưới đây.
// ---------------------------------------------------------------------------
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
print("User's Accuracy [không rừng, rừng]:", cm.consumersAccuracy());
print('Kappa:', cm.kappa());
*/

// ---------------------------------------------------------------------------
// 10. XUẤT RA GOOGLE DRIVE (mở tab Tasks -> bấm Run ở từng dòng)
// ---------------------------------------------------------------------------
periods.forEach(function (p) {
  Export.image.toDrive({
    image: p.bienDong.unmask(0).toByte(),   // 0 = không rừng, 1 = ổn định, 2 = mất, 3 = mới
    description: 'RNM_bien_dong_' + p.a + '_' + p.b,
    region: AOI, scale: SCALE, crs: 'EPSG:4326', maxPixels: 1e13
  });
});
Export.table.toDrive({
  collection: bangDienTich, description: 'RNM_bang_dien_tich_theo_moc_nam', fileFormat: 'CSV'
});
Export.table.toDrive({
  collection: bangBienDong, description: 'RNM_bang_bien_dong_theo_giai_doan', fileFormat: 'CSV'
});
