"""
Backend API Client for AI Worker

012-precedent-integration: T044-T047
AI Worker에서 Backend API를 호출하여 자동 추출된 인물/관계를 저장합니다.

주요 기능:
- POST /cases/{case_id}/parties/auto-extract: 자동 추출된 인물 저장
- POST /cases/{case_id}/relationships/auto-extract: 자동 추출된 관계 저장
- 재시도 로직 (3회)
- 에러 로깅 (DynamoDB)
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)


@dataclass
class AutoExtractedParty:
    """자동 추출된 인물 요청 데이터"""
    name: str
    type: str  # plaintiff, defendant, child, third_party, etc.
    extraction_confidence: float
    source_evidence_id: str
    alias: Optional[str] = None
    birth_year: Optional[int] = None
    occupation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "type": self.type,
            "extraction_confidence": self.extraction_confidence,
            "source_evidence_id": self.source_evidence_id,
        }
        if self.alias:
            data["alias"] = self.alias
        if self.birth_year:
            data["birth_year"] = self.birth_year
        if self.occupation:
            data["occupation"] = self.occupation
        return data


@dataclass
class AutoExtractedRelationship:
    """자동 추출된 관계 요청 데이터"""
    source_party_id: str
    target_party_id: str
    type: str  # marriage, affair, parent_child, sibling, etc.
    extraction_confidence: float
    evidence_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "source_party_id": self.source_party_id,
            "target_party_id": self.target_party_id,
            "type": self.type,
            "extraction_confidence": self.extraction_confidence,
        }
        if self.evidence_text:
            data["evidence_text"] = self.evidence_text
        return data


@dataclass
class PartyResponse:
    """인물 저장 응답"""
    id: str
    name: str
    is_duplicate: bool
    matched_party_id: Optional[str] = None


@dataclass
class RelationshipResponse:
    """관계 저장 응답"""
    id: str
    created: bool


class BackendAPIClient:
    """
    Backend API 클라이언트

    사용법:
        client = BackendAPIClient()
        response = client.save_auto_extracted_party(
            case_id="case_001",
            party=AutoExtractedParty(
                name="김철수",
                type="plaintiff",
                extraction_confidence=0.85,
                source_evidence_id="ev_abc123"
            )
        )
    """

    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds (doubles each retry)

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        service_token: Optional[str] = None,
    ):
        """
        Args:
            base_url: Backend API base URL (기본: 환경변수 BACKEND_API_URL)
            api_key: API 키 (기본: 환경변수 BACKEND_API_KEY)
            service_token: 서비스 간 인증 토큰 (기본: 환경변수 AI_WORKER_SERVICE_TOKEN)
        """
        self.base_url = base_url or os.getenv("BACKEND_API_URL", "http://localhost:8000/api")
        self.api_key = api_key or os.getenv("BACKEND_API_KEY", "")
        self.service_token = service_token or os.getenv("AI_WORKER_SERVICE_TOKEN", "")

        # Remove trailing slash
        self.base_url = self.base_url.rstrip("/")

        logger.info(f"BackendAPIClient initialized: {self.base_url}")

    def _get_headers(self) -> Dict[str, str]:
        """인증 헤더 생성"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "LEH-AI-Worker/1.0",
        }

        # 서비스 토큰 우선 (서비스 간 인증)
        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key

        return headers

    def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Optional[Dict]:
        """
        재시도 로직이 포함된 HTTP 요청

        Args:
            method: HTTP 메서드 (GET, POST, etc.)
            endpoint: API 엔드포인트 (예: /cases/123/parties/auto-extract)
            json_data: JSON 요청 본문
            timeout: 타임아웃 (초)

        Returns:
            응답 JSON 또는 None (실패 시)
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        last_error = None
        delay = self.RETRY_DELAY

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.debug(f"API Request [{attempt}/{self.MAX_RETRIES}]: {method} {url}")

                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    timeout=timeout,
                )

                # 성공 (2xx)
                if response.ok:
                    return response.json()

                # 클라이언트 에러 (4xx) - 재시도하지 않음
                if 400 <= response.status_code < 500:
                    logger.error(
                        f"API Client Error [{response.status_code}]: {response.text}",
                        extra={
                            "url": url,
                            "status_code": response.status_code,
                            "response": response.text[:500],
                        }
                    )
                    return None

                # 서버 에러 (5xx) - 재시도
                logger.warning(
                    f"API Server Error [{response.status_code}], retrying... ({attempt}/{self.MAX_RETRIES})"
                )
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"

            except Timeout as e:
                logger.warning(f"API Timeout, retrying... ({attempt}/{self.MAX_RETRIES})")
                last_error = f"Timeout: {e}"

            except ConnectionError as e:
                logger.warning(f"API Connection Error, retrying... ({attempt}/{self.MAX_RETRIES})")
                last_error = f"Connection Error: {e}"

            except RequestException as e:
                logger.warning(f"API Request Error, retrying... ({attempt}/{self.MAX_RETRIES})")
                last_error = f"Request Error: {e}"

            # 재시도 전 대기 (exponential backoff)
            if attempt < self.MAX_RETRIES:
                time.sleep(delay)
                delay *= 2

        # 모든 재시도 실패
        logger.error(
            f"API Request failed after {self.MAX_RETRIES} retries: {last_error}",
            extra={"url": url, "last_error": last_error}
        )
        return None

    def save_auto_extracted_party(
        self,
        case_id: str,
        party: AutoExtractedParty,
    ) -> Optional[PartyResponse]:
        """
        자동 추출된 인물 저장

        Args:
            case_id: 케이스 ID
            party: 자동 추출된 인물 데이터

        Returns:
            PartyResponse 또는 None (실패 시)
        """
        endpoint = f"/cases/{case_id}/parties/auto-extract"

        response = self._request_with_retry(
            method="POST",
            endpoint=endpoint,
            json_data=party.to_dict(),
        )

        if response:
            return PartyResponse(
                id=response.get("id", ""),
                name=response.get("name", party.name),
                is_duplicate=response.get("is_duplicate", False),
                matched_party_id=response.get("matched_party_id"),
            )

        return None

    def save_auto_extracted_relationship(
        self,
        case_id: str,
        relationship: AutoExtractedRelationship,
    ) -> Optional[RelationshipResponse]:
        """
        자동 추출된 관계 저장

        Args:
            case_id: 케이스 ID
            relationship: 자동 추출된 관계 데이터

        Returns:
            RelationshipResponse 또는 None (실패 시)
        """
        endpoint = f"/cases/{case_id}/relationships/auto-extract"

        response = self._request_with_retry(
            method="POST",
            endpoint=endpoint,
            json_data=relationship.to_dict(),
        )

        if response:
            return RelationshipResponse(
                id=response.get("id", ""),
                created=response.get("created", True),
            )

        return None

    def save_extracted_graph(
        self,
        case_id: str,
        persons: List[Dict],
        relationships: List[Dict],
        source_evidence_id: str,
        min_confidence: float = 0.7,
    ) -> Dict[str, Any]:
        """
        추출된 인물 및 관계 그래프 일괄 저장

        Args:
            case_id: 케이스 ID
            persons: PersonExtractor에서 추출된 인물 목록
            relationships: RelationshipInferrer에서 추론된 관계 목록
            source_evidence_id: 출처 증거 ID
            min_confidence: 최소 신뢰도 (기본 0.7)

        Returns:
            저장 결과 요약
        """
        result = {
            "parties_saved": 0,
            "parties_duplicates": 0,
            "parties_failed": 0,
            "relationships_saved": 0,
            "relationships_failed": 0,
            "party_id_map": {},  # name -> party_id 매핑
        }

        # 1. 인물 저장
        for person in persons:
            confidence = person.get("confidence", 0.5)
            if confidence < min_confidence:
                logger.debug(f"Skipping low-confidence party: {person.get('name')} ({confidence})")
                continue

            # PersonRole → PartyType 매핑
            role_to_type = {
                "plaintiff": "plaintiff",
                "defendant": "defendant",
                "child": "child",
                "third_party": "third_party",
                "plaintiff_parent": "third_party",
                "defendant_parent": "third_party",
                "relative": "third_party",
                "friend": "third_party",
                "colleague": "third_party",
                "witness": "third_party",
                "unknown": "third_party",
            }

            party = AutoExtractedParty(
                name=person.get("name", "Unknown"),
                type=role_to_type.get(person.get("role", "unknown"), "third_party"),
                extraction_confidence=confidence,
                source_evidence_id=source_evidence_id,
                alias=person.get("aliases", [None])[0] if person.get("aliases") else None,
            )

            response = self.save_auto_extracted_party(case_id, party)

            if response:
                result["party_id_map"][party.name] = response.id
                if response.is_duplicate:
                    result["parties_duplicates"] += 1
                    logger.info(f"Party duplicate: {party.name} -> {response.matched_party_id}")
                else:
                    result["parties_saved"] += 1
                    logger.info(f"Party saved: {party.name} -> {response.id}")
            else:
                result["parties_failed"] += 1
                logger.warning(f"Party save failed: {party.name}")

        # 2. 관계 저장 (인물 ID 매핑 필요)
        for rel in relationships:
            confidence = rel.get("confidence", 0.5)
            if confidence < min_confidence:
                logger.debug(f"Skipping low-confidence relationship: {rel.get('source')} -> {rel.get('target')} ({confidence})")
                continue

            source_name = rel.get("source", "")
            target_name = rel.get("target", "")

            # 이름으로 party_id 조회
            source_party_id = result["party_id_map"].get(source_name)
            target_party_id = result["party_id_map"].get(target_name)

            if not source_party_id or not target_party_id:
                logger.debug(f"Skipping relationship (party not found): {source_name} -> {target_name}")
                continue

            # RelationshipType 매핑
            rel_type_map = {
                "spouse": "marriage",
                "ex_spouse": "divorce",
                "parent": "parent_child",
                "child": "parent_child",
                "sibling": "sibling",
                "in_law": "in_law",
                "relative": "relative",
                "friend": "friend",
                "colleague": "colleague",
                "affair": "affair",
                "acquaintance": "other",
                "unknown": "other",
            }

            relationship_obj = AutoExtractedRelationship(
                source_party_id=source_party_id,
                target_party_id=target_party_id,
                type=rel_type_map.get(rel.get("relationship", "unknown"), "other"),
                extraction_confidence=confidence,
                evidence_text=rel.get("evidence", "")[:500] if rel.get("evidence") else None,
            )

            response = self.save_auto_extracted_relationship(case_id, relationship_obj)

            if response:
                result["relationships_saved"] += 1
                logger.info(f"Relationship saved: {source_name} -> {target_name} ({rel.get('relationship')})")
            else:
                result["relationships_failed"] += 1
                logger.warning(f"Relationship save failed: {source_name} -> {target_name}")

        logger.info(
            f"Graph save complete: {result['parties_saved']} parties, "
            f"{result['parties_duplicates']} duplicates, "
            f"{result['relationships_saved']} relationships"
        )

        return result


# ============================================
# 간편 함수
# ============================================

_default_client: Optional[BackendAPIClient] = None


def get_backend_client() -> BackendAPIClient:
    """기본 Backend API 클라이언트 인스턴스 반환"""
    global _default_client
    if _default_client is None:
        _default_client = BackendAPIClient()
    return _default_client


def save_extracted_graph_to_backend(
    case_id: str,
    persons: List[Dict],
    relationships: List[Dict],
    source_evidence_id: str,
    min_confidence: float = 0.7,
) -> Dict[str, Any]:
    """
    추출된 인물 및 관계를 Backend에 저장 (간편 함수)

    Args:
        case_id: 케이스 ID
        persons: PersonExtractor에서 추출된 인물 목록
        relationships: RelationshipInferrer에서 추론된 관계 목록
        source_evidence_id: 출처 증거 ID
        min_confidence: 최소 신뢰도 (기본 0.7)

    Returns:
        저장 결과 요약
    """
    client = get_backend_client()
    return client.save_extracted_graph(
        case_id=case_id,
        persons=persons,
        relationships=relationships,
        source_evidence_id=source_evidence_id,
        min_confidence=min_confidence,
    )
