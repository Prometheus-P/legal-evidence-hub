"""
Unit tests for PromptBuilder Service
TDD - Improving test coverage for prompt_builder.py
"""

from unittest.mock import patch, MagicMock
from app.services.prompt_builder import PromptBuilder, get_prompt_builder


class TestPromptBuilderInit:
    """Unit tests for PromptBuilder initialization"""

    def test_init_without_rag_orchestrator(self):
        """Creates default RAGOrchestrator if none provided"""
        with patch('app.services.prompt_builder.RAGOrchestrator') as mock_rag:
            mock_rag_instance = MagicMock()
            mock_rag.return_value = mock_rag_instance

            builder = PromptBuilder()

            assert builder.rag == mock_rag_instance
            mock_rag.assert_called_once()

    def test_init_with_rag_orchestrator(self):
        """Uses provided RAGOrchestrator"""
        mock_rag = MagicMock()

        builder = PromptBuilder(rag_orchestrator=mock_rag)

        assert builder.rag == mock_rag


class TestBuildDraftPrompt:
    """Unit tests for build_draft_prompt method"""

    @patch('app.services.prompt_builder.get_template_schema_for_prompt')
    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_draft_prompt_with_json_schema(self, mock_rag_class, mock_template):
        """Builds JSON output prompt when template schema available"""
        mock_rag = MagicMock()
        mock_rag.format_evidence_context.return_value = "증거 컨텍스트"
        mock_rag.format_legal_context.return_value = "법률 컨텍스트"
        mock_rag_class.return_value = mock_rag
        mock_template.return_value = '{"type": "object"}'  # Schema exists

        mock_case = MagicMock()
        mock_case.title = "테스트 케이스"
        mock_case.description = "테스트 설명"

        builder = PromptBuilder()
        messages = builder.build_draft_prompt(
            case=mock_case,
            sections=["청구취지", "청구원인"],
            evidence_context=[{"id": "1"}],
            legal_context=[{"article": "840조"}]
        )

        # Should return system and user messages
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

        # JSON mode should be mentioned in system message
        assert "JSON" in messages[0]["content"]
        assert "스키마" in messages[0]["content"]

        # User message should request JSON
        assert "JSON" in messages[1]["content"]

    @patch('app.services.prompt_builder.get_template_schema_for_prompt')
    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_draft_prompt_without_json_schema(self, mock_rag_class, mock_template):
        """Builds plain text prompt when no template schema"""
        mock_rag = MagicMock()
        mock_rag.format_evidence_context.return_value = "증거 컨텍스트"
        mock_rag.format_legal_context.return_value = "법률 컨텍스트"
        mock_rag_class.return_value = mock_rag
        mock_template.return_value = None  # No schema

        mock_case = MagicMock()
        mock_case.title = "테스트 케이스"
        mock_case.description = None  # Test None description

        builder = PromptBuilder()
        messages = builder.build_draft_prompt(
            case=mock_case,
            sections=["청구취지"],
            evidence_context=[],
            legal_context=[]
        )

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

        # Plain text mode
        assert "마크다운" in messages[0]["content"]
        assert "소장 초안을 작성해 주세요" in messages[1]["content"]

    @patch('app.services.prompt_builder.get_template_schema_for_prompt')
    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_draft_prompt_formats_context(self, mock_rag_class, mock_template):
        """Calls RAGOrchestrator to format contexts"""
        mock_rag = MagicMock()
        mock_rag.format_evidence_context.return_value = "formatted_evidence"
        mock_rag.format_legal_context.return_value = "formatted_legal"
        mock_rag_class.return_value = mock_rag
        mock_template.return_value = None

        mock_case = MagicMock()
        mock_case.title = "테스트"
        mock_case.description = "설명"

        evidence = [{"id": "ev1"}, {"id": "ev2"}]
        legal = [{"article": "840"}]

        builder = PromptBuilder()
        messages = builder.build_draft_prompt(
            case=mock_case,
            sections=["청구원인"],
            evidence_context=evidence,
            legal_context=legal
        )

        # Should call formatters
        mock_rag.format_evidence_context.assert_called_once_with(evidence)
        mock_rag.format_legal_context.assert_called_once_with(legal)

        # Formatted content should appear in user message
        assert "formatted_evidence" in messages[1]["content"]
        assert "formatted_legal" in messages[1]["content"]

    @patch('app.services.prompt_builder.get_template_schema_for_prompt')
    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_draft_prompt_includes_sections(self, mock_rag_class, mock_template):
        """Includes requested sections in user message"""
        mock_rag = MagicMock()
        mock_rag.format_evidence_context.return_value = ""
        mock_rag.format_legal_context.return_value = ""
        mock_rag_class.return_value = mock_rag
        mock_template.return_value = None

        mock_case = MagicMock()
        mock_case.title = "케이스"
        mock_case.description = "설명"

        sections = ["청구취지", "청구원인", "입증방법"]

        builder = PromptBuilder()
        messages = builder.build_draft_prompt(
            case=mock_case,
            sections=sections,
            evidence_context=[],
            legal_context=[]
        )

        # All sections should appear in user message
        for section in sections:
            assert section in messages[1]["content"]

    @patch('app.services.prompt_builder.get_template_schema_for_prompt')
    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_draft_prompt_includes_language_and_style(self, mock_rag_class, mock_template):
        """Includes language and style parameters"""
        mock_rag = MagicMock()
        mock_rag.format_evidence_context.return_value = ""
        mock_rag.format_legal_context.return_value = ""
        mock_rag_class.return_value = mock_rag
        mock_template.return_value = None

        mock_case = MagicMock()
        mock_case.title = "케이스"
        mock_case.description = "설명"

        builder = PromptBuilder()
        messages = builder.build_draft_prompt(
            case=mock_case,
            sections=["청구취지"],
            evidence_context=[],
            legal_context=[],
            language="en",
            style="informal"
        )

        # Language and style should appear in user message
        assert "en" in messages[1]["content"]
        assert "informal" in messages[1]["content"]


