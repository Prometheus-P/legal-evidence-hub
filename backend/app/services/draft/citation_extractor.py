"""
Citation Extractor - Extracts and formats citations for draft documents
Extracted from DraftService for better modularity (Issue #325)
"""

from typing import List
from urllib.parse import quote

from app.db.schemas import DraftCitation, PrecedentCitation


class CitationExtractor:
    """
    Extracts and formats citations from RAG results and precedents.
    """

    def extract_evidence_citations(self, rag_results: List[dict]) -> List[DraftCitation]:
        """
        Extract citations from RAG results

        Args:
            rag_results: List of evidence documents from RAG search

        Returns:
            List of DraftCitation objects
        """
        citations = []

        for i, doc in enumerate(rag_results):
            # AI Worker 필드명 호환: chunk_id, evidence_id, id 순으로 시도
            evidence_id = (
                doc.get("chunk_id") or
                doc.get("evidence_id") or
                doc.get("id") or
                f"evidence_{i+1}"
            )
            # AI Worker 필드명 호환: document, content 순으로 시도
            content = doc.get("document") or doc.get("content", "")
            # AI Worker 필드명 호환: legal_categories, labels 순으로 시도
            labels = doc.get("legal_categories") or doc.get("labels") or []

            # Create snippet (first 200 chars)
            snippet = content[:200] + "..." if len(content) > 200 else content

            citations.append(
                DraftCitation(
                    evidence_id=evidence_id,
                    snippet=snippet,
                    labels=labels
                )
            )

        return citations

    def extract_precedent_citations(self, precedent_results: List[dict]) -> List[PrecedentCitation]:
        """
        Convert precedent results to PrecedentCitation objects

        Args:
            precedent_results: List of precedent dictionaries

        Returns:
            List of PrecedentCitation objects
        """
        citations = []
        for p in precedent_results:
            # Generate source_url using 법령한글주소 format
            case_ref = p.get("case_ref", "")
            decision_date = p.get("decision_date", "")
            source_url = None

            if case_ref and decision_date:
                # Convert ISO date to YYYYMMDD
                date_val = decision_date.replace("-", "")
                params = f"{case_ref},{date_val}"
                encoded_params = quote(params, safe="")
                source_url = f"https://www.law.go.kr/판례/({encoded_params})"

            citations.append(
                PrecedentCitation(
                    case_ref=case_ref,
                    court=p.get("court", ""),
                    decision_date=decision_date,
                    summary=p.get("summary", "")[:300],  # Truncate for citation
                    key_factors=p.get("key_factors", []),
                    similarity_score=p.get("similarity_score", 0.0),
                    source_url=source_url
                )
            )
        return citations

    def format_citations_for_document(
        self,
        evidence_citations: List[DraftCitation],
        precedent_citations: List[PrecedentCitation] = None
    ) -> dict:
        """
        Format citations for document content structure

        Args:
            evidence_citations: List of evidence citations
            precedent_citations: List of precedent citations

        Returns:
            Dict with formatted citation arrays
        """
        result = {
            "evidence": [
                {
                    "evidence_id": c.evidence_id,
                    "snippet": c.snippet,
                    "labels": c.labels
                }
                for c in evidence_citations
            ]
        }

        if precedent_citations:
            result["precedents"] = [
                {
                    "case_ref": c.case_ref,
                    "court": c.court,
                    "decision_date": c.decision_date,
                    "summary": c.summary,
                    "source_url": c.source_url
                }
                for c in precedent_citations
            ]

        return result
