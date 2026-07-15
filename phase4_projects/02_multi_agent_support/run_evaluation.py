import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from main import CustomerServiceSystem, USE_MOCK, MockLLM
from eval_dataset import EVAL_DATASET

class Evaluator:
    def __init__(self):
        self.system = CustomerServiceSystem()
        self.mock = MockLLM()
        self.results = []

    def evaluate_full_flow(self, tc):
        result = self.system.handle_message(tc.query)
        response = result.get("response", "")
        intent = result.get("intent", "")
        escalated = result.get("escalated", False)
        matched_kw = [kw for kw in tc.expected_keywords if kw in response]
        keyword_coverage = len(matched_kw) / len(tc.expected_keywords) if tc.expected_keywords else 0
        return {
            "id": tc.id, "query": tc.query,
            "expected_intent": tc.expected_intent,
            "predicted_intent": intent,
            "intent_correct": intent == tc.expected_intent,
            "should_escalate": tc.should_escalate,
            "escalated": escalated,
            "escalation_correct": escalated == tc.should_escalate,
            "keyword_coverage": keyword_coverage,
            "response_length": len(response),
            "difficulty": tc.difficulty,
        }

    def run_full_evaluation(self):
        print("=" * 60)
        print("  多智能体客服系统 - 自动化评测报告")
        print("=" * 60)
        print("  评测数据集: {} 条测试用例".format(len(EVAL_DATASET)))

        self.results = [self.evaluate_full_flow(tc) for tc in EVAL_DATASET]

        total = len(self.results)
        intent_ok = sum(1 for r in self.results if r["intent_correct"])
        escalation_ok = sum(1 for r in self.results if r["escalation_correct"])
        avg_kw = sum(r["keyword_coverage"] for r in self.results) / total
        intent_acc = intent_ok / total * 100
        escalation_acc = escalation_ok / total * 100
        avg_kw_pct = avg_kw * 100

        print("\n" + "=" * 60)
        print("  [ Overall Metrics ]")
        print("=" * 60)
        print("  意图分类准确率 (Intent Accuracy):    {:.1f}%".format(intent_acc))
        print("  升级决策准确率 (Escalation Accuracy): {:.1f}%".format(escalation_acc))
        print("  回复关键词覆盖率 (Keyword Coverage):  {:.1f}%".format(avg_kw_pct))

        # By difficulty
        print("\n  [ By Difficulty ]")
        for diff, label in [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]:
            subset = [r for r in self.results if r["difficulty"] == diff]
            if not subset:
                continue
            si = sum(1 for r in subset if r["intent_correct"]) / len(subset) * 100
            sk = sum(r["keyword_coverage"] for r in subset) / len(subset) * 100
            se = sum(1 for r in subset if r["escalation_correct"]) / len(subset) * 100
            print("    {} ({} cases): Intent {:.0f}% | Esc {:.0f}% | KW {:.0f}%".format(label, len(subset), si, se, sk))

        # By scene
        print("\n  [ By Scene ]")
        scenes = {}
        for r in self.results:
            s = r["expected_intent"]
            if s not in scenes:
                scenes[s] = []
            scenes[s].append(r)
        scene_labels = {
            "tech_support": "Tech Support",
            "order_service": "Order Service",
            "product_consult": "Product Consult",
            "escalate": "Escalation"
        }
        for scene, items in scenes.items():
            si = sum(1 for r in items if r["intent_correct"]) / len(items) * 100
            sk = sum(r["keyword_coverage"] for r in items) / len(items) * 100
            label = scene_labels.get(scene, scene)
            print("    {} ({} cases): Intent {:.0f}% | KW {:.0f}%".format(label, len(items), si, sk))

        # Failure analysis
        failures = [r for r in self.results if not r["intent_correct"]]
        print("\n  [ Failure Analysis ]")
        print("    Intent misclassification: {}/{} cases".format(len(failures), total))
        for r in failures[:5]:
            print("    [{}] Expected: {} -> Predicted: {}  |  {}".format(
                r["id"], r["expected_intent"], r["predicted_intent"], r["query"][:25]))

        # Precision / Recall
        tp = sum(1 for r in self.results if r["should_escalate"] and r["escalated"])
        fp = sum(1 for r in self.results if not r["should_escalate"] and r["escalated"])
        fn = sum(1 for r in self.results if r["should_escalate"] and not r["escalated"])
        tn = sum(1 for r in self.results if not r["should_escalate"] and not r["escalated"])

        p = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
        r = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0

        print("\n  [ Escalation Quality ]")
        print("    Precision: {:.1f}%  Recall: {:.1f}%  F1: {:.1f}%".format(p, r, f1))
        print("    Confusion Matrix: TP={} FP={} FN={} TN={}".format(tp, fp, fn, tn))

        # Summary table
        print("\n" + "=" * 60)
        print("  [ Summary ]")
        print("=" * 60)
        print("""
  +---------------------------+----------+
  | Metric                    | Score    |
  +---------------------------+----------+
  | Intent Accuracy           | {:>5.1f}%   |
  | Escalation Accuracy       | {:>5.1f}%   |
  | Escalation Precision      | {:>5.1f}%   |
  | Escalation Recall         | {:>5.1f}%   |
  | F1 Score                  | {:>5.1f}%   |
  | Keyword Coverage          | {:>5.1f}%   |
  +---------------------------+----------+""".format(intent_acc, escalation_acc, p, r, f1, avg_kw_pct))

        # Optimization suggestions
        print("\n  [ Optimization Roadmap ]")
        print("  - Replace the small Mock rule set with real-LLM and adversarial evaluations")
        print("  - Persist multi-turn troubleshooting state with a SQLite/Redis checkpointer")
        print("  - Use run_rag_evaluation.py for retrieval metrics; keyword coverage is legacy")
        print("\n  {} test cases evaluated. Done.".format(total))

if __name__ == "__main__":
    ev = Evaluator()
    ev.run_full_evaluation()
