"""
Keypoint Extractor - LSSP 핵심 쟁점 추출 모듈

증거 청크에서 법적 쟁점(Keypoint)을 자동 추출합니다.

핵심 기능:
- 증거 텍스트에서 핵심 쟁점 식별
- 법적 근거(민법 840조 등)와 자동 매핑
- 신뢰도 점수 계산
- 증거 인용/요약 추출

Note:
    프롬프트 설정은 config/prompts/keypoint.yaml에서 관리
    카테고리-코드 매핑은 config/prompts/keypoint.yaml의 category_to_ground_code에서 관리
"""

import json
import logging
import os
from typing import List, Optional, Dict

from openai import OpenAI

from src.schemas import (
    EvidenceChunk,
    LegalCategory,
)
from src.schemas.keypoint import (
    Keypoint,
    KeypointSource,
    EvidenceExtract,
    EvidenceExtractType,
    KeypointExtractionResult,
)
from config import ConfigLoader

logger = logging.getLogger(__name__)


def _get_category_to_ground_code() -> Dict[LegalCategory, str]:
    """YAML 설정에서 카테고리-코드 매핑 로드"""
    prompts = ConfigLoader.load("prompts/keypoint")
    mapping = prompts.get("category_to_ground_code", {})

    # YAML 키 → LegalCategory 매핑
    category_name_mapping = {
        "adultery": LegalCategory.ADULTERY,
        "desertion": LegalCategory.DESERTION,
        "mistreatment_by_inlaws": LegalCategory.MISTREATMENT_BY_INLAWS,
        "harm_to_own_parents": LegalCategory.HARM_TO_OWN_PARENTS,
        "unknown_whereabouts": LegalCategory.UNKNOWN_WHEREABOUTS,
        "irreconcilable_differences": LegalCategory.IRRECONCILABLE_DIFFERENCES,
        "domestic_violence": LegalCategory.DOMESTIC_VIOLENCE,
        "financial_misconduct": LegalCategory.FINANCIAL_MISCONDUCT,
        "general": LegalCategory.GENERAL,
    }

    result = {}
    for yaml_key, category_enum in category_name_mapping.items():
        if yaml_key in mapping:
            result[category_enum] = mapping[yaml_key]
        else:
            # 기본값
            result[category_enum] = "840-6"

    return result


def _get_tone_guidelines() -> str:
    """YAML 설정에서 톤 가이드라인 로드"""
    prompts = ConfigLoader.load("prompts/tone_guidelines")
    return prompts.get("objective_tone_guidelines", "")


def _get_system_prompt() -> str:
    """YAML 설정에서 시스템 프롬프트 로드"""
    prompts = ConfigLoader.load("prompts/keypoint")
    return prompts.get("system_prompt", "")


def _get_user_prompt() -> str:
    """YAML 설정에서 사용자 프롬프트 로드"""
    prompts = ConfigLoader.load("prompts/keypoint")
    return prompts.get("user_prompt", "")


def _get_confidence_mapping() -> Dict[int, float]:
    """YAML 설정에서 신뢰도 레벨 매핑 로드"""
    prompts = ConfigLoader.load("prompts/keypoint")
    return prompts.get("confidence_level_mapping", {1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.95})


# 법적 카테고리 → 법적 근거 코드 매핑 (하위 호환성 유지)
CATEGORY_TO_GROUND_CODE = _get_category_to_ground_code() or {
    LegalCategory.ADULTERY: "840-1",
    LegalCategory.DESERTION: "840-2",
    LegalCategory.MISTREATMENT_BY_INLAWS: "840-3",
    LegalCategory.HARM_TO_OWN_PARENTS: "840-4",
    LegalCategory.UNKNOWN_WHEREABOUTS: "840-5",
    LegalCategory.IRRECONCILABLE_DIFFERENCES: "840-6",
    LegalCategory.DOMESTIC_VIOLENCE: "DOMESTIC_VIOLENCE",
    LegalCategory.FINANCIAL_MISCONDUCT: "FINANCIAL",
    LegalCategory.GENERAL: "840-6",
}

