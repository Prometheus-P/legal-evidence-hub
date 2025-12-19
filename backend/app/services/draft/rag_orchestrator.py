"""
RAG Orchestrator - Handles RAG search and context formatting for draft generation
Extracted from DraftService for better modularity (Issue #325)
"""

from typing import List
import logging

# Import functions via utils module for direct usage
# Note: Tests can patch at 'app.services.draft.rag_orchestrator.search_evidence_by_semantic'
from app.utils.qdrant import (
    search_evidence_by_semantic,
    search_legal_knowledge,
)
from app.services.precedent_service import PrecedentService

logger = logging.getLogger(__name__)

# Re-export for patching at this module level
__all__ = [
    'RAGOrchestrator',
    'search_evidence_by_semantic',
    'search_legal_knowledge',
]


class RAGOrchestrator:
    """
    Orchestrates RAG (Retrieval Augmented Generation) search operations
    for draft generation.
    """

    def __init__(self, precedent_service: PrecedentService = None):
        """
        Initialize RAG orchestrator

        Args:
            precedent_service: Optional PrecedentService for precedent search
        """
        self.precedent_service = precedent_service

    def perform_rag_search(self, case_id: str, sections: List[str]) -> dict:
        """
        Perform semantic search in Qdrant for RAG context

        Args:
            case_id: Case ID
            sections: Sections being generated

        Returns:
            Dict with 'evidence' and 'legal' results
        """
        # Build search query based on sections
        if "청구원인" in sections:
            # Search for fault evidence (guilt factors)
            query = "이혼 사유 귀책사유 폭언 불화 부정행위"
            evidence_results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=5  # Reduced for faster response (30s API Gateway limit)
            )
            # Search legal knowledge for divorce grounds (no doc_type filter to avoid index error)
            legal_results = search_legal_knowledge(
                query="재판상 이혼 사유 민법 제840조",
                top_k=3
            )
        else:
            # General search for all sections
            query = " ".join(sections)
            evidence_results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=3  # Reduced for faster response
            )
            legal_results = search_legal_knowledge(
                query="이혼 " + query,
                top_k=2
            )

        return {
            "evidence": evidence_results,
            "legal": legal_results
        }

    def search_precedents(self, case_id: str, limit: int = 5, min_score: float = 0.5) -> List[dict]:
        """
        Search similar precedents for draft generation

        Args:
            case_id: Case ID
            limit: Maximum number of precedents to return
            min_score: Minimum similarity score

        Returns:
            List of precedent dictionaries
        """
        if not self.precedent_service:
            return []

        try:
            result = self.precedent_service.search_similar_precedents(
                case_id=case_id,
                limit=limit,
                min_score=min_score
            )
            # Convert PrecedentCase objects to dicts for prompt building
            return [
                {
                    "case_ref": p.case_ref,
                    "court": p.court,
                    "decision_date": p.decision_date,
                    "summary": p.summary,
                    "key_factors": p.key_factors,
                    "similarity_score": p.similarity_score,
                    "division_ratio": {
                        "plaintiff": p.division_ratio.plaintiff,
                        "defendant": p.division_ratio.defendant
                    } if p.division_ratio else None
                }
                for p in result.precedents
            ]
        except Exception as e:
            logger.warning(f"Precedent search failed for case {case_id}: {e}")
            return []

    def format_evidence_context(self, evidence_results: List[dict]) -> str:
        """
        Format evidence search results for GPT-4o prompt

        Args:
            evidence_results: List of evidence documents from RAG search

        Returns:
            Formatted evidence context string
        """
        if not evidence_results:
            return "(증거 자료 없음 - 기본 템플릿으로 작성)"

        context_parts = []
        for i, doc in enumerate(evidence_results, start=1):
            # AI Worker 필드명과 매핑 (chunk_id, document, legal_categories, sender)
            evidence_id = doc.get("chunk_id") or doc.get("id", f"evidence_{i}")
            content = doc.get("document") or doc.get("content", "")
            labels = doc.get("legal_categories") or doc.get("labels", [])
            speaker = doc.get("sender") or doc.get("speaker", "")
            timestamp = doc.get("timestamp", "")

            # Truncate content if too long
            if len(content) > 500:
                content = content[:500] + "..."

            context_parts.append(f"""
[갑 제{i}호증] (ID: {evidence_id})
- 분류: {", ".join(labels) if labels else "N/A"}
- 화자: {speaker or "N/A"}
- 시점: {timestamp or "N/A"}
- 내용: {content}
""")

        return "\n".join(context_parts)

    def format_legal_context(self, legal_results: List[dict]) -> str:
        """
        Format legal knowledge search results for GPT-4o prompt

        Args:
            legal_results: List of legal documents from RAG search

        Returns:
            Formatted legal context string
        """
        if not legal_results:
            return "(관련 법률 조문 없음)"

        context_parts = []
        for doc in legal_results:
            article_number = doc.get("article_number", "")
            statute_name = doc.get("statute_name", "민법")
            # Qdrant payload uses "document" field, not "text"
            content = doc.get("document", "") or doc.get("text", "")

            if article_number and content:
                context_parts.append(f"""
【{statute_name} {article_number}】
{content}
""")

        return "\n".join(context_parts) if context_parts else "(관련 법률 조문 없음)"

    def format_precedent_context(self, precedent_results: List[dict]) -> str:
        """
        Format precedent results for GPT-4o prompt

        Args:
            precedent_results: List of precedent dictionaries

        Returns:
            Formatted precedent context string
        """
        if not precedent_results:
            return "(관련 판례 없음)"

        context_parts = []
        for i, p in enumerate(precedent_results, 1):
            case_ref = p.get("case_ref", "")
            court = p.get("court", "")
            decision_date = p.get("decision_date", "")
            summary = p.get("summary", "")
            key_factors = p.get("key_factors", [])
            similarity = p.get("similarity_score", 0.0)

            # Format division ratio if exists
            division_str = ""
            if p.get("division_ratio"):
                dr = p["division_ratio"]
                division_str = f"\n   - 재산분할: 원고 {dr.get('plaintiff', 50)}% / 피고 {dr.get('defendant', 50)}%"

            # Truncate summary safely
            summary_truncated = summary[:200] + "..." if len(summary) > 200 else summary
            factors_str = ', '.join(key_factors) if key_factors else 'N/A'

            context_parts.append(
                f"【판례 {i}】 {case_ref} ({court}, {decision_date}) [유사도: {similarity:.0%}]\n"
                f"   - 요지: {summary_truncated}\n"
                f"   - 주요 요인: {factors_str}{division_str}"
            )

        return "\n\n".join(context_parts)

    def format_rag_context(self, rag_results: List[dict]) -> str:
        """
        Format RAG search results for GPT-4o prompt (legacy format)

        Args:
            rag_results: List of evidence documents from RAG search

        Returns:
            Formatted context string
        """
        if not rag_results:
            return "(증거 자료 없음 - 기본 템플릿으로 작성)"

        context_parts = []
        for i, doc in enumerate(rag_results, start=1):
            evidence_id = doc.get("id", f"evidence_{i}")
            content = doc.get("content", "")
            labels = doc.get("labels", [])
            speaker = doc.get("speaker", "")
            timestamp = doc.get("timestamp", "")

            # Truncate content if too long
            if len(content) > 500:
                content = content[:500] + "..."

            context_parts.append(f"""
[증거 {i}] (ID: {evidence_id})
- 분류: {", ".join(labels) if labels else "N/A"}
- 화자: {speaker or "N/A"}
- 시점: {timestamp or "N/A"}
- 내용: {content}
""")

        return "\n".join(context_parts)
