"""Static site generator — reads _data/, writes ai-breakthroughs/."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "_data"
TEMPLATE_DIR = ROOT_DIR / "_templates"
STATIC_SRC = ROOT_DIR / "_static"
OUTPUT_DIR = ROOT_DIR / "ai-breakthroughs"

BASE_URL = "/ai-breakthroughs"


def get_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=ROOT_DIR,
        )
        return result.stdout.strip()[:8]
    except Exception:
        return "dev"


def build():
    from .loaders import load_site_data
    from .timeline_data import build_timeline_json
    from .search_index import build_search_index

    print("Loading data...")
    data = load_site_data(DATA_DIR)

    print(f"  {len(data.questions)} questions, {len(data.breakthroughs)} breakthroughs, {len(data.progress)} progress updates")

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=True,
    )
    env.globals["base_url"] = BASE_URL
    env.globals["build_meta"] = {
        "git_sha": get_git_sha(),
        "build_date": __import__("datetime").date.today().isoformat(),
    }
    env.globals["data"] = data

    # Ensure output dirs exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "static" / "js" / "vendor").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "static" / "data").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "questions").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "breakthroughs").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "open-questions").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "eras").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "search").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "about").mkdir(parents=True, exist_ok=True)

    # --- Generate data files ---
    print("Building timeline data...")
    (OUTPUT_DIR / "static" / "data" / "timeline.json").write_text(
        build_timeline_json(data)
    )

    print("Building search index...")
    (OUTPUT_DIR / "static" / "data" / "search-index.json").write_text(
        build_search_index(data)
    )

    # --- Render pages ---
    print("Rendering pages...")

    # Landing page
    tmpl = env.get_template("index.html")
    answered = [q for q in data.questions if q.status == "ANSWERED"]
    open_qs = [q for q in data.questions if q.status in ("OPEN", "PARTIALLY_ANSWERED")]
    (OUTPUT_DIR / "index.html").write_text(tmpl.render(
        answered_questions=answered,
        open_questions=open_qs,
        recent_breakthroughs=data.breakthroughs[-5:],
    ))

    # Questions list
    tmpl = env.get_template("questions_list.html")
    (OUTPUT_DIR / "questions" / "index.html").write_text(tmpl.render(
        questions=data.questions,
    ))

    # Individual question pages
    tmpl = env.get_template("question.html")
    for q in data.questions:
        qdir = OUTPUT_DIR / "questions" / q.slug
        qdir.mkdir(parents=True, exist_ok=True)
        (qdir / "index.html").write_text(tmpl.render(question=q))

    # Individual breakthrough pages
    tmpl = env.get_template("breakthrough.html")
    for b in data.breakthroughs:
        bdir = OUTPUT_DIR / "breakthroughs" / b.slug
        bdir.mkdir(parents=True, exist_ok=True)
        (bdir / "index.html").write_text(tmpl.render(breakthrough=b))

    # Open questions dashboard
    tmpl = env.get_template("open_questions.html")
    (OUTPUT_DIR / "open-questions" / "index.html").write_text(tmpl.render(
        questions=open_qs,
    ))

    # Era pages
    tmpl = env.get_template("era.html")
    for era in data.eras:
        era_qs = [q for q in data.questions if q.era == era.id]
        era_bs = [b for b in data.breakthroughs
                  if any(qid in data.questions_by_id and data.questions_by_id[qid].era == era.id
                         for qid in b.question_ids)]
        edir = OUTPUT_DIR / "eras" / era.id
        edir.mkdir(parents=True, exist_ok=True)
        (edir / "index.html").write_text(tmpl.render(
            era=era, questions=era_qs, breakthroughs=era_bs,
        ))

    # Search page
    tmpl = env.get_template("search.html")
    (OUTPUT_DIR / "search" / "index.html").write_text(tmpl.render())

    # About page
    tmpl = env.get_template("about.html")
    (OUTPUT_DIR / "about" / "index.html").write_text(tmpl.render())

    # --- Copy static assets ---
    print("Copying static assets...")
    if STATIC_SRC.exists():
        shutil.copytree(STATIC_SRC, OUTPUT_DIR / "static", dirs_exist_ok=True)

    print(f"Build complete! Output in {OUTPUT_DIR}/")


if __name__ == "__main__":
    build()
