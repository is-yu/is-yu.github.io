"""Build client-side search index for lunr.js."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .loaders import SiteData


def build_search_index(data: SiteData) -> str:
    """Build a JSON search index for client-side search.

    Since lunr.py may not be installed, we produce a simple JSON document
    list that search.js can index client-side on page load.
    """
    docs = []

    for q in data.questions:
        docs.append({
            "id": q.id,
            "type": "question",
            "title": q.text,
            "body": q.description,
            "tags": ", ".join(q.tags),
            "status": q.status,
            "url": f"/ai-breakthroughs/questions/{q.slug}/",
        })

    for b in data.breakthroughs:
        findings_text = " ".join(f.finding for f in b.key_findings)
        docs.append({
            "id": b.id,
            "type": "breakthrough",
            "title": b.title,
            "body": f"{b.summary} {findings_text}",
            "tags": b.significance_level,
            "authors": ", ".join(b.authors[:5]),
            "url": f"/ai-breakthroughs/breakthroughs/{b.slug}/",
        })

    for p in data.progress:
        docs.append({
            "id": p.id,
            "type": "progress",
            "title": p.title,
            "body": p.finding,
            "url": f"/ai-breakthroughs/questions/{data.questions_by_id[p.question_id].slug}/" if p.question_id in data.questions_by_id else "#",
        })

    return json.dumps({"docs": docs}, indent=2)
