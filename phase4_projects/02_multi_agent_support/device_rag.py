"""Lightweight, dependency-free hybrid RAG for electronic-device support.

The implementation intentionally stays small enough for beginners to read:
BM25 handles exact model/error-code matches, character TF-IDF handles colloquial
Chinese descriptions, and metadata filtering prevents cross-model instructions.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True)
class Document:
    id: str
    product_type: str
    model: str
    doc_type: str
    section: str
    page: int
    risk_level: str
    content: str


@dataclass(frozen=True)
class SearchResult:
    document: Document
    score: float

    @property
    def citation(self) -> str:
        return f"《{self.document.model} {self.document.doc_type}》{self.document.section}（第{self.document.page}页）"


def _tokens(text: str) -> list[str]:
    """Tokenize Chinese with character bigrams while retaining model codes."""
    normalized = re.sub(r"\s+", "", text.lower())
    latin = re.findall(r"[a-z]+\d*|\d+", normalized)
    chinese = re.findall(r"[\u4e00-\u9fff]", normalized)
    bigrams = ["".join(chinese[i : i + 2]) for i in range(len(chinese) - 1)]
    return latin + chinese + bigrams


class DeviceKnowledgeBase:
    # Chinese characters count as ``\w`` in Python, so ASCII lookarounds are
    # used instead of ``\b`` (e.g. "WatchS更新" must still match WatchS).
    MODEL_PATTERN = re.compile(r"(?<![a-z0-9])(?:ear|watch|band)[- ]?(?:lite|pro|max|s|5|6)(?![a-z0-9])", re.I)

    def __init__(self, data_path: str | Path | None = None):
        path = Path(data_path) if data_path else Path(__file__).parent / "knowledge_base" / "devices.json"
        raw_documents = json.loads(path.read_text(encoding="utf-8"))
        self.documents = [Document(**item) for item in raw_documents]
        self.corpus = [_tokens(doc.content + doc.section + doc.model) for doc in self.documents]
        self.doc_frequency = Counter(token for tokens in map(set, self.corpus) for token in tokens)
        self.avg_length = sum(map(len, self.corpus)) / max(len(self.corpus), 1)

    @staticmethod
    def normalize_model(model: str) -> str:
        return re.sub(r"[- ]", "", model).lower()

    def detect_model(self, query: str) -> str | None:
        match = self.MODEL_PATTERN.search(query)
        return self.normalize_model(match.group()) if match else None

    def _bm25(self, query_tokens: list[str], index: int) -> float:
        terms = Counter(self.corpus[index])
        length = len(self.corpus[index])
        score = 0.0
        for token in query_tokens:
            df = self.doc_frequency.get(token, 0)
            if not df:
                continue
            idf = math.log(1 + (len(self.documents) - df + 0.5) / (df + 0.5))
            tf = terms[token]
            score += idf * tf * 2.2 / (tf + 1.2 * (1 - 0.75 + 0.75 * length / self.avg_length))
        return score

    def _tfidf_cosine(self, query_tokens: list[str], index: int) -> float:
        query_counts, doc_counts = Counter(query_tokens), Counter(self.corpus[index])
        vocabulary = set(query_counts) | set(doc_counts)
        query_vector, doc_vector = [], []
        for token in vocabulary:
            idf = math.log((len(self.documents) + 1) / (self.doc_frequency.get(token, 0) + 1)) + 1
            query_vector.append(query_counts[token] * idf)
            doc_vector.append(doc_counts[token] * idf)
        dot = sum(a * b for a, b in zip(query_vector, doc_vector))
        q_norm = math.sqrt(sum(value * value for value in query_vector))
        d_norm = math.sqrt(sum(value * value for value in doc_vector))
        return dot / (q_norm * d_norm) if q_norm and d_norm else 0.0

    @staticmethod
    def _normalize(scores: Iterable[float]) -> list[float]:
        values = list(scores)
        maximum = max(values, default=0.0)
        return [value / maximum if maximum else 0.0 for value in values]

    def search(self, query: str, model: str | None = None, top_k: int = 3) -> list[SearchResult]:
        query_tokens = _tokens(query)
        detected_model = self.normalize_model(model) if model else self.detect_model(query)
        candidate_indexes = [
            index for index, doc in enumerate(self.documents)
            if not detected_model or self.normalize_model(doc.model) == detected_model
        ]
        if not candidate_indexes:
            return []

        bm25 = self._normalize(self._bm25(query_tokens, index) for index in candidate_indexes)
        tfidf = self._normalize(self._tfidf_cosine(query_tokens, index) for index in candidate_indexes)
        ranked = sorted(
            (
                SearchResult(self.documents[index], round(0.6 * bm25[pos] + 0.4 * tfidf[pos], 4))
                for pos, index in enumerate(candidate_indexes)
            ),
            key=lambda result: result.score,
            reverse=True,
        )
        return [result for result in ranked[:top_k] if result.score >= 0.12]

    def answer(self, query: str, model: str | None = None) -> str:
        if not model and not self.detect_model(query):
            return "请先补充产品型号（例如 EarPro、EarLite、WatchPro、WatchS、Band5 或 Band6），以免引用其他型号的操作步骤。"
        results = self.search(query, model=model)
        if not results:
            return "[需要人工] 未检索到足够可靠的产品资料，请补充产品型号或联系人工客服。"

        high_risk = any(result.document.risk_level == "high" for result in results)
        lines = ["【知识库检索结果】"]
        for number, result in enumerate(results, 1):
            lines.append(f"{number}. {result.document.content}")
            lines.append(f"   依据：{result.citation}；相关度：{result.score:.2f}")
        if high_risk:
            lines.append("[需要人工] 涉及电池、进水或拆机风险，请停止使用设备并转人工售后，勿自行维修。")
        return "\n".join(lines)
