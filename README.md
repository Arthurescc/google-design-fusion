<div align="center">
  <img src="./assets/logo.svg" width="124" alt="Google Design Fusion logo" />
  <h1>Google Design Fusion</h1>
  <p><strong>An open-source, cross-agent skill that fuses the full <code>design.google</code> idea system with curated <code>awesome-design-md</code> / <code>DESIGN.md</code> style references, then turns that fusion into a retrieval-backed front-end design workflow.</strong></p>
  <p><a href="./README.md">English</a> | <a href="./README.zh-CN.md">简体中文</a></p>
</div>

![Before and after comparison](./assets/screenshots/comparison.png)

## What It Is

`google-design-fusion` is not a prompt wrapper and not a loose folder of notes.

It is designed to be reusable across Codex, OpenClaw, Claude Code, Hermes Agent, and other tools that can read or adapt `SKILL.md`-style instructions.

It is a packaged skill system with:

- a local design corpus built from `design.google`
- a fused style layer built from `awesome-design-md`
- a retrieval harness that changes behavior by design phase
- anti-AI-slop guardrails for common front-end generation mistakes
- validation scripts that keep the skill, harness, and docs aligned

## Compatibility

This repo is intentionally packaged as a portable skill system, not a one-tool experiment.

- Works well in: Codex, OpenClaw, Claude Code, Hermes Agent
- Usually portable to: agents that support custom Markdown skills, instruction packs, or workflow playbooks
- Best fit: front-end design generation, design review, design-system direction, UI audits, and retrieval-backed prompt shaping

The goal is simple: make AI-generated front-end work feel more intentional, more reviewable, and much less generic.

## What It Comes From

This repository combines two source systems on purpose.

### 1. Judgment Layer

Source:

- the full crawlable `design.google` surface
- selected high-value external articles linked from legacy `design.google` pages

What it contributes:

- hierarchy and attention design
- motion used for meaning, not decoration
- typography, readability, and accessibility judgment
- AI trust, explainability, and human-centered interaction thinking
- ambient, hardware, and XR constraints when relevant

### 2. Style Layer

Source:

- `awesome-design-md`

What it contributes:

- visual atmosphere
- typography personality
- density and rhythm
- surface language
- component signatures and composition references

In short:

`design.google` provides judgment. `awesome-design-md` provides style seeds. The skill fuses them into one retrieval-guided workflow.

## Why It Exists

Most AI front-end output still falls into the same traps:

- fake KPI cards with no product meaning
- tiny helper text patching weak hierarchy
- too many focal points at once
- decorative gradients doing the explanatory work
- motion used as chrome instead of guidance
- generic component-library layouts passed off as finished design

This skill pushes the work upstream:

1. retrieve better design evidence first
2. reject common anti-patterns early
3. separate principles from style references
4. return a usable packet for concept, UI, polish, or audit work

## Validated Value

Current included corpus:

- `328` crawl records from the `design.google` site map and direct recovery passes
- `248` indexed `design.google` source pages
- `32` indexed high-value external references
- `54` `awesome-design-md` samples
- `6457` retrieval chunks in the local vector library

The generated corpus is checked into the repo because it is part of the skill's practical value, not just build output.

## Before / After

Artifacts in this repo:

- Without skill demo: [examples/without-skill/index.html](./examples/without-skill/index.html)
- With skill demo: [examples/with-skill/index.html](./examples/with-skill/index.html)
- Comparison page: [examples/comparison/index.html](./examples/comparison/index.html)
- Rendered comparison: [assets/screenshots/comparison.png](./assets/screenshots/comparison.png)

Observed difference:

| Without skill | With `google-design-fusion` |
| --- | --- |
| Stacked noise, fake metrics, decorative helper text | One dominant story, clearer hierarchy, restrained proof blocks |
| Style guessed from defaults | Style guided by retrieved references |
| No source trail | Evidence packet tied to corpus retrieval |
| Easy to drift into AI slop | Guardrails explicitly block common failure modes |

## Architecture

The repo is organized as a layered skill runtime.

### Corpus Builder

Implemented in:

- [skills/google-design-fusion/scripts/build_design_fusion_vector_db.py](./skills/google-design-fusion/scripts/build_design_fusion_vector_db.py)

Responsibilities:

- crawl `design.google`
- preserve canonical and redirect facts
- selectively ingest stable external design references
- ingest `awesome-design-md`
- build chunked sparse retrieval indexes and manifest metadata

