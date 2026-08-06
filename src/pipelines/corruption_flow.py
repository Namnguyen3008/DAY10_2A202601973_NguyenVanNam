from __future__ import annotations


import pandas as pd

from core.config import load_settings
from core.utils import now_utc, read_json, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    print("=== STARTING CORRUPTION, EVALUATION, REPAIR & COMPARISON FLOW ===")
    settings = load_settings()

    print("1. Loading baseline clean dataset and baseline metrics...")
    if not settings.paths.clean_csv.exists() or not settings.paths.baseline_metrics.exists():
        raise RuntimeError("Baseline artifacts missing. Please run `script/run_phase1.py` first.")
    
    df_baseline = pd.read_csv(settings.paths.clean_csv)
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    print(f"   -> Loaded baseline dataset with {len(df_baseline)} records.")

    print("2. Simulating data corruption scenario...")
    df_corrupted = corrupt_clean_dataframe(df_baseline, settings.paths.corruption_log)
    write_csv(df_corrupted, settings.paths.corrupted_clean_csv)
    write_json(settings.paths.corrupted_clean_json, df_corrupted.to_dict(orient="records"))
    print(f"   -> Corrupted dataset created with {len(df_corrupted)} records.")

    print("3. Building vector embeddings and ChromaDB index for corrupted dataset...")
    index_corrupted = LocalEmbeddingIndex.build(
        df=df_corrupted,
        settings=settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json,
    )
    print(f"   -> Corrupted index built for collection '{index_corrupted.collection_name}'.")

    print("4. Evaluating corrupted RAG pipeline on original test set...")
    bundle_corrupted = evaluate_pipeline(
        settings=settings,
        index=index_corrupted,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )
    print(f"   -> Corrupted Hit Rate: {bundle_corrupted.summary['retrieval_hit_rate']*100:.1f}%, LLM Judge Score: {bundle_corrupted.summary['mean_judge_score']:.2f}")

    print("5. Executing data quality and freshness checks on corrupted dataset...")
    quality_corrupted = run_data_quality_checks(df_corrupted, settings, report_name="corrupted")
    freshness_corrupted = build_freshness_report(
        df_corrupted,
        settings,
        report_path=settings.paths.quality_dir / "corrupted_freshness_report.json",
    )

    print("6. Executing automated data repair from raw source records...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    df_repaired = build_clean_dataframe(raw_records, run_date=now_utc())
    write_csv(df_repaired, settings.paths.repaired_clean_csv)
    write_json(settings.paths.repaired_clean_json, df_repaired.to_dict(orient="records"))
    print(f"   -> Repaired dataset restored with {len(df_repaired)} records.")

    print("7. Building vector embeddings and ChromaDB index for repaired dataset...")
    index_repaired = LocalEmbeddingIndex.build(
        df=df_repaired,
        settings=settings,
        embeddings_output_path=settings.paths.repaired_embeddings_json,
    )
    print(f"   -> Repaired index built for collection '{index_repaired.collection_name}'.")

    print("8. Evaluating repaired RAG pipeline on original test set...")
    bundle_repaired = evaluate_pipeline(
        settings=settings,
        index=index_repaired,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )
    print(f"   -> Repaired Hit Rate: {bundle_repaired.summary['retrieval_hit_rate']*100:.1f}%, LLM Judge Score: {bundle_repaired.summary['mean_judge_score']:.2f}")

    print("9. Executing data quality and freshness checks on repaired dataset...")
    quality_repaired = run_data_quality_checks(df_repaired, settings, report_name="repaired")
    freshness_repaired = build_freshness_report(
        df_repaired,
        settings,
        report_path=settings.paths.quality_dir / "repaired_freshness_report.json",
    )

    print("10. Generating Markdown comparison report...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=bundle_corrupted.summary,
        repaired_metrics=bundle_repaired.summary,
        corrupted_quality=quality_corrupted,
        repaired_quality=quality_repaired,
        corrupted_freshness=freshness_corrupted,
        repaired_freshness=freshness_repaired,
    )
    print(f"   -> Comparison report generated at {settings.paths.comparison_report}")

    print("=== CORRUPTION & REPAIR FLOW COMPLETED SUCCESSFULLY ===")

