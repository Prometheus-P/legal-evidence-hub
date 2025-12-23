"""
Contract tests for Draft Preview API
009-mvp-gap-closure Feature - T020

Tests for POST /cases/{case_id}/draft-preview endpoint:
- Authentication requirements
- Permission validation
- Request/Response structure
- Error handling
"""

from fastapi import status
from unittest.mock import patch


class TestDraftPreviewAuth:
    """Contract tests for draft-preview authentication"""

    def test_draft_preview_requires_auth(self, client, test_case):
        """
        Given: No authentication
        When: POST /cases/{id}/draft-preview is called
        Then:
            - Returns 401 Unauthorized
        """
        response = client.post(
            f"/cases/{test_case.id}/draft-preview",
            json={"sections": ["청구취지", "청구원인"]}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_draft_preview_rejects_invalid_token(self, client, test_case):
        """
        Given: Invalid JWT token
        When: POST /cases/{id}/draft-preview is called
        Then:
            - Returns 401 Unauthorized
        """
        response = client.post(
            f"/cases/{test_case.id}/draft-preview",
            json={"sections": ["청구취지"]},
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDraftPreviewPermissions:
    """Contract tests for draft-preview permissions"""

    def test_draft_preview_requires_case_membership(
        self, client, auth_headers, test_env
    ):
        """
        Given: Authenticated user who is NOT a case member
        When: POST /cases/{id}/draft-preview is called for unrelated case
        Then:
            - Returns 403 Forbidden
        """
        # Create a case without adding the test user as member
        from app.db.session import get_db
        from app.db.models import Case, User, CaseMember
        from app.core.security import hash_password
        import uuid

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Create another user to own the case
        other_user = User(
            email=f"other_user_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Other User",
            role="lawyer"
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        # Create case owned by other user
        case = Case(
            title=f"Draft Test Case {unique_id}",
            created_by=other_user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Add owner as member
        member = CaseMember(
            case_id=case.id,
            user_id=other_user.id,
            role="owner"
        )
        db.add(member)
        db.commit()

        try:
            # When: test_user (via auth_headers) tries to access
            response = client.post(
                f"/cases/{case.id}/draft-preview",
                json={"sections": ["청구취지"]},
                headers=auth_headers
            )

            # Then: Should be forbidden
            assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            # Cleanup
            db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
            db.delete(case)
            db.delete(other_user)
            db.commit()
            db.close()

    def test_draft_preview_case_member_can_access(
        self, client, auth_headers, test_case
    ):
        """
        Given: Authenticated user who IS a case member
        When: POST /cases/{id}/draft-preview is called
        Then:
            - Returns 200 OK or 422 (validation error due to no evidence)
        """
        # test_case fixture includes test_user as owner

        # Mock the external services (Qdrant, OpenAI, DynamoDB)
        with patch('app.services.draft_service.get_case_fact_summary') as mock_fact_summary, \
             patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic') as mock_qdrant, \
             patch('app.services.draft.rag_orchestrator.search_legal_knowledge') as mock_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            # Setup mocks
            mock_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}
            mock_dynamo.return_value = [
                {"evidence_id": "ev1", "status": "done", "content": "test"}
            ]
            mock_qdrant.return_value = [
                {"id": "ev1", "content": "Test evidence", "labels": ["폭언"]}
            ]
            mock_legal.return_value = []
            mock_openai.return_value = "테스트 초안 본문"
            mock_template.return_value = None

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={"sections": ["청구취지", "청구원인"]},
                headers=auth_headers
            )

            # Should succeed with mocked services
            assert response.status_code == status.HTTP_200_OK


class TestDraftPreviewRequest:
    """Contract tests for draft-preview request validation"""

    def test_draft_preview_accepts_default_sections(
        self, client, auth_headers, test_case
    ):
        """
        Given: Authenticated case member
        When: POST /cases/{id}/draft-preview is called without sections
        Then:
            - Request is accepted (uses default sections)
        """
        with patch('app.services.draft_service.get_case_fact_summary') as mock_fact_summary, \
             patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic') as mock_qdrant, \
             patch('app.services.draft.rag_orchestrator.search_legal_knowledge') as mock_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            mock_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}
            mock_dynamo.return_value = [{"evidence_id": "ev1", "status": "done"}]
            mock_qdrant.return_value = []
            mock_legal.return_value = []
            mock_openai.return_value = "테스트 초안"
            mock_template.return_value = None

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={},  # No sections - use defaults
                headers=auth_headers
            )

            # Should succeed with defaults
            assert response.status_code == status.HTTP_200_OK

    def test_draft_preview_accepts_custom_language(
        self, client, auth_headers, test_case
    ):
        """
        Given: Authenticated case member
        When: POST /cases/{id}/draft-preview with custom language
        Then:
            - Request is accepted
        """
        with patch('app.services.draft_service.get_case_fact_summary') as mock_fact_summary, \
             patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic') as mock_qdrant, \
             patch('app.services.draft.rag_orchestrator.search_legal_knowledge') as mock_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            mock_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}
            mock_dynamo.return_value = [{"evidence_id": "ev1", "status": "done"}]
            mock_qdrant.return_value = []
            mock_legal.return_value = []
            mock_openai.return_value = "Test draft"
            mock_template.return_value = None

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={"language": "en"},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK


class TestDraftPreviewResponse:
    """Contract tests for draft-preview response structure"""

    def test_draft_preview_response_structure(
        self, client, auth_headers, test_case
    ):
        """
        Given: Authenticated case member
        When: POST /cases/{id}/draft-preview is called successfully
        Then:
            - Response contains case_id
            - Response contains draft_text
            - Response contains citations list
            - Response contains generated_at timestamp
            - Response contains preview_disclaimer (FR-007 clarification)
        """
        with patch('app.services.draft_service.get_case_fact_summary') as mock_fact_summary, \
             patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic') as mock_qdrant, \
             patch('app.services.draft.rag_orchestrator.search_legal_knowledge') as mock_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            mock_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}
            mock_dynamo.return_value = [{"evidence_id": "ev1", "status": "done"}]
            mock_qdrant.return_value = [
                {"id": "ev1", "content": "폭언 내용", "labels": ["폭언"]}
            ]
            mock_legal.return_value = []
            mock_openai.return_value = "테스트 초안 본문 [EV-ev1]"
            mock_template.return_value = None

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={"sections": ["청구원인"]},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            # Required fields per contract
            assert "case_id" in data
            assert "draft_text" in data
            assert "citations" in data
            assert "generated_at" in data
            assert "preview_disclaimer" in data  # T026: Preview Only disclaimer

            # Verify types
            assert data["case_id"] == test_case.id
            assert isinstance(data["draft_text"], str)
            assert isinstance(data["citations"], list)
            assert isinstance(data["preview_disclaimer"], str)
            assert "미리보기" in data["preview_disclaimer"]  # Korean "preview"
            assert "검토" in data["preview_disclaimer"]  # Korean "review"

    def test_draft_preview_citations_format(
        self, client, auth_headers, test_case
    ):
        """
        Given: Authenticated case member with fact summary
        When: POST /cases/{id}/draft-preview returns response
        Then:
            - Response contains citations list (may be empty per 016-draft-fact-summary)
            - citations is a list type

        Note: 016-draft-fact-summary uses fact summary instead of evidence RAG,
        so citations array may be empty as evidence_results = []
        """
        with patch('app.services.draft_service.get_case_fact_summary') as mock_fact_summary, \
             patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic') as mock_qdrant, \
             patch('app.services.draft.rag_orchestrator.search_legal_knowledge') as mock_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            mock_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}
            mock_dynamo.return_value = [{"evidence_id": "ev1", "status": "done"}]
            mock_qdrant.return_value = []  # Empty - using fact summary
            mock_legal.return_value = []
            mock_openai.return_value = "테스트 초안"
            mock_template.return_value = None

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={"sections": ["청구원인"]},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            # Citations is always a list (016-draft-fact-summary may result in empty list)
            assert isinstance(data["citations"], list)


class TestDraftPreviewErrors:
    """Contract tests for draft-preview error handling"""

    def test_draft_preview_404_nonexistent_case(
        self, client, auth_headers
    ):
        """
        Given: Authenticated user
        When: POST /cases/{id}/draft-preview for non-existent case
        Then:
            - Returns 403 Forbidden (not 404 to prevent enumeration)
        """
        response = client.post(
            "/cases/nonexistent-case-id/draft-preview",
            json={"sections": ["청구취지"]},
            headers=auth_headers
        )

        # Should return 403, not 404 (security: prevent case enumeration)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_draft_preview_400_no_fact_summary(
        self, client, auth_headers, test_case
    ):
        """
        Given: Authenticated case member
        When: POST /cases/{id}/draft-preview for case without fact summary
        Then:
            - Returns 400 Bad Request with helpful message (016-draft-fact-summary)
        """
        with patch('app.services.draft_service.get_case_fact_summary') as mock_fact_summary:
            # No fact summary exists
            mock_fact_summary.return_value = None

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={"sections": ["청구원인"]},
                headers=auth_headers
            )

            # Should return validation error (400 Bad Request)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

            data = response.json()
            # Error response structure: {"error": {"message": "..."}}
            assert "error" in data
            assert "message" in data["error"]
            # Korean error message per spec (016-draft-fact-summary)
            assert "사실관계 요약" in data["error"]["message"]


