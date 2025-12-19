"""
Unit tests for Evidence Service
TDD - Improving test coverage for evidence_service.py
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch
import uuid

from app.services.evidence_service import EvidenceService
from app.db.schemas import (
    PresignedUrlRequest,
    UploadCompleteRequest,
    Article840Category,
)
from app.db.models import Case, CaseMember, User, CaseStatus, CaseMemberRole
from app.middleware import NotFoundError, PermissionError


# Common mock targets for evidence service tests
# Patch at the destination module (where the function is used) per Python patching best practices
# Since evidence_service.py does: from app.utils.dynamo import get_evidence_by_id
# The function becomes an attribute of app.services.evidence_service module
MOCK_SAVE_METADATA = 'app.services.evidence_service.save_evidence_metadata'
MOCK_INVOKE_AI = 'app.services.evidence_service.invoke_ai_worker'
MOCK_UPDATE_STATUS = 'app.services.evidence_service.update_evidence_status'
MOCK_GET_EVIDENCE = 'app.services.evidence_service.get_evidence_by_id'
MOCK_GET_EVIDENCE_BY_CASE = 'app.services.evidence_service.get_evidence_by_case'
MOCK_PRESIGNED_URL = 'app.services.evidence_service.generate_presigned_upload_url'


class TestParseArticle840Tags:
    """Unit tests for _parse_article_840_tags static method"""

    def test_parse_valid_tags(self):
        """Valid tags are parsed correctly"""
        evidence_data = {
            "article_840_tags": {
                "categories": ["adultery", "desertion"],
                "confidence": 0.95,
                "matched_keywords": ["외도", "유기"]
            }
        }
        result = EvidenceService._parse_article_840_tags(evidence_data)

        assert result is not None
        assert len(result.categories) == 2
        assert Article840Category.ADULTERY in result.categories
        assert Article840Category.DESERTION in result.categories
        assert result.confidence == 0.95
        assert "외도" in result.matched_keywords

    def test_parse_no_tags(self):
        """None returned when no tags"""
        evidence_data = {}
        result = EvidenceService._parse_article_840_tags(evidence_data)
        assert result is None

    def test_parse_invalid_category(self):
        """Invalid category returns None"""
        evidence_data = {
            "article_840_tags": {
                "categories": ["invalid_category"],
                "confidence": 0.5
            }
        }
        result = EvidenceService._parse_article_840_tags(evidence_data)
        assert result is None


class TestGetContentType:
    """Unit tests for _get_content_type static method"""

    def test_image_types(self):
        """Image extensions return correct content type"""
        assert EvidenceService._get_content_type("jpg") == "image/jpeg"
        assert EvidenceService._get_content_type("jpeg") == "image/jpeg"
        assert EvidenceService._get_content_type("png") == "image/png"
        assert EvidenceService._get_content_type("gif") == "image/gif"

    def test_audio_types(self):
        """Audio extensions return correct content type"""
        assert EvidenceService._get_content_type("mp3") == "audio/mpeg"
        assert EvidenceService._get_content_type("wav") == "audio/wav"
        assert EvidenceService._get_content_type("m4a") == "audio/mp4"

    def test_video_types(self):
        """Video extensions return correct content type"""
        assert EvidenceService._get_content_type("mp4") == "video/mp4"
        assert EvidenceService._get_content_type("avi") == "video/x-msvideo"
        assert EvidenceService._get_content_type("mov") == "video/quicktime"

    def test_document_types(self):
        """Document extensions return correct content type"""
        assert EvidenceService._get_content_type("pdf") == "application/pdf"
        assert EvidenceService._get_content_type("txt") == "text/plain"
        assert EvidenceService._get_content_type("csv") == "text/csv"
        assert EvidenceService._get_content_type("json") == "application/json"

    def test_unknown_type(self):
        """Unknown extension returns octet-stream"""
        assert EvidenceService._get_content_type("xyz") == "application/octet-stream"


class TestGenerateUploadPresignedUrl:
    """Unit tests for generate_upload_presigned_url method"""

    def test_presigned_url_success(self, test_env):
        """Successful presigned URL generation"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"presign_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Presign User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Presign Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)
        request = PresignedUrlRequest(
            case_id=case.id,
            filename="test.jpg",
            content_type="image/jpeg"
        )

        with patch(MOCK_PRESIGNED_URL) as mock_presign:
            mock_presign.return_value = {
                "upload_url": "https://s3.amazonaws.com/...",
                "fields": {"key": "value"}
            }

            result = service.generate_upload_presigned_url(request, user.id)

            assert result.upload_url == "https://s3.amazonaws.com/..."
            assert result.evidence_temp_id is not None
            assert case.id in result.s3_key

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_presigned_url_case_not_found(self, test_env):
        """NotFoundError when case doesn't exist"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"nf_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = EvidenceService(db)
        request = PresignedUrlRequest(
            case_id="nonexistent-case",
            filename="test.jpg",
            content_type="image/jpeg"
        )

        with pytest.raises(NotFoundError):
            service.generate_upload_presigned_url(request, user.id)

        db.delete(user)
        db.commit()
        db.close()

    def test_presigned_url_no_access(self, test_env):
        """PermissionError when user has no access"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"own_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        other = User(
            email=f"oth_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Other",
            role="lawyer"
        )
        db.add(other)
        db.commit()
        db.refresh(other)

        case = Case(
            title="Private Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)
        request = PresignedUrlRequest(
            case_id=case.id,
            filename="test.jpg",
            content_type="image/jpeg"
        )

        with pytest.raises(PermissionError):
            service.generate_upload_presigned_url(request, other.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(other)
        db.commit()
        db.close()


class TestHandleUploadComplete:
    """Unit tests for handle_upload_complete method"""

    def test_upload_complete_success(self, test_env):
        """Successful upload completion handling"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"upload_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Upload User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Upload Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        request = UploadCompleteRequest(
            case_id=case.id,
            s3_key=f"cases/{case.id}/raw/test123_photo.jpg",
            evidence_temp_id="test123",
            file_size=1024,
            note="Test note"
        )

        service = EvidenceService(db)

        with patch(MOCK_SAVE_METADATA) as mock_save, \
             patch(MOCK_INVOKE_AI, return_value={"status": "invoked"}) as mock_invoke, \
             patch(MOCK_UPDATE_STATUS):

            result = service.handle_upload_complete(request, user.id)

            assert result.evidence_id == "test123"
            assert result.case_id == case.id
            # Status is "processing" when invoke_ai_worker succeeds (no exception)
            assert result.status == "processing"
            # Verify mocks were called
            assert mock_save.called
            assert mock_invoke.called

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_upload_complete_ai_worker_failure(self, test_env):
        """Handle AI worker invocation failure"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"fail_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Fail User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Fail Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)
        request = UploadCompleteRequest(
            case_id=case.id,
            s3_key=f"cases/{case.id}/raw/test456_photo.jpg",
            evidence_temp_id="test456",
            file_size=1024
        )

        with patch(MOCK_SAVE_METADATA), \
             patch(MOCK_INVOKE_AI) as mock_invoke, \
             patch(MOCK_UPDATE_STATUS):

            mock_invoke.side_effect = Exception("Lambda invocation failed")

            result = service.handle_upload_complete(request, user.id)

            assert result.status == "failed"
            assert result.evidence_id == "test456"

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestHandleUploadCompletePermissions:
    """Unit tests for handle_upload_complete permission checks"""

    def test_upload_complete_case_not_found(self, test_env):
        """NotFoundError when case doesn't exist (line 160)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"ucnf_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = EvidenceService(db)
        request = UploadCompleteRequest(
            case_id="nonexistent-case",
            s3_key="cases/nonexistent/raw/test_photo.jpg",
            evidence_temp_id="test123",
            file_size=1024
        )

        with pytest.raises(NotFoundError):
            service.handle_upload_complete(request, user.id)

        db.delete(user)
        db.commit()
        db.close()

    def test_upload_complete_no_access(self, test_env):
        """PermissionError when user has no access (line 164)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"ucown_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        other = User(
            email=f"ucoth_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Other",
            role="lawyer"
        )
        db.add(other)
        db.commit()
        db.refresh(other)

        case = Case(
            title="Private Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)
        request = UploadCompleteRequest(
            case_id=case.id,
            s3_key=f"cases/{case.id}/raw/test_photo.jpg",
            evidence_temp_id="test123",
            file_size=1024
        )

        with pytest.raises(PermissionError):
            service.handle_upload_complete(request, other.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(other)
        db.commit()
        db.close()


class TestGetEvidenceList:
    """Unit tests for get_evidence_list method"""

    def test_get_evidence_list_success(self, test_env):
        """Successfully get evidence list"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"list_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="List User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="List Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE_BY_CASE) as mock_get:
            mock_get.return_value = [
                {
                    "evidence_id": "ev1",
                    "case_id": case.id,
                    "type": "image",
                    "filename": "photo.jpg",
                    "size": 1024,
                    "created_at": "2025-01-01T00:00:00",
                    "status": "completed"
                }
            ]

            result = service.get_evidence_list(case.id, user.id)

            assert len(result) == 1
            assert result[0].id == "ev1"
            assert result[0].type == "image"

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_evidence_list_with_category_filter(self, test_env):
        """Filter evidence by Article 840 category"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"cat_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Cat User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Cat Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE_BY_CASE) as mock_get:
            mock_get.return_value = [
                {
                    "evidence_id": "ev1",
                    "case_id": case.id,
                    "type": "image",
                    "filename": "photo1.jpg",
                    "size": 1024,
                    "created_at": "2025-01-01T00:00:00",
                    "status": "completed",
                    "article_840_tags": {
                        "categories": ["adultery"],
                        "confidence": 0.9
                    }
                },
                {
                    "evidence_id": "ev2",
                    "case_id": case.id,
                    "type": "image",
                    "filename": "photo2.jpg",
                    "size": 2048,
                    "created_at": "2025-01-02T00:00:00",
                    "status": "completed",
                    "article_840_tags": {
                        "categories": ["desertion"],
                        "confidence": 0.85
                    }
                }
            ]

            result = service.get_evidence_list(
                case.id,
                user.id,
                categories=[Article840Category.ADULTERY]
            )

            assert len(result) == 1
            assert result[0].id == "ev1"

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestGetEvidenceDetail:
    """Unit tests for get_evidence_detail method"""

    def test_get_evidence_detail_success(self, test_env):
        """Successfully get evidence detail"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"det_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Det User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Det Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "type": "image",
                "filename": "photo.jpg",
                "size": 1024,
                "s3_key": f"cases/{case.id}/raw/ev1_photo.jpg",
                "content_type": "image/jpeg",
                "created_at": "2025-01-01T00:00:00",
                "status": "completed",
                "ai_summary": "Test summary",
                "article_840_tags": {
                    "categories": ["adultery"],
                    "confidence": 0.9,
                    "matched_keywords": ["외도"]
                }
            }

            result = service.get_evidence_detail("ev1", user.id)

            assert result.id == "ev1"
            assert result.type == "image"
            assert result.ai_summary == "Test summary"
            assert result.article_840_tags is not None
            assert Article840Category.ADULTERY in result.article_840_tags.categories

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_evidence_detail_not_found(self, test_env):
        """NotFoundError when evidence doesn't exist"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"nf_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="NF User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = None

            with pytest.raises(NotFoundError):
                service.get_evidence_detail("nonexistent", user.id)

        db.delete(user)
        db.commit()
        db.close()


class TestRetryProcessing:
    """Unit tests for retry_processing method"""

    def test_retry_processing_success(self, test_env):
        """Successfully retry processing"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"retry_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Retry User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Retry Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        mock_evidence = {
            "evidence_id": "ev1",
            "case_id": case.id,
            "status": "failed",
            "s3_key": f"cases/{case.id}/raw/ev1_photo.jpg"
        }

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE, return_value=mock_evidence) as mock_get, \
             patch(MOCK_INVOKE_AI, return_value={"status": "invoked"}) as mock_invoke, \
             patch(MOCK_UPDATE_STATUS):

            result = service.retry_processing("ev1", user.id)

            assert result["success"] is True
            assert result["status"] == "processing"
            # Verify mocks were called
            assert mock_get.called
            assert mock_invoke.called

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_retry_processing_invalid_status(self, test_env):
        """ValueError when evidence not in failed state"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"invst_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="InvSt User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="InvSt Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "status": "completed",
                "s3_key": f"cases/{case.id}/raw/ev1_photo.jpg"
            }

            with pytest.raises(ValueError):
                service.retry_processing("ev1", user.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestGetCaseEvidence:
    """Unit tests for get_evidence_list (get_case_evidence) method"""

    def test_get_case_evidence_case_not_found(self, test_env):
        """PermissionError when case doesn't exist (prevents info leakage)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"cenfnd_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = EvidenceService(db)

        # PermissionError instead of NotFoundError to prevent info leakage
        with pytest.raises(PermissionError):
            service.get_evidence_list("nonexistent-case", user.id)

        db.delete(user)
        db.commit()
        db.close()

    def test_get_case_evidence_no_access(self, test_env):
        """PermissionError when user has no access (line 282)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"ceown_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        other = User(
            email=f"ceoth_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Other",
            role="lawyer"
        )
        db.add(other)
        db.commit()
        db.refresh(other)

        case = Case(
            title="Private Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with pytest.raises(PermissionError):
            service.get_evidence_list(case.id, other.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(other)
        db.commit()
        db.close()


class TestGetEvidenceDetailPermission:
    """Unit tests for get_evidence_detail permission checks"""

    def test_get_evidence_detail_no_access(self, test_env):
        """PermissionError when user has no access to case (line 338)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"edtown_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        other = User(
            email=f"edtoth_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Other",
            role="lawyer"
        )
        db.add(other)
        db.commit()
        db.refresh(other)

        case = Case(
            title="Private Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "type": "image",
                "filename": "photo.jpg"
            }

            with pytest.raises(PermissionError):
                service.get_evidence_detail("ev1", other.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(other)
        db.commit()
        db.close()


class TestRetryProcessingEdgeCases:
    """Unit tests for retry_processing edge cases"""

    def test_retry_processing_evidence_not_found(self, test_env):
        """NotFoundError when evidence doesn't exist (line 392)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rpnf_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = None

            with pytest.raises(NotFoundError):
                service.retry_processing("nonexistent", user.id)

        db.delete(user)
        db.commit()
        db.close()

    def test_retry_processing_no_access(self, test_env):
        """PermissionError when user has no access (line 397)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"rpown_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        other = User(
            email=f"rpoth_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Other",
            role="lawyer"
        )
        db.add(other)
        db.commit()
        db.refresh(other)

        case = Case(
            title="Private Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "status": "failed",
                "s3_key": f"cases/{case.id}/raw/ev1.jpg"
            }

            with pytest.raises(PermissionError):
                service.retry_processing("ev1", other.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(other)
        db.commit()
        db.close()

    def test_retry_processing_missing_s3_key(self, test_env):
        """ValueError when evidence missing s3_key (line 407)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"rpms3_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Test Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "status": "failed",
                "s3_key": None  # Missing s3_key
            }

            with pytest.raises(ValueError, match="missing s3_key"):
                service.retry_processing("ev1", user.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_retry_processing_ai_worker_failure(self, test_env):
        """AI Worker failure returns failed status (lines 428-433)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"rpfail_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Test Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get, \
             patch(MOCK_UPDATE_STATUS), \
             patch(MOCK_INVOKE_AI) as mock_invoke:

            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "status": "failed",
                "s3_key": f"cases/{case.id}/raw/ev1.jpg"
            }
            mock_invoke.side_effect = Exception("Lambda invocation failed")

            result = service.retry_processing("ev1", user.id)

            assert result["success"] is False
            assert result["status"] == "failed"
            assert "Lambda invocation failed" in result["message"]

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestGetEvidenceStatusPermission:
    """Unit tests for get_evidence_status permission checks"""

    def test_get_evidence_status_no_access(self, test_env):
        """PermissionError when user has no access (line 461)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"esown_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        other = User(
            email=f"esoth_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Other",
            role="lawyer"
        )
        db.add(other)
        db.commit()
        db.refresh(other)

        case = Case(
            title="Private Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "status": "processing"
            }

            with pytest.raises(PermissionError):
                service.get_evidence_status("ev1", other.id)

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(other)
        db.commit()
        db.close()


class TestGetEvidenceStatus:
    """Unit tests for get_evidence_status method"""

    def test_get_evidence_status_success(self, test_env):
        """Successfully get evidence status"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"status_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Status User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Status Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = {
                "evidence_id": "ev1",
                "case_id": case.id,
                "status": "processing",
                "error_message": None,
                "updated_at": "2025-01-01T00:00:00"
            }

            result = service.get_evidence_status("ev1", user.id)

            assert result["evidence_id"] == "ev1"
            assert result["status"] == "processing"
            assert result["error_message"] is None

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_evidence_status_not_found(self, test_env):
        """NotFoundError when evidence doesn't exist"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"nfst_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="NFSt User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = EvidenceService(db)

        with patch(MOCK_GET_EVIDENCE) as mock_get:
            mock_get.return_value = None

            with pytest.raises(NotFoundError):
                service.get_evidence_status("nonexistent", user.id)

        db.delete(user)
        db.commit()
        db.close()
