# Day 10 - Data Pipeline & Data Observability

## Bảng phân công công việc nhóm (5 Thành viên)

| STT | Thành viên | MSSV | Phân công nhiệm vụ chính | Mô-đun phụ trách trong mã nguồn |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **Nguyễn Đàm Kiên** | `2A202602015` | **Data Ingestion & Raw Extraction** | `src/ingestion/crossref.py` |
| **2** | **Lê Nguyễn Phước Thành** | `2A202601032` | **Data Cleaning & Preprocessing** | `src/ingestion/cleaning.py` |
| **3** | **Nguyễn Văn Nam** | `2A202601973` | **Vector Indexing & RAG Pipeline Orchestration** | `src/retrieval/`, `src/pipelines/` |
| **4** | **Lê Kim Tính** | `2A202601560` | **Evaluation Set & LLM Judge Scoring** | `src/evaluation/` |
| **5** | **Trần Chí Hiển** | `2A202601162` | **Data Observability, Quality & Reporting** | `src/observability/` |

---

## Mục tiêu bài lab

Bài lab mô phỏng quy trình xây dựng và vận hành data pipeline cho một hệ thống RAG sử dụng dữ liệu bài báo học thuật từ Crossref.

Học viên sẽ thực hiện toàn bộ vòng đời dữ liệu:

- Lấy dữ liệu từ nguồn bên ngoài và lưu lại raw artifacts để có thể truy vết.
- Làm sạch, chuẩn hóa và chuyển dữ liệu sang schema phù hợp cho embedding.
- Tạo embedding, nạp dữ liệu vào ChromaDB và dùng corpus này để trả lời câu hỏi.
- Xây evaluation set và đo chất lượng retrieval/câu trả lời trên dữ liệu sạch.
- Chủ động tạo các lỗi dữ liệu như thiếu bản ghi, summary rỗng, text nhiễu, ngày cũ và duplicate.
- Đo ảnh hưởng của dữ liệu lỗi lên chất lượng agent bằng cùng một evaluation set.
- Repair dữ liệu từ nguồn raw, chạy đánh giá lại và so sánh ba trạng thái: baseline, corrupted và repaired.
- Tạo data quality report, freshness report và báo cáo so sánh để phát hiện vấn đề trước khi người dùng nhận câu trả lời sai.

Trọng tâm của bài không chỉ là làm cho ETL chạy được. Học viên phải **chứng minh bằng artifact và metrics rằng chất lượng dữ liệu ảnh hưởng trực tiếp đến chất lượng của RAG/agent**, đồng thời cho thấy pipeline có thể phát hiện và phục hồi sau lỗi dữ liệu.

## Luồng thực hiện và đầu ra

Pipeline hoàn chỉnh đi theo luồng:

```text
Crossref API
    -> raw data
    -> cleaned data
    -> embedding + ChromaDB
    -> RAG evaluation
    -> quality/freshness reports
    -> corrupt data
    -> evaluate impact
    -> repair from raw data
    -> compare baseline/corrupted/repaired
```

Kết thúc bài lab, học viên cần có:

- Baseline pipeline chạy end-to-end trên dữ liệu sạch.
- Corruption flow tạo được dữ liệu lỗi có chủ đích.
- Repaired pipeline phục hồi dữ liệu và chạy đánh giá lại.
- Metrics và câu trả lời của agent ở cả ba trạng thái để đối chiếu.
- Data quality, freshness và comparison reports trong `data/`.

Xem yêu cầu chi tiết tại:

- [Hướng dẫn từng bước](Guide.md)
- [Rubric chấm điểm](Rubric.md)

## 1. Yêu cầu trước khi bắt đầu

