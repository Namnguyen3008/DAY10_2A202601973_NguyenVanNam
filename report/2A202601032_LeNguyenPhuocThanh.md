# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

* **Họ và tên**: Lê Nguyễn Phước Thành
* **Mã học viên (MSSV)**: `2A202601032`
* **Lớp**: 2A2026
* **Vai trò phụ trách**: Kỹ sư xử lý & phá hủy dữ liệu (Data Cleaning & Corruption Developer)

---

## 1. Nhiệm vụ & Vai trò phụ trách
Đảm nhận các khâu **Data Cleaning & Preprocessing** (Làm sạch & tiền xử lý) và **Data Corruption Simulation** (Giả lập lỗi dữ liệu):
* Chuẩn hóa và làm sạch văn bản cho mô hình embedding.
* Viết kịch bản phá hủy dữ liệu lỗi có chủ ý để kiểm định hệ thống giám sát.

## 2. Mô-đun mã nguồn đảm nhiệm
* **File tiền xử lý**: `src/ingestion/cleaning.py`
* **File giả lập lỗi**: `src/ingestion/corruption.py`
* **Thư mục đầu ra**: `data/clean/` (Chứa `papers_clean.csv`, `papers_clean_corrupted.csv`, `papers_clean_repaired.csv`)

## 3. Kết quả thực hiện & Đóng góp chi tiết
* **Chuẩn hóa văn bản**: Xây dựng bộ lọc loại bỏ thẻ XML/HTML, định dạng thống nhất ngày tháng xuất bản sang định dạng ISO 8601 quốc tế, tính tuổi dữ liệu `age_days`.
* **Xây dựng trường văn bản tổng hợp**: Thiết lập trường `text_for_embedding` bằng cách ghép Title và Summary của bài báo để tối ưu hóa hiệu quả tìm kiếm ngữ nghĩa.
* **Giả lập dữ liệu lỗi**: Thiết lập hàm `corrupt_clean_dataframe` thực thi 6 loại lỗi dữ liệu (lọc bỏ dòng mới, xóa cột nội dung, chèn text nhiễu, làm stale ngày tháng, trùng lặp dòng).

## 4. Tự đánh giá mức độ hoàn thành
* **Kết quả**: Quy trình xử lý hoạt động mượt mà. Kịch bản lỗi dữ liệu tạo thành công làm tụt hiệu năng RAG từ 100% xuống 50%, giúp kiểm thử observability xuất sắc.
* **Độ hoàn thành**: **100%**
