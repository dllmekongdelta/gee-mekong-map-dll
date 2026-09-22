# shapefile_dbscl

Ranh giới 5 tỉnh/thành phố thuộc vùng Đồng bằng sông Cửu Long (ĐBSCL) theo cơ cấu hành chính mới, sáp nhập từ 01/07/2025 (Nghị quyết 202/2025/QH15, Nghị quyết 306/NQ-CP): **Đồng Tháp, An Giang, Vĩnh Long, Cần Thơ, Cà Mau**.

- **Nguồn:** cắt (lọc theo `maTinh`) từ `D:\2_DATA_GIS\Ranh_gioi_hanh_chinh\RANHGIOI_HANHCHINH_2025\DiaPhan_Tinh_2025.shp` — file nguồn không bị chỉnh sửa.
- **Mã tỉnh (`maTinh`) đã chọn:** 803 (Đồng Tháp), 805 (An Giang), 809 (Vĩnh Long), 815 (Cần Thơ), 823 (Cà Mau).
- **Không gồm:** Tây Ninh (mã 709) — tuy tỉnh Tây Ninh mới đã sáp nhập thêm Long An (cũ, vốn thuộc ĐBSCL địa lý), nhưng theo phân loại vùng hành chính chính thức sau sáp nhập, Tây Ninh **không** thuộc vùng ĐBSCL.
- **Hệ toạ độ:** EPSG:4326 (WGS 84), khớp CRS với các shapefile khác trong repo.
- **Diện tích tổng (theo cột `dienTich`):** ~36.427 km². **Dân số tổng (cột `danSo`):** ~20.386.361 người.
- **Cột thuộc tính:** `maTinh`, `tenTinh`, `dienTich`, `danSo`, `tptinhtruo` (các tỉnh cũ đã sáp nhập vào), `trungtamhc` (trung tâm hành chính), `name`, `geometry`.

Dùng để làm vùng nghiên cứu (AOI) toàn ĐBSCL trên Google Earth Engine, theo cùng cách tải shapefile lên Assets như `shapefile_commune/` (xem [docs/HUONG_DAN_GEE_BIEN_DONG_RNM.md](../docs/HUONG_DAN_GEE_BIEN_DONG_RNM.md) mục 2.5).
