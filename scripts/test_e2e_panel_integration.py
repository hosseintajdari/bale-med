#!/usr/bin/env python3
"""
تست end-to-end اتصال bale-med → bale-panel (shadow emitter)

حالت‌ها:
  --mock   : بدون سرور واقعی — mock HTTP server روی پورت رندوم (پیش‌فرض)
  --live   : ارسال واقعی به bale-panel (نیاز به .env معتبر دارد)

استفاده:
  python scripts/test_e2e_panel_integration.py
  python scripts/test_e2e_panel_integration.py --live
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ─── افزودن ریشه پروژه به sys.path ──────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.shadow_emitter import (  # noqa: E402
    EmitterSettings,
    build_shadow_payload,
    emit_shadow_record,
)

# ─── رنگ‌های ANSI ──────────────────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

PASS = f"{GREEN}✔ PASS{RESET}"
FAIL = f"{RED}✗ FAIL{RESET}"
SKIP = f"{YELLOW}⊘ SKIP{RESET}"


def banner(title: str) -> None:
    line = "─" * 60
    print(f"\n{CYAN}{BOLD}{line}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{BOLD}{line}{RESET}")


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = PASS if condition else FAIL
    print(f"  {status}  {label}", end="")
    if detail:
        print(f"  {YELLOW}({detail}){RESET}", end="")
    print()
    return condition


# ─────────────────────────────────────────────────────────────────────────────
# Mock HTTP Server — دریافت POST /api/pipeline/ingest/shadow-trace
# ─────────────────────────────────────────────────────────────────────────────

class _MockHandler(BaseHTTPRequestHandler):
    """Handler ساده برای دریافت درخواست mock."""

    received: list[dict] = []
    expected_token: str = "test-secret-token"

    def log_message(self, *args):  # noqa: D401
        pass  # سکوت — خروجی تست را کثیف نمی‌کند

    def do_POST(self):  # noqa: N802
        endpoint = "/api/pipeline/ingest/shadow-trace"
        if self.path != endpoint:
            self.send_response(404)
            self.end_headers()
            return

        # بررسی Authorization
        auth = self.headers.get("Authorization", "")
        expected = f"Bearer {_MockHandler.expected_token}"
        if auth != expected:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"Unauthorized"}')
            return

        # خواندن بدنه
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
            _MockHandler.received.append(payload)
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"queued"}')
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()


def _start_mock_server(token: str) -> tuple[HTTPServer, int]:
    _MockHandler.expected_token = token
    _MockHandler.received = []
    server = HTTPServer(("127.0.0.1", 0), _MockHandler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, port


# ─────────────────────────────────────────────────────────────────────────────
# تست‌ها
# ─────────────────────────────────────────────────────────────────────────────

def run_payload_builder_tests() -> int:
    """تأیید ساختار payload بدون هیچ I/O."""
    banner("۱ — تست سازنده Payload")
    failures = 0

    ts = datetime.now(timezone.utc).isoformat()
    payload = build_shadow_payload(
        chat_id="123456",
        user_message="آموفوکسین با داروی دیابت تداخل دارد؟",
        proposed_reply="بله، لطفاً با پزشک مشورت کنید.",
        timestamp=ts,
        extracted_fields={
            "risk_flags": {"dose_interaction_mention": True},
            "needs_review": True,
        },
        deterministic_rule="interaction_mention",
        confidence_score=0.87,
    )

    si = payload.get("shadow_item", {})

    failures += 0 if check("engine_id موجود است", payload.get("engine_id") == "bale-med-v2") else 1
    failures += 0 if check("shadow_item موجود است", isinstance(si, dict)) else 1
    failures += 0 if check("id با sh- شروع می‌شود", str(si.get("id", "")).startswith("sh-")) else 1
    failures += 0 if check("sessionId با bale- شروع می‌شود", str(si.get("sessionId", "")).startswith("bale-")) else 1
    failures += 0 if check("channel = bale", si.get("channel") == "bale") else 1
    failures += 0 if check("riskLevel = redline (تداخل دارویی)", si.get("riskLevel") == "redline") else 1
    failures += 0 if check("status = pending", si.get("status") == "pending") else 1
    failures += 0 if check("timestamp ISO دریافت شده", si.get("timestamp") == ts) else 1
    failures += 0 if check("confidenceScore = 0.87", si.get("confidenceScore") == 0.87) else 1
    failures += 0 if check("deterministicRuleApplied درست است", si.get("deterministicRuleApplied") == "interaction_mention") else 1

    # تست سطح ریسک caution
    p2 = build_shadow_payload(
        chat_id="999",
        user_message="آیا در بارداری می‌توان مصرف کرد؟",
        proposed_reply="توصیه نمی‌شود.",
        timestamp=ts,
        extracted_fields={"risk_flags": {"pregnancy_lactation": True}},
    )
    failures += 0 if check("riskLevel = caution (بارداری)", p2["shadow_item"]["riskLevel"] == "caution") else 1

    # تست سطح ریسک safe
    p3 = build_shadow_payload(
        chat_id="111",
        user_message="قیمت دارو چقدر است؟",
        proposed_reply="متأسفانه قیمت‌گذاری نمی‌کنیم.",
        timestamp=ts,
    )
    failures += 0 if check("riskLevel = safe (سؤال عادی)", p3["shadow_item"]["riskLevel"] == "safe") else 1

    return failures


def run_disabled_emitter_test() -> int:
    """وقتی PANEL_EMIT_ENABLED=false است، باید skip شود."""
    banner("۲ — تست emitter غیرفعال (disabled)")
    failures = 0

    settings = EmitterSettings(
        enabled=False,
        base_url="http://127.0.0.1:1",  # پورت invalid — نباید تلاش شود
        token="irrelevant",
        timeout_seconds=1.0,
    )
    ts = datetime.now(timezone.utc).isoformat()
    payload = build_shadow_payload(
        chat_id="1", user_message="test", proposed_reply="test", timestamp=ts
    )
    result = emit_shadow_record(payload, settings=settings)

    failures += 0 if check("success=False وقتی disabled", not result.success) else 1
    failures += 0 if check("skipped=True وقتی disabled", result.skipped) else 1
    failures += 0 if check("status_code=None وقتی disabled", result.status_code is None) else 1

    return failures


def run_missing_token_test() -> int:
    """وقتی token خالی است، باید skip شود."""
    banner("۳ — تست token خالی")
    failures = 0

    settings = EmitterSettings(
        enabled=True,
        base_url="http://127.0.0.1:1",
        token="",  # خالی
        timeout_seconds=1.0,
    )
    ts = datetime.now(timezone.utc).isoformat()
    payload = build_shadow_payload(
        chat_id="2", user_message="test", proposed_reply="test", timestamp=ts
    )
    result = emit_shadow_record(payload, settings=settings)

    failures += 0 if check("success=False وقتی token خالی", not result.success) else 1
    failures += 0 if check("skipped=True وقتی token خالی", result.skipped) else 1

    return failures


def run_mock_server_tests() -> int:
    """ارسال واقعی به mock HTTP server."""
    banner("۴ — تست ارسال واقعی به Mock Server")
    failures = 0

    token = "e2e-test-token-abc123"
    server, port = _start_mock_server(token)
    base_url = f"http://127.0.0.1:{port}"

    settings_ok = EmitterSettings(
        enabled=True,
        base_url=base_url,
        token=token,
        timeout_seconds=3.0,
    )

    ts = datetime.now(timezone.utc).isoformat()
    payload = build_shadow_payload(
        chat_id="7654321",
        user_message="آسپرین با وارفارین چطور؟",
        proposed_reply="این ترکیب خطرناک است.",
        timestamp=ts,
        extracted_fields={"risk_flags": {"dose_interaction_mention": True}},
        confidence_score=0.95,
    )

    result = emit_shadow_record(payload, settings=settings_ok)

    failures += 0 if check("emit موفق (success=True)", result.success) else 1
    failures += 0 if check("status_code = 201", result.status_code == 201) else 1
    failures += 0 if check("skipped=False", not result.skipped) else 1
    failures += 0 if check("mock یک رکورد دریافت کرد", len(_MockHandler.received) == 1) else 1

    if _MockHandler.received:
        rec = _MockHandler.received[0]
        si = rec.get("shadow_item", {})
        failures += 0 if check("payload صحیح دریافت شد", si.get("riskLevel") == "redline") else 1
        failures += 0 if check("sessionId = bale-7654321", si.get("sessionId") == "bale-7654321") else 1

    # تست token اشتباه → 401
    settings_bad = EmitterSettings(
        enabled=True,
        base_url=base_url,
        token="wrong-token",
        timeout_seconds=3.0,
    )
    result_bad = emit_shadow_record(payload, settings=settings_bad)
    failures += 0 if check("token اشتباه → success=False", not result_bad.success) else 1
    failures += 0 if check("token اشتباه → status_code=401", result_bad.status_code == 401) else 1

    server.shutdown()
    return failures


def run_live_tests() -> int:
    """تست واقعی با بله-پنل از طریق متغیرهای محیطی."""
    banner("۵ — تست LIVE (بله-پنل واقعی)")

    # بارگذاری .env
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

    panel_url = os.getenv("PANEL_BASE_URL", "")
    panel_token = os.getenv("PANEL_OPERATOR_TOKEN", "")
    enabled = os.getenv("PANEL_EMIT_ENABLED", "false").lower() in {"1", "true", "yes"}

    if not enabled:
        print(f"  {SKIP}  PANEL_EMIT_ENABLED=false — تست live رد شد")
        print(f"         برای اجرا: PANEL_EMIT_ENABLED=true در .env تنظیم کنید")
        return 0

    if not panel_token or panel_token == "CHANGE_ME_MUST_MATCH_PANEL_API_SECRET":
        print(f"  {SKIP}  PANEL_OPERATOR_TOKEN تنظیم نشده — تست live رد شد")
        return 0

    print(f"  {CYAN}→ ارسال به: {panel_url}{RESET}")

    settings = EmitterSettings(
        enabled=True,
        base_url=panel_url,
        token=panel_token,
        timeout_seconds=float(os.getenv("PANEL_EMIT_TIMEOUT", "5")),
    )

    ts = datetime.now(timezone.utc).isoformat()
    payload = build_shadow_payload(
        chat_id="e2e-live-test",
        user_message="[E2E TEST] آزمون اتصال bale-med → bale-panel",
        proposed_reply="[E2E TEST] پاسخ آزمایشی",
        timestamp=ts,
        extracted_fields={"risk_flags": {}},
        confidence_score=1.0,
    )

    result = emit_shadow_record(payload, settings=settings)

    failures = 0
    failures += 0 if check("emit موفق (live)", result.success, f"status={result.status_code}") else 1
    if not result.success:
        print(f"         خطا: {result.error}")

    return failures


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="E2E test: bale-med → bale-panel shadow emitter")
    parser.add_argument("--live", action="store_true", help="اجرای تست واقعی (نیاز به .env معتبر)")
    args = parser.parse_args()

    start = time.perf_counter()
    total_failures = 0

    total_failures += run_payload_builder_tests()
    total_failures += run_disabled_emitter_test()
    total_failures += run_missing_token_test()
    total_failures += run_mock_server_tests()

    if args.live:
        total_failures += run_live_tests()
    else:
        banner("۵ — تست LIVE")
        print(f"  {SKIP}  برای تست live اجرا کنید: python {Path(__file__).name} --live")

    elapsed = time.perf_counter() - start
    banner("نتیجه نهایی")
    if total_failures == 0:
        print(f"  {GREEN}{BOLD}همه تست‌ها موفق بودند ✔  ({elapsed:.2f}s){RESET}\n")
    else:
        print(f"  {RED}{BOLD}{total_failures} تست شکست خورد ✗  ({elapsed:.2f}s){RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
