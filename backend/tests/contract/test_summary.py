"""
Contract tests for Summary API
US8 - 진행 상태 요약 카드 (Progress Summary Cards)

Tests for summary card endpoints:
- GET /cases/{case_id}/summary (get summary data)
- GET /cases/{case_id}/summary/pdf (download as PDF/HTML)
"""

import pytest
from fastapi import status


# ============== Summary Get Tests ==============


class TestGetCaseSummary:
    """
    Contract tests for GET /cases/{case_id}/summary
    """

    def test_should_return_summary_for_valid_case(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Authenticated user with access to case
        When: GET /cases/{case_id}/summary
        Then:
            - Returns 200 status code
            - Response contains case_id
            - Response contains case_title
            - Response contains current_stage (may be null)
            - Response contains progress_percent
            - Response contains completed_stages array
            - Response contains next_schedules array
            - Response contains generated_at timestamp
        """
        response = client.get(
            f"/cases/{test_case.id}/summary",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["case_id"] == test_case.id
        assert "case_title" in data
        assert "current_stage" in data  # Can be null
        assert "progress_percent" in data
        assert isinstance(data["progress_percent"], int)
        assert 0 <= data["progress_percent"] <= 100
        assert "completed_stages" in data
        assert isinstance(data["completed_stages"], list)
        assert "next_schedules" in data
        assert isinstance(data["next_schedules"], list)
        assert "generated_at" in data
        assert "lawyer" in data

    def test_should_reject_unauthenticated_request(self, client, test_case):
        """
        Given: No authentication token
        When: GET /cases/{case_id}/summary
        Then: Returns 401 Unauthorized
        """
        response = client.get(f"/cases/{test_case.id}/summary")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_should_return_404_for_nonexistent_case(
        self, client, auth_headers
    ):
        """
        Given: Authenticated user
        When: GET /cases/{nonexistent_id}/summary
        Then: Returns 404 Not Found
        """
        response = client.get(
            "/cases/nonexistent_case_id/summary",
            headers=auth_headers
        )
        # 403 because access verification fails first
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


class TestGetCaseSummaryWithProcedure:
    """
    Contract tests for summary with initialized procedure stages
    """

    def test_should_include_completed_stages_in_summary(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Case with initialized procedure stages
        When: GET /cases/{case_id}/summary
        Then:
            - Response includes procedure stage information
            - Progress is calculated based on stages
        """
        # First initialize procedure stages
        init_response = client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )
        assert init_response.status_code == status.HTTP_200_OK

        # Then get summary
        response = client.get(
            f"/cases/{test_case.id}/summary",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # After initialization, there should be current stage info
        # The first stage (filed) starts as in_progress
        assert data["current_stage"] is not None
        assert "소장 접수" in data["current_stage"] or "대기" in data["current_stage"]

    def test_should_update_progress_after_completing_stage(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Case with one completed procedure stage
        When: GET /cases/{case_id}/summary
        Then:
            - Progress percent reflects completion
            - Completed stages list is not empty
        """
        # Initialize stages
        init_response = client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )
        assert init_response.status_code == status.HTTP_200_OK
        stages = init_response.json()["stages"]
        filed_stage_id = stages[0]["id"]

        # Complete the first stage
        complete_response = client.post(
            f"/cases/{test_case.id}/procedure/stages/{filed_stage_id}/complete?outcome=접수완료",
            headers=auth_headers
        )
        assert complete_response.status_code == status.HTTP_200_OK

        # Get summary
        response = client.get(
            f"/cases/{test_case.id}/summary",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have progress
        assert data["progress_percent"] > 0

        # Should have completed stages
        assert len(data["completed_stages"]) > 0
        assert data["completed_stages"][0]["stage_label"] == "소장 접수"


# ============== PDF Export Tests ==============


class TestGetCaseSummaryPdf:
    """
    Contract tests for GET /cases/{case_id}/summary/pdf
    """

    def test_should_return_html_for_pdf(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Authenticated user with access to case
        When: GET /cases/{case_id}/summary/pdf
        Then:
            - Returns 200 status code
            - Response content-type is text/html
            - Response includes Content-Disposition header
        """
        response = client.get(
            f"/cases/{test_case.id}/summary/pdf",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")
        assert "attachment" in response.headers.get("content-disposition", "")

    def test_should_reject_unauthenticated_pdf_request(self, client, test_case):
        """
        Given: No authentication token
        When: GET /cases/{case_id}/summary/pdf
        Then: Returns 401 Unauthorized
        """
        response = client.get(f"/cases/{test_case.id}/summary/pdf")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_pdf_should_contain_case_info(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Authenticated user with access to case
        When: GET /cases/{case_id}/summary/pdf
        Then:
            - Response HTML contains case title
            - Response HTML contains summary sections
        """
        response = client.get(
            f"/cases/{test_case.id}/summary/pdf",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode('utf-8')

        # Check HTML structure
        assert "<!DOCTYPE html>" in content
        assert "사건 진행 현황 요약" in content
        assert "현재 단계" in content
        assert "완료된 단계" in content
        assert "다음 일정" in content


# ============== Lawyer Info Tests ==============


class TestSummaryLawyerInfo:
    """
    Contract tests for lawyer info in summary
    """

    def test_should_include_lawyer_info(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Case with assigned lawyer (creator)
        When: GET /cases/{case_id}/summary
        Then:
            - Response includes lawyer object
            - Lawyer has name and email
        """
        response = client.get(
            f"/cases/{test_case.id}/summary",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["lawyer"] is not None
        assert "name" in data["lawyer"]
        assert "email" in data["lawyer"]
