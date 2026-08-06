from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import write_json



def build_test_set(df: pd.DataFrame, output_path: Path) -> list[dict[str, Any]]:
    """Generates an evaluation test set of 32 structured questions from a DataFrame of paper records."""
    if df.empty:
        raise ValueError("Cannot build test set from an empty DataFrame.")

    sample_size = min(len(df), 8)
    sampled_df = df.iloc[:sample_size]

    test_set: list[dict[str, Any]] = []
    item_id = 1

    for _, row in sampled_df.iterrows():
        title = row["title"]
        paper_id = row["paper_id"]
        doc_ids = [paper_id]

        # 1. Authors question
        if row.get("authors_joined"):
            test_set.append(
                {
                    "id": f"q_{item_id:03d}",
                    "question_type": "authors",
                    "question": f"Who authored the paper '{title}'?",
                    "ground_truth": str(row["authors_joined"]),
                    "ground_truth_doc_ids": doc_ids,
                }
            )
            item_id += 1

        # 2. Date question
        if row.get("published"):
            test_set.append(
                {
                    "id": f"q_{item_id:03d}",
                    "question_type": "date",
                    "question": f"When was the paper '{title}' published?",
                    "ground_truth": str(row["published"]),
                    "ground_truth_doc_ids": doc_ids,
                }
            )
            item_id += 1

        # 3. Categories question
        if row.get("categories_joined"):
            test_set.append(
                {
                    "id": f"q_{item_id:03d}",
                    "question_type": "categories",
                    "question": f"What categories are associated with the paper '{title}'?",
                    "ground_truth": str(row["categories_joined"]),
                    "ground_truth_doc_ids": doc_ids,
                }
            )
            item_id += 1

        # 4. Summary question
        if row.get("summary"):
            test_set.append(
                {
                    "id": f"q_{item_id:03d}",
                    "question_type": "summary",
                    "question": f"What is the main finding of the paper '{title}'?",
                    "ground_truth": str(row["summary"]),
                    "ground_truth_doc_ids": doc_ids,
                }
            )
            item_id += 1

    write_json(Path(output_path), test_set)
    return test_set

