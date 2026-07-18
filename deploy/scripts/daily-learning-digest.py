#!/usr/bin/env python3
"""Build a daily vibe-coder learning digest from Cursor queue + git activity."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = REPO_ROOT / ".cursor" / "learning-queue"
TRANSCRIPTS_DIR = Path.home() / ".cursor" / "projects" / "c-Users-hosse-OneDrive-Documents-BaleMed" / "agent-transcripts"

READ_MORE_BY_TOPIC: dict[str, list[dict[str, str]]] = {
    "python_backend": [
        {"title": "FastAPI Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"},
        {"title": "Pydantic V2 docs", "url": "https://docs.pydantic.dev/latest/"},
    ],
    "devops": [
        {"title": "systemd service basics", "url": "https://www.freedesktop.org/software/systemd/man/systemd.service.html"},
        {"title": "Caddy reverse proxy", "url": "https://caddyserver.com/docs/quick-starts/reverse-proxy"},
    ],
    "tooling_integration": [
        {"title": "Notion API — Create a page", "url": "https://developers.notion.com/reference/post-page"},
        {"title": "Cursor Automations docs", "url": "https://cursor.com/docs"},
    ],
    "git_workflow": [
        {"title": "Git branching (Atlassian)", "url": "https://www.atlassian.com/git/tutorials/using-branches"},
    ],
    "architecture_gap": [
        {"title": "FastAPI project structure", "url": "https://fastapi.tiangolo.com/tutorial/bigger-applications/"},
    ],
    "english_learning": [
        {"title": "Plain English for developers", "url": "https://plainenglish.com/"},
    ],
}

VIDEO_BY_TOPIC: dict[str, list[dict[str, str]]] = {
    "python_backend": [
        {"title": "FastAPI — Full Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=tLKKmouUams"},
    ],
    "devops": [
        {"title": "Linux systemd explained", "url": "https://www.youtube.com/watch?v=AtEqCemd1Ec"},
    ],
    "tooling_integration": [
        {"title": "Notion databases overview", "url": "https://www.youtube.com/watch?v=9Xzm597UlNc"},
    ],
    "git_workflow": [
        {"title": "Git and GitHub for beginners", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk"},
    ],
    "debugging": [
        {"title": "Python debugging with pdb", "url": "https://www.youtube.com/watch?v=VQ9kJcLqRKI"},
    ],
}

VOCAB_HINT_TERMS: tuple[str, ...] = (
    "commit",
    "deploy",
    "webhook",
    "endpoint",
    "middleware",
    "lifespan",
    "merge",
    "branch",
    "rollback",
    "validate",
    "hook",
    "automation",
    "mcp",
    "relation",
    "shadow",
    "digest",
    "systemd",
    "dry-run",
    "pr",
    "pull request",
)


def _parse_day(value: str | None) -> date:
    if not value or value.lower() in {"today", "now"}:
        return datetime.now().date()
    if value.lower() == "yesterday":
        return datetime.now().date() - timedelta(days=1)
    return date.fromisoformat(value)


def _load_queue_signals(day: date) -> list[dict[str, Any]]:
    queue_file = QUEUE_DIR / f"{day.isoformat()}.jsonl"
    if not queue_file.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in queue_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _scan_transcripts(day: date) -> list[dict[str, Any]]:
    if not TRANSCRIPTS_DIR.exists():
        return []
    start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    hits: list[dict[str, Any]] = []
    for path in TRANSCRIPTS_DIR.glob("*.jsonl"):
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if not (start <= modified < end):
            continue
        preview = path.read_text(encoding="utf-8", errors="ignore")[:800]
        hits.append(
            {
                "transcript_id": path.stem,
                "modified_at": modified.isoformat(),
                "preview": preview.replace("\n", " ")[:400],
            }
        )
    return hits


def _git_activity(day: date) -> dict[str, Any]:
    since = day.isoformat()
    until = (day + timedelta(days=1)).isoformat()
    cmd = [
        "git",
        "-C",
        str(REPO_ROOT),
        "log",
        f"--since={since}",
        f"--until={until}",
        "--pretty=format:%h|%s|%an",
        "--name-only",
    ]
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"commits": [], "changed_files": []}

    commits: list[dict[str, str]] = []
    changed_files: list[str] = []
    block_lines = [line for line in output.splitlines() if line.strip()]
    idx = 0
    while idx < len(block_lines):
        line = block_lines[idx]
        if "|" in line and not line.startswith(" "):
            parts = line.split("|", 2)
            commit = {"hash": parts[0], "subject": parts[1] if len(parts) > 1 else "", "author": parts[2] if len(parts) > 2 else ""}
            commits.append(commit)
            idx += 1
            files: list[str] = []
            while idx < len(block_lines) and "|" not in block_lines[idx]:
                files.append(block_lines[idx].strip())
                idx += 1
            changed_files.extend(files)
            continue
        idx += 1
    return {"commits": commits, "changed_files": sorted(set(changed_files))}


def _aggregate_blind_spots(signals: list[dict[str, Any]]) -> list[str]:
    counter: Counter[str] = Counter()
    for row in signals:
        for label in row.get("blind_spots") or []:
            counter[label] += 1
    return [label for label, _ in counter.most_common()]


def _suggest_learning_pages(blind_spots: list[str], changed_files: list[str]) -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    if "tooling_integration" in blind_spots or any("notion" in path.lower() for path in changed_files):
        pages.append(
            {
                "title": "بخش ۱ — ابزارها و یکپارچه‌سازی",
                "focus": "Notion MCP، Cursor Automations، تفاوت hook و automation زمان‌بندی‌شده",
            }
        )
    if "python_backend" in blind_spots or any(path.endswith(".py") for path in changed_files):
        pages.append(
            {
                "title": "بخش ۲ — الگوهای Python backend",
                "focus": "FastAPI، guard clause، type hint، مرزهای ایمنی داروخانه",
            }
        )
    if "devops" in blind_spots or any(path.startswith("deploy/") for path in changed_files):
        pages.append(
            {
                "title": "بخش ۳ — دیپلوی و عملیات",
                "focus": "VPS dry-run، scp، systemd، rollback",
            }
        )
    if "english_learning" in blind_spots or len(pages) < 3:
        pages.append(
            {
                "title": "بخش ۴ — اصطلاحات فنی",
                "focus": "واژه‌های commit، PR، و doc — با مثال کوتاه",
            }
        )
    while len(pages) < 3:
        pages.append(
            {
                "title": f"بخش {len(pages) + 1} — مرور پایه",
                "focus": "مرور AGENTS.md و یک ADR از docs/adr/",
            }
        )
    return pages[:4]


def _collect_resources(blind_spots: list[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    read_more: list[dict[str, str]] = []
    videos: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for label in blind_spots:
        for item in READ_MORE_BY_TOPIC.get(label, []):
            if item["url"] in seen_urls:
                continue
            seen_urls.add(item["url"])
            read_more.append(item)
        for item in VIDEO_BY_TOPIC.get(label, []):
            if item["url"] in seen_urls:
                continue
            seen_urls.add(item["url"])
            videos.append(item)
    if not read_more:
        read_more.append({"title": "BaleMed HANDOFF", "url": "https://github.com/hosseintajdari/bale-med/blob/main/docs/agents/HANDOFF.md"})
    if not videos:
        videos.append({"title": "Python for beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"})
    return read_more[:8], videos[:6]


def _extract_vocabulary_hints(
    git_info: dict[str, Any],
    blind_spots: list[str],
) -> list[dict[str, str]]:
    haystack_parts: list[str] = []
    for commit in git_info.get("commits") or []:
        haystack_parts.append(commit.get("subject") or "")
    haystack_parts.extend(git_info.get("changed_files") or [])
    haystack = " ".join(haystack_parts).lower()

    hints: list[dict[str, str]] = []
    seen: set[str] = set()
    for term in VOCAB_HINT_TERMS:
        if term not in haystack:
            continue
        key = term.replace(" ", "-")
        if key in seen:
            continue
        seen.add(key)
        hints.append({"term": key, "source": "git_activity"})

    if "english_learning" in blind_spots and len(hints) < 3:
        for fallback in ("commit", "deploy", "webhook"):
            if fallback in seen:
                continue
            seen.add(fallback)
            hints.append({"term": fallback, "source": "blind_spot"})
            if len(hints) >= 5:
                break

    return hints[:5]


def build_digest(day: date) -> dict[str, Any]:
    signals = _load_queue_signals(day)
    transcripts = _scan_transcripts(day)
    git_info = _git_activity(day)
    blind_spots = _aggregate_blind_spots(signals)
    learning_pages = _suggest_learning_pages(blind_spots, git_info.get("changed_files") or [])
    read_more, videos = _collect_resources(blind_spots)
    vocabulary_hints = _extract_vocabulary_hints(git_info, blind_spots)

    has_activity = bool(signals or transcripts or git_info.get("commits"))
    return {
        "date": day.isoformat(),
        "has_activity": has_activity,
        "signal_count": len(signals),
        "transcript_count": len(transcripts),
        "git": git_info,
        "blind_spots": blind_spots,
        "learning_pages": learning_pages,
        "read_more": read_more,
        "videos": videos,
        "vocabulary_hints": vocabulary_hints,
        "notion": {
            "parent_page_url": "https://app.notion.com/p/3a0f6d55a67381ca8421fc4fa9a81b42",
            "database_hint": "یادگیری روزانه (Daily Learning Log) — Knowledge Hub > Embednet OS",
            "database_id": "a3d4f11a-b597-4e46-80ee-2f0d32dec714",
            "vocab_database_id": "342d997fca984776a8f0323eec4ea32a",
            "vocab_hub_url": "https://app.notion.com/p/3a1f6d55a67381788defe158055d19b2",
            "title": f"یادگیری روزانه — {day.isoformat()}",
            "properties": {
                "عنوان": f"یادگیری روزانه — {day.isoformat()}",
                "تاریخ": day.isoformat(),
                "وضعیت": "آماده",
                "صفحات": 4,
            },
            "sections": [
                "امروز چه کار کردیم",
                "نقاط کور",
                "نکات آموزشی",
                "لینک و ویدیو",
                "اصطلاحات امروز",
            ],
        },
        "agent_prompt": (
            "یک صفحه در database «یادگیری روزانه» (Daily Learning Log) بساز. "
            "متن اصلی فارسی ساده باشد؛ نام ابزار (Notion، FastAPI، Cursor) انگلیسی OK. "
            "۴–۵ بخش: ۱) امروز چه کار کردیم ۲) نقاط کور ۳) نکات آموزشی "
            "۴) لینک و ویدیو ۵) اصطلاحات امروز از vocabulary_hints — جستجو در «واژه‌نامه برنامه‌نویسی»، "
            "relation بزن یا پیشنهاد ثبت (بدون auto-create). "
            "Properties: عنوان، تاریخ=امروز، وضعیت=آماده، موضوعات از blind_spots، صفحات=۳ یا ۴. "
            "اگر کار repo بود Project=BaleMed. بدون secret، token، یا داده بیمار."
        ),
    }


def _format_markdown(digest: dict[str, Any]) -> str:
    lines = [
        f"# یادگیری روزانه — {digest['date']}",
        "",
        "## امروز چه کار کردیم",
        f"- سیگنال Cursor: {digest['signal_count']}",
        f"- transcript: {digest['transcript_count']}",
        f"- commit گیت: {len(digest['git'].get('commits') or [])}",
        "",
        "## نقاط کور",
    ]
    if digest["blind_spots"]:
        lines.extend(f"- {item}" for item in digest["blind_spots"])
    else:
        lines.append("- هنوز سیگنالی نیست — امروز در Cursor کار کن.")

    lines.extend(["", "## نکات آموزشی (۳–۴ بخش)"])
    for page in digest["learning_pages"]:
        lines.append(f"- **{page['title']}** — {page['focus']}")

    lines.extend(["", "## لینک بیشتر"])
    for item in digest["read_more"]:
        lines.append(f"- [{item['title']}]({item['url']})")

    lines.extend(["", "## ویدیو"])
    for item in digest["videos"]:
        lines.append(f"- [{item['title']}]({item['url']})")

    lines.extend(["", "## اصطلاحات امروز"])
    if digest.get("vocabulary_hints"):
        for item in digest["vocabulary_hints"]:
            lines.append(f"- `{item['term']}` ({item['source']})")
    else:
        lines.append("- هنوز واژه پیشنهادی نیست.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build daily vibe-coder learning digest")
    parser.add_argument("--date", default="today", help="ISO date, today, or yesterday")
    parser.add_argument("--json", action="store_true", help="Print JSON digest")
    parser.add_argument("--markdown", action="store_true", help="Print markdown digest")
    args = parser.parse_args()

    day = _parse_day(args.date)
    digest = build_digest(day)

    if args.json or (not args.json and not args.markdown):
        print(json.dumps(digest, ensure_ascii=False, indent=2))
        return
    if args.markdown:
        print(_format_markdown(digest))


if __name__ == "__main__":
    main()
