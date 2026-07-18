#!/usr/bin/env python3
"""Publish triage reference article to Notion Knowledge database.

Requires NOTION_TOKEN in the environment (integration with access to Knowledge DB).

Usage:
  export NOTION_TOKEN=secret_...
  python3 scripts/publish-triage-notion.py
  python3 scripts/publish-triage-notion.py --dry-run

See docs/notion-import/README.md for manual import if token is unavailable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

KNOWLEDGE_DATABASE_ID = "bde89f17-aae0-48f7-b111-b3494323cd91"
ARTICLE_PATH = Path(__file__).resolve().parent.parent / "docs/research/triage-referral-design-fa.md"

PAGE_TITLE = "طراحی تریاژ و ارجاع — بات داروخانه BaleMed (با/بدون LLM)"
PAGE_SUMMARY = (
    "مرجع طراحی تریاژ D0/D1/D2 برای بات BaleMed: ارجاع داروساز، red flags اورژانس، "
    "و دو مسیر ADR فنی با/بدون LLM. bot تشخیص نمی‌دهد — فقط disposition."
)


def _chunk_text(text: str, limit: int = 1900) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + limit])
        start += limit
    return chunks


def markdown_to_blocks(markdown: str) -> list[dict]:
    """Convert markdown lines to simple Notion paragraph blocks."""
    blocks: list[dict] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        for chunk in _chunk_text(stripped):
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}],
                    },
                }
            )
    return blocks[:95]


def build_page_payload(markdown: str) -> dict:
    properties = {
        "Entry": {"title": [{"text": {"content": PAGE_TITLE}}]},
        "Category": {"select": {"name": "Reference"}},
        "Status": {"select": {"name": "Draft"}},
        "Summary": {
            "rich_text": [{"text": {"content": PAGE_SUMMARY[:2000]}}],
        },
    }
    tags_prop = os.environ.get("NOTION_TAGS_PROPERTY", "Tags")
    if tags_prop:
        properties[tags_prop] = {
            "multi_select": [
                {"name": "BaleMed"},
                {"name": "Pharmacy"},
                {"name": "Safety"},
                {"name": "LLM"},
            ],
        }
    return {
        "parent": {"database_id": KNOWLEDGE_DATABASE_ID},
        "properties": properties,
        "children": markdown_to_blocks(markdown),
    }


def notion_request(method: str, path: str, body: dict | None = None) -> dict:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit(
            "NOTION_TOKEN is not set. Export it or use manual import: "
            "docs/notion-import/README.md"
        )
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"https://api.notion.com/v1{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        raise SystemExit(f"Notion API error {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload summary without calling Notion API",
    )
    parser.add_argument(
        "--article",
        type=Path,
        default=ARTICLE_PATH,
        help=f"Markdown source (default: {ARTICLE_PATH})",
    )
    args = parser.parse_args()

    if not args.article.is_file():
        raise SystemExit(f"Article not found: {args.article}")

    markdown = args.article.read_text(encoding="utf-8")
    payload = build_page_payload(markdown)

    if args.dry_run:
        print(json.dumps({"title": PAGE_TITLE, "blocks": len(payload["children"])}, ensure_ascii=False))
        print("Dry run OK — set NOTION_TOKEN and rerun without --dry-run to publish.")
        return 0

    result = notion_request("POST", "/pages", payload)
    url = result.get("url", result.get("id", "unknown"))
    print(f"Created Notion page: {url}")
    print("Next: link from Knowledge Hub and relate vocab (ADR, workflow, schema).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