class TestDraftPreviewInlineCitations:
    """Contract tests for inline citation format [EV-xxx] (FR-007)"""

    def test_draft_text_can_include_inline_citations(
        self, client, auth_headers, test_case
    ):
        """
        Given: Evidence exists for case
        When: POST /cases/{id}/draft-preview generates draft
        Then:
            - draft_text may include [EV-xxx] or [갑 제N호증] format citations

        Note: This test verifies the API accepts and returns inline citations,
        not that GPT-4o always produces them (that's model behavior)
        """
        with patch('app.services.draft_service.get_case_fact_summary') as mock_fact_summary, \
             patch('app.services.draft_service.get_evidence_by_case') as mock_dynamo, \
             patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic') as mock_qdrant, \
             patch('app.services.draft.rag_orchestrator.search_legal_knowledge') as mock_legal, \
             patch('app.services.draft_service.generate_chat_completion') as mock_openai, \
             patch('app.services.draft_service.get_template_by_type') as mock_template:

            mock_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}
            mock_dynamo.return_value = [{"evidence_id": "ev1", "status": "done"}]
            mock_qdrant.return_value = [
                {"id": "ev1", "content": "폭언 내용", "labels": ["폭언"]}
            ]
            mock_legal.return_value = []
            # Mock GPT response with inline citation
            mock_openai.return_value = (
                "원고와 피고는 2020년 결혼하였으나, "
                "피고의 계속된 폭언 [갑 제1호증]으로 인해 혼인관계가 파탄에 이르렀습니다."
            )
            mock_template.return_value = None

            response = client.post(
                f"/cases/{test_case.id}/draft-preview",
                json={"sections": ["청구원인"]},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            # Verify inline citation format exists in draft
            assert "[갑 제1호증]" in data["draft_text"]
