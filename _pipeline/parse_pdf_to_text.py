"""Extract text from PDFs using pdftotext. Adapted from arxiv-sanity-preserver/parse_pdf_to_text.py.

Same pdftotext subprocess approach. Requires poppler-utils installed.
"""

from __future__ import annotations

import os
import subprocess

from .config import PDF_DIR, TEXT_DIR


def parse_pdfs():
    """Convert all PDFs in pdfs/ to text in texts/."""
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    if not PDF_DIR.exists():
        print("No PDFs directory found. Run download_pdfs first.")
        return

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs.")

    converted = 0
    skipped = 0

    for pdf_path in pdf_files:
        txt_path = TEXT_DIR / f"{pdf_path.stem}.txt"

        if txt_path.exists():
            skipped += 1
            continue

        try:
            # pdftotext invocation (same as arxiv-sanity)
            result = subprocess.run(
                ["pdftotext", str(pdf_path), str(txt_path)],
                capture_output=True,
                timeout=30,
            )
            if result.returncode != 0:
                # Create empty marker file on failure
                txt_path.write_text("")
                print(f"  Failed to convert {pdf_path.name}")
            else:
                converted += 1
        except subprocess.TimeoutExpired:
            txt_path.write_text("")
            print(f"  Timeout converting {pdf_path.name}")
        except FileNotFoundError:
            print("pdftotext not found. Install poppler-utils: brew install poppler")
            return

    print(f"Done. Converted {converted}, skipped {skipped} existing.")


def main():
    parse_pdfs()


if __name__ == "__main__":
    main()
