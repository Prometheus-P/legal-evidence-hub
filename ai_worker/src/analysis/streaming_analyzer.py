"""
Streaming Analyzer - 실시간 GPT 응답 스트리밍

GPT 응답을 실시간으로 출력하여 사용자 경험 개선

Features:
- OpenAI Streaming API 사용
- AsyncGenerator 지원
- 청크 단위 실시간 출력
- 분석 결과 누적 파싱

Usage:
    from src.analysis.streaming_analyzer import StreamingAnalyzer

    analyzer = StreamingAnalyzer()

    # 동기 스트리밍
    for chunk in analyzer.analyze_stream(evidence_chunk):
        print(chunk, end="", flush=True)

    # 비동기 스트리밍
    async for chunk in analyzer.analyze_stream_async(evidence_chunk):
        yield chunk
"""

import os
import json
import logging
from typing import Generator, AsyncGenerator, Optional
from dataclasses import dataclass

from src.schemas import (
    EvidenceChunk,
    LegalAnalysis,
    EvidenceClassification,
    classification_to_legal_analysis,
    get_system_prompt_categories,
)
from src.exceptions import AnalysisError
from src.prompts.tone_guidelines import OBJECTIVE_TONE_GUIDELINES

logger = logging.getLogger(__name__)


# 시스템 프롬프트 (ai_analyzer.py와 동일)
SYSTEM_PROMPT = """당신은 대한민국 가사소송 전문 법률 AI입니다.
주어진 메시지/증거를 분석하여 민법 제840조 이혼 사유에 해당하는지 판단합니다.

{categories}

## 신뢰도 기준 (confidence: 0.0-1.0)

- 0.0-0.2: 관련성 불확실 - 이혼 사유와 무관하거나 맥락 불명확
- 0.2-0.4: 약한 정황 - 간접적 암시, 단일 키워드만 존재
- 0.4-0.6: 의심 정황 - 의심스러운 패턴, 맥락상 가능성 있음
- 0.6-0.8: 강력한 정황 - 복수의 증거, 간접 인정 포함
- 0.8-1.0: 확정적 증거 - 직접 인정, 명백한 증거

## 출력 형식

반드시 아래 JSON 스키마를 따르세요:
{{
    "primary_ground": "부정행위|악의의유기|배우자학대|시댁학대|직계존속학대|생사불명|가정폭력|재정비행|자녀학대|약물남용|기타중대사유|무관",
    "secondary_grounds": [],
    "confidence": 0.0-1.0,
    "key_phrases": ["핵심 문구"],
    "reasoning": "분류 이유 (한국어)",
    "mentioned_entities": ["인물/장소/금액"],
    "requires_review": true/false,
    "review_reason": "검토 필요 시 이유 또는 null"
}}"""


@dataclass
class StreamingConfig:
    """스트리밍 분석기 설정"""
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 500


