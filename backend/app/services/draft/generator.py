"""
Draft Generator Module
RAG 기반 초안 생성
"""

from sqlalchemy.orm import Session
from typing import List, Tuple
from datetime import datetime, timezone
from io import BytesIO

from app.db.schemas import (
    DraftPreviewRequest,
    DraftPreviewResponse,
    DraftExportFormat
)
from app.repositories.case_repository import CaseRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.utils.dynamo import get_evidence_by_case
from app.utils.qdrant import search_evidence_by_semantic
from app.utils.openai_client import generate_chat_completion
from app.middleware import NotFoundError, PermissionError, ValidationError

from .formatter import build_draft_prompt, extract_citations
from .exporter import generate_docx, generate_pdf


class DraftGenerator:
    """
    Draft generation with RAG
    """

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.member_repo = CaseMemberRepository(db)

    def generate_draft_preview(
        self,
        case_id: str,
        request: DraftPreviewRequest,
        user_id: str
    ) -> DraftPreviewResponse:
        """
        Generate draft preview using RAG + GPT-4o

        Process:
        1. Validate case access
        2. Retrieve evidence metadata from DynamoDB
        3. Perform semantic search in Qdrant (RAG)
        4. Build GPT-4o prompt with RAG context
        5. Generate draft text
        6. Extract citations

        Args:
            case_id: Case ID
            request: Draft generation request (sections, language, style)
            user_id: User ID requesting draft

        Returns:
            Draft preview with citations

        Raises:
            NotFoundError: Case not found
            PermissionError: User does not have access to case
            ValidationError: No evidence in case
        """
        # 1. Validate case access
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # 2. Retrieve evidence metadata from DynamoDB
        evidence_list = get_evidence_by_case(case_id)

        # Check if there's any evidence
        if not evidence_list:
            raise ValidationError("사건에 증거가 하나도 없습니다. 증거를 업로드한 후 초안을 생성해 주세요.")

        # Filter for completed evidence only (status="done")
        completed_evidence = [ev for ev in evidence_list if ev.get("status") == "done"]
        if not completed_evidence:
            logger.warning(f"No completed evidence found for case {case_id}")

        # 3. Perform semantic RAG search in Qdrant
        rag_results = self._perform_rag_search(case_id, request.sections)

        # 4. Build GPT-4o prompt with RAG context
        prompt_messages = build_draft_prompt(
            case=case,
            sections=request.sections,
            rag_context=rag_results,
            language=request.language,
            style=request.style
        )

        # 5. Generate draft text using GPT-4o
        draft_text = generate_chat_completion(
            messages=prompt_messages,
            temperature=0.3,
            max_tokens=4000
        )

        # 6. Extract citations from RAG results
        citations = extract_citations(rag_results)

        return DraftPreviewResponse(
            case_id=case_id,
            draft_text=draft_text,
            citations=citations,
            generated_at=datetime.now(timezone.utc)
        )

    def _perform_rag_search(self, case_id: str, sections: List[str]) -> List[dict]:
        """
        Perform semantic search in Qdrant for RAG context

        Args:
            case_id: Case ID
            sections: Sections being generated

        Returns:
            List of relevant evidence documents
        """
        if "청구원인" in sections:
            query = "이혼 사유 귀책사유 폭언 불화 부정행위"
            results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=10
            )
        else:
            query = " ".join(sections)
            results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=5
            )

        return results

    def export_draft(
        self,
        case_id: str,
        user_id: str,
        export_format: DraftExportFormat = DraftExportFormat.DOCX
    ) -> Tuple[BytesIO, str, str]:
        """
        Export draft as DOCX or PDF file

        Process:
        1. Validate case access
        2. Generate draft preview using RAG + GPT-4o
        3. Convert to requested format (DOCX or PDF)

        Args:
            case_id: Case ID
            user_id: User ID requesting export
            export_format: Output format (docx or pdf)

        Returns:
            Tuple of (file_bytes, filename, content_type)

        Raises:
            NotFoundError: Case not found
            PermissionError: User does not have access to case
            ValidationError: Export format not supported
        """
        # 1. Validate case access
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # 2. Generate draft preview
        request = DraftPreviewRequest()
        draft_response = self.generate_draft_preview(case_id, request, user_id)

        # 3. Convert to requested format
        if export_format == DraftExportFormat.DOCX:
            return generate_docx(case, draft_response)
        elif export_format == DraftExportFormat.PDF:
            return generate_pdf(case, draft_response)
        else:
            raise ValidationError(f"Unsupported export format: {export_format}")
