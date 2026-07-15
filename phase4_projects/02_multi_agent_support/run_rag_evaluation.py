"""Evaluate retrieval quality and model isolation without an API key."""

from device_rag import DeviceKnowledgeBase
from rag_eval_dataset import RAG_EVAL_DATASET


def main() -> None:
    knowledge_base = DeviceKnowledgeBase()
    hits_at_1 = hits_at_3 = reciprocal_rank = 0.0
    for case in RAG_EVAL_DATASET:
        results = knowledge_base.search(case["query"], top_k=3)
        ids = [result.document.id for result in results]
        if ids and ids[0] == case["expected_id"]:
            hits_at_1 += 1
        if case["expected_id"] in ids:
            hits_at_3 += 1
            reciprocal_rank += 1 / (ids.index(case["expected_id"]) + 1)
        print(f"{'PASS' if case['expected_id'] in ids else 'FAIL'} {case['query']} -> {ids}")

    total = len(RAG_EVAL_DATASET)
    print("\n=== Device RAG Evaluation ===")
    print(f"Recall@1: {hits_at_1 / total:.1%}")
    print(f"Recall@3: {hits_at_3 / total:.1%}")
    print(f"MRR:      {reciprocal_rank / total:.3f}")

    cross_model = knowledge_base.search("EarLite连接失败", model="EarLite", top_k=5)
    leakage = [result.document.model for result in cross_model if result.document.model != "EarLite"]
    print(f"Model leakage: {len(leakage)} (expected 0)")


if __name__ == "__main__":
    main()
