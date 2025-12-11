"""
RAG Orchestrator Service - Handles RAG search and context formatting

Extracted from DraftService God Class (Phase 13 refactoring)
Manages Qdrant vector search operations for evidence and legal knowledge retrieval.
"""

from typing import List, Dict, Any

from app.utils.qdrant import (
    search_evidence_by_semantic,
    search_legal_knowledge
)


class RAGOrchestrator:
    """
    Orchestrates RAG (Retrieval-Augmented Generation) operations.

    Responsibilities:
    - Perform semantic search in Qdrant for case evidence
    - Search legal knowledge base for relevant statutes
    - Format search results as context for LLM prompts
    """

    def perform_rag_search(self, case_id: str, sections: List[str]) -> Dict[str, List[dict]]:
        """
        Perform semantic search in Qdrant for RAG context.

        Args:
            case_id: Case ID for evidence search
            sections: Sections being generated (e.g., ["청구원인", "청구취지"])

        Returns:
            Dict with 'evidence' and 'legal' search results
        """
        # Build search query based on sections
        if "청구원인" in sections:
            # Search for fault evidence (guilt factors)
            query = "이혼 사유 귀책사유 폭언 불화 부정행위"
            evidence_results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=10
            )
            # Search legal knowledge for divorce grounds
            legal_results = search_legal_knowledge(
                query="재판상 이혼 사유 민법 제840조",
                top_k=5,
                doc_type="statute"
            )
        else:
            # General search for all sections
            query = " ".join(sections)
            evidence_results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=5
            )
            legal_results = search_legal_knowledge(
                query="이혼 " + query,
                top_k=3
            )

        return {
            "evidence": evidence_results,
            "legal": legal_results
        }

    def build_qdrant_filter(self, case_id: str, labels: List[str] = None) -> Dict[str, Any]:
        """
        Build Qdrant filter for evidence search.

        Args:
            case_id: Case ID to filter by
            labels: Optional list of evidence labels to filter

        Returns:
            Qdrant filter dict
        """
        filter_conditions = [
            {"key": "case_id", "match": {"value": case_id}}
        ]

        if labels:
            filter_conditions.append({
                "key": "labels",
                "match": {"any": labels}
            })

        return {"must": filter_conditions}

    def format_evidence_context(self, evidence_results: List[dict]) -> str:
        """
        Format evidence search results for GPT-4o prompt.

        Args:
            evidence_results: List of evidence documents from RAG search

        Returns:
            Formatted evidence context string with citation numbers
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
        Format legal knowledge search results for GPT-4o prompt.

        Args:
            legal_results: List of legal documents from RAG search

        Returns:
            Formatted legal context string with statute references
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

    def format_rag_context(self, rag_results: List[dict]) -> str:
        """
        Format general RAG search results for GPT-4o prompt.

        Legacy method for backward compatibility.

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


# Singleton instance for convenience
_rag_orchestrator = None


def get_rag_orchestrator() -> RAGOrchestrator:
    """Get or create RAGOrchestrator singleton instance."""
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator()
    return _rag_orchestrator
