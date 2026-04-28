"""Claude API prompt templates for paper analysis."""

SYSTEM_PROMPT = """\
You are an expert AI research historian and analyst. Your role is to analyze
academic papers and determine their significance in the history of artificial
intelligence research.

You have deep knowledge of:
- The full history of AI from the 1950s Dartmouth Conference to 2026
- Key paradigm shifts: symbolic AI, expert systems, connectionism, statistical ML,
  deep learning, foundation models
- The questions that drove each era of research
- How breakthroughs build on and relate to each other

You output structured YAML. Be precise, conservative in significance ratings,
and ground every claim in specific paper content.
"""

CLAIM_EXTRACTION_PROMPT = """\
Analyze the following paper and extract its key claims, findings, and significance.

**Paper**: {title}
**Authors**: {authors}

**Abstract**:
{abstract}

**Full Text** (truncated):
{full_text}

Respond in YAML with exactly this structure:

```yaml
claims:
  - claim: "<one-sentence factual claim>"
    evidence: "<brief evidence from the paper>"
    novelty: "high | moderate | low"
  - claim: "..."
    evidence: "..."
    novelty: "..."

significance: "paradigm-shift | major | significant | incremental"
# paradigm-shift: fundamentally changes how the field thinks (rare, ~1-2 per decade)
# major: important advance that enables new research directions
# significant: solid contribution that advances the state of the art
# incremental: useful but builds modestly on existing work

confidence: 0.0-1.0

reasoning: |
  Brief explanation of why this paper has the assessed level of significance,
  referencing specific claims and their relationship to the broader field.
```
"""

QUESTION_MAPPING_PROMPT = """\
Given the following claims extracted from the paper "{title}", map them to
existing questions in our AI breakthroughs knowledge base, and suggest any
new questions this paper raises.

**Extracted Claims**:
{claims}

**Existing Questions in Knowledge Base**:
{questions_summary}

Respond in YAML:

```yaml
mappings:
  - question_id: "q-NNN"
    relevance: "answers | partially-answers | provides-evidence | tangential"
    explanation: "How this paper relates to the question"
  - ...

new_questions:
  - text: "The new question this paper raises"
    category: "deep-learning | nlp | computer-vision | reinforcement-learning | generative-models | optimization | theory | symbolic-ai | robotics | safety-alignment"
    rationale: "Why this is an important open question"
  - ...
```

Only suggest new questions that are genuinely novel and important — not
restatements of existing questions. A good new question identifies a gap
revealed by this paper's findings.
"""
