# BÁO CÁO ĐÓNG GÓP CÁ NHÂN (INDIVIDUAL REPORT)

* **Họ và tên**: Nguyễn Văn Nam
* **Mã học viên (MSSV)**: `2A202601973`
* **Lớp**: 2A2026
* **Vai trò phụ trách**: Nhóm trưởng & Kỹ sư hệ thống RAG (Team Leader & RAG Architect)

---

## 1. Nhiệm vụ & Vai trò phụ trách
Đảm nhận quản lý nhóm và trực tiếp phát triển kiến trúc cốt lõi **Vector Indexing**, **RAG Retrieval Agent**, và **Pipeline Orchestration**:
* Xây dựng kho lưu trữ ChromaDB và điều phối các kịch bản pipeline.
* Tích hợp, điều phối và tối ưu hóa hiệu năng gọi mô hình LLM/Embedding.

## 2. Mô-đun mã nguồn đảm nhiệm
* **Mã nguồn cốt lõi**:
  - `src/retrieval/index.py`
  - `src/retrieval/embeddings.py`
  - `src/retrieval/llm.py`
  - `src/pipelines/`
* **Kịch bản chạy**: `script/run_phase1.py`, `script/run_corruption_flow.py`

## 3. Kết quả thực hiện & Đóng góp chi tiết
* **ChromaDB Indexing**: Thiết lập và tích hợp ChromaDB làm Vector Database lưu trữ index dưới dạng cosine similarity.
* **Xoay tua API Key & Model**: Viết cơ chế xoay tua thông minh giữa `gemini-3.1-flash-lite` và `gemini-3.5-flash-lite` trên pool 7 API Key.
* **Tối ưu hóa đa luồng & gom Batch**: Viết lớp `MultiKeyMistralEmbeddings` đa luồng, tối ưu hóa gửi batch 50 tài liệu giúp rút ngắn thời gian sinh embeddings xuống **1.5 giây**. Tích hợp HTTP connection pooling.
* **Orchestration**: Thiết kế và liên kết toàn bộ luồng chạy của Phase 1 và kịch bản khôi phục (Corruption/Repair Flow) khép kín.

## 4. Tự đánh giá mức độ hoàn thành
* **Kết quả**: Hoàn thành xuất sắc vai trò nhóm trưởng. Kết nối thành công mã nguồn của các thành viên. Pipeline chạy trơn tru với tốc độ tối đa.
* **Độ hoàn thành**: **100%**