class TestBuildSystemMessage:
    """Unit tests for _build_system_message method"""

    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_system_message_json_mode(self, mock_rag_class):
        """Builds JSON-specific system message"""
        mock_rag_class.return_value = MagicMock()

        builder = PromptBuilder()
        message = builder._build_system_message(
            template_schema='{"type": "object"}',
            use_json_output=True
        )

        assert message["role"] == "system"
        assert "JSON 스키마" in message["content"]
        assert '{"type": "object"}' in message["content"]

    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_system_message_text_mode(self, mock_rag_class):
        """Builds text-specific system message"""
        mock_rag_class.return_value = MagicMock()

        builder = PromptBuilder()
        message = builder._build_system_message(
            template_schema=None,
            use_json_output=False
        )

        assert message["role"] == "system"
        assert "마크다운" in message["content"]
        assert "소장 구조" in message["content"]

    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_system_message_includes_principles(self, mock_rag_class):
        """System message includes core principles"""
        mock_rag_class.return_value = MagicMock()

        builder = PromptBuilder()

        # Test both modes
        for use_json in [True, False]:
            message = builder._build_system_message(
                template_schema='{}' if use_json else None,
                use_json_output=use_json
            )

            # Core principles should be in both modes
            assert "핵심 원칙" in message["content"]
            assert "증거" in message["content"]
            assert "AI 생성 초안" in message["content"]


class TestBuildUserMessage:
    """Unit tests for _build_user_message method"""

    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_user_message_json_mode(self, mock_rag_class):
        """Builds JSON-specific user message"""
        mock_rag_class.return_value = MagicMock()

        mock_case = MagicMock()
        mock_case.title = "테스트 사건"
        mock_case.description = "사건 설명"

        builder = PromptBuilder()
        message = builder._build_user_message(
            case=mock_case,
            sections=["청구취지"],
            evidence_context_str="증거 내용",
            legal_context_str="법률 내용",
            language="ko",
            style="formal",
            use_json_output=True
        )

        assert message["role"] == "user"
        assert "테스트 사건" in message["content"]
        assert "사건 설명" in message["content"]
        assert "JSON 형식" in message["content"]
        assert "JSON 외의 텍스트는 출력하지 마세요" in message["content"]

    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_user_message_text_mode(self, mock_rag_class):
        """Builds text-specific user message"""
        mock_rag_class.return_value = MagicMock()

        mock_case = MagicMock()
        mock_case.title = "테스트 사건"
        mock_case.description = "사건 설명"

        builder = PromptBuilder()
        message = builder._build_user_message(
            case=mock_case,
            sections=["청구원인"],
            evidence_context_str="증거",
            legal_context_str="법률",
            language="ko",
            style="formal",
            use_json_output=False
        )

        assert message["role"] == "user"
        assert "테스트 사건" in message["content"]
        assert "소장 초안을 작성해 주세요" in message["content"]
        assert "[갑 제1호증]" in message["content"]

    @patch('app.services.prompt_builder.RAGOrchestrator')
    def test_build_user_message_none_description(self, mock_rag_class):
        """Handles None description gracefully"""
        mock_rag_class.return_value = MagicMock()

        mock_case = MagicMock()
        mock_case.title = "제목"
        mock_case.description = None

        builder = PromptBuilder()
        message = builder._build_user_message(
            case=mock_case,
            sections=["청구취지"],
            evidence_context_str="",
            legal_context_str="",
            language="ko",
            style="formal",
            use_json_output=False
        )

        assert "N/A" in message["content"]


class TestGetPromptBuilder:
    """Unit tests for get_prompt_builder singleton function"""

    def test_get_prompt_builder_returns_instance(self):
        """Returns PromptBuilder instance"""
        with patch('app.services.prompt_builder.RAGOrchestrator'):
            # Reset singleton
            import app.services.prompt_builder as module
            module._prompt_builder = None

            result = get_prompt_builder()

            assert isinstance(result, PromptBuilder)

    def test_get_prompt_builder_returns_same_instance(self):
        """Returns same instance on multiple calls (singleton)"""
        with patch('app.services.prompt_builder.RAGOrchestrator'):
            import app.services.prompt_builder as module
            module._prompt_builder = None

            result1 = get_prompt_builder()
            result2 = get_prompt_builder()

            assert result1 is result2
