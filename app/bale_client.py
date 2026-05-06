import json
from typing import Any
from urllib import error, request
from urllib.parse import urlparse

from .config import Settings, get_settings


class BaleAPIError(Exception):
    def __init__(self, error_code: int | None, description: str):
        self.error_code = error_code
        self.description = description
        super().__init__(f"Bale API error ({error_code}): {description}")


class BaleClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def _method_url(self, method_name: str) -> str:
        token = self.settings.bale_bot_token.strip()
        if not token:
            raise BaleAPIError(None, "BALE_BOT_TOKEN is not configured.")
        base = self.settings.bale_api_base_url.strip().rstrip("/")
        parsed = urlparse(base)
        if not base or not parsed.scheme or not parsed.netloc:
            raise BaleAPIError(
                None,
                "Invalid BALE_API_BASE_URL. Expected absolute URL like https://tapi.bale.ai",
            )
        return f"{base}/bot{token}/{method_name}"

    def _request_json(self, method_name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self._method_url(method_name)
        body = json.dumps(payload or {}).encode("utf-8")
        try:
            req = request.Request(
                url=url,
                data=body,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with request.urlopen(req, timeout=15) as response:
                raw = response.read().decode("utf-8")
        except ValueError as exc:
            raise BaleAPIError(None, f"Invalid Bale request URL: {exc}") from exc
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
                desc = data.get("description", f"HTTP {exc.code}")
                raise BaleAPIError(data.get("error_code", exc.code), str(desc))
            except json.JSONDecodeError:
                raise BaleAPIError(exc.code, raw or f"HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise BaleAPIError(None, f"Network error: {exc.reason}") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BaleAPIError(None, "Non-JSON response from Bale API.") from exc

        if not isinstance(data, dict):
            raise BaleAPIError(None, "Unexpected Bale API response format.")

        if data.get("ok") is False:
            raise BaleAPIError(data.get("error_code"), str(data.get("description", "Unknown Bale API error.")))

        return data

    def get_me(self) -> dict[str, Any]:
        return self._request_json("getMe")

    def send_message(
        self,
        chat_id: str | int,
        text: str,
        reply_to_message_id: str | int | None = None,
    ) -> dict[str, Any]:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("text must not be empty.")
        if len(clean_text) > 4096:
            raise ValueError("text must be 1 to 4096 characters.")

        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": clean_text,
        }
        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id

        return self._request_json("sendMessage", payload)

    def set_webhook(self, url: str) -> dict[str, Any]:
        if not url.startswith("https://"):
            raise ValueError("Webhook url must start with https://")
        return self._request_json("setWebhook", {"url": url})

    def get_webhook_info(self) -> dict[str, Any]:
        return self._request_json("getWebhookInfo")
