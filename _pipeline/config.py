import os
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).parent.parent

# Claude API
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_MODEL_DEEP = "claude-opus-4-6-20250918"
MAX_TOKENS = 4096
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# arXiv fetch
ARXIV_CATEGORIES = [
    "cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE",
    "cs.RO", "cs.MA", "stat.ML",
]
ARXIV_MAX_RESULTS_PER_FETCH = 200
ARXIV_WAIT_SECONDS = 5.0

# Paths
DATA_DIR = ROOT_DIR / "_data"
STAGING_DIR = ROOT_DIR / "_staging"
OUTPUT_DIR = ROOT_DIR / "ai-breakthroughs"
PDF_DIR = STAGING_DIR / "pdfs"
TEXT_DIR = STAGING_DIR / "texts"
PENDING_DIR = STAGING_DIR / "pending"
APPROVED_DIR = STAGING_DIR / "approved"

# TF-IDF (adapted from arxiv-sanity analyze.py)
TFIDF_MAX_FEATURES = 5000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MAX_TRAIN_DOCS = 5000
MIN_TEXT_LENGTH = 1000
MAX_TEXT_LENGTH = 500000
