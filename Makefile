# AI Breakthroughs — Build & Pipeline Orchestration

# === Data Pipeline ===
fetch:
	python -m _pipeline.fetch_papers

download:
	python -m _pipeline.download_pdfs

extract:
	python -m _pipeline.parse_pdf_to_text

analyze:
	python -m _pipeline.claude_analyzer --batch-new

review:
	python -m _pipeline.review_cli

merge:
	python -m _pipeline.merge_approved

validate:
	python -m _pipeline.validate_data

pipeline: fetch download extract analyze
	@echo "Pipeline complete. Run 'make review' to review suggestions."

# === Site Build ===
build:
	python -m _generator.build --output-dir ai-breakthroughs/

serve:
	python -m http.server 8000

# === Combined ===
all: pipeline review merge validate build

# === Testing ===
test:
	python -m pytest _tests/ -v

.PHONY: fetch download extract analyze review merge validate pipeline build serve all test
