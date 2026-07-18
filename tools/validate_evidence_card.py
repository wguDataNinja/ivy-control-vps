#!/usr/bin/env python3
"""Validate a supplied evidence card without accessing live infrastructure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.evidence_cards import is_expired, load_card, validate_card


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a local JSON evidence card")
    parser.add_argument("card", type=Path)
    parser.add_argument("--asset", help="expected asset identifier")
    parser.add_argument("--evidence-type", help="expected evidence type")
    parser.add_argument("--allow-expired", action="store_true",
                        help="report structural validity without failing expired evidence")
    args = parser.parse_args()
    try:
        card = load_card(args.card)
    except ValueError as exc:
        print(f"FAIL: {args.card}\n  - {exc}")
        return 1
    errors = validate_card(card, expected_asset=args.asset,
                           expected_evidence_type=args.evidence_type)
    if is_expired(card) and not args.allow_expired:
        errors.append("evidence is expired")
    if errors:
        print(f"FAIL: {args.card}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS: {args.card}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
