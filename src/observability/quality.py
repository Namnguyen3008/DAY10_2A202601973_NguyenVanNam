from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import write_json



def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    total_rows = len(df)
    
    if total_rows == 0:
        result = {
            "report_name": report_name,
            "total_rows": 0,
            "passed_all": False,
            "checks": {
                "row_count": {"status": "FAIL", "detail": "DataFrame is empty (0 rows)."}
            },
        }
        output_file = settings.paths.quality_dir / f"{report_name}_quality.json"
        write_json(output_file, result)
        return result

    paper_id_nulls = int(df["paper_id"].isnull().sum()) if "paper_id" in df else total_rows
    paper_id_duplicates = int(df.duplicated(subset=["paper_id"]).sum()) if "paper_id" in df else 0
    title_nulls = int(df["title"].isnull().sum()) if "title" in df else total_rows
    
    summary_series = df["summary"].fillna("").astype(str) if "summary" in df else pd.Series([""] * total_rows)
    summary_blanks = int((summary_series.str.strip() == "").sum())
    summary_short = int((summary_series.str.len() < 20).sum())
    
    stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum()) if "age_days" in df else 0

    checks = {
        "non_empty_dataset": {
            "status": "PASS" if total_rows > 0 else "FAIL",
            "detail": f"Total rows = {total_rows}",
        },
        "paper_id_not_null": {
            "status": "PASS" if paper_id_nulls == 0 else "FAIL",
            "detail": f"Null paper_id count = {paper_id_nulls}",
        },
        "paper_id_unique": {
            "status": "PASS" if paper_id_duplicates == 0 else "FAIL",
            "detail": f"Duplicate paper_id count = {paper_id_duplicates}",
        },
        "title_not_null": {
            "status": "PASS" if title_nulls == 0 else "FAIL",
            "detail": f"Null title count = {title_nulls}",
        },
        "summary_not_blank": {
            "status": "PASS" if summary_blanks == 0 else "FAIL",
            "detail": f"Blank summary count = {summary_blanks}",
        },
        "summary_min_length": {
            "status": "PASS" if summary_short == 0 else "FAIL",
            "detail": f"Short summary count (<20 chars) = {summary_short}",
        },
        "freshness_threshold": {
            "status": "PASS" if stale_rows == 0 else "WARN",
            "detail": f"Stale rows (> {settings.freshness_threshold_days} days) = {stale_rows}",
        },
    }

    passed_all = all(c["status"] == "PASS" for c in checks.values())

    report = {
        "report_name": report_name,
        "total_rows": total_rows,
        "passed_all": passed_all,
        "checks": checks,
    }

    output_file = settings.paths.quality_dir / f"{report_name}_quality.json"
    write_json(output_file, report)
    return report


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    total_rows = len(df)
    if total_rows == 0:
        payload = {
            "latest_published": "N/A",
            "oldest_published": "N/A",
            "stale_rows": 0,
            "fresh_rows": 0,
            "total_rows": 0,
            "freshness_threshold_days": settings.freshness_threshold_days,
            "is_fresh": False,
        }
        write_json(Path(report_path), payload)
        return payload

    published_series = df["published"].dropna().astype(str) if "published" in df else pd.Series([])
    latest_published = published_series.max() if not published_series.empty else "N/A"
    oldest_published = published_series.min() if not published_series.empty else "N/A"

    stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum()) if "age_days" in df else 0
    fresh_rows = total_rows - stale_rows
    is_fresh = stale_rows == 0

    payload = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "fresh_rows": fresh_rows,
        "total_rows": total_rows,
        "freshness_threshold_days": settings.freshness_threshold_days,
        "is_fresh": is_fresh,
    }

    write_json(Path(report_path), payload)
    return payload

