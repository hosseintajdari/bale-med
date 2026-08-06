#!/usr/bin/env python3
"""Save one shadow review annotation via local API."""
from __future__ import annotations

import argparse
import sys

import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("message_id", type=int)
    parser.add_argument("--needs-review-ok", choices=("yes", "no", "skip"), default="skip")
    parser.add_argument("--drug-name-ok", choices=("yes", "no", "skip"), default="skip")
    parser.add_argument("--corrected-drug-name", default=None)
    parser.add_argument("--owner-notes", default=None)
    args = parser.parse_args()

    payload: dict[str, object] = {}
    if args.needs_review_ok != "skip":
        payload["needs_review_ok"] = args.needs_review_ok == "yes"
    if args.drug_name_ok != "skip":
        payload["drug_name_ok"] = args.drug_name_ok == "yes"
    if args.corrected_drug_name:
        payload["corrected_drug_name"] = args.corrected_drug_name
    if args.owner_notes:
        payload["owner_notes"] = args.owner_notes

    response = httpx.post(
        f"http://127.0.0.1:8000/local/shadow-reviews/{args.message_id}/annotate",
        json=payload,
        timeout=30.0,
    )
    print(response.status_code)
    print(response.text)
    if response.status_code >= 400:
        sys.exit(1)


if __name__ == "__main__":
    main()
