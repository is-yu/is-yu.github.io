"""Claude API integration for paper analysis.

Analyzes papers in two steps:
1. Claim extraction and significance assessment
2. Question mapping and new question suggestion

Uses prompt caching on the knowledge base context to reduce costs.
"""

from __future__ import annotations

import argparse
import re
import time
from datetime import datetime
from pathlib import Path

import yaml

from .config import (
    CLAUDE_MODEL,
    DATA_DIR,
    MAX_TOKENS,
    SUGGESTIONS_DIR,
    TEXT_DIR,
)
from .prompts import (
    CLAIM_EXTRACTION_PROMPT,
    QUESTION_MAPPING_PROMPT,
    SYSTEM_PROMPT,
)


def _load_all_questions() -> list[dict]:
    """Load all questions from _data/questions/."""
    questions = []
    qdir = DATA_DIR / "questions"
    if qdir.exists():
        for path in sorted(qdir.glob("q-*.yaml")):
            questions.append(yaml.safe_load(path.read_text()))
    return questions


def _load_all_breakthroughs() -> list[dict]:
    """Load all breakthroughs from _data/breakthroughs/."""
    breakthroughs = []
    bdir = DATA_DIR / "breakthroughs"
    if bdir.exists():
        for path in sorted(bdir.glob("b-*.yaml")):
            breakthroughs.append(yaml.safe_load(path.read_text()))
    return breakthroughs


def _build_kb_context(questions: list[dict], breakthroughs: list[dict]) -> str:
    """Build knowledge base context string for Claude."""
    lines = ["# Existing Knowledge Base\n"]
    lines.append("## Questions\n")
    for q in questions:
        lines.append(f"- {q['id']}: [{q['status']}] {q['text']}")
    lines.append("\n## Breakthroughs\n")
    for b in breakthroughs:
        lines.append(f"- {b['id']}: {b['title']} ({b['date']}) [{b['significance_level']}]")
    return "\n".join(lines)


def _questions_summary(questions: list[dict]) -> str:
    """Build a compact summary of questions for the mapping prompt."""
    lines = []
    for q in questions:
        lines.append(f"- {q['id']} [{q['status']}] ({q['category']}): {q['text']}")
    return "\n".join(lines)


def _parse_yaml_response(text: str) -> dict:
    """Extract YAML from Claude's response (may be in a code block)."""
    # Try to find YAML in a code block
    match = re.search(r"```(?:yaml)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        text = match.group(1)
    try:
        return yaml.safe_load(text) or {}
    except Exception:
        return {}


def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_date() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def analyze_paper(paper_yaml_path: str, full_text_path: str | None = None) -> dict:
    """Analyze a single paper against the existing knowledge base."""
    import anthropic

    client = anthropic.Anthropic()

    paper = yaml.safe_load(open(paper_yaml_path).read())

    questions = _load_all_questions()
    breakthroughs = _load_all_breakthroughs()
    kb_context = _build_kb_context(questions, breakthroughs)

    # Read full text if available
    content = ""
    if full_text_path and Path(full_text_path).exists():
        content = Path(full_text_path).read_text()[:80_000]
    else:
        content = paper.get("abstract", "")

    # Step 1: Extract claims and assess significance
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {"type": "text", "text": SYSTEM_PROMPT},
            {
                "type": "text",
                "text": kb_context,
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[
            {
                "role": "user",
                "content": CLAIM_EXTRACTION_PROMPT.format(
                    title=paper.get("title", ""),
                    authors=", ".join(paper.get("authors", [])),
                    abstract=paper.get("abstract", ""),
                    full_text=content[:30_000],
                ),
            }
        ],
    )
    analysis = _parse_yaml_response(response.content[0].text)

    # Step 2: Map to existing questions
    response2 = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {"type": "text", "text": SYSTEM_PROMPT},
            {
                "type": "text",
                "text": kb_context,
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[
            {
                "role": "user",
                "content": QUESTION_MAPPING_PROMPT.format(
                    title=paper.get("title", ""),
                    claims=yaml.dump(analysis.get("claims", [])),
                    questions_summary=_questions_summary(questions),
                ),
            }
        ],
    )
    mapping = _parse_yaml_response(response2.content[0].text)

    suggestion = {
        "paper_ref": paper.get("arxiv_id", ""),
        "paper_title": paper.get("title", ""),
        "analyzed_at": _now_iso(),
        "claims": analysis.get("claims", []),
        "significance_assessment": analysis.get("significance", "incremental"),
        "question_mappings": mapping.get("mappings", []),
        "new_questions_suggested": mapping.get("new_questions", []),
        "is_breakthrough": analysis.get("significance", "") in ("paradigm-shift", "major"),
        "confidence": analysis.get("confidence", 0.5),
        "reasoning": analysis.get("reasoning", ""),
    }

    return suggestion


def analyze_batch(limit: int = 20):
    """Analyze new papers that haven't been analyzed yet."""
    SUGGESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    papers_dir = DATA_DIR / "papers"

    if not papers_dir.exists():
        print("No papers found. Run fetch_papers first.")
        return

    # Find papers not yet analyzed
    already_analyzed = set()
    for path in SUGGESTIONS_DIR.glob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        if data and "paper_ref" in data:
            already_analyzed.add(data["paper_ref"])

    paper_files = sorted(papers_dir.glob("*.yaml"))
    to_analyze = []

    for path in paper_files:
        paper = yaml.safe_load(path.read_text())
        if paper and paper.get("arxiv_id") not in already_analyzed:
            to_analyze.append(path)

    to_analyze = to_analyze[:limit]
    print(f"Analyzing {len(to_analyze)} papers...")

    for i, paper_path in enumerate(to_analyze):
        paper = yaml.safe_load(paper_path.read_text())
        arxiv_id = paper.get("arxiv_id", "unknown")
        print(f"  [{i+1}/{len(to_analyze)}] {arxiv_id}: {paper.get('title', '')[:60]}...")

        text_path = TEXT_DIR / f"{arxiv_id}.txt"

        try:
            suggestion = analyze_paper(
                str(paper_path),
                str(text_path) if text_path.exists() else None,
            )
            out_path = SUGGESTIONS_DIR / f"{_now_date()}-{arxiv_id}.yaml"
            with open(out_path, "w") as f:
                yaml.dump(suggestion, f, default_flow_style=False, allow_unicode=True)
            print(f"    -> {suggestion['significance_assessment']} (confidence: {suggestion['confidence']})")
        except Exception as e:
            print(f"    Error: {e}")

        time.sleep(1)  # Rate limiting between API calls

    print(f"Done. Check {SUGGESTIONS_DIR} for suggestions.")


def main():
    parser = argparse.ArgumentParser(description="Analyze papers with Claude API")
    parser.add_argument("--batch-new", action="store_true", help="Analyze new unprocessed papers")
    parser.add_argument("--limit", type=int, default=20, help="Max papers to analyze")
    parser.add_argument("--paper", type=str, default=None, help="Analyze a single paper YAML file")
    args = parser.parse_args()

    if args.paper:
        suggestion = analyze_paper(args.paper)
        print(yaml.dump(suggestion, default_flow_style=False))
    elif args.batch_new:
        analyze_batch(limit=args.limit)
    else:
        print("Specify --batch-new or --paper <path>")


if __name__ == "__main__":
    main()
