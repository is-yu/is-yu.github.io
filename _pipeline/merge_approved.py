"""Merge approved suggestions into the _data/ directory.

Reads _staging/approved/*.yaml and creates the appropriate files in
_data/breakthroughs/, _data/progress/, and _data/questions/.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .config import APPROVED_DIR, DATA_DIR


def _next_id(prefix: str, directory: Path) -> str:
    """Find the next sequential ID (e.g., b-017, q-021, p-003)."""
    existing = []
    pattern = re.compile(rf"^{prefix}-(\d+)")
    for path in directory.glob(f"{prefix}-*.yaml"):
        m = pattern.match(path.stem)
        if m:
            existing.append(int(m.group(1)))
    next_num = max(existing, default=0) + 1
    return f"{prefix}-{next_num:03d}"


def _slugify(text: str) -> str:
    """Create a URL-safe slug from text."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = slug.strip("-")
    return slug[:50]


def merge_approved():
    """Process all approved suggestions and write into _data/."""
    if not APPROVED_DIR.exists():
        print("No approved directory found.")
        return

    approved_files = sorted(APPROVED_DIR.glob("*.yaml"))
    if not approved_files:
        print("No approved suggestions to merge.")
        return

    print(f"Merging {len(approved_files)} approved suggestion(s)...")

    breakthroughs_dir = DATA_DIR / "breakthroughs"
    progress_dir = DATA_DIR / "progress"
    questions_dir = DATA_DIR / "questions"

    breakthroughs_dir.mkdir(parents=True, exist_ok=True)
    progress_dir.mkdir(parents=True, exist_ok=True)
    questions_dir.mkdir(parents=True, exist_ok=True)

    for path in approved_files:
        suggestion = yaml.safe_load(path.read_text())
        if not suggestion:
            continue

        paper_ref = suggestion.get("paper_ref", "")
        paper_title = suggestion.get("paper_title", "")
        print(f"  Processing: {paper_title[:60]}")

        is_breakthrough = suggestion.get("is_breakthrough", False)
        significance = suggestion.get("significance_assessment", "incremental")

        # Create breakthrough entry if significant enough
        if is_breakthrough:
            bid = _next_id("b", breakthroughs_dir)
            slug = _slugify(paper_title)
            claims = suggestion.get("claims", [])
            key_findings = []
            for c in claims[:3]:
                if isinstance(c, dict):
                    key_findings.append({
                        "finding": c.get("claim", ""),
                        "significance": c.get("evidence", ""),
                    })

            bt = {
                "id": bid,
                "slug": slug,
                "title": paper_title,
                "paper_refs": [paper_ref] if paper_ref else [],
                "authors": [],  # Would need to be filled from paper metadata
                "date": suggestion.get("analyzed_at", "")[:10],
                "venue": "arXiv",
                "question_ids": [
                    m["question_id"]
                    for m in suggestion.get("question_mappings", [])
                    if isinstance(m, dict) and m.get("relevance") in ("answers", "partially-answers")
                ],
                "key_findings": key_findings,
                "significance_level": significance,
                "new_questions_raised": [],
                "context": suggestion.get("reasoning", ""),
                "summary": claims[0].get("claim", "") if claims and isinstance(claims[0], dict) else "",
            }

            bt_path = breakthroughs_dir / f"{bid}-{slug}.yaml"
            with open(bt_path, "w") as f:
                yaml.dump(bt, f, default_flow_style=False, allow_unicode=True)
            print(f"    Created breakthrough: {bt_path.name}")

        # Create progress entries for question mappings
        for mapping in suggestion.get("question_mappings", []):
            if not isinstance(mapping, dict):
                continue
            if mapping.get("relevance") in ("provides-evidence", "partially-answers"):
                pid = _next_id("p", progress_dir)
                slug = _slugify(paper_title)
                p = {
                    "id": pid,
                    "question_id": mapping.get("question_id", ""),
                    "paper_ref": paper_ref,
                    "title": paper_title,
                    "authors": [],
                    "date": suggestion.get("analyzed_at", "")[:10],
                    "finding": mapping.get("explanation", ""),
                    "impact_on_question": mapping.get("explanation", ""),
                    "advancement_level": "moderate",
                }
                p_path = progress_dir / f"{pid}-{slug}.yaml"
                with open(p_path, "w") as f:
                    yaml.dump(p, f, default_flow_style=False, allow_unicode=True)
                print(f"    Created progress: {p_path.name}")

        # Create new question entries
        for new_q in suggestion.get("new_questions_suggested", []):
            if not isinstance(new_q, dict):
                continue
            qid = _next_id("q", questions_dir)
            slug = _slugify(new_q.get("text", ""))
            q = {
                "id": qid,
                "slug": slug,
                "text": new_q.get("text", ""),
                "description": new_q.get("rationale", ""),
                "status": "OPEN",
                "category": new_q.get("category", "deep-learning"),
                "era": "foundation-models",
                "date_first_posed": suggestion.get("analyzed_at", "")[:10],
                "answered_by": [],
                "related_questions": [],
                "tags": [],
            }
            q_path = questions_dir / f"{qid}-{slug}.yaml"
            with open(q_path, "w") as f:
                yaml.dump(q, f, default_flow_style=False, allow_unicode=True)
            print(f"    Created question: {q_path.name}")

        # Remove processed file
        path.unlink()

    print(f"\nMerge complete. Run 'python -m _generator.build' to rebuild the site.")


def main():
    merge_approved()


if __name__ == "__main__":
    main()
