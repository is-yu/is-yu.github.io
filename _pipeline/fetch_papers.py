"""Fetch papers from arXiv API. Adapted from arxiv-sanity-preserver/fetch_papers.py.

Reuses the arXiv API interaction pattern, feedparser parsing, and rate limiting
from the original. Outputs individual YAML files to _data/papers/ instead of
a pickle database.
"""

from __future__ import annotations

import argparse
import random
import time
import urllib.request

import feedparser
import yaml

from .config import (
    ARXIV_CATEGORIES,
    ARXIV_MAX_RESULTS_PER_FETCH,
    ARXIV_WAIT_SECONDS,
    DATA_DIR,
)

BASE_URL = "http://export.arxiv.org/api/query?"
PAPERS_DIR = DATA_DIR / "papers"


def parse_arxiv_url(url: str) -> tuple[str, int]:
    """Extract arxiv ID and version from URL.

    Adapted from arxiv-sanity-preserver utils.py.
    """
    ix = url.rfind("/")
    idversion = url[ix + 1:]
    parts = idversion.split("v")
    arxiv_id = parts[0]
    version = int(parts[1]) if len(parts) > 1 else 1
    return arxiv_id, version


def encode_feedparser_dict(d) -> dict:
    """Encode feedparser entry to a clean dict.

    Adapted from arxiv-sanity-preserver utils.py.
    """
    result = {}
    if d.get("title"):
        result["title"] = d["title"].replace("\n", " ").strip()
    if d.get("summary"):
        result["abstract"] = d["summary"].replace("\n", " ").strip()
    if d.get("authors"):
        result["authors"] = [a.get("name", "") for a in d.get("authors", [])]
    if d.get("links"):
        for link in d["links"]:
            if link.get("type") == "application/pdf":
                result["pdf_url"] = link["href"]
    if d.get("id"):
        result["abs_url"] = d["id"]
    if d.get("published"):
        result["published"] = d["published"]
    if d.get("updated"):
        result["updated"] = d["updated"]
    if d.get("arxiv_primary_category"):
        result["primary_category"] = d["arxiv_primary_category"].get("term", "")
    if d.get("tags"):
        result["categories"] = [t["term"] for t in d["tags"]]
    return result


def fetch_papers(
    search_query: str | None = None,
    start_index: int = 0,
    max_results: int = 200,
    results_per_iteration: int = 100,
    wait_time: float = 5.0,
):
    """Fetch papers from arXiv and save as YAML files."""
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    if search_query is None:
        search_query = "+OR+".join(f"cat:{cat}" for cat in ARXIV_CATEGORIES)

    print(f"Fetching papers for query: {search_query}")
    print(f"Starting at index {start_index}, max {max_results}")

    num_added = 0
    num_skipped = 0

    for i in range(start_index, max_results, results_per_iteration):
        batch_size = min(results_per_iteration, max_results - i)
        query = f"search_query={search_query}&sortBy=lastUpdatedDate&start={i}&max_results={batch_size}"
        url = BASE_URL + query

        print(f"Fetching batch {i}-{i + batch_size}...")

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                raw = response.read()
        except Exception as e:
            print(f"  Error fetching: {e}")
            time.sleep(wait_time)
            continue

        parse = feedparser.parse(raw)

        if not parse.entries:
            print("  No more entries. Done.")
            break

        for entry in parse.entries:
            paper = encode_feedparser_dict(entry)

            if "abs_url" not in paper:
                continue

            arxiv_id, version = parse_arxiv_url(paper["abs_url"])
            paper["arxiv_id"] = arxiv_id
            paper["version"] = version

            paper_path = PAPERS_DIR / f"{arxiv_id}.yaml"

            # Skip if already exists with same or newer version
            if paper_path.exists():
                existing = yaml.safe_load(paper_path.read_text())
                if existing and existing.get("version", 0) >= version:
                    num_skipped += 1
                    continue

            # Set defaults
            paper.setdefault("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}v{version}")
            paper.setdefault("categories", [])
            paper.setdefault("authors", [])
            paper.setdefault("doi", None)
            paper.setdefault("journal_ref", None)
            paper["has_full_text"] = False
            paper["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            with open(paper_path, "w") as f:
                yaml.dump(paper, f, default_flow_style=False, allow_unicode=True)

            num_added += 1

        print(f"  Processed {len(parse.entries)} entries. Added: {num_added}, Skipped: {num_skipped}")

        # Rate limiting (adapted from arxiv-sanity)
        time.sleep(wait_time + random.uniform(0, 1))

    print(f"\nDone. Added {num_added} new papers, skipped {num_skipped}.")


def main():
    parser = argparse.ArgumentParser(description="Fetch papers from arXiv")
    parser.add_argument("--search-query", type=str, default=None)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--max-results", type=int, default=ARXIV_MAX_RESULTS_PER_FETCH)
    parser.add_argument("--results-per-iteration", type=int, default=100)
    parser.add_argument("--wait-time", type=float, default=ARXIV_WAIT_SECONDS)
    args = parser.parse_args()

    fetch_papers(
        search_query=args.search_query,
        start_index=args.start_index,
        max_results=args.max_results,
        results_per_iteration=args.results_per_iteration,
        wait_time=args.wait_time,
    )


if __name__ == "__main__":
    main()
