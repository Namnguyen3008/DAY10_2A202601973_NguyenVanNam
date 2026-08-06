# Báo cáo Đóng góp Cá nhân - Dự án Nhóm Lab Day 10

---

## 1. Thành viên: Nguyễn Đàm Kiên
* **MSSV**: `2A202602015`
* **Vị trí phụ trách**: Kỹ sư dữ liệu đầu vào (Data Ingestion Developer)
* **Mô-đun thực hiện**: [`src/ingestion/crossref.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/ingestion/crossref.py)
* **Đóng góp cụ thể**:
  - Nghiên cứu và tích hợp thành công Crossref REST API để truy vấn bài báo học thuật theo chủ đề chỉ định.
  - Thiết kế cơ chế lưu trữ raw artifacts (`crossref_response.json`, `crossref_records.json`) giúp bảo toàn dữ liệu nguồn phục vụ tái lập hoặc sửa lỗi.
  - Xây dựng hệ thống tự động thử lại (Retry) kèm giãn cách thời gian (Exponential Backoff) giúp tránh bị chặn bởi API Rate Limit.

---

## 2. Thành viên: Lê Nguyễn Phước Thành
* **MSSV**: `2A202601032`
* **Vị trí phụ trách**: Kỹ sư xử lý & phá hủy dữ liệu (Data Cleaning & Corruption Developer)
* **Mô-đun thực hiện**: 
  - [`src/ingestion/cleaning.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/ingestion/cleaning.py)
  - [`src/ingestion/corruption.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/ingestion/corruption.py)
* **Đóng góp cụ thể**:
  - Thiết kế quy trình làm sạch văn bản, loại bỏ các thẻ HTML/XML, đồng bộ hóa định dạng ngày tháng sang ISO 8601.
  - Thiết lập thuộc tính `age_days` xác định độ tuổi của bài báo khoa học.
  - Xây dựng module `corruption.py` giả lập 6 kịch bản lỗi dữ liệu cực kỳ thực tế để thử thách tính nhạy bén của hệ thống giám sát.

---

## 3. Thành viên: Nguyễn Văn Nam
* **MSSV**: `2A202601973`
* **Vị trí phụ trách**: Nhóm trưởng & Kiến trúc sư hệ thống RAG (Team Leader & RAG Architect)
* **Mô-đun thực hiện**:
  - [`src/retrieval/index.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/retrieval/index.py)
  - [`src/retrieval/embeddings.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/retrieval/embeddings.py)
  - [`src/retrieval/llm.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/retrieval/llm.py)
  - [`src/pipelines/`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/pipelines/)
* **Đóng góp cụ thể**:
  - Quản lý, điều phối tiến độ và phân chia công việc tối ưu cho các thành viên trong nhóm.
  - Tích hợp và tối ưu hóa thư viện ChromaDB làm kho lưu trữ vector index cục bộ.
  - Phát triển lớp `MultiKeyMistralEmbeddings` đa luồng, hỗ trợ gom cụm (batching 50 tài liệu/lần) giúp tăng tốc độ sinh vector lên **gấp 10 lần**.
  - Thiết lập cơ chế xoay tua luôn phiên giữa hai model LLM (`gemini-3.1-flash-lite` và `gemini-3.5-flash-lite`) trên pool 7 API Key.

---

## 4. Thành viên: Lê Kim Tính
* **MSSV**: `2A202601560`
* **Vị trí phụ trách**: Kỹ sư đánh giá chất lượng (QA Evaluation Developer)
* **Mô-đun thực hiện**:
  - [`src/evaluation/testset.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/evaluation/testset.py)
  - [`src/evaluation/metrics.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/evaluation/metrics.py)
* **Đóng góp cụ thể**:
  - Xây dựng bộ quy tắc sinh câu hỏi kiểm thử ngẫu nhiên (`test_set.json`) đa dạng hóa các nhóm chủ đề khác nhau (summary, authors, date, categories).
  - Triển khai thuật toán tính toán độ trùng khớp từ vựng Token F1-score và tích hợp LLM Judge để cho điểm câu trả lời một cách khách quan.
  - Thiết kế đa luồng `ThreadPoolExecutor` chạy song song 14 luồng giúp chấm điểm bộ câu hỏi RAG siêu tốc chỉ dưới **15 giây**.

---

## 5. Thành viên: Trần Chí Hiển
* **MSSV**: `2A202601162`
* **Vị trí phụ trách**: Kỹ sư quan sát và báo cáo (Data Observability & Reporting Developer)
* **Mô-đun thực hiện**:
  - [`src/observability/quality.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/observability/quality.py)
  - [`src/observability/reporting.py`](file:///c:/Users/Namdr/Downloads/DAY%2010/src/observability/reporting.py)
* **Đóng góp cụ thể**:
  - Định nghĩa các bộ quy tắc chất lượng dữ liệu (Data Quality Rules) như kiểm tra tính duy nhất của ID bài báo, độ dài tiêu đề tối thiểu, và tính hợp lệ của tóm tắt.
  - Tích hợp báo cáo độ tươi mới dữ liệu (Freshness Report) giúp cảnh báo kịp thời các tài liệu cũ vượt ngưỡng quy định.
  - Phát triển module sinh báo cáo tự động Markdown đẹp mắt, trực quan giúp so sánh rõ ràng các chỉ số RAG qua ba giai đoạn Baseline, Corrupted và Repaired.
