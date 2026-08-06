# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

* **Họ và tên**: Trần Chí Hiển
* **Mã học viên (MSSV)**: `2A202601162`
* **Lớp**: 2A2026
* **Vai trò phụ trách**: Kỹ sư giám sát & báo cáo dữ liệu (Data Observability & Reporting Developer)

---

## 1. Nhiệm vụ & Vai trò phụ trách
Đảm nhận thiết kế khâu giám sát chất lượng dữ liệu **Data Observability** (Data Quality & Freshness) và xuất báo cáo tự động **Reporting**:
* Triển khai hệ thống Great Expectations kiểm định dữ liệu.
* Phát triển các module tổng hợp và so sánh kết quả 3 giai đoạn tự động.

## 2. Mô-đun mã nguồn đảm nhiệm
* **Mô-đun giám sát**:
  - `src/observability/quality.py`
  - `src/observability/reporting.py`
* **Thư mục đầu ra**: `data/reports/` (Chứa `phase1_report.md` và `corruption_report.md`)

## 3. Kết quả thực hiện & Đóng góp chi tiết
* **Kiểm tra chất lượng dữ liệu (Data Quality Checks)**: Viết các quy tắc kiểm tra tính toàn vẹn dữ liệu (ID duy nhất, cột nội dung không rỗng, độ dài tiêu đề chuẩn).
* **Báo cáo độ tươi mới (Freshness Validation)**: Triển khai kiểm tra và cảnh báo khi dữ liệu cũ quá 180 ngày so với thời gian chạy thực tế.
* **Mẫu báo cáo Markdown tự động**: Xây dựng module tự động tính toán các chỉ số chênh lệch delta (như Delta F1, Delta Hit rate) và tạo lập báo cáo Markdown tổng hợp so sánh trực quan.

## 4. Tự đánh giá mức độ hoàn thành
* **Kết quả**: Hệ thống giám sát dữ liệu bắt đúng lỗi ở tập Corrupted (báo 🔴 FAILED) và tự động ghi nhận trạng thái sạch sau khi sửa (🟢 PASSED).
* **Độ hoàn thành**: **100%**
