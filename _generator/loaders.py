"""Load YAML data files and build cross-reference graph."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel


class Era(BaseModel):
    id: str
    name: str
    start_year: int
    end_year: Optional[int] = None
    color: str
    description: str


class Category(BaseModel):
    id: str
    name: str


class KeyFinding(BaseModel):
    finding: str
    significance: str


class Question(BaseModel):
    id: str
    slug: str
    text: str
    description: str
    status: str
    category: str
    era: str
    date_first_posed: date
    date_answered: Optional[date] = None
    answered_by: list[str] = []
    related_questions: list[str] = []
    tags: list[str] = []
    # Populated by cross-reference
    breakthroughs: list = []
    progress_updates: list = []
    related_question_objects: list = []

    class Config:
        arbitrary_types_allowed = True


class Breakthrough(BaseModel):
    id: str
    slug: str
    title: str
    paper_refs: list[str] = []
    authors: list[str]
    date: date
    venue: str
    question_ids: list[str]
    key_findings: list[KeyFinding]
    significance_level: str
    new_questions_raised: list[str] = []
    context: str
    summary: str
    # Populated by cross-reference
    questions: list = []
    new_questions: list = []

    class Config:
        arbitrary_types_allowed = True


class Progress(BaseModel):
    id: str
    question_id: str
    paper_ref: str
    title: str
    authors: list[str]
    date: date
    finding: str
    impact_on_question: str
    advancement_level: str
    # Populated by cross-reference
    question: Optional[Question] = None

    class Config:
        arbitrary_types_allowed = True


class SiteData(BaseModel):
    eras: list[Era]
    categories: list[Category]
    questions: list[Question]
    breakthroughs: list[Breakthrough]
    progress: list[Progress]

    # Lookup dicts populated after loading
    questions_by_id: dict = {}
    breakthroughs_by_id: dict = {}
    eras_by_id: dict = {}
    categories_by_id: dict = {}

    class Config:
        arbitrary_types_allowed = True


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_site_data(data_dir: Path) -> SiteData:
    """Load all YAML data and build cross-reference graph."""

    # Load eras config
    eras_config = load_yaml(data_dir / "eras.yaml")
    eras = [Era(**e) for e in eras_config["eras"]]
    categories = [Category(**c) for c in eras_config["categories"]]

    # Load questions
    questions = []
    for path in sorted((data_dir / "questions").glob("q-*.yaml")):
        questions.append(Question(**load_yaml(path)))

    # Load breakthroughs
    breakthroughs = []
    for path in sorted((data_dir / "breakthroughs").glob("b-*.yaml")):
        breakthroughs.append(Breakthrough(**load_yaml(path)))

    # Load progress
    progress = []
    progress_dir = data_dir / "progress"
    if progress_dir.exists():
        for path in sorted(progress_dir.glob("p-*.yaml")):
            progress.append(Progress(**load_yaml(path)))

    # Build lookup dicts
    questions_by_id = {q.id: q for q in questions}
    breakthroughs_by_id = {b.id: b for b in breakthroughs}
    eras_by_id = {e.id: e for e in eras}
    categories_by_id = {c.id: c for c in categories}

    # Cross-reference: questions <-> breakthroughs
    for b in breakthroughs:
        for qid in b.question_ids:
            if qid in questions_by_id:
                q = questions_by_id[qid]
                q.breakthroughs.append(b)
                b.questions.append(q)
        for qid in b.new_questions_raised:
            if qid in questions_by_id:
                b.new_questions.append(questions_by_id[qid])

    # Cross-reference: questions <-> progress
    for p in progress:
        if p.question_id in questions_by_id:
            q = questions_by_id[p.question_id]
            q.progress_updates.append(p)
            p.question = q

    # Cross-reference: related questions
    for q in questions:
        for rqid in q.related_questions:
            if rqid in questions_by_id:
                q.related_question_objects.append(questions_by_id[rqid])

    # Sort progress by date (newest first)
    for q in questions:
        q.progress_updates.sort(key=lambda p: p.date, reverse=True)

    return SiteData(
        eras=eras,
        categories=categories,
        questions=sorted(questions, key=lambda q: q.date_first_posed),
        breakthroughs=sorted(breakthroughs, key=lambda b: b.date),
        progress=sorted(progress, key=lambda p: p.date, reverse=True),
        questions_by_id=questions_by_id,
        breakthroughs_by_id=breakthroughs_by_id,
        eras_by_id=eras_by_id,
        categories_by_id=categories_by_id,
    )