- **Python 3.11, 3.12 hoặc 3.13** (theo `pyproject.toml` và `uv.lock`)
- Khuyến nghị dùng [uv](https://docs.astral.sh/uv/getting-started/installation/) để cài đúng dependency từ lockfile
- Internet để lấy dữ liệu từ Crossref và tải embedding model lần đầu
- API key của ít nhất một LLM provider nếu chạy các bước có gọi LLM

Nếu máy có nhiều phiên bản Python, hãy chọn Python trong khoảng 3.11-3.13 trước khi cài dependency.

## 2. Cài môi trường

### Cách A - Dùng uv (khuyến nghị)

Tại thư mục gốc của project:

```bash
uv sync
```

`uv sync` tạo môi trường `.venv`, cài project và dependency theo `uv.lock`.

### Cách B - Dùng pip

Tạo và kích hoạt virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

> Không chỉ chạy `pip install -r requirements.txt`: lệnh đó cài các thư viện nhưng không cài package nằm trong `src/`.  ` cài cả project và dependency cần thiết.

## 3. Cấu hình `.env`

Tạo `.env` từ file mẫu.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Mặc định project dùng Gemini:

```dotenv
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your_key_here
```

Project cũng hỗ trợ `openai`, `anthropic`, `openrouter`, `ollama` và OpenAI-compatible custom endpoint. Chỉ điền credential của provider bạn sử dụng.

Không commit `.env`, API key hoặc secret lên GitHub.

## 4. Hiểu starter trước khi code

Các thư mục chính:

| Thư mục              | Chức năng                                       |
| ---------------------- | ------------------------------------------------- |
| `src/core/`          | Cấu hình, đường dẫn và utility dùng chung |
| `src/ingestion/`     | Lấy dữ liệu Crossref, cleaning và corruption  |
| `src/retrieval/`     | Embedding, ChromaDB, LLM providers và agent      |
| `src/evaluation/`    | Tạo test set và tính metrics                   |
| `src/observability/` | Data quality, freshness và báo cáo             |
| `src/pipelines/`     | Điều phối baseline flow và corruption flow    |
| `script/`            | Hai entrypoint để chạy pipeline                |
| `data/`              | Artifact sinh ra khi chạy lab                    |

Starter cố ý chứa `TODO(student)` và `NotImplementedError`. Đây là trạng thái mong đợi, không phải lỗi setup.

Tìm tất cả phần cần hoàn thành:

```bash
rg -n "TODO\(student\)|NotImplementedError" src
```

Nếu chưa cài `rg`, dùng một trong các lệnh sau.

Windows PowerShell:

```powershell
Get-ChildItem src -Recurse -Filter *.py | Select-String -Pattern 'TODO\(student\)|NotImplementedError'
```

macOS/Linux:

```bash
grep -RInE 'TODO\(student\)|NotImplementedError' src
```

Hoặc dùng chức năng Search của VS Code với từ khóa `TODO(student)`.

## 5. Thứ tự thực hiện

### Pha 1 - Baseline với dữ liệu sạch

1. Implement Crossref ingestion trong `src/ingestion/crossref.py`.
2. Implement cleaning trong `src/ingestion/cleaning.py`.
3. Tạo evaluation set trong `src/evaluation/testset.py`.
4. Implement quality/freshness checks và report trong `src/observability/`.
5. Ghép các bước trong `src/pipelines/phase1.py`.
6. Chạy baseline:

```bash
uv run python script/run_phase1.py
```

Nếu dùng pip và đã kích hoạt `.venv`:

```bash
python script/run_phase1.py
```

### Pha 2 - Corruption, repair và comparison

Chỉ bắt đầu pha này sau khi baseline chạy thành công.

1. Implement corruption trong `src/ingestion/corruption.py`.
2. Ghép corruption, evaluation, repair và comparison trong `src/pipelines/corruption_flow.py`.
3. Chạy flow:

```bash
uv run python script/run_corruption_flow.py
```

Nếu dùng pip:

```bash
python script/run_corruption_flow.py
```

## 6. Kiểm tra kết quả

Sau baseline, tối thiểu cần kiểm tra:

- `data/raw/`: raw response và records từ Crossref
- `data/clean/`: cleaned CSV/JSON
- `data/embeddings/`: embedding manifest
- `data/eval/`: evaluation test set
- `data/results/baseline_metrics.json`: metrics của baseline
- `data/quality/`: data quality và freshness report
- `data/reports/phase1_report.md`: báo cáo baseline

Sau corruption flow, kiểm tra thêm:

- corrupted/repaired dataset và metrics trong `data/`
- `data/results/corruption_log.json`
- `data/reports/corruption_report.md`

Các chỉ số trọng tâm:

- `retrieval_hit_rate`
- `mean_token_f1`
- `judge_accuracy`
- `mean_judge_score`
- trạng thái data quality và freshness

Mục tiêu không chỉ là pipeline chạy xong, mà phải có bằng chứng cho thấy data corruption làm thay đổi chất lượng agent và repair giúp khôi phục chất lượng.

## 7. Lỗi setup thường gặp

| Triệu chứng                                         | Nguyên nhân thường gặp                          | Cách kiểm tra/xử lý                                                             |
| ----------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `requires a different Python`                       | Python nằm ngoài khoảng 3.11-3.13                 | Chạy`python --version`, chọn Python phù hợp rồi tạo lại `.venv`          |
| `No module named 'pipelines'`                       | Mới cài`requirements.txt`, chưa cài project    | Trong`.venv`, chạy `python -m pip install -e .`                                |
| `GOOGLE_API_KEY is required`                        | Provider mặc định là Gemini nhưng chưa có key | Điền`GOOGLE_API_KEY` hoặc đổi `LLM_PROVIDER` sang provider đã cấu hình |
| `NotImplementedError: Student task...`              | Chạm tới phần starter chưa implement             | Mở đúng file được ghi trong traceback và hoàn thành`TODO(student)`       |
| Crossref trả`429`/`503`                          | Rate limit hoặc lỗi tạm thời                     | Implement retry/backoff theo yêu cầu trong`src/ingestion/crossref.py`           |
| Chạy corruption flow nhưng thiếu baseline artifact | Chưa chạy xong Pha 1                               | Chạy baseline và kiểm tra`data/results/baseline_metrics.json` trước          |

## 8. Checklist trước khi nộp

- [ ] Cài đặt được trên môi trường sạch bằng một trong hai cách ở trên
- [ ] Baseline pipeline chạy end-to-end
- [ ] Corruption flow chạy sau baseline
- [ ] Có đầy đủ raw, clean, embedding, evaluation, quality và report artifacts
- [ ] Metrics/report khớp với artifact thực tế
- [ ] Chứng minh được before/corrupted/repaired bằng số liệu
- [ ] Không có API key hoặc `.env` trong Git
- [ ] Đã đối chiếu [Rubric.md](Rubric.md)
