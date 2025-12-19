"""
KeypointExtractor 테스트

LSSP Keypoint 추출 모듈의 단위 테스트
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from src.schemas.keypoint import (
    Keypoint,
    KeypointSource,
    EvidenceExtract,
    EvidenceExtractType,
    KeypointExtractionResult,
    LEGAL_GROUND_CODES,
)
from src.schemas import (
    EvidenceChunk,
    LegalAnalysis,
    LegalCategory,
    ConfidenceLevel,
    SourceLocation,
    FileType,
)
from src.analysis.keypoint_extractor import (
    KeypointExtractor,
    extract_keypoints_from_evidence,
    CATEGORY_TO_GROUND_CODE,
)


class TestKeypointSchemas:
    """Keypoint 스키마 테스트"""
    
    def test_evidence_extract_creation(self):
        """EvidenceExtract 생성 테스트"""
        extract = EvidenceExtract(
            evidence_id="ev-123",
            extract_type=EvidenceExtractType.QUOTE,
            content="피고가 2023년 3월부터 집에 들어오지 않았다",
            relevance_score=0.85,
            source_location="page 2",
        )
        
        assert extract.evidence_id == "ev-123"
        assert extract.extract_type == EvidenceExtractType.QUOTE
        assert extract.relevance_score == 0.85
        
        # to_dict 테스트
        d = extract.to_dict()
        assert d["extract_type"] == "quote"
        assert d["relevance_score"] == 0.85
    
    def test_keypoint_creation(self):
        """Keypoint 생성 테스트"""
        extract = EvidenceExtract(
            evidence_id="ev-123",
            extract_type=EvidenceExtractType.SUMMARY,
            content="피고의 장기 부재",
            relevance_score=0.8,
        )
        
        keypoint = Keypoint(
            statement="피고가 2023년 3월부터 정당한 사유 없이 가출하여 동거 의무를 위반함",
            confidence_score=0.85,
            source=KeypointSource.AI_EXTRACTED,
            evidence_extracts=[extract],
            legal_ground_codes=["840-2"],
            is_disputed=False,
        )
        
        assert keypoint.statement.startswith("피고가")
        assert keypoint.confidence_score == 0.85
        assert keypoint.source == KeypointSource.AI_EXTRACTED
        assert len(keypoint.evidence_extracts) == 1
        assert "840-2" in keypoint.legal_ground_codes
        
        # to_dict 테스트
        d = keypoint.to_dict()
        assert d["source"] == "ai_extracted"
        assert len(d["evidence_extracts"]) == 1
    
    def test_keypoint_extraction_result(self):
        """KeypointExtractionResult 생성 테스트"""
        kp = Keypoint(
            statement="테스트 쟁점",
            confidence_score=0.7,
            source=KeypointSource.AI_EXTRACTED,
        )
        
        result = KeypointExtractionResult(
            keypoints=[kp],
            total_evidence_processed=5,
            extraction_summary="5개 증거에서 1개 쟁점 추출",
        )
        
        assert len(result.keypoints) == 1
        assert result.total_evidence_processed == 5
        
        d = result.to_dict()
        assert len(d["keypoints"]) == 1
    
    def test_legal_ground_codes_constant(self):
        """법적 근거 코드 상수 테스트"""
        assert "840-1" in LEGAL_GROUND_CODES
        assert LEGAL_GROUND_CODES["840-1"] == "부정행위"
        assert "DOMESTIC_VIOLENCE" in LEGAL_GROUND_CODES


class TestKeypointExtractor:
    """KeypointExtractor 테스트"""
    
    @pytest.fixture
    def mock_openai(self):
        """OpenAI 클라이언트 모킹"""
        with patch('src.analysis.keypoint_extractor.OpenAI') as mock:
            yield mock
    
    @pytest.fixture
    def sample_chunk(self):
        """테스트용 EvidenceChunk"""
        text = "2023년 5월 15일, 피고는 원고에게 '이혼하자'고 말하고 집을 나갔습니다. 이후 피고는 연락을 끊고 돌아오지 않았습니다."
        import hashlib
        return EvidenceChunk(
            chunk_id="chunk-001",
            file_id="file-001",
            case_id="case-001",
            content=text,
            content_hash=hashlib.sha256(text.encode()).hexdigest(),
            source_location=SourceLocation(
                file_name="진술서.pdf",
                file_type=FileType.PDF,
                page_number=1,
            ),
        )
    
    @pytest.fixture
    def sample_chunk_with_analysis(self, sample_chunk):
        """기존 분석이 있는 EvidenceChunk"""
        sample_chunk.legal_analysis = LegalAnalysis(
            primary_category=LegalCategory.DESERTION,
            confidence_level=ConfidenceLevel.STRONG,
            reasoning="피고가 2023년 5월 가출하여 동거 의무 위반",
            matched_keywords=["가출", "유기"],
        )
        return sample_chunk
    
    def test_extractor_initialization(self, mock_openai):
        """KeypointExtractor 초기화 테스트"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = KeypointExtractor()
            assert extractor.api_key == 'test-key'
    
    def test_extractor_requires_api_key(self, mock_openai):
        """API 키 없으면 에러"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                KeypointExtractor()
    
    def test_from_legal_analysis(self, mock_openai, sample_chunk_with_analysis):
        """기존 LegalAnalysis에서 Keypoint 생성 테스트"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = KeypointExtractor()
            keypoint = extractor._from_legal_analysis(sample_chunk_with_analysis)
            
            assert keypoint is not None
            assert keypoint.statement == "피고가 2023년 5월 가출하여 동거 의무 위반"
            assert keypoint.source == KeypointSource.AI_EXTRACTED
            assert "840-2" in keypoint.legal_ground_codes  # DESERTION → 840-2
            assert keypoint.confidence_score == 0.8  # STRONG (4) → 0.8
    
    def test_extract_with_gpt_success(self, mock_openai, sample_chunk):
        """GPT 기반 추출 성공 테스트"""
        # Mock GPT 응답
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "keypoints": [
                {
                    "statement": "피고가 2023년 5월 15일 집을 나가 연락을 끊음",
                    "confidence_score": 0.85,
                    "legal_ground_codes": ["840-2"],
                    "evidence_extracts": [
                        {
                            "content": "피고는 원고에게 '이혼하자'고 말하고 집을 나갔습니다",
                            "extract_type": "quote",
                            "relevance_score": 0.9
                        }
                    ],
                    "is_disputed": False
                }
            ],
            "extraction_summary": "1개 쟁점 추출"
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = KeypointExtractor()
            keypoints = extractor._extract_with_gpt(sample_chunk)
            
            assert len(keypoints) == 1
            assert keypoints[0].statement == "피고가 2023년 5월 15일 집을 나가 연락을 끊음"
            assert keypoints[0].confidence_score == 0.85
            assert len(keypoints[0].evidence_extracts) == 1
            assert keypoints[0].evidence_extracts[0].extract_type == EvidenceExtractType.QUOTE
    
    def test_extract_with_gpt_empty_text(self, mock_openai, sample_chunk):
        """텍스트가 너무 짧으면 빈 결과 반환"""
        sample_chunk.content = "짧은 텍스트"
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = KeypointExtractor()
            keypoints = extractor._extract_with_gpt(sample_chunk)
            
            assert keypoints == []
    
    def test_deduplicate_keypoints(self, mock_openai):
        """중복 쟁점 제거 테스트"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = KeypointExtractor()
            
            keypoints = [
                Keypoint(
                    statement="피고가 가출함",
                    confidence_score=0.9,
                    source=KeypointSource.AI_EXTRACTED,
                ),
                Keypoint(
                    statement="피고가 가출함",  # 중복
                    confidence_score=0.7,
                    source=KeypointSource.AI_EXTRACTED,
                ),
                Keypoint(
                    statement="원고에게 폭력 행사",
                    confidence_score=0.8,
                    source=KeypointSource.AI_EXTRACTED,
                ),
            ]
            
            unique = extractor._deduplicate_keypoints(keypoints)
            
            assert len(unique) == 2
            # 높은 confidence 유지
            assert unique[0].confidence_score == 0.9
    
    def test_category_to_ground_code_mapping(self):
        """카테고리→법적 근거 코드 매핑 테스트"""
        assert CATEGORY_TO_GROUND_CODE[LegalCategory.ADULTERY] == "840-1"
        assert CATEGORY_TO_GROUND_CODE[LegalCategory.DESERTION] == "840-2"
        assert CATEGORY_TO_GROUND_CODE[LegalCategory.DOMESTIC_VIOLENCE] == "DOMESTIC_VIOLENCE"


class TestExtractKeypointsFromEvidence:
    """편의 함수 테스트"""
    
    def test_extract_keypoints_from_evidence(self):
        """extract_keypoints_from_evidence 함수 테스트"""
        with patch('src.analysis.keypoint_extractor.KeypointExtractor') as MockExtractor:
            mock_instance = MagicMock()
            mock_instance.extract_from_chunks.return_value = KeypointExtractionResult(
                keypoints=[],
                total_evidence_processed=0,
                extraction_summary="테스트",
            )
            MockExtractor.return_value = mock_instance
            
            result = extract_keypoints_from_evidence([], "test-key")
            
            assert isinstance(result, KeypointExtractionResult)
            mock_instance.extract_from_chunks.assert_called_once()
