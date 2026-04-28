"""Download PDFs for fetched papers. Adapted from arxiv-sanity-preserver/download_pdfs.py.

Same urllib download pattern with rate limiting and timeout protection.
"""

from __future__ import annotations

import argparse
import random
import shutil
import time
import urllib.request

import yaml

from .config import DATA_DIR, PDF_DIR


def download_pdfs(limit: int | None = None):
    """Download PDFs for all papers that don't have them yet."""
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    papers_dir = DATA_DIR / "papers"

    if not papers_dir.exists():
        print("No papers directory found. Run fetch_papers first.")
        return

    paper_files = sorted(papers_dir.glob("*.yaml"))
    print(f"Found {len(paper_files)} paper files.")

    downloaded = 0
    skipped = 0

    for path in paper_files:
        if limit and downloaded >= limit:
            break

        paper = yaml.safe_load(path.read_text())
        if not paper:
            continue

        arxiv_id = paper.get("arxiv_id", "")
        pdf_path = PDF_DIR / f"{arxiv_id}.pdf"

        if pdf_path.exists():
            skipped += 1
            continue

        pdf_url = paper.get("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}")

        try:
            print(f"  Downloading {arxiv_id}...")
            req = urllib.request.urlopen(pdf_url, timeout=10)
            with open(pdf_path, "wb") as f:
                shutil.copyfileobj(req, f)
            downloaded += 1
        except Exception as e:
            print(f"  Failed to download {arxiv_id}: {e}")

        # Rate limiting (adapted from arxiv-sanity)
        time.sleep(0.05 + random.uniform(0, 0.1))

    print(f"Done. Downloaded {downloaded}, skipped {skipped} existing.")


def main():
    parser = argparse.ArgumentParser(description="Download PDFs for fetched papers")
    parser.add_argument("--limit", type=int, default=None, help="Max PDFs to download")
    args = parser.parse_args()
    download_pdfs(limit=args.limit)


if __name__ == "__main__":
    main()
