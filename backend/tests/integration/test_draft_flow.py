"""
Integration tests for Draft Generation Flow
009-mvp-gap-closure Feature - T027

Tests the full end-to-end flow:
1. Case creation
2. Evidence upload (mocked S3/DynamoDB)
3. RAG search (mocked Qdrant)
4. Draft preview generation (mocked OpenAI)
5. Response validation

Note: This test uses mocks for external services (AWS, OpenAI, Qdrant)
but tests the actual integration between backend components.
"""

import pytest
from unittest.mock import patch
from fastapi import status


class TestDraftGenerationFlow:
    """Integration tests for complete draft generation flow"""

    @pytest.fixture
    def case_with_evidence(self, test_env, test_user):
        """
        Create a test case with simulated evidence in DynamoDB

        This fixture creates:
        - A case owned by test_user
        - Mocked evidence records in DynamoDB
        """
        from app.db.session import get_db
        from app.db.models import Case, CaseMember
        from sqlalchemy.orm import Session
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        db: Session = next(get_db())

        try:
            # Create case
            case = Case(
                title=f"이혼 소송 사건 {unique_id}",
                description="통합 테스트용 케이스",
                status="active",
                created_by=test_user.id
            )
            db.add(case)
            db.commit()
            db.refresh(case)

            # Add owner as member
            member = CaseMember(
                case_id=case.id,
                user_id=test_user.id,
                role="owner"
            )
            db.add(member)
            db.commit()

            yield {
                "case": case,
                "evidence": [
                    {
                        "case_id": case.id,
                        "evidence_id": f"EV-{unique_id}-001",
                        "type": "text",
                        "status": "done",
                        "timestamp": "2024-01-15T14:30:00Z",
                        "speaker": "피고",
                        "labels": ["폭언", "정서적 학대"],
                        "content": "피고가 원고에게 '너는 쓸모없는 사람이야'라고 말함",
                        "ai_summary": "피고의 폭언 내용"
                    },
                    {
                        "case_id": case.id,
                        "evidence_id": f"EV-{unique_id}-002",
                        "type": "audio",
                        "status": "done",
                        "timestamp": "2024-02-20T19:00:00Z",
                        "speaker": "피고",
                        "labels": ["협박", "폭언"],
                        "content": "피고가 큰 소리로 협박성 발언을 함",
                        "ai_summary": "협박성 발언 녹음"
                    }
                ]
            }

            # Cleanup
            db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
            db.delete(case)
            db.commit()
        finally:
            db.close()

    def test_full_draft_generation_flow(
        self, client, auth_headers, case_with_evidence
    ):
        """
        Integration test: Full draft generation flow

        Flow:
        1. Create case (done in fixture)
        2. Evidence exists (mocked DynamoDB)
        3. RAG search finds relevant evidence (mocked Qdrant)
        4. GPT-4o generates draft with citations (mocked OpenAI)
        5. Response includes all required fields
        """
        case = case_with_evidence["case"]
        evidence = case_with_evidence["evidence"]

        with patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft_service.search_evidence_by_semantic') as mock_qdrant_evidence, \
             patch('app.services.draft_service.search_legal_knowledge') as mock_qdrant_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            # Setup DynamoDB mock - return evidence list
            mock_dynamo.return_value = evidence

            # Setup Qdrant evidence search mock
            mock_qdrant_evidence.return_value = [
                {
                    "id": evidence[0]["evidence_id"],
                    "evidence_id": evidence[0]["evidence_id"],
                    "content": evidence[0]["content"],
                    "labels": evidence[0]["labels"],
                    "speaker": evidence[0]["speaker"],
                    "timestamp": evidence[0]["timestamp"]
                },
                {
                    "id": evidence[1]["evidence_id"],
                    "evidence_id": evidence[1]["evidence_id"],
                    "content": evidence[1]["content"],
                    "labels": evidence[1]["labels"],
                    "speaker": evidence[1]["speaker"],
                    "timestamp": evidence[1]["timestamp"]
                }
            ]

            # Setup Qdrant legal search mock
            mock_qdrant_legal.return_value = [
                {
                    "article_number": "제840조",
                    "statute_name": "민법",
                    "document": "재판상 이혼 원인: 1. 배우자에 부정한 행위가 있었을 때..."
                }
            ]

            # Setup OpenAI mock - generate draft with inline citations
            mock_openai.return_value = """소    장

원고: [미확인]
피고: [미확인]

청 구 취 지

1. 원고와 피고는 이혼한다.
2. 피고는 원고에게 위자료 금 30,000,000원을 지급하라.

청 구 원 인

1. 당사자들의 관계
   원고와 피고는 [확인 필요] 혼인신고를 마친 법률상 부부입니다.

2. 이혼 사유
   피고는 2024년 1월 15일 원고에게 "너는 쓸모없는 사람이야"라고 폭언하였고 [갑 제1호증],
   2024년 2월 20일에는 큰 소리로 협박성 발언을 하였습니다 [갑 제2호증].

   이러한 피고의 행위는 민법 제840조 제6호의 "기타 혼인을 계속하기 어려운 중대한 사유"에
   해당하므로, 재판상 이혼을 청구합니다.

3. 위자료 청구
   피고의 계속된 폭언과 협박으로 원고는 심각한 정신적 고통을 받았으므로,
   위자료 금 30,000,000원의 지급을 구합니다.

입 증 방 법

1. 갑 제1호증 - 카카오톡 대화 기록
2. 갑 제2호증 - 음성 녹음 파일

※ 본 문서는 AI가 생성한 초안이며, 변호사의 검토 및 수정이 필수입니다.
"""
            mock_template.return_value = None

            # Make request
            response = client.post(
                f"/cases/{case.id}/draft-preview",
                json={
                    "sections": ["청구취지", "청구원인"],
                    "language": "ko",
                    "style": "법원 제출용_표준"
                },
                headers=auth_headers
            )

            # Verify response
            assert response.status_code == status.HTTP_200_OK

            data = response.json()

            # Verify structure
            assert data["case_id"] == case.id
            assert "draft_text" in data
            assert "citations" in data
            assert "generated_at" in data
            assert "preview_disclaimer" in data

            # Verify draft content includes inline citations
            assert "갑 제1호증" in data["draft_text"]
            assert "갑 제2호증" in data["draft_text"]

            # Verify citations list
            assert len(data["citations"]) == 2
            assert data["citations"][0]["evidence_id"] == evidence[0]["evidence_id"]

            # Verify disclaimer
            assert "미리보기" in data["preview_disclaimer"]

    def test_draft_flow_with_empty_evidence(
        self, client, auth_headers, test_case
    ):
        """
        Integration test: Draft generation fails gracefully with no evidence

        Expected: 400 Bad Request with helpful error message
        """
        with patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo:
            # No evidence
            mock_dynamo.return_value = []

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={"sections": ["청구원인"]},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            # Error response structure: {"error": {"message": "..."}}
            assert "증거" in data["error"]["message"]

    def test_draft_flow_preserves_citation_order(
        self, client, auth_headers, case_with_evidence
    ):
        """
        Integration test: Citations are returned in RAG relevance order
        """
        case = case_with_evidence["case"]
        evidence = case_with_evidence["evidence"]

        with patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft_service.search_evidence_by_semantic') as mock_qdrant_evidence, \
             patch('app.services.draft_service.search_legal_knowledge') as mock_qdrant_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            mock_dynamo.return_value = evidence
            # Return in specific order (most relevant first)
            mock_qdrant_evidence.return_value = [
                {"id": "ev2", "evidence_id": "EV-002", "content": "협박", "labels": ["협박"]},
                {"id": "ev1", "evidence_id": "EV-001", "content": "폭언", "labels": ["폭언"]},
            ]
            mock_qdrant_legal.return_value = []
            mock_openai.return_value = "테스트 초안"
            mock_template.return_value = None

            response = client.post(
                f"/cases/{case.id}/draft-preview",
                json={"sections": ["청구원인"]},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify citation order matches RAG order
            assert len(data["citations"]) == 2
            assert data["citations"][0]["evidence_id"] == "EV-002"
            assert data["citations"][1]["evidence_id"] == "EV-001"


class TestDraftExportFlow:
    """Integration tests for draft export flow"""

    def test_draft_export_requires_existing_draft(
        self, client, auth_headers, test_case
    ):
        """
        Integration test: Export requires a saved draft

        Flow:
        1. Try to export non-existent draft
        2. Should return 404
        """
        response = client.post(
            f"/cases/{test_case.id}/drafts/nonexistent-draft-id/export",
            params={"format": "docx"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDraftServiceIntegration:
    """Integration tests for DraftService internal flows"""

    def test_draft_service_extracts_citations_correctly(self, test_env):
        """
        Integration test: DraftService._extract_citations works correctly
        """
        from app.db.session import get_db
        from app.services.draft_service import DraftService
        from sqlalchemy.orm import Session

        db: Session = next(get_db())
        try:
            service = DraftService(db)

            # Test RAG results
            rag_results = [
                {
                    "id": "chunk_001",
                    "evidence_id": "EV-001",
                    "content": "피고가 원고에게 폭언을 하였습니다. 이것은 매우 긴 내용입니다." * 10,
                    "labels": ["폭언", "정서적 학대"]
                },
                {
                    "id": "chunk_002",
                    "evidence_id": "EV-002",
                    "content": "협박 내용",
                    "labels": ["협박"]
                }
            ]

            citations = service._extract_citations(rag_results)

            # Verify extraction
            assert len(citations) == 2

            # First citation
            assert citations[0].evidence_id == "EV-001"
            assert len(citations[0].snippet) <= 203  # 200 + "..."
            assert citations[0].labels == ["폭언", "정서적 학대"]

            # Second citation
            assert citations[1].evidence_id == "EV-002"
            assert citations[1].snippet == "협박 내용"
            assert citations[1].labels == ["협박"]

        finally:
            db.close()

    def test_draft_service_formats_evidence_context(self, test_env):
        """
        Integration test: DraftService._format_evidence_context works correctly
        """
        from app.db.session import get_db
        from app.services.draft_service import DraftService
        from sqlalchemy.orm import Session

        db: Session = next(get_db())
        try:
            service = DraftService(db)

            evidence_results = [
                {
                    "chunk_id": "ev1",
                    "document": "폭언 내용입니다",
                    "legal_categories": ["폭언"],
                    "sender": "피고",
                    "timestamp": "2024-01-15T14:30:00Z"
                }
            ]

            context = service._format_evidence_context(evidence_results)

            # Verify formatting
            assert "[갑 제1호증]" in context
            assert "ev1" in context  # ID included
            assert "폭언" in context
            assert "피고" in context
            assert "폭언 내용입니다" in context

        finally:
            db.close()

    def test_draft_service_formats_legal_context(self, test_env):
        """
        Integration test: DraftService._format_legal_context works correctly
        """
        from app.db.session import get_db
        from app.services.draft_service import DraftService
        from sqlalchemy.orm import Session

        db: Session = next(get_db())
        try:
            service = DraftService(db)

            legal_results = [
                {
                    "article_number": "제840조",
                    "statute_name": "민법",
                    "document": "재판상 이혼 원인..."
                }
            ]

            context = service._format_legal_context(legal_results)

            # Verify formatting
            assert "민법" in context
            assert "제840조" in context
            assert "재판상 이혼 원인" in context

        finally:
            db.close()

    def test_draft_service_empty_legal_context(self, test_env):
        """
        Integration test: Empty legal results are handled gracefully
        """
        from app.db.session import get_db
        from app.services.draft_service import DraftService
        from sqlalchemy.orm import Session

        db: Session = next(get_db())
        try:
            service = DraftService(db)
            context = service._format_legal_context([])

            assert "관련 법률 조문 없음" in context

        finally:
            db.close()
