---
name: google-design-fusion
description: Fuse design.google research, a local Google Design vector library, and awesome-design-md style references into a full design workflow for landing pages, app shells, brand systems, UI audits, and frontend design prompts. Use when Codex needs to (1) research Google Design principles, Material history, accessibility, motion, typography, AI UI, or hardware/XR design, (2) blend those principles with `awesome-design-md` visual samples, (3) retrieve references from the local `google-design-vector-db`, (4) generate or refine a distinctive UI direction, or (5) reject common AI-generated design mistakes before implementation.
---

# Google Design Fusion

## Overview

Use this skill to turn the local Google Design research corpus plus `awesome-design-md` into a structured design workflow. Treat `design.google` as the principle engine, `awesome-design-md` as the surface-style engine, and the local retrieval harness as the bridge between them.

## Preflight

Before proposing any UI, run this check mentally:

1. Remove decorative helper text, fake labels, and tiny captions unless they explain a real constraint.
2. Reject low-contrast gray text on colorful, glass, or gradient surfaces.
3. Ensure each screen has one dominant task, one dominant hero, or one dominant metric cluster.
4. Delete decorative cards, gauges, badges, glow, gradients, shadows, or charts that do not carry meaning.
5. Reject default component-library stacks unless typography, spacing, surface treatment, and state rules are explicitly re-authored.
6. Require obvious selected, current, hover, focus, and active states.
7. Let motion explain hierarchy, focus, causality, or responsiveness. Never animate for ornament alone.
8. Keep core actions out of tiny icon-only affordances, transient UI, or hover-only interactions.

If the request already contains these failure modes, say so and correct course before generating output.

Read [references/anti-patterns.md](references/anti-patterns.md) before any substantial UI direction, prompt writing, or critique.

## Workflow

### 1. Choose the phase

Use one of these phases:

- `research`: map the domain and principle space
- `concept`: choose a design thesis and contrast options
- `wireframe`: lock hierarchy, flow, and interaction rhythm
- `ui`: define the surface system, component language, and visual identity
- `polish`: refine copy density, motion, states, and finish
- `audit`: critique an existing design or prompt against the guardrails

Read [references/workflow.md](references/workflow.md) if the phase is not obvious.

### 2. Make sure the corpus exists

If the workspace vector library is missing or stale relative to the task, rebuild it from the workspace root:

```bash
python skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
```

This builds a local corpus from:

- `design.google` sitemap pages
- the sibling `awesome-design-md` repository that the builder script targets by default

### 3. Retrieve context

Use the harness to pull the best evidence for the task:

```bash
python skills/google-design-fusion/scripts/design_harness.py "AI glasses notification motion" --phase research --top-k 8
python skills/google-design-fusion/scripts/design_harness.py "brand-forward premium landing page typography" --phase ui --top-k 8
```

The harness gives you:

- phase guidance
- preflight guardrails
- ranked evidence across Google Design and `awesome-design-md`

Read [references/source-selection.md](references/source-selection.md) when deciding how much weight to give each source family.

### 4. Fuse principles and style samples

Use this fusion order:

1. Pick `1` principle cluster from Google Design.
2. Pick `2-3` strong style seeds from `awesome-design-md`.
3. Optionally add `1` stretch sample that changes the temperature, density, or geometry.
4. Translate the mix into explicit style axes before writing UI.

Never average many samples into one muddy result. Prefer a strong base plus one deliberate contrast.

Read [references/fusion-rules.md](references/fusion-rules.md) before combining multiple style families.

### 5. Produce the output

Your output should be structured enough that another model or engineer can use it directly. Depending on the request, this may be:

- a design direction
- a prompt pack for frontend generation
- a UI critique
- a style system
- a principle summary
- a retrieval-backed rationale

Before finalizing, read [references/output-contract.md](references/output-contract.md).

## When to use which source

- Use `design.google` for reasoning about attention, accessibility, motion, typography, color behavior, AI affordances, hardware constraints, and the evolution of Material.
- Use `awesome-design-md` for brand tone, surface language, component signatures, density, geometry, and landing-page/app-shell references.
- Use both when the user wants a polished, distinctive interface instead of a generic component-library layout.

## Scripts

- `scripts/build_design_fusion_vector_db.py`
  Rebuild the local design corpus and sparse vectors.
- `scripts/design_harness.py`
  Retrieve ranked evidence and guardrails for a query and phase.
- `scripts/validate_harness.py`
  Smoke-test retrieval quality.
- `scripts/validate_skill_contract.py`
  Check that the skill files are internally consistent.
- `scripts/run_full_validation.py`
  Run the recommended validation stack for this skill.

## References

- `references/workflow.md`
  Core phase flow and execution order.
- `references/source-selection.md`
  How to choose between Google Design, `awesome-design-md`, and anti-pattern guidance.
- `references/fusion-rules.md`
  How to fuse principle clusters and style samples without collapsing into AI slop.
- `references/anti-patterns.md`
  Guardrails and source-backed pitfalls to reject before generating UI.
- `references/output-contract.md`
  What the final output must contain.
- `references/harness.md`
  Current harness layers, responsibilities, and extension points.

## Validation

Run this before claiming the skill is ready:

```bash
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/google-design-fusion
python skills/google-design-fusion/scripts/validate_skill_contract.py
python skills/google-design-fusion/scripts/validate_harness.py
python skills/google-design-fusion/scripts/run_full_validation.py
```
