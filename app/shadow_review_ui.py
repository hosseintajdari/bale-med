from __future__ import annotations

import html
import json
from typing import Any

from .shadow_review import TriStateChoice


def build_shadow_review_ui_page(
    items: list[dict[str, Any]],
    *,
    limit: int,
    saved_message_id: int | None = None,
) -> str:
    rows = "\n".join(_render_shadow_review_row(item) for item in items)
    saved_banner = ""
    if saved_message_id is not None:
        saved_banner = f'<p class="banner ok">Annotation saved for message #{saved_message_id}.</p>'

    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BaleMed P2 Shadow Review</title>
  <style>
    body {{
      font-family: Tahoma, Arial, sans-serif;
      margin: 1rem;
      background: #f7f7f8;
      color: #1f2937;
      line-height: 1.5;
    }}
    h1 {{
      margin-bottom: 0.25rem;
      font-size: 1.35rem;
    }}
    .meta {{
      color: #4b5563;
      margin-bottom: 1rem;
    }}
    .banner.ok {{
      background: #dcfce7;
      border: 1px solid #86efac;
      padding: 0.75rem;
      border-radius: 0.5rem;
      margin-bottom: 1rem;
    }}
    .card {{
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 0.75rem;
      padding: 1rem;
      margin-bottom: 1rem;
    }}
    .card h2 {{
      margin: 0 0 0.5rem;
      font-size: 1rem;
    }}
    .preview {{
      background: #f3f4f6;
      padding: 0.75rem;
      border-radius: 0.5rem;
      white-space: pre-wrap;
      word-break: break-word;
      margin: 0.5rem 0 1rem;
    }}
    pre {{
      background: #111827;
      color: #f9fafb;
      padding: 0.75rem;
      border-radius: 0.5rem;
      overflow-x: auto;
      font-size: 0.85rem;
      direction: ltr;
      text-align: left;
    }}
    label {{
      display: block;
      margin: 0.35rem 0;
    }}
    .choices {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin: 0.35rem 0 0.75rem;
    }}
    .choices label {{
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      margin: 0;
    }}
    input[type="text"], textarea {{
      width: 100%;
      box-sizing: border-box;
      padding: 0.5rem;
      border: 1px solid #d1d5db;
      border-radius: 0.5rem;
      font: inherit;
    }}
    textarea {{
      min-height: 4rem;
      resize: vertical;
    }}
    button {{
      background: #2563eb;
      color: #fff;
      border: 0;
      border-radius: 0.5rem;
      padding: 0.55rem 0.9rem;
      cursor: pointer;
      font: inherit;
    }}
    .annotated {{
      border-color: #86efac;
      box-shadow: inset 0 0 0 1px #bbf7d0;
    }}
    .footnote {{
      color: #6b7280;
      font-size: 0.9rem;
      margin-top: 1rem;
    }}
  </style>
</head>
<body>
  <h1>P2 Shadow Review (local only)</h1>
  <p class="meta">Showing up to {limit} recent <code>shadow_ok</code> messages. Compare LLM output with pharmacist judgment.</p>
  {saved_banner}
  {rows or "<p>No shadow_ok messages found yet.</p>"}
  <p class="footnote">Access via SSH tunnel only. Caddy blocks <code>/local/*</code> on the public domain.</p>
</body>
</html>
"""


def _render_shadow_review_row(item: dict[str, Any]) -> str:
    message_id = int(item["id"])
    annotation = item.get("annotation") or {}
    card_class = "card annotated" if annotation else "card"
    extracted_json = json.dumps(item.get("llm_extracted"), ensure_ascii=False, indent=2)
    if extracted_json == "null":
        extracted_json = "{}"

    return f"""
<section class="{card_class}" id="message-{message_id}">
  <h2>Message #{message_id} · {html.escape(str(item.get("received_at") or ""))}</h2>
  <div class="preview">{html.escape(str(item.get("text") or ""))}</div>
  <pre>{html.escape(extracted_json)}</pre>
  <form method="post" action="/local/shadow-reviews/{message_id}/annotate">
    <input type="hidden" name="redirect_to_ui" value="1">
    <p><strong>needs_review</strong> درست بود؟</p>
    <div class="choices">{_render_tristate_radios("needs_review_ok", annotation.get("needs_review_ok"))}</div>
    <p><strong>drug_name</strong> درست بود؟</p>
    <div class="choices">{_render_tristate_radios("drug_name_ok", annotation.get("drug_name_ok"))}</div>
    <label>نام داروی صحیح (اختیاری)
      <input type="text" name="corrected_drug_name" maxlength="120" value="{html.escape(str(annotation.get("corrected_drug_name") or ""))}">
    </label>
    <label>یادداشت داروساز (اختیاری)
      <textarea name="owner_notes" maxlength="500">{html.escape(str(annotation.get("owner_notes") or ""))}</textarea>
    </label>
    <p><button type="submit">Save annotation</button></p>
  </form>
</section>
"""


def _render_tristate_radios(field_name: str, selected_value: bool | None) -> str:
    selected: TriStateChoice
    if selected_value is True:
        selected = "yes"
    elif selected_value is False:
        selected = "no"
    else:
        selected = "skip"

    options = (
        ("yes", "بله"),
        ("no", "خیر"),
        ("skip", "نامشخص"),
    )
    rendered = []
    for value, label in options:
        checked = " checked" if selected == value else ""
        rendered.append(
            f'<label><input type="radio" name="{field_name}" value="{value}"{checked}> {label}</label>'
        )
    return "\n".join(rendered)
