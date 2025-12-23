"""
Google Gemini API utilities for Draft generation

Gemini 2.0 Flash for fast, reliable legal document generation.
"""

import logging
from typing import List, Dict, Optional
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

# Gemini API endpoint
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def generate_chat_completion_gemini(
    messages: List[Dict[str, str]],
    model: str = "gemini-2.0-flash",
    temperature: float = 0.3,
    max_tokens: int = 4000
) -> str:
    """
    Generate chat completion using Google Gemini model

    Args:
        messages: List of message dicts with 'role' and 'content'
                  (OpenAI format - will be converted to Gemini format)
        model: Model name (default: gemini-2.0-flash)
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text response

    Raises:
        ValueError: If API key is not configured
        requests.RequestException: If API call fails
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Please set it in your environment variables."
        )

    # Convert OpenAI message format to Gemini format
    gemini_contents = _convert_messages_to_gemini_format(messages)

    url = f"{GEMINI_API_BASE}/models/{model}:generateContent"
    params = {"key": settings.GEMINI_API_KEY}

    payload = {
        "contents": gemini_contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "topP": 0.95,
            "topK": 40
        }
    }

    try:
        logger.info(f"Calling Gemini API with model={model}")

        response = requests.post(
            url,
            params=params,
            json=payload,
            timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS
        )

        if response.status_code != 200:
            error_msg = response.json().get("error", {}).get("message", response.text)
            logger.error(f"Gemini API error: {response.status_code} - {error_msg}")
            raise ValueError(f"Gemini API error: {error_msg}")

        result = response.json()
        candidates = result.get("candidates", [])

        if not candidates:
            raise ValueError("Gemini API returned no candidates")

        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        if not text:
            raise ValueError("Gemini API returned empty response")

        # Log token usage if available
        usage = result.get("usageMetadata", {})
        if usage:
            logger.info(
                f"Gemini response received, tokens: "
                f"prompt={usage.get('promptTokenCount', 'N/A')}, "
                f"output={usage.get('candidatesTokenCount', 'N/A')}"
            )
        else:
            logger.info(f"Gemini response received, length: {len(text)} chars")

        return text

    except requests.Timeout:
        logger.error(f"Gemini API timeout after {settings.LLM_REQUEST_TIMEOUT_SECONDS}s")
        raise
    except requests.RequestException as e:
        logger.error(f"Gemini API request error: {e}")
        raise
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


def _convert_messages_to_gemini_format(messages: List[Dict[str, str]]) -> List[Dict]:
    """
    Convert OpenAI message format to Gemini format

    OpenAI format:
        [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]

    Gemini format:
        [{"role": "user", "parts": [{"text": "..."}]}]

    Note: Gemini doesn't have a "system" role, so we prepend it to the first user message
    """
    gemini_contents = []
    system_content = ""

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            # Gemini doesn't support system role, save for prepending
            system_content = content
        elif role == "user":
            # Prepend system content to first user message
            if system_content:
                content = f"{system_content}\n\n---\n\n{content}"
                system_content = ""

            gemini_contents.append({
                "role": "user",
                "parts": [{"text": content}]
            })
        elif role == "assistant":
            gemini_contents.append({
                "role": "model",
                "parts": [{"text": content}]
            })

    return gemini_contents
