---
name: huashu-fusion-studio
description: Use when a task must convert google-design-fusion retrieval evidence into a source-backed execution brief, then route that brief into artifact production workflows such as prototype, slides, motion, infographic, or critique.
---

# Huashu Fusion Studio

Use this skill when design reasoning must stay traceable while execution output stays mode-specific.

## System relationship (required framing)

- `google-design-fusion` = retrieval engine.
- `huashu-fusion-studio` = execution-first orchestrator.
- `alchaincyf/huashu-design` derived subset (`vendor/huashu-derived/`) = execution doctrine.

Interpretation rules:

- Retrieval evidence comes from `google-design-fusion` packets, not from ad-hoc stylistic guessing.
- `huashu-fusion-studio` is responsible for deterministic routing from packet to execution brief.
- The derived huashu subset contributes workflow/asset/export doctrine only; keep provenance and license boundaries explicit.

## When to use

- Retrieval evidence exists (or must be generated) with `google-design-fusion`.
- The next step is a deterministic execution brief for a concrete artifact mode.
- The delivery needs explicit provenance, routing, and verification rules.

## Execution-first contract

1. Accept a retrieval packet from `google-design-fusion` (or generate one through the harness path).
2. Produce an execution brief that satisfies `references/execution-brief-contract.md`.
3. Route by `artifact_mode` using `references/artifact-routing.md`.
4. Apply huashu-derived doctrine for execution behavior while preserving upstream attribution and license scope.
5. Verify coverage/export-readiness before final output.

Minimal execution-brief output stub (top-level keys):

```json
{
  "query": "",
  "phase": "",
  "artifact_mode": "",
  "dominant_story": "",
  "principle_cluster": [],
  "style_seed_set": [],
  "motion_role": "",
  "brand_asset_requirements": [],
  "layout_rules": [],
  "execution_rules": [],
  "verification_rules": [],
  "export_targets": [],
  "evidence": []
}
```

## Core references

- `references/orchestration-workflow.md`
- `references/execution-brief-contract.md`
- `references/artifact-routing.md`
- `references/provenance-and-license.md`
- `references/asset-protocol.md`
