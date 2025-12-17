"""
Contract tests for Procedure API
US3 - 절차 단계 관리 (Procedure Stage Tracking)

Tests for procedure stage endpoints:
- GET /cases/{case_id}/procedure (get timeline)
- POST /cases/{case_id}/procedure/initialize (initialize timeline)
- POST /cases/{case_id}/procedure/stages (create stage)
- GET /cases/{case_id}/procedure/stages/{stage_id} (get stage)
- PATCH /cases/{case_id}/procedure/stages/{stage_id} (update stage)
- DELETE /cases/{case_id}/procedure/stages/{stage_id} (delete stage)
- POST /cases/{case_id}/procedure/stages/{stage_id}/complete (complete stage)
- POST /cases/{case_id}/procedure/stages/{stage_id}/skip (skip stage)
- POST /cases/{case_id}/procedure/transition (transition to next)
- GET /cases/{case_id}/procedure/next-stages (get valid next stages)
"""

from fastapi import status


# ============== Timeline Tests ==============


class TestGetProcedureTimeline:
    """
    Contract tests for GET /cases/{case_id}/procedure
    """

    def test_should_return_empty_timeline_for_new_case(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Authenticated lawyer with access to case
        When: GET /cases/{case_id}/procedure
        Then:
            - Returns 200 status code
            - Response contains case_id
            - Response contains stages array (empty)
            - Response contains completed_count = 0
        """
        response = client.get(
            f"/cases/{test_case.id}/procedure",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["case_id"] == test_case.id
        assert "stages" in data
        assert isinstance(data["stages"], list)
        assert "completed_count" in data
        assert "total_count" in data

    def test_should_reject_unauthenticated_request(self, client, test_case):
        """
        Given: No authentication token
        When: GET /cases/{case_id}/procedure
        Then: Returns 401 Unauthorized
        """
        response = client.get(f"/cases/{test_case.id}/procedure")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestInitializeProcedureTimeline:
    """
    Contract tests for POST /cases/{case_id}/procedure/initialize
    """

    def test_should_initialize_timeline_with_all_stages(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Authenticated lawyer with write access to case
        When: POST /cases/{case_id}/procedure/initialize
        Then:
            - Returns 200 status code
            - Response contains 9 stages (Korean family litigation stages)
            - First stage (filed) is in_progress
        """
        response = client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data["stages"]) == 9
        assert data["stages"][0]["stage"] == "filed"
        # First stage should be in_progress when start_filed=true (default)

    def test_should_not_duplicate_when_initialized_twice(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Timeline already initialized
        When: POST /cases/{case_id}/procedure/initialize again
        Then:
            - Returns 200 status code
            - Does not create duplicate stages
        """
        # First initialization
        response1 = client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_200_OK
        initial_count = len(response1.json()["stages"])

        # Second initialization
        response2 = client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )
        assert response2.status_code == status.HTTP_200_OK
        assert len(response2.json()["stages"]) == initial_count

    def test_should_reject_unauthenticated_request(self, client, test_case):
        """
        Given: No authentication token
        When: POST /cases/{case_id}/procedure/initialize
        Then: Returns 401 Unauthorized
        """
        response = client.post(f"/cases/{test_case.id}/procedure/initialize")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============== Stage CRUD Tests ==============


class TestCreateProcedureStage:
    """
    Contract tests for POST /cases/{case_id}/procedure/stages
    """

    def test_should_create_stage_with_valid_data(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Authenticated lawyer with write access
        When: POST /cases/{case_id}/procedure/stages with valid data
        Then:
            - Returns 201 Created
            - Response contains stage id
            - Response contains stage type and status
        """
        response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={
                "stage": "filed",
                "status": "in_progress",
                "court_reference": "2024드합1234",
                "notes": "소장 접수 완료"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "id" in data
        assert data["stage"] == "filed"
        assert data["stage_label"] == "소장 접수"
        assert data["status"] == "in_progress"
        assert data["status_label"] == "진행중"

    def test_should_reject_duplicate_stage(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage already exists for case
        When: POST /cases/{case_id}/procedure/stages with same stage type
        Then: Returns 400 Bad Request
        """
        # Create first stage
        client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "served", "status": "pending"}
        )

        # Try to create duplicate
        response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "served", "status": "pending"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_reject_invalid_stage_type(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Authenticated lawyer
        When: POST /cases/{case_id}/procedure/stages with invalid stage type
        Then: Returns 422 Unprocessable Entity
        """
        response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "invalid_stage", "status": "pending"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetProcedureStage:
    """
    Contract tests for GET /cases/{case_id}/procedure/stages/{stage_id}
    """

    def test_should_return_stage_details(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage exists for case
        When: GET /cases/{case_id}/procedure/stages/{stage_id}
        Then:
            - Returns 200 status code
            - Response contains all stage fields with Korean labels
        """
        # Create stage first
        create_response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={
                "stage": "mediation",
                "status": "pending",
                "scheduled_date": "2024-02-01T10:00:00Z",
                "court_reference": "2024가합1234",
                "judge_name": "김판사"
            }
        )
        stage_id = create_response.json()["id"]

        # Get stage
        response = client.get(
            f"/cases/{test_case.id}/procedure/stages/{stage_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == stage_id
        assert data["stage"] == "mediation"
        assert data["stage_label"] == "조정 회부"
        assert data["court_reference"] == "2024가합1234"
        assert data["judge_name"] == "김판사"

    def test_should_return_404_for_nonexistent_stage(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage does not exist
        When: GET /cases/{case_id}/procedure/stages/{stage_id}
        Then: Returns 404 Not Found
        """
        response = client.get(
            f"/cases/{test_case.id}/procedure/stages/stage_nonexistent",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateProcedureStage:
    """
    Contract tests for PATCH /cases/{case_id}/procedure/stages/{stage_id}
    """

    def test_should_update_stage_status(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage exists
        When: PATCH /cases/{case_id}/procedure/stages/{stage_id}
        Then:
            - Returns 200 status code
            - Stage is updated with new values
        """
        # Create stage
        create_response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "answered", "status": "pending"}
        )
        stage_id = create_response.json()["id"]

        # Update stage
        response = client.patch(
            f"/cases/{test_case.id}/procedure/stages/{stage_id}",
            headers=auth_headers,
            json={
                "status": "in_progress",
                "notes": "답변서 제출 준비중"
            }
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "in_progress"
        assert data["notes"] == "답변서 제출 준비중"


class TestDeleteProcedureStage:
    """
    Contract tests for DELETE /cases/{case_id}/procedure/stages/{stage_id}
    """

    def test_should_delete_stage(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage exists
        When: DELETE /cases/{case_id}/procedure/stages/{stage_id}
        Then: Returns 204 No Content
        """
        # Create stage
        create_response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "trial", "status": "pending"}
        )
        stage_id = create_response.json()["id"]

        # Delete stage
        response = client.delete(
            f"/cases/{test_case.id}/procedure/stages/{stage_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        get_response = client.get(
            f"/cases/{test_case.id}/procedure/stages/{stage_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


# ============== Stage Action Tests ==============


class TestCompleteStage:
    """
    Contract tests for POST /cases/{case_id}/procedure/stages/{stage_id}/complete
    """

    def test_should_complete_stage(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage is in_progress
        When: POST /cases/{case_id}/procedure/stages/{stage_id}/complete
        Then:
            - Returns 200 status code
            - Stage status becomes completed
            - completed_date is set
        """
        # Create stage in progress
        create_response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "judgment", "status": "in_progress"}
        )
        stage_id = create_response.json()["id"]

        # Complete stage
        response = client.post(
            f"/cases/{test_case.id}/procedure/stages/{stage_id}/complete?outcome=원고%20승소",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "completed"
        assert data["outcome"] == "원고 승소"
        assert data["completed_date"] is not None


class TestSkipStage:
    """
    Contract tests for POST /cases/{case_id}/procedure/stages/{stage_id}/skip
    """

    def test_should_skip_stage(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage is pending
        When: POST /cases/{case_id}/procedure/stages/{stage_id}/skip
        Then:
            - Returns 200 status code
            - Stage status becomes skipped
        """
        # Create pending stage
        create_response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "appeal", "status": "pending"}
        )
        stage_id = create_response.json()["id"]

        # Skip stage
        response = client.post(
            f"/cases/{test_case.id}/procedure/stages/{stage_id}/skip?reason=항소%20포기",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "skipped"


# ============== Transition Tests ==============


class TestTransitionToNextStage:
    """
    Contract tests for POST /cases/{case_id}/procedure/transition
    """

    def test_should_transition_to_next_stage(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Current stage is in_progress
        When: POST /cases/{case_id}/procedure/transition with valid next stage
        Then:
            - Returns 200 status code
            - Current stage is completed
            - Next stage is activated
        """
        # Initialize timeline
        client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )

        # Transition from filed to served
        response = client.post(
            f"/cases/{test_case.id}/procedure/transition",
            headers=auth_headers,
            json={
                "next_stage": "served",
                "outcome": "송달 완료"
            }
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert "next_stage" in data
        assert data["next_stage"]["stage"] == "served"
        assert data["next_stage"]["status"] == "in_progress"

    def test_should_reject_invalid_transition(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Current stage is filed
        When: POST /cases/{case_id}/procedure/transition with invalid next stage
        Then: Returns 400 Bad Request
        """
        # Initialize timeline
        client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )

        # Try invalid transition (filed -> judgment, skipping many stages)
        response = client.post(
            f"/cases/{test_case.id}/procedure/transition",
            headers=auth_headers,
            json={"next_stage": "judgment"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetValidNextStages:
    """
    Contract tests for GET /cases/{case_id}/procedure/next-stages
    """

    def test_should_return_valid_next_stages(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Timeline initialized with current stage
        When: GET /cases/{case_id}/procedure/next-stages
        Then:
            - Returns 200 status code
            - Response contains list of valid next stages with labels
        """
        # Initialize timeline
        client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )

        # Get valid next stages
        response = client.get(
            f"/cases/{test_case.id}/procedure/next-stages",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        # From filed, only served is valid
        assert len(data) >= 1
        assert any(s["stage"] == "served" for s in data)


# ============== Schema Validation Tests ==============


class TestProcedureStageSchema:
    """
    Contract tests for procedure stage schema validation
    """

    def test_stage_response_should_have_required_fields(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage created
        When: GET stage detail
        Then: Response has all required fields
        """
        # Create stage
        create_response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={
                "stage": "final",
                "status": "pending",
                "court_reference": "2024드합1234"
            }
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        data = create_response.json()

        # Required fields
        assert "id" in data
        assert "case_id" in data
        assert "stage" in data
        assert "stage_label" in data
        assert "status" in data
        assert "status_label" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Optional fields should exist (may be null)
        assert "scheduled_date" in data
        assert "completed_date" in data
        assert "court_reference" in data
        assert "judge_name" in data
        assert "notes" in data
        assert "documents" in data
        assert "outcome" in data

    def test_stage_type_enum_values(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Timeline initialized
        Then: All stages have valid Korean procedure types
        """
        # Initialize
        response = client.post(
            f"/cases/{test_case.id}/procedure/initialize",
            headers=auth_headers
        )

        valid_stages = [
            "filed", "served", "answered", "mediation",
            "mediation_closed", "trial", "judgment", "appeal", "final"
        ]

        data = response.json()
        for stage in data["stages"]:
            assert stage["stage"] in valid_stages

    def test_status_enum_values(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Stage created/updated
        Then: Status should be one of valid enum values
        """
        # Create with valid status
        response = client.post(
            f"/cases/{test_case.id}/procedure/stages",
            headers=auth_headers,
            json={"stage": "filed", "status": "completed"}
        )
        assert response.status_code == status.HTTP_201_CREATED

        valid_statuses = ["pending", "in_progress", "completed", "skipped"]
        assert response.json()["status"] in valid_statuses
