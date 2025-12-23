"""
Unit tests for FactSummaryService speaker mapping prompt injection
015-evidence-speaker-mapping: T018, T019
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.fact_summary_service import FactSummaryService


class TestBuildGenerationPromptWithSpeakerMapping:
    """Unit tests for _build_generation_prompt with speaker mapping"""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create FactSummaryService with mocked dependencies"""
        with patch.object(FactSummaryService, '__init__', lambda self, db: None):
            service = FactSummaryService.__new__(FactSummaryService)
            service.db = mock_db
            service.case_repo = MagicMock()
            service.member_repo = MagicMock()
            return service

    def test_prompt_includes_speaker_mapping(self, service):
        """T018: Prompt should include speaker mapping when available"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "카카오톡 대화에서 '나'가 '상대방'에게 폭언을 했다.",
                "labels": ["폭언"],
                "speaker_mapping": {
                    "나": {"party_id": "party_001", "party_name": "김동우"},
                    "상대방": {"party_id": "party_002", "party_name": "김도연"},
                }
            }
        ]

        messages = service._build_generation_prompt(evidence_list, "이혼 소송")

        # Find user message
        user_message = next(m for m in messages if m["role"] == "user")

        # Should include speaker mapping info
        assert "[화자 정보: 나=김동우, 상대방=김도연]" in user_message["content"] or \
               "[화자 정보: 상대방=김도연, 나=김동우]" in user_message["content"]

    def test_prompt_without_speaker_mapping_backward_compat(self, service):
        """T019: Prompt should work without speaker mapping (backward compatibility)"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "카카오톡 대화에서 폭언이 있었다.",
                "labels": ["폭언"],
                # No speaker_mapping field
            }
        ]

        messages = service._build_generation_prompt(evidence_list, "이혼 소송")

        # Should still work without speaker mapping
        user_message = next(m for m in messages if m["role"] == "user")
        assert "[증거1]" in user_message["content"]
        assert "폭언" in user_message["content"]

        # Should NOT include speaker mapping info
        assert "[화자 정보:" not in user_message["content"]

    def test_prompt_with_empty_speaker_mapping(self, service):
        """Empty speaker mapping should not add info"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "카카오톡 대화 내용",
                "speaker_mapping": {}  # Empty mapping
            }
        ]

        messages = service._build_generation_prompt(evidence_list, "이혼 소송")
        user_message = next(m for m in messages if m["role"] == "user")

        # Empty mapping should not add speaker info
        assert "[화자 정보:" not in user_message["content"]

    def test_prompt_with_none_speaker_mapping(self, service):
        """None speaker mapping should not add info"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "카카오톡 대화 내용",
                "speaker_mapping": None
            }
        ]

        messages = service._build_generation_prompt(evidence_list, "이혼 소송")
        user_message = next(m for m in messages if m["role"] == "user")

        assert "[화자 정보:" not in user_message["content"]

    def test_system_prompt_includes_speaker_mapping_instruction(self, service):
        """System prompt should include instruction to use speaker mapping"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "대화 내용",
            }
        ]

        messages = service._build_generation_prompt(evidence_list, "테스트")
        system_message = next(m for m in messages if m["role"] == "system")

        # Should include instruction about using speaker mapping
        assert "[화자 정보]" in system_message["content"]
        assert "실제 인물 이름" in system_message["content"]

    def test_prompt_multiple_evidence_mixed_mapping(self, service):
        """Handle multiple evidence items with mixed speaker mapping status"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "첫 번째 증거 (매핑 있음)",
                "speaker_mapping": {
                    "나": {"party_id": "party_001", "party_name": "김동우"},
                }
            },
            {
                "evidence_id": "evt_002",
                "type": "audio",
                "timestamp": "2024-01-16T10:00:00Z",
                "ai_summary": "두 번째 증거 (매핑 없음)",
                # No speaker_mapping
            },
            {
                "evidence_id": "evt_003",
                "type": "image",
                "timestamp": "2024-01-17T10:00:00Z",
                "ai_summary": "세 번째 증거 (다른 매핑)",
                "speaker_mapping": {
                    "상대방": {"party_id": "party_002", "party_name": "김도연"},
                }
            },
        ]

        messages = service._build_generation_prompt(evidence_list, "테스트")
        user_message = next(m for m in messages if m["role"] == "user")

        # First evidence should have speaker info
        assert "나=김동우" in user_message["content"]

        # Third evidence should have its speaker info
        assert "상대방=김도연" in user_message["content"]

        # All three evidence items should be present
        assert "[증거1]" in user_message["content"]
        assert "[증거2]" in user_message["content"]
        assert "[증거3]" in user_message["content"]

    def test_prompt_speaker_mapping_with_invalid_item_format(self, service):
        """Handle malformed speaker mapping gracefully"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "테스트",
                "speaker_mapping": {
                    "나": "invalid_string_value",  # Should be dict, not string
                    "상대방": {"party_id": "party_002", "party_name": "김도연"},
                }
            }
        ]

        # Should not raise, gracefully handle malformed data
        messages = service._build_generation_prompt(evidence_list, "테스트")
        user_message = next(m for m in messages if m["role"] == "user")

        # Only valid mapping should be included
        assert "상대방=김도연" in user_message["content"]

    def test_prompt_speaker_mapping_missing_party_name(self, service):
        """Handle speaker mapping with missing party_name"""
        evidence_list = [
            {
                "evidence_id": "evt_001",
                "type": "image",
                "timestamp": "2024-01-15T10:00:00Z",
                "ai_summary": "테스트",
                "speaker_mapping": {
                    "나": {"party_id": "party_001"},  # Missing party_name
                    "상대방": {"party_id": "party_002", "party_name": "김도연"},
                }
            }
        ]

        messages = service._build_generation_prompt(evidence_list, "테스트")
        user_message = next(m for m in messages if m["role"] == "user")

        # Only mapping with party_name should be included
        assert "상대방=김도연" in user_message["content"]
        # "나" mapping without party_name should be skipped
        assert "나=" not in user_message["content"]