class StreamingAnalyzer:
    """
    실시간 스트리밍 분석기

    GPT 응답을 실시간으로 스트리밍하여 사용자 경험을 개선합니다.

    Usage:
        analyzer = StreamingAnalyzer()

        # 동기 스트리밍 (Generator)
        for chunk in analyzer.analyze_stream(evidence):
            print(chunk, end="", flush=True)

        # 비동기 스트리밍 (AsyncGenerator)
        async for chunk in analyzer.analyze_stream_async(evidence):
            await websocket.send(chunk)
    """

    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
        self._client = None
        self._async_client = None
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 생성 (톤 가이드라인 포함)"""
        categories = get_system_prompt_categories()
        base_prompt = SYSTEM_PROMPT.format(categories=categories)
        return f"{base_prompt}\n\n{OBJECTIVE_TONE_GUIDELINES}"

    def _get_client(self):
        """OpenAI 클라이언트 (lazy initialization)"""
        if self._client is None:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise AnalysisError(
                        "OPENAI_API_KEY 환경변수가 설정되지 않았습니다",
                        analysis_type="streaming",
                        fallback_available=False
                    )
                self._client = OpenAI(api_key=api_key)
            except ImportError:
                raise AnalysisError(
                    "OpenAI 패키지가 설치되지 않았습니다. pip install openai",
                    analysis_type="streaming",
                    fallback_available=False
                )
        return self._client

    def _get_async_client(self):
        """AsyncOpenAI 클라이언트 (lazy initialization)"""
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise AnalysisError(
                        "OPENAI_API_KEY 환경변수가 설정되지 않았습니다",
                        analysis_type="streaming",
                        fallback_available=False
                    )
                self._async_client = AsyncOpenAI(api_key=api_key)
            except ImportError:
                raise AnalysisError(
                    "OpenAI 패키지가 설치되지 않았습니다. pip install openai",
                    analysis_type="streaming",
                    fallback_available=False
                )
        return self._async_client

    def _build_user_prompt(self, chunk: EvidenceChunk) -> str:
        """사용자 프롬프트 생성"""
        parts = ["다음 메시지를 분석해주세요:\n"]

        # 메시지 내용
        parts.append(f"## 메시지 내용\n{chunk.content}\n")

        # 컨텍스트 정보
        context_parts = []
        if chunk.sender:
            context_parts.append(f"- 발신자: {chunk.sender}")
        if chunk.timestamp:
            context_parts.append(f"- 시간: {chunk.timestamp}")
        if chunk.source_location:
            context_parts.append(f"- 출처: {chunk.source_location.to_citation()}")

        if context_parts:
            parts.append("## 컨텍스트\n" + "\n".join(context_parts))

        return "\n".join(parts)

    def analyze_stream(
        self,
        chunk: EvidenceChunk
    ) -> Generator[str, None, LegalAnalysis]:
        """
        동기 스트리밍 분석

        Args:
            chunk: 분석할 증거 청크

        Yields:
            str: 응답 텍스트 청크

        Returns:
            LegalAnalysis: 최종 분석 결과
        """
        client = self._get_client()
        user_prompt = self._build_user_prompt(chunk)

        try:
            stream = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
                response_format={"type": "json_object"}
            )

            full_response = ""
            for response_chunk in stream:
                if response_chunk.choices[0].delta.content:
                    content = response_chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # 최종 결과 파싱
            return self._parse_response(full_response)

        except Exception as e:
            logger.error(f"스트리밍 분석 실패: {e}")
            raise AnalysisError(
                f"스트리밍 분석 실패: {e}",
                analysis_type="streaming",
                fallback_available=True
            )

    async def analyze_stream_async(
        self,
        chunk: EvidenceChunk
    ) -> AsyncGenerator[str, None]:
        """
        비동기 스트리밍 분석

        Args:
            chunk: 분석할 증거 청크

        Yields:
            str: 응답 텍스트 청크

        Note:
            최종 LegalAnalysis를 얻으려면 analyze_async() 사용
        """
        client = self._get_async_client()
        user_prompt = self._build_user_prompt(chunk)

        try:
            stream = await client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
                response_format={"type": "json_object"}
            )

            async for response_chunk in stream:
                if response_chunk.choices[0].delta.content:
                    yield response_chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"비동기 스트리밍 실패: {e}")
            raise AnalysisError(
                f"비동기 스트리밍 실패: {e}",
                analysis_type="streaming",
                fallback_available=True
            )

    async def analyze_async(self, chunk: EvidenceChunk) -> LegalAnalysis:
        """
        비동기 분석 (스트리밍 + 결과 반환)

        Args:
            chunk: 분석할 증거 청크

        Returns:
            LegalAnalysis: 분석 결과
        """
        full_response = ""
        async for content in self.analyze_stream_async(chunk):
            full_response += content

        return self._parse_response(full_response)

    def analyze_with_callback(
        self,
        chunk: EvidenceChunk,
        on_chunk: callable,
        on_complete: Optional[callable] = None
    ) -> LegalAnalysis:
        """
        콜백 기반 스트리밍 분석

        Args:
            chunk: 분석할 증거 청크
            on_chunk: 청크 수신 시 호출될 콜백 (content: str) -> None
            on_complete: 완료 시 호출될 콜백 (analysis: LegalAnalysis) -> None

        Returns:
            LegalAnalysis: 분석 결과
        """
        full_response = ""

        for content in self.analyze_stream(chunk):
            full_response += content
            on_chunk(content)

        analysis = self._parse_response(full_response)

        if on_complete:
            on_complete(analysis)

        return analysis

    def _parse_response(self, response: str) -> LegalAnalysis:
        """
        응답 문자열을 LegalAnalysis로 파싱

        Args:
            response: JSON 응답 문자열

        Returns:
            LegalAnalysis: 파싱된 분석 결과
        """
        try:
            result_dict = json.loads(response)
            classification = EvidenceClassification.model_validate(result_dict)
            return classification_to_legal_analysis(classification)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            raise AnalysisError(
                f"응답 파싱 실패: {e}",
                analysis_type="streaming",
                fallback_available=True
            )
        except Exception as e:
            logger.error(f"분석 결과 변환 실패: {e}")
            raise AnalysisError(
                f"결과 변환 실패: {e}",
                analysis_type="streaming",
                fallback_available=True
            )


# 간편 함수
def stream_analysis(
    chunk: EvidenceChunk,
    model: str = "gpt-4o-mini"
) -> Generator[str, None, LegalAnalysis]:
    """
    단일 청크 스트리밍 분석 (간편 함수)

    Usage:
        for text in stream_analysis(chunk):
            print(text, end="", flush=True)
    """
    config = StreamingConfig(model=model)
    analyzer = StreamingAnalyzer(config=config)
    return analyzer.analyze_stream(chunk)


async def stream_analysis_async(
    chunk: EvidenceChunk,
    model: str = "gpt-4o-mini"
) -> AsyncGenerator[str, None]:
    """
    단일 청크 비동기 스트리밍 분석 (간편 함수)

    Usage:
        async for text in stream_analysis_async(chunk):
            await send(text)
    """
    config = StreamingConfig(model=model)
    analyzer = StreamingAnalyzer(config=config)
    async for content in analyzer.analyze_stream_async(chunk):
        yield content


# 모듈 export
__all__ = [
    "StreamingConfig",
    "StreamingAnalyzer",
    "stream_analysis",
    "stream_analysis_async",
]