### Retrieval Harness

Implemented in:

- [skills/google-design-fusion/scripts/design_harness.py](./skills/google-design-fusion/scripts/design_harness.py)

Responsibilities:

- classify requests by phase
- query the fused corpus
- weight results with phase-aware profiles
- inject anti-pattern guardrails
- return a reusable design packet

### Skill Surface

Implemented in:

- [skills/google-design-fusion/SKILL.md](./skills/google-design-fusion/SKILL.md)
- [skills/google-design-fusion/agents/openai.yaml](./skills/google-design-fusion/agents/openai.yaml)

Responsibilities:

- teach the model when and how to use the corpus
- separate research, concept, wireframe, UI, polish, and audit behavior
- keep source-backed reasoning visible

### Validation Layer

Implemented in:

- [skills/google-design-fusion/scripts/validate_skill_contract.py](./skills/google-design-fusion/scripts/validate_skill_contract.py)
- [skills/google-design-fusion/scripts/validate_harness.py](./skills/google-design-fusion/scripts/validate_harness.py)
- [skills/google-design-fusion/scripts/validate_workspace_docs.py](./skills/google-design-fusion/scripts/validate_workspace_docs.py)
- [skills/google-design-fusion/scripts/run_full_validation.py](./skills/google-design-fusion/scripts/run_full_validation.py)

Responsibilities:

- verify skill packaging
- verify harness behavior
- verify docs against the real corpus build

## Harness Mechanism

The harness is the operational core of the skill.

It works in four steps:

1. **Build the local library**
   The corpus builder creates a fused local index from `design.google`, selected external references, and `awesome-design-md`.

2. **Classify the request by phase**
   Requests are mapped to `research`, `concept`, `wireframe`, `ui`, `polish`, or `audit`.

3. **Retrieve with phase-specific rules**
   The harness applies phase profiles, source weighting, and per-page caps so `audit` does not behave like `ui`, and `polish` does not behave like `research`.

4. **Return a design packet**
   The output includes the phase goal, ranked evidence, anti-pattern guardrails, and deduped page-level references.

That is the main difference between this skill and a normal prompt template: the model is steered by retrieval, not just by taste claims.

## Anti-Pattern Guardrails

The skill includes explicit warnings against common AI front-end mistakes, including:

- meaningless KPI numerics
- tiny explanatory captions that hurt visual balance
- over-dense card grids
- ornamental motion with no product role
- style mixing without hierarchy discipline
- polished-looking output with no source-backed rationale

Related research:

- [research/ai-design-antipatterns.md](./research/ai-design-antipatterns.md)

## Repository Layout

```text
skills/google-design-fusion/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
google-design-vector-db/
research/
examples/
assets/
README.md
README.zh-CN.md
```

## Quick Start

Clone the repo, place the skill in your preferred agent skills workspace, and restart or refresh that agent.

Common locations:

```text
Codex:       ~/.codex/skills/google-design-fusion
Claude Code: ~/.claude/skills/google-design-fusion
OpenClaw:    ~/.openclaw/skills/google-design-fusion
Hermes:      ~/.hermes/skills/google-design-fusion
```

If you want to rebuild or inspect locally:

```bash
python skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
python skills/google-design-fusion/scripts/design_harness.py "premium glassmorphism landing page with calmer hierarchy" --phase ui --top-k 8
python skills/google-design-fusion/scripts/run_full_validation.py
```

## Research Docs

Key supporting documents:

- [research/design-google-site-map.md](./research/design-google-site-map.md)
- [research/design-google-principles.md](./research/design-google-principles.md)
- [research/google-design-awesome-fusion.md](./research/google-design-awesome-fusion.md)
- [research/ai-design-antipatterns.md](./research/ai-design-antipatterns.md)
- [research/validation-report.md](./research/validation-report.md)

## Publishing Notes

External references are only ingested when they pass a higher bar:

- stable access
- meaningful design-learning value
- usable text extraction quality

Video shells, weak redirects, and low-signal landing pages stay out of the indexed corpus.

## FAQ

### Is this only for Codex?

No. The repo uses an open `SKILL.md` structure and is meant to be reused across multiple coding-agent ecosystems.

### What makes this different from a design prompt collection?

It includes a local corpus, a retrieval harness, validation scripts, and explicit anti-pattern guardrails. The behavior comes from the system, not from one pasted prompt.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT. See [LICENSE](./LICENSE).
