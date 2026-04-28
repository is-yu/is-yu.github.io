"""Interactive CLI for reviewing AI-generated suggestions.

Reads pending suggestions from _staging/pending/, lets the curator
approve, edit, skip, or reject each one.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

from .config import APPROVED_DIR, PENDING_DIR


def review():
    """Interactive review of pending suggestions."""
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)

    pending_files = sorted(PENDING_DIR.glob("*.yaml"))
    if not pending_files:
        print("No pending suggestions to review.")
        return

    print(f"\n{len(pending_files)} pending suggestion(s)\n")

    for i, path in enumerate(pending_files):
        suggestion = yaml.safe_load(path.read_text())
        if not suggestion:
            continue

        print("=" * 70)
        print(f"[{i+1}/{len(pending_files)}] {suggestion.get('paper_title', 'Unknown')}")
        print(f"  Paper: {suggestion.get('paper_ref', '?')}")
        print(f"  Significance: {suggestion.get('significance_assessment', '?')}")
        print(f"  Confidence: {suggestion.get('confidence', '?')}")
        print(f"  Is breakthrough: {suggestion.get('is_breakthrough', False)}")
        print()

        claims = suggestion.get("claims", [])
        if claims:
            print("  Claims:")
            for j, c in enumerate(claims[:3]):
                claim_text = c.get("claim", "") if isinstance(c, dict) else str(c)
                print(f"    {j+1}. {claim_text[:100]}")
            print()

        mappings = suggestion.get("question_mappings", [])
        if mappings:
            print("  Question mappings:")
            for m in mappings[:3]:
                if isinstance(m, dict):
                    print(f"    -> {m.get('question_id', '?')}: {m.get('relevance', '?')}")
            print()

        new_qs = suggestion.get("new_questions_suggested", [])
        if new_qs:
            print("  New questions suggested:")
            for nq in new_qs[:2]:
                if isinstance(nq, dict):
                    print(f"    ? {nq.get('text', '?')[:80]}")
            print()

        reasoning = suggestion.get("reasoning", "")
        if reasoning:
            print(f"  Reasoning: {reasoning[:200]}...")
            print()

        while True:
            choice = input("  [a]pprove / [s]kip / [r]eject / [q]uit: ").strip().lower()
            if choice in ("a", "s", "r", "q"):
                break
            print("  Invalid choice. Try again.")

        if choice == "a":
            dest = APPROVED_DIR / path.name
            shutil.move(str(path), str(dest))
            print("  -> Approved")
        elif choice == "r":
            path.unlink()
            print("  -> Rejected (deleted)")
        elif choice == "q":
            print("\nReview session ended.")
            break
        else:
            print("  -> Skipped (will review later)")

    print(f"\nDone. Run 'python -m _pipeline.merge_approved' to merge approved suggestions.")


def main():
    review()


if __name__ == "__main__":
    main()
