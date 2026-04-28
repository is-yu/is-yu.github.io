"""Schema validation for all YAML data files."""

from __future__ import annotations

import sys
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, field_validator

from .config import DATA_DIR


class QuestionStatus(str, Enum):
    ANSWERED = "ANSWERED"
    OPEN = "OPEN"
    PARTIALLY_ANSWERED = "PARTIALLY_ANSWERED"


class SignificanceLevel(str, Enum):
    PARADIGM_SHIFT = "paradigm-shift"
    MAJOR = "major"
    SIGNIFICANT = "significant"
    INCREMENTAL = "incremental"


class AdvancementLevel(str, Enum):
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"


class Question(BaseModel):
    id: str
    slug: str
    text: str
    description: str
    status: QuestionStatus
    category: str
    era: str
    date_first_posed: date
    date_answered: Optional[date] = None
    answered_by: list[str] = []
    related_questions: list[str] = []
    tags: list[str] = []


class KeyFinding(BaseModel):
    finding: str
    significance: str


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
    significance_level: SignificanceLevel
    new_questions_raised: list[str] = []
    context: str
    summary: str


class Progress(BaseModel):
    id: str
    question_id: str
    paper_ref: str
    title: str
    authors: list[str]
    date: date
    finding: str
    impact_on_question: str
    advancement_level: AdvancementLevel


class Paper(BaseModel):
    arxiv_id: str
    version: int = 1
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: str
    pdf_url: str
    abs_url: str
    doi: Optional[str] = None
    journal_ref: Optional[str] = None
    fetched_at: Optional[str] = None
    has_full_text: bool = False


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


class ErasConfig(BaseModel):
    eras: list[Era]
    categories: list[Category]


def load_and_validate_yaml(path: Path, model_class):
    """Load a YAML file and validate against a pydantic model."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return model_class(**data)


def validate_all():
    """Validate all data files. Returns (errors, warnings)."""
    errors = []
    warnings = []

    # Load eras config
    eras_path = DATA_DIR / "eras.yaml"
    if not eras_path.exists():
        errors.append(f"Missing {eras_path}")
        return errors, warnings

    try:
        eras_config = load_and_validate_yaml(eras_path, ErasConfig)
        valid_eras = {e.id for e in eras_config.eras}
        valid_categories = {c.id for c in eras_config.categories}
    except Exception as e:
        errors.append(f"Invalid eras.yaml: {e}")
        return errors, warnings

    # Validate questions
    questions = {}
    for path in sorted((DATA_DIR / "questions").glob("q-*.yaml")):
        try:
            q = load_and_validate_yaml(path, Question)
            if q.id in questions:
                errors.append(f"Duplicate question ID {q.id}: {path}")
            questions[q.id] = q
            if q.era not in valid_eras:
                errors.append(f"{path}: unknown era '{q.era}'")
            if q.category not in valid_categories:
                errors.append(f"{path}: unknown category '{q.category}'")
        except Exception as e:
            errors.append(f"Invalid {path.name}: {e}")

    # Validate breakthroughs
    breakthroughs = {}
    for path in sorted((DATA_DIR / "breakthroughs").glob("b-*.yaml")):
        try:
            b = load_and_validate_yaml(path, Breakthrough)
            if b.id in breakthroughs:
                errors.append(f"Duplicate breakthrough ID {b.id}: {path}")
            breakthroughs[b.id] = b
            for qid in b.question_ids:
                if qid not in questions:
                    errors.append(f"{path.name}: references unknown question '{qid}'")
            for qid in b.new_questions_raised:
                if qid not in questions:
                    warnings.append(f"{path.name}: new_questions_raised references unknown '{qid}'")
        except Exception as e:
            errors.append(f"Invalid {path.name}: {e}")

    # Validate progress
    for path in sorted((DATA_DIR / "progress").glob("p-*.yaml")):
        try:
            p = load_and_validate_yaml(path, Progress)
            if p.question_id not in questions:
                errors.append(f"{path.name}: references unknown question '{p.question_id}'")
        except Exception as e:
            errors.append(f"Invalid {path.name}: {e}")

    # Cross-reference: answered_by should point to real breakthroughs
    for qid, q in questions.items():
        for bid in q.answered_by:
            if bid not in breakthroughs:
                errors.append(f"Question {qid}: answered_by references unknown breakthrough '{bid}'")
        for rqid in q.related_questions:
            if rqid not in questions:
                warnings.append(f"Question {qid}: related_questions references unknown '{rqid}'")

    return errors, warnings


def main():
    print("Validating data files...")
    errors, warnings = validate_all()

    for w in warnings:
        print(f"  WARNING: {w}")
    for e in errors:
        print(f"  ERROR: {e}")

    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"\nAll valid. {len(warnings)} warning(s)")


if __name__ == "__main__":
    main()
