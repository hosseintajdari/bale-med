import json
import logging
import time
from typing import Any

import httpx

from ..config import Settings
from .client import CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_USER_TEMPLATE, LLMClient

logger = logging.getLogger(__name__)


class OpenAICompatibleLLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def classify_message(self, snippet: str) -> dict[str, Any]:
        if not self.settings.bale_llm_api_base_url.strip():
            raise ValueError("BALE_LLM_API_BASE_URL is not configured")

        url = f"{self.settings.bale_llm_api_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        # Some gateways (e.g. Arvan URL-token) embed auth in the base URL.
        # Skip Bearer when key is empty or a local placeholder.
        api_key = self.settings.bale_llm_api_key.strip()
        if api_key and api_key.lower() not in {"arvan", "none", "-"}:
            headers["Authorization"] = f"Bearer {api_key}"
        body = {
            "model": self.settings.bale_llm_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": CLASSIFICATION_USER_TEMPLATE.format(snippet=snippet),
                },
            ],
        }

        with httpx.Client(timeout=self.settings.bale_llm_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()

        content = _extract_message_content(payload)
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response JSON must be an object")
        return parsed


def _extract_message_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("LLM response missing choices")

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise ValueError("LLM response missing message")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM response missing content")
    return content


def build_llm_client(settings: Settings) -> LLMClient:
    return OpenAICompatibleLLMClient(settings)


def measure_llm_call(client: LLMClient, snippet: str) -> tuple[dict[str, Any], int]:
    started = time.perf_counter()
    payload = client.classify_message(snippet)
    latency_ms = int((time.perf_counter() - started) * 1000)
    return payload, latency_ms
