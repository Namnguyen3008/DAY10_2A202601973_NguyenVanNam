# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

* **Họ và tên**: Nguyễn Đàm Kiên
* **Mã học viên (MSSV)**: `2A202602015`
* **Lớp**: 2A2026
* **Vai trò phụ trách**: Kỹ sư dữ liệu đầu vào (Data Ingestion Developer)

---

## 1. Nhiệm vụ & Vai trò phụ trách
Đảm nhận toàn bộ pha **Data Ingestion** (Thu thập dữ liệu đầu vào) trong chuỗi cung ứng dữ liệu RAG:
* Kết nối, truy vấn dữ liệu từ API bên ngoài.
* Thiết lập hệ thống lưu trữ raw data nguyên bản.

## 2. Mô-đun mã nguồn đảm nhiệm
* **File chính**: `src/ingestion/crossref.py`
* **Thư mục đầu ra**: `data/raw/` (Chứa `crossref_response.json` và `crossref_records.json`)

## 3. Kết quả thực hiện & Đóng góp chi tiết
* **Truy vấn Crossref REST API**: Viết mã nguồn gọi API Crossref bằng từ khóa "agentic retrieval augmented generation large language model", lọc theo ngày xuất bản và yêu cầu có tóm tắt.
* **Cơ chế Retry & Backoff**: Triển khai cơ chế tự động thử lại khi API quá tải, sử dụng Exponential Backoff để tránh bị khóa bởi máy chủ.
* **Lưu trữ dữ liệu thô (Raw Artifacts)**: Lưu trữ kết quả gốc trả về dưới dạng JSON thô để có thể truy vết nguồn gốc dữ liệu khi phát sinh lỗi hệ thống.

## 4. Tự đánh giá mức độ hoàn thành
* **Kết quả**: Hoàn thành xuất sắc nhiệm vụ. Dữ liệu thô thu thập đủ 24 bản ghi chuẩn, chạy ổn định và không gặp lỗi ngắt quãng.
* **Độ hoàn thành**: **100%**
