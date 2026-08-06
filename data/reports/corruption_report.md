# Data Corruption, Repair, and Comparison Report

## 1. Executive Summary

This report evaluates the impact of intentional data corruptions on RAG retrieval accuracy and answer quality, and verifies the efficacy of automated data repair from raw source records.

---

## 2. Performance Comparison Across Pipelines

| Metric | Baseline | Corrupted | Repaired | Delta (Corrupted) | Delta (Repaired) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Retrieval Hit Rate** | `100.0%` | `50.0%` | `100.0%` | `-50.0%` | `+0.0%` |
| **Mean Token F1** | `0.8292` | `0.5142` | `0.8292` | `-0.3150` | `+0.0000` |
| **LLM Judge Accuracy** | `78.1%` | `50.0%` | `78.1%` | `-28.1%` | `+0.0%` |
| **Mean Judge Score** | `4.28` | `3.00` | `4.28` | `-1.28` | `+0.00` |

---

## 3. Data Observability & Quality Comparison

| State | Quality Status | Total Rows | Stale Rows | Freshness Status |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline** | 🟢 Passed All | `24` | `0` | Fresh |
| **Corrupted** | 🔴 Failed | `23` | `4` | Stale |
| **Repaired** | 🟢 Passed | `24` | `0` | Fresh |

---

## 4. Key Findings & Data Repair Audit

1. **Impact of Data Corruption**:
   - Dropping records directly degraded retrieval hit rate because the target documents were missing from vector search index.
   - Blanking summaries and injecting noise reduced semantic similarity search precision and impaired LLM answer generation.
   - Truncated titles and stale dates broken metadata queries and exact lookup logic.

2. **Automated Recovery Efficacy**:
   - Re-running the ETL cleaning pipeline directly from `data/raw/crossref_records.json` restored 100% of missing papers and cleaned noise.
   - Repaired metrics successfully returned to baseline levels (`100.0%` retrieval hit rate and `78.1%` judge accuracy).

---
*Report generated automatically by Observability Reporting Module.*
