from __future__ import annotations


from core.config import load_settings
from core.utils import now_utc, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex
from retrieval.qa import answer_question


def main() -> None:
    print("=== STARTING PHASE 1 BASELINE PIPELINE ===")
    settings = load_settings()
    
    print("1. Ingesting raw records from source...")
    raw_records = fetch_source_records(settings)
    print(f"   -> Fetched/loaded {len(raw_records)} raw records.")

    print("2. Cleaning records and modeling dataset...")
    df_clean = build_clean_dataframe(raw_records, run_date=now_utc())
    write_csv(df_clean, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, df_clean.to_dict(orient="records"))
    print(f"   -> Clean dataset built with {len(df_clean)} records.")

    print("3. Building vector embeddings and ChromaDB index...")
    index = LocalEmbeddingIndex.build(
        df=df_clean,
        settings=settings,
        embeddings_output_path=settings.paths.embeddings_json,
    )
    print(f"   -> Vector index built for collection '{index.collection_name}'.")

    print("4. Building evaluation test set...")
    test_set = build_test_set(df_clean, settings.paths.eval_testset)
    print(f"   -> Generated {len(test_set)} test set questions.")

    print("5. Evaluating RAG baseline pipeline...")
    bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )
    print(f"   -> Baseline Hit Rate: {bundle.summary['retrieval_hit_rate']*100:.1f}%, LLM Judge Score: {bundle.summary['mean_judge_score']:.2f}")

    print("6. Executing data quality and freshness checks...")
    quality_res = run_data_quality_checks(df_clean, settings, report_name="baseline")
    freshness_res = build_freshness_report(df_clean, settings, settings.paths.freshness_report)

    print("7. Generating Phase 1 Markdown report...")
    source_summary = {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "raw_records_count": len(raw_records),
        "clean_records_count": len(df_clean),
        "collection_name": index.collection_name,
    }
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=bundle.summary,
        quality=quality_res,
        freshness=freshness_res,
    )
    print(f"   -> Report generated at {settings.paths.baseline_report}")

    print("8. Running agent demo QA sample...")
    demo_questions = [
        f"What is the main finding of '{df_clean.iloc[0]['title']}'?",
        f"Who authored the paper '{df_clean.iloc[0]['title']}'?",
    ]
    demo_answers = []
    for q in demo_questions:
        res = answer_question(q, settings=settings, index=index)
        demo_answers.append(
            {
                "question": res.question,
                "answer": res.answer,
                "retrieved_titles": res.retrieved_titles,
            }
        )
    write_json(settings.paths.demo_answers, demo_answers)
    print(f"   -> Demo answers written to {settings.paths.demo_answers}")

    print("=== PHASE 1 BASELINE PIPELINE COMPLETED SUCCESSFULLY ===")

