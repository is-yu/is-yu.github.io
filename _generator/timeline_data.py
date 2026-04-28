"""Generate timeline.json for D3.js visualization."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .loaders import SiteData


def build_timeline_json(data: SiteData) -> str:
    """Build the timeline JSON consumed by timeline.js."""

    eras = []
    for e in data.eras:
        eras.append({
            "id": e.id,
            "name": e.name,
            "start": e.start_year,
            "end": e.end_year or 2027,
            "color": e.color,
        })

    events = []

    # Add breakthroughs
    for b in data.breakthroughs:
        events.append({
            "id": b.id,
            "type": "breakthrough",
            "title": b.title[:60],
            "slug": b.slug,
            "date": b.date.isoformat(),
            "year": b.date.year,
            "significance": b.significance_level,
            "questions_answered": b.question_ids,
            "url": f"/ai-breakthroughs/breakthroughs/{b.slug}/",
        })

    # Add questions
    for q in data.questions:
        event_type = "question-answered" if q.status == "ANSWERED" else "question-posed"
        events.append({
            "id": q.id,
            "type": event_type if q.status == "ANSWERED" else "question-open",
            "title": q.text[:60],
            "slug": q.slug,
            "date": q.date_first_posed.isoformat(),
            "year": q.date_first_posed.year,
            "status": q.status,
            "category": q.category,
            "url": f"/ai-breakthroughs/questions/{q.slug}/",
        })

    # Connections (breakthrough -> question it answers)
    connections = []
    for b in data.breakthroughs:
        for qid in b.question_ids:
            connections.append({
                "from": b.id,
                "to": qid,
                "type": "answers",
            })

    timeline = {
        "eras": eras,
        "events": sorted(events, key=lambda e: e["date"]),
        "connections": connections,
    }

    return json.dumps(timeline, indent=2)
