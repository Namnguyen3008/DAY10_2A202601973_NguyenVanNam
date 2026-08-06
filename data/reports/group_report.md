# Báo cáo Dự án Nhóm - Lab Day 10: Data Pipeline & Data Observability

## 1. Thông tin chung
* **Tên đề tài**: Xây dựng Data Pipeline & Data Observability cho hệ thống RAG học thuật
* **Nhóm thực hiện**: Nhóm 5 thành viên (Lớp 2A2026)
* **Repository**: https://github.com/Namnguyen3008/DAY10_2A202601973_NguyenVanNam

---

## 2. Kiến trúc & Giải pháp kỹ thuật

Hệ thống được thiết kế theo mô hình Data Pipeline khép kín gồm 7 thành phần chính:

```
[Crossref API] 
      │ (Ingestion)
      ▼
 [Raw JSON] ──► [Cleaning Pipeline] ──► [Clean CSV] 
                                            │
   ┌────────────────────────────────────────┴────────────────────────────────────────┐
   ▼ (Baseline)                                                                      ▼ (Corruption Flow)
[ChromaDB Baseline]                                                            [Data Corruption]
   │                                                                                 │
   ▼                                                                                 ▼
[RAG Agent Assessment]                                                         [Corrupted DB] 
   │ (Accuracy: 100%)                                                                │ (Accuracy: 50%)
   ▼                                                                                 ▼
[Phase 1 Report]                                                               [Observability Alert: FAILED]
                                                                                     │
                                                                                     ▼
                                                                             [Automated Repair]
                                                                                     │
                                                                                     ▼
                                                                             [Repaired Index] 
                                                                                     │ (Accuracy: 100%)
                                                                                     ▼
                                                                             [Comparison Report]
```

1. **Data Ingestion**: Thu thập bất đồng bộ dữ liệu học thuật từ Crossref REST API qua từ khóa tìm kiếm, lưu trữ dưới dạng raw JSON.
2. **Data Cleaning**: Loại bỏ nhiễu HTML, đồng bộ định dạng ngày tháng, tính toán thuộc tính `age_days` và sinh cột văn bản tích hợp `text_for_embedding`.
3. **Vector Database**: Sử dụng ChromaDB persistent client và embedding model `mistral-embed` để đánh chỉ mục các bài báo.
4. **Test Set Generator**: Sinh tự động 32 câu hỏi test set thuộc 4 nhóm chủ đề phục vụ đánh giá chéo.
5. **Data Corruption**: Giả lập phá hủy dữ liệu (trùng lặp, làm cũ thời gian, xóa cột quan trọng, rỗng tóm tắt) để kiểm thử hệ thống.
6. **Data Observability**: Tích hợp các kiểm tra chất lượng dữ liệu (Data Quality Checks) và độ tươi mới (Freshness Validation).
7. **Automated Repair**: Khôi phục dữ liệu tự động từ raw JSON gốc để tái tạo lại vector index hoàn chỉnh.

---

## 3. Kết quả đánh giá hiệu năng (Benchmark)

| Chỉ số | Baseline (Sạch) | Corrupted (Lỗi) | Repaired (Đã sửa) | Nhận xét |
| :--- | :---: | :---: | :---: | :--- |
| **Tỷ lệ tìm kiếm đúng (Hit Rate)** | `100.0%` | `50.0%` | `100.0%` | Độ chính xác khôi phục hoàn toàn về 100%. |
| **Điểm LLM Judge trung bình** | `4.31 / 5.0` | `3.00 / 5.0` | `4.41 / 5.0` | Tập Repaired tối ưu hơn do loại bỏ nhiễu. |
| **Trạng thái chất lượng dữ liệu** | `🟢 PASSED` | `🔴 FAILED` | `🟢 PASSED` | Hệ thống giám sát bắt chính xác 100% lỗi dữ liệu. |
| **Độ tươi mới dữ liệu** | `Fresh` | `Stale` | `Fresh` | Phát hiện chính xác dữ liệu cũ trên 180 ngày. |

---

## 4. Kết luận & Bài học kinh nghiệm
* **Tác động của chất lượng dữ liệu**: Dữ liệu lỗi/thiếu hụt trực tiếp kéo giảm 50% hiệu năng tìm kiếm thông tin của RAG Agent.
* **Tầm quan trọng của Observability**: Việc có các chốt chặn kiểm tra chất lượng tự động giúp phát hiện lỗi hệ thống trước khi trả thông tin sai lệch cho người dùng cuối.
* **Khả năng tự phục hồi**: Tách biệt pha Ingest (Raw) và Clean giúp dễ dàng chạy lại pipeline khôi phục dữ liệu mà không cần gọi lại API nguồn.
