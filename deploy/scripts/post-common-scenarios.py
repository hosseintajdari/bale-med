#!/usr/bin/env python3
"""Post common pharmacy shadow-test scenarios via local webhook loopback."""
from __future__ import annotations

import json
import os
import sys
import time

import httpx

os.chdir("/opt/bale-bot")
sys.path.insert(0, "/opt/bale-bot")

from app.config import get_settings

SCENARIOS: list[dict[str, str]] = [
    {
        "id": "S01",
        "label": "drug_availability_specific",
        "text": "سلام، ibuprofen 400 موجود دارید؟",
    },
    {
        "id": "S02",
        "label": "misspelled_drug",
        "text": "ایبوپروفن ۴۰۰ موجوده؟",
    },
    {
        "id": "S03",
        "label": "allergy_mention",
        "text": "به پنی‌سیلین حساسیت دارم، چه آنتی‌بیوتیکی بگیرم؟",
    },
    {
        "id": "S04",
        "label": "pregnancy",
        "text": "باردارم، می‌تونم قرص سرماخوردگی بخورم؟",
    },
    {
        "id": "S05",
        "label": "pediatric",
        "text": "برای بچه ۳ ساله شربت سرفه می‌خوام",
    },
    {
        "id": "S06",
        "label": "dose_question",
        "text": "لووتیروکسین را چند میلی‌گرم بخورم؟",
    },
    {
        "id": "S07",
        "label": "urgent_symptoms",
        "text": "درد قفسه سینه دارم و تنگی نفس دارم",
    },
    {
        "id": "S08",
        "label": "simple_greeting",
        "text": "سلام وقت بخیر",
    },
    {
        "id": "S09",
        "label": "drug_interaction",
        "text": "آیا آسپرین با وارفارین تداخل دارد؟",
    },
    {
        "id": "S10",
        "label": "side_effect",
        "text": "بعد از متفورمین معده‌ام درد می‌گیرد",
    },
    {
        "id": "S11",
        "label": "refill_request",
        "text": "نسخه قبلیم را می‌خواهم تمدید کنم",
    },
    {
        "id": "S12",
        "label": "generic_pain_med",
        "text": "قرص مسکن برای سردرد شدید می‌خواهم",
    },
]

BASE_MESSAGE_ID = 910_000


def main() -> None:
    settings = get_settings()
    url = f"http://127.0.0.1:8000/webhook/bale/{settings.bale_webhook_secret}"
    results: list[dict[str, object]] = []

    for index, scenario in enumerate(SCENARIOS, start=1):
        message_id = BASE_MESSAGE_ID + index
        response = httpx.post(
            url,
            json={
                "message": {
                    "message_id": message_id,
                    "chat": {"id": "shadow-scenario-chat"},
                    "text": scenario["text"],
                }
            },
            timeout=120.0,
        )
        payload = response.json() if response.content else {}
        row = {
            "scenario_id": scenario["id"],
            "label": scenario["label"],
            "text": scenario["text"],
            "http_status": response.status_code,
            "ok": payload.get("ok"),
            "message_id": message_id,
        }
        results.append(row)
        print(json.dumps(row, ensure_ascii=False))
        time.sleep(4)

    print(f"scenario_count={len(results)}")


if __name__ == "__main__":
    main()
