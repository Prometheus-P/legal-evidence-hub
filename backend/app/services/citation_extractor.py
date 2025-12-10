"""
Citation Extractor Service - Extracts and formats citations from RAG results

Extracted from DraftService God Class (Phase 13 refactoring)
Handles citation parsing and DraftCitation object creation.
"""

from typing import List
import re

from app.db.schemas import DraftCitation


class CitationExtractor:
    """
    Extracts citations from RAG search results.

    Responsibilities:
    - Parse evidence RAG results into citation objects
    - Format citation snippets with appropriate truncation
    - Extract evidence labels and metadata
    """

    def extract_citations(self, rag_results: List[dict]) -> List[DraftCitation]:
        """
        Extract citations from RAG results.

        Args:
            rag_results: List of evidence documents from RAG search

        Returns:
            List of DraftCitation objects with evidence references
        """
        citations = []

        for doc in rag_results:
            evidence_id = doc.get("evidence_id") or doc.get("id")
            content = doc.get("content", "")
            labels = doc.get("labels", [])

            # Create snippet (first 200 chars)
            snippet = self._create_snippet(content)

            citations.append(
                DraftCitation(
                    evidence_id=evidence_id,
                    snippet=snippet,
                    labels=labels
                )
            )

        return citations

    def _create_snippet(self, content: str, max_length: int = 200) -> str:
        """
        Create a truncated snippet from content.

        Args:
            content: Full content string
            max_length: Maximum snippet length

        Returns:
            Truncated snippet with ellipsis if needed
        """
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    def parse_citation_refs(self, text: str) -> List[str]:
        """
        Parse citation references from generated draft text.

        Extracts references in Korean legal format:
        - [갑 제N호증]
        - [을 제N호증]

        Args:
            text: Generated draft text

        Returns:
            List of citation reference strings
        """
        # Match Korean legal citation format
        pattern = r'\[(?:갑|을)\s*제\d+호증(?:의\d+)?\]'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Remove duplicates

    def map_citations_to_evidence(
        self,
        citation_refs: List[str],
        rag_results: List[dict]
    ) -> dict:
        """
        Map citation references to actual evidence documents.

        Args:
            citation_refs: List of citation reference strings (e.g., "[갑 제1호증]")
            rag_results: List of evidence documents from RAG search

        Returns:
            Dict mapping citation refs to evidence IDs
        """
        mapping = {}

        for i, doc in enumerate(rag_results, start=1):
            evidence_id = doc.get("evidence_id") or doc.get("id")
            ref = f"[갑 제{i}호증]"
            mapping[ref] = evidence_id

        return mapping


# Singleton instance for convenience
_citation_extractor = None


def get_citation_extractor() -> CitationExtractor:
    """Get or create CitationExtractor singleton instance."""
    global _citation_extractor
    if _citation_extractor is None:
        _citation_extractor = CitationExtractor()
    return _citation_extractor
