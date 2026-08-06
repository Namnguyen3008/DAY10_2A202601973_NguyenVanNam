# Phase 1 Baseline Report - Data Pipeline & Observability

## 1. Executive Summary & Data Source

This report documents the baseline performance and data observability metrics for the Crossref Data Pipeline.

- **Data Source**: Crossref REST API
- **Query Filter**: `agentic retrieval augmented generation large language model`
- **Raw Records Ingested**: 24
- **Cleaned Records Processed**: 24
- **Vector Index Collection**: `papers-baseline`

---

## 2. Baseline RAG & Retrieval Performance

| Metric | Score | Target / Notes |
| :--- | :--- | :--- |
| **Retrieval Hit Rate** | `100.0%` | Ground truth document in top-k context |
| **Mean Token F1** | `0.8292` | Overlap between model answer and reference |
| **LLM Judge Accuracy** | `78.1%` | Material correctness score (>=3) |
| **Mean LLM Judge Score** | `4.28 / 5.0` | 1-5 scale evaluator score |

---

## 3. Data Quality Checks

Overall Quality Status: **🟢 PASSED ALL CHECKS**

| Check Name | Status | Details |
| :--- | :--- | :--- |
| `non_empty_dataset` | 🟢 PASS | Total rows = 24 |
| `paper_id_not_null` | 🟢 PASS | Null paper_id count = 0 |
| `paper_id_unique` | 🟢 PASS | Duplicate paper_id count = 0 |
| `title_not_null` | 🟢 PASS | Null title count = 0 |
| `summary_not_blank` | 🟢 PASS | Blank summary count = 0 |
| `summary_min_length` | 🟢 PASS | Short summary count (<20 chars) = 0 |
| `freshness_threshold` | 🟢 PASS | Stale rows (> 180 days) = 0 |

---

## 4. Data Freshness Monitoring

- **Status**: 🟢 Fresh
- **Latest Publication Date**: `2026-08-05`
- **Oldest Publication Date**: `2026-02-12`
- **Stale Records (> 180 days)**: `0 / 24`

---
*Report generated automatically by Observability Reporting Module.*
