# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | Lớp 2A2026 |
| Tên nhóm         | Nhóm 5 thành viên |
| Repository         | https://github.com/Namnguyen3008/DAY10_2A202601973_NguyenVanNam.git |
| Ngày hoàn thành | 2026-08-06 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Nguyễn Đàm Kiên | 2A202602015 | Ingestion | `src/ingestion/crossref.py` |
| 2 | Lê Nguyễn Phước Thành | 2A202601032 | Cleaning | `src/ingestion/cleaning.py`, `src/ingestion/corruption.py` |
| 3 | Nguyễn Văn Nam | 2A202601973 | Vector Indexing | `src/retrieval/index.py`, `src/pipelines/` |
| 4 | Lê Kim Tính | 2A202601560 | Evaluation | `src/evaluation/testset.py`, `src/evaluation/metrics.py` |
| 5 | Trần Chí Hiển | 2A202601162 | Observability | `src/observability/quality.py`, `src/observability/reporting.py` |

## 2. Tóm tắt kết quả

Nhóm đã hoàn thành trọn vẹn 100% mục tiêu của bài lab, bao gồm:
* Xây dựng pipeline thu thập dữ liệu học thuật tự động từ Crossref API, thực hiện làm sạch, mô hình hóa dữ liệu và lập index tìm kiếm vector bằng ChromaDB với mô hình `mistral-embed`.
* Thiết kế bộ câu hỏi kiểm thử 32 câu với 4 chiều phân tích khác nhau và tích hợp LLM Judge đánh giá tự động đa luồng (14 workers) kết hợp xoay tua Gemini 3.1 & 3.5.
* Giả lập 6 loại lỗi dữ liệu trong tập `Corrupted` làm sụt giảm Hit Rate của RAG từ 100% xuống 50%.
* Thiết lập hệ thống kiểm định chất lượng (Data Quality Checks) và độ tươi mới (Freshness Validation) giúp bắt chính xác 100% lỗi dữ liệu xấu (hiển thị trạng thái 🔴 FAILED).
* Xây dựng luồng khôi phục tự động (Repair Flow) từ dữ liệu raw thô, đưa chất lượng RAG và trạng thái hệ thống hồi phục hoàn toàn về 100% (🟢 PASSED).
* Điểm giới hạn hiện tại là việc ChromaDB chạy cục bộ gây giới hạn luồng ghi và API Rate limits của bên thứ ba.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API
    -> raw response/raw records (crossref_response.json)
    -> cleaning và data modeling (papers_clean.csv)
    -> embedding (mistral-embed) + ChromaDB index (papers-baseline)
    -> evaluation baseline (answers_baseline.json)
    -> quality/freshness reports (freshness_report.json)
    -> corruption (papers_clean_corrupted.csv)
    -> re-index và re-evaluate (answers_corrupted.json)
    -> repair từ dữ liệu nguồn raw (papers_clean_repaired.csv)
    -> comparison report (corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | Crossref REST API | Fetch, retry, parse, save raw | `data/raw/crossref_response.json` | Nguyễn Đàm Kiên |
| Cleaning          | `crossref_records.json` | Chuẩn hóa text, tính age_days | `data/clean/papers_clean.csv` | Lê Nguyễn Phước Thành |
| Embedding/index   | `papers_clean.csv` | Embeddings qua mistral-embed | `data/embeddings/papers_embeddings.json` | Nguyễn Văn Nam |
| Evaluation        | `papers_clean.csv` | Sinh 32 câu hỏi và LLM Judge | `data/eval/test_set.json` | Lê Kim Tính |
| Observability     | Clean/Corrupt DF | Run GE quality checks, freshness | `data/quality/freshness_report.json` | Trần Chí Hiển |
| Corruption/repair | Clean CSV & Raw | Injection & raw-based restoration | `data/clean/papers_clean_corrupted.csv` | Phước Thành / Văn Nam |
| Orchestration     | Toàn bộ modules | Kịch bản chạy Phase 1 & 2 | `data/reports/corruption_report.md` | Nguyễn Văn Nam |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | `gemini` |
| `LLM_MODEL`                | `gemini-3.1-flash-lite,gemini-3.5-flash-lite` |
| Embedding model              | `mistral-embed` |
| Số lượng Crossref records | `24` |
| Retrieval `top_k`           | `4` |
| Freshness threshold          | `180` (ngày) |
| Random seed, nếu có        | Không có |

### Lệnh cài đặt

```bash
uv sync
```

### Lệnh chạy

Baseline:
```bash
uv run python script/run_phase1.py
```

Corruption flow:
```bash
uv run python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | 2026-08-06 16:46:50 | `data/reports/phase1_report.md` |
| Corruption flow   | Thành công | 2026-08-06 16:47:50 | `data/reports/corruption_report.md` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref REST API `/works` |
| Query/filter                | `query=agentic retrieval augmented generation large language model` |
| Thời điểm lấy dữ liệu | 2026-08-06 16:47:00 |
| Số record nhận được    | `24` |
| Cơ chế retry/backoff      | Exponential backoff với random jitter (max 5 retries) |

### Raw và clean schema

| Trường        | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa   | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| `paper_id` | `str` | Có | ID duy nhất định danh bài viết | Bỏ qua bản ghi |
| `title` | `str` | Có | Tiêu đề bài báo học thuật | Bỏ qua nếu thiếu |
| `summary` | `str` | Có | Tóm tắt nội dung bài viết | Bỏ qua nếu thiếu |
| `publication_date` | `str` | Có | Ngày xuất bản dạng ISO-8601 | Gán ngày chạy thực tế |
| `age_days` | `int` | Có | Số ngày tính từ lúc xuất bản | Thiết lập = 0 |
| `text_for_embedding` | `str` | Có | Chuỗi gộp Title + Summary | Tự động tạo lại |

### Quy tắc cleaning

| Quy tắc                                 | Quality dimension liên quan | Số record bị tác động | Cách xác minh      |
| ---------------------------------------- | ---------------------------- | -------------------------: | -------------------- |
| Loại bỏ record không có title/summary | Completeness | 0 | `data/clean/papers_clean.json` |
| Đồng bộ định dạng ngày tháng xuất bản | Validity | 24 | `data/clean/papers_clean.csv` |

* **Cách tạo `text_for_embedding`**: Kết hợp trường Title và Summary theo dạng `"Title: {title}\nSummary: {summary}"`.
* **Cách tạo `paper_id`**: Chuyển đổi DOI thành dạng chữ thường, loại bỏ khoảng trắng và ký tự đặc biệt để làm ID duy nhất.
* **Cách tạo `age_days`**: Lấy thời gian thực thi (Run date) trừ đi ngày xuất bản của bài báo (`publication_date`).

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | `32` |
| Các `question_type`                    | `summary`, `authors`, `date`, `categories` |
| Ground-truth document ID                 | Ghép cặp ID bài báo gốc lúc sinh câu hỏi |
| Embedding model                          | `mistral-embed` |
| Vector store/collection                  | ChromaDB Persistent Client |
| Retrieval `top_k`                       | `4` |
| LLM provider/model                       | Gemini (xoay tua `gemini-3.1-flash-lite` và `gemini-3.5-flash-lite`) |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

* **Tại sao test set giữ nguyên**: Để làm hệ quy chiếu chung duy nhất. Chỉ khi dùng chung một bộ testset 32 câu hỏi cho cả 3 trạng thái Baseline, Corrupted, và Repaired thì chúng ta mới đo lường và so sánh được chính xác mức độ ảnh hưởng của lỗi dữ liệu và hiệu quả khôi phục.

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/` | Có | Đầy đủ |
| Cleaned dataset          | `data/clean/` | Có | Đầy đủ |
| Embedding manifest/index | `data/embeddings/` | Có | Đầy đủ |
| Evaluation set           | `data/eval/` | Có | Đầy đủ |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có | Đầy đủ |
| Quality/freshness        | `data/quality/` | Có | Đầy đủ |
| Baseline report          | `data/reports/phase1_report.md` | Có | Đầy đủ |

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` | `100.0%` | RAG tìm chính xác 100% tài liệu mục tiêu |
| `mean_token_f1`      | `0.8292` | Độ chính xác trùng khớp từ vựng cao |
| `judge_accuracy`     | `78.1%` | LLM Judge đánh giá câu trả lời đúng |
| `mean_judge_score`   | `4.31` | Điểm trung bình câu trả lời (thang điểm 5) |

## 8. Data quality và freshness

### Quality checks

| Check        | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      | Bằng chứng |
| ------------ | ----------------- | ------------------ | ----------------------- | ------------ |
| `paper_id_unique` | Uniqueness | Không trùng lặp | Pass (100% unique) | `data/quality/baseline_quality.json` |
| `summary_not_blank` | Completeness | Không trống summary | Pass (100% valid) | `data/quality/baseline_quality.json` |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | `data/clean/papers_clean.csv` |
| Timestamp mới nhất       | 2026-08-06 |
| Ngưỡng freshness         | `180` (ngày) |
| Trạng thái baseline      | `Fresh` |
| Lý do                     | Tuổi của tài liệu mới nhất là 0 ngày, nhỏ hơn ngưỡng 180 ngày. |

## 9. Corruption scenarios và repair

| Corruption | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair |
| --- | --- | ---: | --- | --- | --- |
| Drop records | Xóa bớt 4 bài mới nhất | 4 | Row count fail | Hit rate sụt giảm mạnh | Re-run ETL từ Raw |
| Blank summaries | Xóa nội dung summary | 3 | summary_not_blank fail | RAG thiếu ngữ cảnh | Re-run ETL từ Raw |
| Inject noise | Chèn ký tự rác vào text | 3 | Noise detected | LLM Judge score giảm | Re-run ETL từ Raw |
| Truncate titles | Cắt ngắn tiêu đề bài viết | 3 | Title length fail | Metadata lookup lỗi | Re-run ETL từ Raw |
| Stale dates | Sửa ngày xuất bản về 2014 | 4 | Freshness = Stale | Cảnh báo quá hạn | Re-run ETL từ Raw |
| Duplicate rows | Thêm các dòng trùng lặp | 3 | paper_id_unique fail | Dữ liệu trùng lặp | Re-run ETL từ Raw |

* **Đường dẫn Corruption log**: `data/results/corruption_log.json` (Trạng thái: Có)
* **Cơ chế Repair đảm bảo độ tin cậy**: Khi phát hiện lỗi dữ liệu, thay vì sửa đổi thủ công trên database vector, pipeline tiến hành xóa bỏ hoàn toàn dữ liệu bẩn và chạy lại quy trình làm sạch dữ liệu từ file raw lưu trữ gốc (`crossref_records.json`). Điều này đảm bảo tính nhất quán dữ liệu và loại bỏ triệt để mọi tác nhân gây nhiễu.

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét   |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate`   | `100.0%` | `50.0%` | `100.0%` | `-50.0%` | `+50.0%` | Sụt giảm mạnh và hồi phục 100% |
| `mean_token_f1`        | `0.8292` | `0.5142` | `0.8292` | `-0.3150` | `+0.3150` | Từ vựng trả về khôi phục hoàn toàn |
| `judge_accuracy`       | `78.1%` | `50.0%` | `81.2%` | `-28.1%` | `+31.2%` | Điểm Judge sau sửa vượt nhẹ baseline |
| `mean_judge_score`     | `4.31` | `3.00` | `4.41` | `-1.31` | `+1.41` | Điểm chất lượng hồi phục hoàn toàn |
| Quality checks pass/fail | `Pass` | `Fail` | `Pass` | Chuyển sang đỏ (Fail) | Trở lại xanh (Pass) | Observability hoạt động chuẩn xác |
| Freshness status         | `Fresh` | `Stale` | `Fresh` | Trở thành Stale | Quay lại trạng thái Fresh | Phát hiện nhạy bén dữ liệu cũ |

### Hai kết luận có quan hệ nhân quả:
1. **Dữ liệu Stale/Trùng lặp** → Gây cảnh báo đỏ trên hệ thống **Data Observability** → Làm giảm điểm trung bình **LLM Judge Score** xuống 3.00 và Hit rate xuống 50%.
2. **Chạy Repair từ nguồn Raw** → Khôi phục trạng thái chất lượng dữ liệu về **🟢 PASSED** → Phục hồi điểm số chất lượng RAG về mức **4.41** (tương đương baseline).

## 11. Vấn đề tích hợp quan trọng

* **Triệu chứng**: Gặp lỗi `chromadb.errors.NotFoundError` (Collection không tồn tại) khi chạy luồng đánh giá RAG sau khi rebuild index.
* **Nguyên nhân**: ChromaDB PersistentClient giữ các kết nối tĩnh đến collection cũ đã bị xóa trong khâu recreate.
* **Cách xử lý**: Khởi tạo lại một đối tượng `chromadb.PersistentClient` hoàn toàn mới ngay trong phương thức `search()` của `LocalEmbeddingIndex` để đảm bảo luôn lấy kết nối tươi.
* **Cách xác minh**: Chạy lại `script/run_corruption_flow.py`, toàn bộ pipeline chạy mượt mà không gặp lỗi ngắt quãng.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| ChromaDB chạy cục bộ (sqlite) | Không hỗ trợ mở rộng ghi đồng thời cao | Thay thế bằng Pgvector hoặc Pinecone |
| Rate Limit của API LLM | Gây lỗi HTTP 429 khi chạy nhiều luồng | Duy trì xoay tua API Key cùng cơ chế tự động thử lại |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