# 시스템/유저 프롬프트 (하위 호환성 유지, 실제로는 YAML에서 로드)
KEYPOINT_EXTRACTION_SYSTEM_PROMPT = _get_system_prompt() or """당신은 이혼 소송 전문 법률 AI 분석가입니다.
제공된 증거 텍스트에서 법적으로 의미 있는 핵심 쟁점(Keypoint)을 추출합니다.
"""

KEYPOINT_EXTRACTION_USER_PROMPT = _get_user_prompt() or """다음 증거에서 핵심 쟁점을 추출하세요.

## 증거 정보
- 증거 ID: {evidence_id}
- 파일명: {filename}
- 유형: {evidence_type}

## 증거 내용
{evidence_text}

JSON 형식으로 응답하세요."""


class KeypointExtractor:
    """
    LSSP 핵심 쟁점 추출기
    
    증거 청크에서 법적 쟁점을 자동 추출하고 법적 근거와 매핑합니다.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Args:
            openai_api_key: OpenAI API 키 (없으면 환경변수에서 로드)
        """
        self.api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    
    def extract_from_chunk(
        self,
        chunk: EvidenceChunk,
        use_existing_analysis: bool = True
    ) -> List[Keypoint]:
        """
        단일 증거 청크에서 핵심 쟁점 추출
        
        Args:
            chunk: 분석할 증거 청크
            use_existing_analysis: 기존 법적 분석 결과 활용 여부
        
        Returns:
            추출된 Keypoint 리스트
        """
        keypoints = []
        
        # 1. 기존 분석 결과에서 빠른 추출 (있는 경우)
        if use_existing_analysis and chunk.legal_analysis:
            keypoint = self._from_legal_analysis(chunk)
            if keypoint:
                keypoints.append(keypoint)
        
        # 2. GPT 기반 상세 추출
        gpt_keypoints = self._extract_with_gpt(chunk)
        keypoints.extend(gpt_keypoints)
        
        # 3. 중복 제거 및 병합
        return self._deduplicate_keypoints(keypoints)
    
    def extract_from_chunks(
        self,
        chunks: List[EvidenceChunk],
        batch_size: int = 5
    ) -> KeypointExtractionResult:
        """
        여러 증거 청크에서 핵심 쟁점 일괄 추출
        
        Args:
            chunks: 분석할 증거 청크 리스트
            batch_size: 배치 처리 크기
        
        Returns:
            KeypointExtractionResult
        """
        all_keypoints = []
        
        for chunk in chunks:
            try:
                keypoints = self.extract_from_chunk(chunk)
                all_keypoints.extend(keypoints)
            except Exception as e:
                logger.error(f"청크 {chunk.chunk_id} 추출 실패: {e}")
                continue
        
        # 전체 결과에서 중복 제거 및 병합
        merged_keypoints = self._deduplicate_keypoints(all_keypoints)
        
        return KeypointExtractionResult(
            keypoints=merged_keypoints,
            total_evidence_processed=len(chunks),
            extraction_summary=f"{len(chunks)}개 증거에서 {len(merged_keypoints)}개 핵심 쟁점 추출"
        )
    
    def _from_legal_analysis(self, chunk: EvidenceChunk) -> Optional[Keypoint]:
        """기존 LegalAnalysis에서 Keypoint 빠른 생성"""
        analysis = chunk.legal_analysis
        if not analysis or not analysis.reasoning:
            return None
        
        # 법적 카테고리 → 법적 근거 코드
        ground_code = CATEGORY_TO_GROUND_CODE.get(
            analysis.primary_category,
            "840-6"
        )
        
        # 신뢰도 레벨 → 점수 변환 (YAML 설정에서 로드)
        confidence_map = _get_confidence_mapping()
        confidence_score = confidence_map.get(
            analysis.confidence_level.value if hasattr(analysis.confidence_level, 'value')
            else int(analysis.confidence_level),
            0.5
        )
        
        return Keypoint(
            statement=analysis.reasoning,
            confidence_score=confidence_score,
            source=KeypointSource.AI_EXTRACTED,
            evidence_extracts=[
                EvidenceExtract(
                    evidence_id=chunk.file_id,
                    extract_type=EvidenceExtractType.SUMMARY,
                    content=analysis.reasoning[:500],  # 최대 500자
                    relevance_score=confidence_score,
                    source_location=chunk.source_location.model_dump() if chunk.source_location else None,
                )
            ],
            legal_ground_codes=[ground_code],
            is_disputed=False,
        )
    
    def _extract_with_gpt(self, chunk: EvidenceChunk) -> List[Keypoint]:
        """GPT를 사용한 상세 쟁점 추출"""
        if not chunk.content or len(chunk.content.strip()) < 50:
            return []

        try:
            # 톤 가이드라인과 시스템 프롬프트 로드
            tone_guidelines = _get_tone_guidelines()
            system_prompt = KEYPOINT_EXTRACTION_SYSTEM_PROMPT.format(
                tone_guidelines=tone_guidelines
            )
            
            # file_type이 Enum일 때와 string일 때 모두 처리
            file_type = chunk.source_location.file_type if chunk.source_location else "unknown"
            evidence_type = file_type.value if hasattr(file_type, 'value') else str(file_type)
            
            user_prompt = KEYPOINT_EXTRACTION_USER_PROMPT.format(
                evidence_id=chunk.file_id,
                filename=chunk.source_location.file_name if chunk.source_location else "unknown",
                evidence_type=evidence_type,
                evidence_text=chunk.content[:4000]  # 토큰 제한
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000,
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._parse_gpt_response(result, chunk)
            
        except Exception as e:
            logger.error(f"GPT 추출 실패: {e}")
            return []
    
    def _parse_gpt_response(
        self,
        response: dict,
        chunk: EvidenceChunk
    ) -> List[Keypoint]:
        """GPT 응답을 Keypoint 객체로 변환"""
        keypoints = []
        
        for kp_data in response.get("keypoints", []):
            try:
                # 증거 추출 파싱
                extracts = []
                for ext_data in kp_data.get("evidence_extracts", []):
                    extract_type = EvidenceExtractType.SUMMARY
                    if ext_data.get("extract_type") == "quote":
                        extract_type = EvidenceExtractType.QUOTE
                    elif ext_data.get("extract_type") == "inference":
                        extract_type = EvidenceExtractType.INFERENCE
                    
                    extracts.append(EvidenceExtract(
                        evidence_id=chunk.file_id,
                        extract_type=extract_type,
                        content=ext_data.get("content", "")[:500],
                        relevance_score=float(ext_data.get("relevance_score", 0.5)),
                        source_location=chunk.source_location.model_dump() if chunk.source_location else None,
                    ))
                
                # Keypoint 생성
                keypoint = Keypoint(
                    statement=kp_data.get("statement", ""),
                    confidence_score=float(kp_data.get("confidence_score", 0.5)),
                    source=KeypointSource.AI_EXTRACTED,
                    evidence_extracts=extracts,
                    legal_ground_codes=kp_data.get("legal_ground_codes", []),
                    is_disputed=kp_data.get("is_disputed", False),
                    dispute_reason=kp_data.get("dispute_reason"),
                )
                keypoints.append(keypoint)
                
            except Exception as e:
                logger.warning(f"Keypoint 파싱 실패: {e}")
                continue
        
        return keypoints
    
    def _deduplicate_keypoints(self, keypoints: List[Keypoint]) -> List[Keypoint]:
        """중복 쟁점 제거 및 병합"""
        if not keypoints:
            return []
        
        # 간단한 중복 제거: statement 유사도 기반
        unique = []
        seen_statements = set()
        
        for kp in sorted(keypoints, key=lambda x: x.confidence_score, reverse=True):
            # 정규화된 statement
            normalized = kp.statement.lower().strip()[:100]
            
            if normalized not in seen_statements:
                seen_statements.add(normalized)
                unique.append(kp)
        
        return unique


def extract_keypoints_from_evidence(
    chunks: List[EvidenceChunk],
    openai_api_key: Optional[str] = None
) -> KeypointExtractionResult:
    """
    편의 함수: 증거 청크 리스트에서 핵심 쟁점 추출
    
    Args:
        chunks: 분석할 증거 청크 리스트
        openai_api_key: OpenAI API 키 (선택)
    
    Returns:
        KeypointExtractionResult
    """
    extractor = KeypointExtractor(openai_api_key)
    return extractor.extract_from_chunks(chunks)
