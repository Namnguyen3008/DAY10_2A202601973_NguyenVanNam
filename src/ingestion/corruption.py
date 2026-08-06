from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.utils import compact_join, write_json



def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: Path) -> pd.DataFrame:
    corrupted_df = df.copy()
    initial_count = len(corrupted_df)
    log_entries: list[dict] = []

    # 1. Drop top 4 latest records
    if len(corrupted_df) > 4:
        dropped_records = corrupted_df.iloc[:4]["paper_id"].tolist()
        corrupted_df = corrupted_df.iloc[4:].reset_index(drop=True)
        log_entries.append(
            {
                "type": "drop_latest_records",
                "count": len(dropped_records),
                "affected_paper_ids": dropped_records,
                "description": "Dropped 4 most recent records from the dataset.",
            }
        )

    n = len(corrupted_df)

    # 2. Blank summary for 3 rows
    blank_summary_ids: list[str] = []
    if n >= 3:
        for idx in range(0, 3):
            paper_id = corrupted_df.at[idx, "paper_id"]
            corrupted_df.at[idx, "summary"] = ""
            corrupted_df.at[idx, "summary_chars"] = 0
            blank_summary_ids.append(paper_id)
        log_entries.append(
            {
                "type": "blank_summary",
                "count": len(blank_summary_ids),
                "affected_paper_ids": blank_summary_ids,
                "description": "Blanked summary string for 3 records.",
            }
        )

    # 3. Inject noise into summary for 3 rows
    noise_ids: list[str] = []
    if n >= 6:
        for idx in range(3, 6):
            paper_id = corrupted_df.at[idx, "paper_id"]
            noise_text = "NOISE ERROR GIBBERISH UNDEFINED CORRUPTED DATA NULL VOID UNRELATED SYMBOLS $$$ ### !!!"
            corrupted_df.at[idx, "summary"] = noise_text
            corrupted_df.at[idx, "summary_chars"] = len(noise_text)
            noise_ids.append(paper_id)
        log_entries.append(
            {
                "type": "inject_noise",
                "count": len(noise_ids),
                "affected_paper_ids": noise_ids,
                "description": "Injected text noise into summary for 3 records.",
            }
        )

    # 4. Truncate title for 3 rows
    truncate_ids: list[str] = []
    if n >= 9:
        for idx in range(6, 9):
            paper_id = corrupted_df.at[idx, "paper_id"]
            orig_title = str(corrupted_df.at[idx, "title"])
            truncated = orig_title[:8] if len(orig_title) > 8 else "Trunc..."
            corrupted_df.at[idx, "title"] = truncated
            truncate_ids.append(paper_id)
        log_entries.append(
            {
                "type": "truncate_title",
                "count": len(truncate_ids),
                "affected_paper_ids": truncate_ids,
                "description": "Truncated title to 8 characters for 3 records.",
            }
        )

    # 5. Make publication date stale (10 years old) for 4 rows
    stale_ids: list[str] = []
    if n >= 13:
        for idx in range(9, 13):
            paper_id = corrupted_df.at[idx, "paper_id"]
            corrupted_df.at[idx, "published"] = "2014-01-01"
            corrupted_df.at[idx, "age_days"] = 4500
            stale_ids.append(paper_id)
        log_entries.append(
            {
                "type": "stale_published_date",
                "count": len(stale_ids),
                "affected_paper_ids": stale_ids,
                "description": "Set published date to 2014-01-01 (4500 age_days) for 4 records.",
            }
        )

    # 6. Add duplicate rows (duplicate 3 existing rows)
    dup_ids: list[str] = []
    if len(corrupted_df) >= 3:
        dup_rows = corrupted_df.iloc[:3].copy()
        dup_ids = dup_rows["paper_id"].tolist()
        corrupted_df = pd.concat([corrupted_df, dup_rows], ignore_index=True)
        log_entries.append(
            {
                "type": "duplicate_rows",
                "count": len(dup_rows),
                "affected_paper_ids": dup_ids,
                "description": "Appended 3 duplicate rows into the dataset.",
            }
        )

    # 7. Rebuild text_for_embedding for all rows
    rebuilt_texts: list[str] = []
    for _, row in corrupted_df.iterrows():
        title = row.get("title", "")
        summary = row.get("summary", "")
        authors_joined = row.get("authors_joined", "")
        categories_joined = row.get("categories_joined", "")
        rebuilt_text = (
            f"Title: {title}\n"
            f"Authors: {authors_joined}\n"
            f"Categories: {categories_joined}\n"
            f"Summary: {summary}"
        )
        rebuilt_texts.append(rebuilt_text)
    corrupted_df["text_for_embedding"] = rebuilt_texts

    final_count = len(corrupted_df)

    log_payload = {
        "initial_record_count": initial_count,
        "final_record_count": final_count,
        "corruption_actions": log_entries,
    }

    write_json(Path(output_log_path), log_payload)

    return corrupted_df

