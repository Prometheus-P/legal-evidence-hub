"""
Evidence Service - Business logic for evidence management
Handles presigned URL generation and evidence metadata retrieval
"""

from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.schemas import (
    PresignedUrlRequest,
    PresignedUrlResponse,
    UploadCompleteRequest,
    UploadCompleteResponse,
    EvidenceSummary,
    EvidenceDetail,
    EvidenceReviewResponse,
    Article840Tags,
    Article840Category,
    SpeakerMappingItem,
    SpeakerMappingUpdateRequest,
    SpeakerMappingResponse
)
from app.repositories.case_repository import CaseRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.repositories.user_repository import UserRepository
from app.db.models import UserRole
from app.utils.s3 import generate_presigned_upload_url
from app.utils.dynamo import (
    get_evidence_by_case,
    get_evidence_by_id,
    put_evidence_metadata as save_evidence_metadata,
    update_evidence_status,
    update_evidence_speaker_mapping
)
from app.utils.lambda_client import invoke_ai_worker
from app.utils.evidence import generate_evidence_id, extract_filename_from_s3_key
from app.core.config import settings
from app.middleware import NotFoundError, PermissionError, ValidationError
from app.repositories.party_repository import PartyRepository
from app.utils.audit import log_audit_event
from app.db.schemas.audit import AuditAction
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class EvidenceService:
    """
    Service for evidence management business logic
    """

    # Speaker mapping validation constants
    MAX_SPEAKERS = 10
    MAX_SPEAKER_LABEL_LENGTH = 50

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.member_repo = CaseMemberRepository(db)
        self.user_repo = UserRepository(db)
        self.party_repo = PartyRepository(db)

    @staticmethod
    def _parse_article_840_tags(evidence_data: dict) -> Optional[Article840Tags]:
        """
        Parse Article 840 tags from DynamoDB evidence data

        Args:
            evidence_data: DynamoDB evidence item

        Returns:
            Article840Tags if available, None otherwise
        """
        tags_data = evidence_data.get("article_840_tags")
        if not tags_data:
            return None

        try:
            # Parse categories from string values to Article840Category enum
            categories = [
                Article840Category(cat)
                for cat in tags_data.get("categories", [])
            ]

            return Article840Tags(
                categories=categories,
                confidence=tags_data.get("confidence", 0.0),
                matched_keywords=tags_data.get("matched_keywords", [])
            )
        except (ValueError, KeyError):
            # Invalid category value or malformed data
            return None

    def generate_upload_presigned_url(
        self,
        request: PresignedUrlRequest,
        user_id: str
    ) -> PresignedUrlResponse:
        """
        Generate S3 presigned URL for evidence upload

        Args:
            request: Presigned URL request data
            user_id: ID of user requesting upload

        Returns:
            Presigned URL response with upload_url and fields

        Raises:
            NotFoundError: Case not found
            PermissionError: User does not have access to case

        Security:
            - Validates user has access to case
            - Enforces 5-minute max expiration
            - Uses unique temporary evidence ID
        """
        # Check if case exists
        case = self.case_repo.get_by_id(request.case_id)
        if not case:
            raise NotFoundError("Case")

        # Check if user has access to case
        if not self.member_repo.has_access(request.case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # Generate unique temporary evidence ID
        evidence_temp_id = generate_evidence_id()

        # Construct S3 key with proper prefix
        s3_key = f"cases/{request.case_id}/raw/{evidence_temp_id}_{request.filename}"

        # Generate presigned URL (max 5 minutes per security policy)
        presigned_data = generate_presigned_upload_url(
            bucket=settings.S3_EVIDENCE_BUCKET,
            key=s3_key,
            content_type=request.content_type,
            expires_in=min(settings.S3_PRESIGNED_URL_EXPIRE_SECONDS, 300)
        )

        return PresignedUrlResponse(
            upload_url=presigned_data["upload_url"],
            fields=presigned_data["fields"],
            evidence_temp_id=evidence_temp_id,
            s3_key=s3_key
        )

    def handle_upload_complete(
        self,
        request: UploadCompleteRequest,
        user_id: str
    ) -> UploadCompleteResponse:
        """
        Handle evidence upload completion notification

        Args:
            request: Upload complete request with s3_key and metadata
            user_id: ID of user who uploaded the evidence

        Returns:
            UploadCompleteResponse with created evidence info

        Raises:
            NotFoundError: Case not found
            PermissionError: User does not have access to case

        Process:
            1. Validate user has access to case
            2. Create evidence metadata record in DynamoDB
            3. Trigger AI Worker processing (via SNS or direct invocation)
        """
        # Check if case exists
        case = self.case_repo.get_by_id(request.case_id)
        if not case:
            raise NotFoundError("Case")

        # Check if user has access to case
        if not self.member_repo.has_access(request.case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # Determine review_status based on uploader role
        uploader = self.user_repo.get_by_id(user_id)
        if uploader and uploader.role == UserRole.CLIENT:
            review_status = "pending_review"
        else:
            # Internal users (lawyer, staff, admin) auto-approve
            review_status = "approved"

        # Extract filename from s3_key
        filename = extract_filename_from_s3_key(request.s3_key)

        # Determine file type from extension
        # NOTE: Keep in sync with ai_worker/handler.py route_parser()
        extension = filename.split(".")[-1].lower() if "." in filename else ""
        type_mapping = {
            # Images
            "jpg": "image", "jpeg": "image", "png": "image", "gif": "image", "bmp": "image",
            # Audio
            "mp3": "audio", "wav": "audio", "m4a": "audio", "aac": "audio",
            # Video
            "mp4": "video", "avi": "video", "mov": "video", "mkv": "video",
            # Documents
            "pdf": "pdf",
            "txt": "text", "csv": "text", "json": "text"
        }
        evidence_type = type_mapping.get(extension, "document")

        # Use evidence_temp_id as evidence_id (matches S3 key for AI Worker)
        evidence_id = request.evidence_temp_id
        created_at = datetime.utcnow()

        # Create evidence metadata for DynamoDB
        evidence_metadata = {
            "evidence_id": evidence_id,
            "case_id": request.case_id,
            "type": evidence_type,
            "filename": filename,
            "s3_key": request.s3_key,
            "size": request.file_size,  # File size in bytes
            "content_type": self._get_content_type(extension),
            "status": "pending",  # Waiting for AI Worker processing
            "review_status": review_status,  # pending_review for client, approved for internal
            "created_at": created_at.isoformat(),
            "created_by": user_id,
            "note": request.note,
            "deleted": False
        }

        # Store EXIF metadata if provided (for detective image uploads)
        if request.exif_metadata:
            exif_data = {}
            if request.exif_metadata.gps_latitude is not None:
                exif_data["gps_latitude"] = request.exif_metadata.gps_latitude
            if request.exif_metadata.gps_longitude is not None:
                exif_data["gps_longitude"] = request.exif_metadata.gps_longitude
            if request.exif_metadata.gps_altitude is not None:
                exif_data["gps_altitude"] = request.exif_metadata.gps_altitude
            if request.exif_metadata.datetime_original:
                exif_data["datetime_original"] = request.exif_metadata.datetime_original
            if request.exif_metadata.camera_make:
                exif_data["camera_make"] = request.exif_metadata.camera_make
            if request.exif_metadata.camera_model:
                exif_data["camera_model"] = request.exif_metadata.camera_model
            if exif_data:
                evidence_metadata["exif_metadata"] = exif_data
                logger.info(f"EXIF metadata stored for evidence {evidence_id}: {list(exif_data.keys())}")

        # Save to DynamoDB
        save_evidence_metadata(evidence_metadata)

        # Trigger AI Worker Lambda for processing
        try:
            invoke_result = invoke_ai_worker(
                bucket=settings.S3_EVIDENCE_BUCKET,
                s3_key=request.s3_key,
                evidence_id=evidence_id,
                case_id=request.case_id
            )
            logger.info(f"AI Worker invocation result: {invoke_result}")

            # Check the actual result status from invoke_ai_worker
            result_status = invoke_result.get("status", "")

            if result_status == "invoked":
                # Lambda successfully invoked - update to processing
                update_evidence_status(evidence_id, "processing")
            elif result_status == "skipped":
                # Lambda is disabled - keep as pending, log info
                logger.info(f"AI Worker disabled - evidence {evidence_id} stays pending for manual processing")
                # Don't update status, keep as "pending"
                return UploadCompleteResponse(
                    evidence_id=evidence_id,
                    case_id=request.case_id,
                    filename=filename,
                    s3_key=request.s3_key,
                    status="pending",
                    review_status=review_status,
                    created_at=created_at
                )
            else:
                # Error or unexpected status - mark as failed
                error_msg = invoke_result.get("error_message", f"Lambda invocation failed with status: {result_status}")
                logger.error(f"AI Worker invocation failed for evidence {evidence_id}: {error_msg}")
                update_evidence_status(evidence_id, "failed", error_message=error_msg)
                return UploadCompleteResponse(
                    evidence_id=evidence_id,
                    case_id=request.case_id,
                    filename=filename,
                    s3_key=request.s3_key,
                    status="failed",
                    review_status=review_status,
                    created_at=created_at
                )
        except Exception as e:
            # Mark as failed if AI Worker invocation raises unexpected exception
            logger.error(f"AI Worker invocation exception for evidence {evidence_id}: {e}")
            update_evidence_status(evidence_id, "failed", error_message=str(e))
            # Still return success - the evidence record exists, just needs retry
            return UploadCompleteResponse(
                evidence_id=evidence_id,
                case_id=request.case_id,
                filename=filename,
                s3_key=request.s3_key,
                status="failed",
                review_status=review_status,
                created_at=created_at
            )

        return UploadCompleteResponse(
            evidence_id=evidence_id,
            case_id=request.case_id,
            filename=filename,
            s3_key=request.s3_key,
            status="processing",
            review_status=review_status,
            created_at=created_at
        )

    @staticmethod
    def _get_content_type(extension: str) -> str:
        """Get MIME content type from file extension"""
        content_types = {
            "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif",
            "mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4",
            "mp4": "video/mp4", "avi": "video/x-msvideo", "mov": "video/quicktime",
            "pdf": "application/pdf",
            "txt": "text/plain", "csv": "text/csv", "json": "application/json"
        }
        return content_types.get(extension, "application/octet-stream")

    def get_evidence_list(
        self,
        case_id: str,
        user_id: str,
        categories: Optional[List[Article840Category]] = None
    ) -> List[EvidenceSummary]:
        """
        Get list of evidence for a case

        Args:
            case_id: Case ID
            user_id: User ID requesting access
            categories: Filter by Article 840 categories (optional)

        Returns:
            List of evidence summary

        Raises:
            PermissionError: User does not have access (also for non-existent cases)
        """
        # Check permission first to prevent information leakage
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # Check if case exists (only after permission check)
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Get evidence metadata from DynamoDB
        evidence_list = get_evidence_by_case(case_id)

        # Convert to EvidenceSummary schema
        summaries = [
            EvidenceSummary(
                id=evidence.get("evidence_id") or evidence.get("id"),
                case_id=evidence["case_id"],
                type=evidence["type"],
                filename=evidence["filename"],
                size=evidence.get("size", 0),
                created_at=datetime.fromisoformat(evidence["created_at"]),
                status=evidence.get("status", "pending"),
                ai_summary=evidence.get("ai_summary"),
                article_840_tags=self._parse_article_840_tags(evidence),
                has_speaker_mapping=bool(evidence.get("speaker_mapping"))
            )
            for evidence in evidence_list
        ]

        # Apply category filter if specified
        if categories:
            summaries = [
                summary for summary in summaries
                if summary.article_840_tags and any(
                    cat in summary.article_840_tags.categories
                    for cat in categories
                )
            ]

        return summaries

    def get_evidence_detail(self, evidence_id: str, user_id: str) -> EvidenceDetail:
        """
        Get detailed evidence metadata with AI analysis results

        Args:
            evidence_id: Evidence ID
            user_id: User ID requesting access

        Returns:
            Evidence detail with AI analysis

        Raises:
            NotFoundError: Evidence not found
            PermissionError: User does not have access to case
        """
        # Get evidence metadata from DynamoDB
        evidence = get_evidence_by_id(evidence_id)
        if not evidence:
            raise NotFoundError("Evidence")

        # Check if user has access to the case
        case_id = evidence["case_id"]
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # Parse Article 840 tags
        article_840_tags = self._parse_article_840_tags(evidence)

        # Map categories to labels (for backward compatibility)
        labels = evidence.get("labels", [])
        if article_840_tags and article_840_tags.categories:
            # Convert Article840Category enum to string values
            labels = [cat.value for cat in article_840_tags.categories]

        # Parse speaker mapping for response
        speaker_mapping = None
        raw_mapping = evidence.get("speaker_mapping")
        if raw_mapping:
            speaker_mapping = {
                label: SpeakerMappingItem(
                    party_id=item.get("party_id", ""),
                    party_name=item.get("party_name", "")
                )
                for label, item in raw_mapping.items()
            }

        # Parse speaker_mapping_updated_at
        speaker_mapping_updated_at = None
        if evidence.get("speaker_mapping_updated_at"):
            speaker_mapping_updated_at = datetime.fromisoformat(evidence["speaker_mapping_updated_at"])

        # Convert to EvidenceDetail schema
        return EvidenceDetail(
            id=evidence.get("evidence_id") or evidence.get("id"),
            case_id=evidence["case_id"],
            type=evidence["type"],
            filename=evidence["filename"],
            size=evidence.get("size", 0),
            s3_key=evidence["s3_key"],
            content_type=evidence.get("content_type", "application/octet-stream"),
            created_at=datetime.fromisoformat(evidence["created_at"]),
            status=evidence.get("status", "pending"),
            ai_summary=evidence.get("ai_summary"),
            labels=labels,
            insights=evidence.get("insights", []),
            content=evidence.get("content"),
            speaker=evidence.get("speaker"),
            timestamp=datetime.fromisoformat(evidence["timestamp"]) if evidence.get("timestamp") else None,
            qdrant_id=evidence.get("qdrant_id"),
            article_840_tags=article_840_tags,
            speaker_mapping=speaker_mapping,
            speaker_mapping_updated_at=speaker_mapping_updated_at
        )

    def retry_processing(self, evidence_id: str, user_id: str) -> dict:
        """
        Retry processing for failed evidence

        Args:
            evidence_id: Evidence ID to retry
            user_id: User ID requesting retry

        Returns:
            dict with status and message

        Raises:
            NotFoundError: Evidence not found
            PermissionError: User does not have access
            ValueError: Evidence not in failed state

        State Machine:
            FAILED → PROCESSING (on successful retry)
        """
        # Get evidence metadata from DynamoDB
        evidence = get_evidence_by_id(evidence_id)
        if not evidence:
            raise NotFoundError("Evidence")

        # Check if user has access to the case
        case_id = evidence["case_id"]
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # Allow retry for failed, pending, or stuck processing evidence
        current_status = evidence.get("status", "")
        if current_status not in ["failed", "pending", "processing"]:
            raise ValueError(f"Cannot retry evidence with status '{current_status}'. Only 'failed', 'pending', or 'processing' evidence can be retried.")

        # Get required fields
        s3_key = evidence.get("s3_key")
        if not s3_key:
            raise ValueError("Evidence missing s3_key - cannot retry")

        # Re-invoke AI Worker (status update happens after successful invocation)
        try:
            invoke_result = invoke_ai_worker(
                bucket=settings.S3_EVIDENCE_BUCKET,
                s3_key=s3_key,
                evidence_id=evidence_id,
                case_id=case_id
            )
            logger.info(f"AI Worker retry invocation result for {evidence_id}: {invoke_result}")

            # Check the actual result status from invoke_ai_worker
            result_status = invoke_result.get("status", "")

            if result_status == "invoked":
                # Update status to processing only after successful Lambda invocation
                update_evidence_status(evidence_id, "processing", error_message=None)
                return {
                    "success": True,
                    "message": "Evidence processing restarted",
                    "evidence_id": evidence_id,
                    "status": "processing"
                }
            elif result_status == "skipped":
                # Lambda is disabled - revert to pending
                update_evidence_status(evidence_id, "pending", error_message=None)
                return {
                    "success": False,
                    "message": "AI Worker is disabled. Evidence remains pending for manual processing.",
                    "evidence_id": evidence_id,
                    "status": "pending"
                }
            else:
                # Error or unexpected status
                error_msg = invoke_result.get("error_message", f"Lambda invocation failed with status: {result_status}")
                update_evidence_status(evidence_id, "failed", error_message=error_msg)
                return {
                    "success": False,
                    "message": f"Retry failed: {error_msg}",
                    "evidence_id": evidence_id,
                    "status": "failed"
                }
        except Exception as e:
            # Mark as failed again
            logger.error(f"AI Worker retry failed for evidence {evidence_id}: {e}")
            update_evidence_status(evidence_id, "failed", error_message=str(e))

            return {
                "success": False,
                "message": f"Retry failed: {str(e)}",
                "evidence_id": evidence_id,
                "status": "failed"
            }

    def get_evidence_status(self, evidence_id: str, user_id: str) -> dict:
        """
        Get current status of evidence

        Args:
            evidence_id: Evidence ID
            user_id: User ID requesting status

        Returns:
            dict with status information

        Raises:
            NotFoundError: Evidence not found
            PermissionError: User does not have access
        """
        evidence = get_evidence_by_id(evidence_id)
        if not evidence:
            raise NotFoundError("Evidence")

        case_id = evidence["case_id"]
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        return {
            "evidence_id": evidence_id,
            "status": evidence.get("status", "unknown"),
            "error_message": evidence.get("error_message"),
            "updated_at": evidence.get("updated_at")
        }

    def review_evidence(
        self,
        case_id: str,
        evidence_id: str,
        reviewer_id: str,
        action: str,
        comment: Optional[str] = None
    ) -> EvidenceReviewResponse:
        """
        Review client-uploaded evidence (approve or reject)

        Args:
            case_id: Case ID
            evidence_id: Evidence ID
            reviewer_id: ID of the reviewer (lawyer/admin)
            action: "approve" or "reject"
            comment: Optional review comment

        Returns:
            EvidenceReviewResponse with updated review status

        Raises:
            NotFoundError: Case or evidence not found
            PermissionError: User doesn't have access to case
            ValueError: Evidence is not in pending_review state
        """
        # Check if case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Check if reviewer has access to case
        if not self.member_repo.has_access(case_id, reviewer_id):
            raise PermissionError("You do not have access to this case")

        # Get evidence from DynamoDB
        evidence = get_evidence_by_id(evidence_id)
        if not evidence:
            raise NotFoundError("Evidence")

        # Verify evidence belongs to the case
        if evidence.get("case_id") != case_id:
            raise NotFoundError("Evidence not found in this case")

        # Check if evidence is in pending_review state
        current_review_status = evidence.get("review_status")
        if current_review_status != "pending_review":
            raise ValueError(f"Evidence cannot be reviewed. Current review_status: {current_review_status}")

        # Determine new review_status
        new_review_status = "approved" if action == "approve" else "rejected"
        reviewed_at = datetime.utcnow()

        # Update evidence in DynamoDB
        additional_fields = {
            "review_status": new_review_status,
            "reviewed_by": reviewer_id,
            "reviewed_at": reviewed_at.isoformat(),
        }
        if comment:
            additional_fields["review_comment"] = comment

        update_evidence_status(
            evidence_id=evidence_id,
            status=evidence.get("status", "pending"),  # Keep current processing status
            additional_fields=additional_fields
        )

        return EvidenceReviewResponse(
            evidence_id=evidence_id,
            case_id=case_id,
            review_status=new_review_status,
            reviewed_by=reviewer_id,
            reviewed_at=reviewed_at,
            comment=comment
        )

    # ============================================
    # Speaker Mapping Methods (015-evidence-speaker-mapping)
    # ============================================

    def update_speaker_mapping(
        self,
        evidence_id: str,
        user_id: str,
        request: SpeakerMappingUpdateRequest
    ) -> SpeakerMappingResponse:
        """
        Update speaker mapping for evidence

        Args:
            evidence_id: Evidence ID
            user_id: User ID making the update
            request: Speaker mapping update request

        Returns:
            SpeakerMappingResponse with updated mapping

        Raises:
            NotFoundError: Evidence not found
            PermissionError: User does not have access to case
            ValidationError: Invalid mapping (party not in case, too many speakers, etc.)
        """
        # Get evidence metadata from DynamoDB
        evidence = get_evidence_by_id(evidence_id)
        if not evidence:
            raise NotFoundError("Evidence")

        # Check if user has access to the case
        case_id = evidence["case_id"]
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # Get the mapping from request
        speaker_mapping = request.speaker_mapping

        # If empty, clear the mapping
        if not speaker_mapping:
            success = update_evidence_speaker_mapping(evidence_id, None, user_id)
            if not success:
                raise ValidationError("화자 매핑 삭제에 실패했습니다")

            # Log audit event for clearing speaker mapping
            log_audit_event(
                db=self.db,
                user_id=user_id,
                action=AuditAction.SPEAKER_MAPPING_UPDATE,
                object_id=evidence_id
            )
            self.db.commit()
            logger.info(f"Speaker mapping cleared for evidence {evidence_id} by user {user_id}")

            return SpeakerMappingResponse(
                evidence_id=evidence_id,
                speaker_mapping=None,
                updated_at=datetime.utcnow(),
                updated_by=user_id
            )

        # Validate speaker mapping
        self._validate_speaker_mapping(speaker_mapping, case_id)

        # Convert SpeakerMappingItem to dict for DynamoDB storage
        mapping_dict = {
            label: {"party_id": item.party_id, "party_name": item.party_name}
            for label, item in speaker_mapping.items()
        }

        # Update in DynamoDB
        success = update_evidence_speaker_mapping(evidence_id, mapping_dict, user_id)
        if not success:
            raise ValidationError("화자 매핑 저장에 실패했습니다")

        # Log audit event for speaker mapping update
        log_audit_event(
            db=self.db,
            user_id=user_id,
            action=AuditAction.SPEAKER_MAPPING_UPDATE,
            object_id=evidence_id
        )
        self.db.commit()
        logger.info(f"Speaker mapping updated for evidence {evidence_id} by user {user_id}")

        return SpeakerMappingResponse(
            evidence_id=evidence_id,
            speaker_mapping=speaker_mapping,
            updated_at=datetime.utcnow(),
            updated_by=user_id
        )

    def _validate_speaker_mapping(
        self,
        speaker_mapping: Dict[str, SpeakerMappingItem],
        case_id: str
    ) -> None:
        """
        Validate speaker mapping data

        Args:
            speaker_mapping: Speaker mapping to validate
            case_id: Case ID for party validation

        Raises:
            ValidationError: If validation fails
        """
        # Check max speakers
        if len(speaker_mapping) > self.MAX_SPEAKERS:
            raise ValidationError(
                f"화자는 최대 {self.MAX_SPEAKERS}명까지 매핑 가능합니다"
            )

        # Collect all party IDs for batch validation
        party_ids = set()

        for label, item in speaker_mapping.items():
            # Check label length
            if len(label) > self.MAX_SPEAKER_LABEL_LENGTH:
                raise ValidationError(
                    f"화자명은 {self.MAX_SPEAKER_LABEL_LENGTH}자 이하여야 합니다"
                )

            party_ids.add(item.party_id)

        # Validate all party IDs belong to this case (Case Isolation)
        for party_id in party_ids:
            party = self.party_repo.get_by_id(party_id)
            if not party:
                raise ValidationError(
                    f"인물 '{party_id}'을(를) 찾을 수 없습니다"
                )
            if party.case_id != case_id:
                raise ValidationError(
                    "선택한 인물이 이 사건에 속하지 않습니다"
                )
