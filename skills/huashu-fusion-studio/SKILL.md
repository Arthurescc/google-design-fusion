---
name: huashu-fusion-studio
description: Use when a task must convert google-design-fusion retrieval evidence into a source-backed execution brief, then route that brief into artifact production workflows such as prototype, slides, motion, infographic, or critique.
---

# Huashu Fusion Studio

Use this skill when design reasoning must stay traceable while execution output stays mode-specific.

## System relationship (required framing)

- `google-design-fusion` = retrieval engine.
- `huashu-fusion-studio` = execution-first orchestrator.
- `alchaincyf/huashu-design` derived subset (synced locally into `vendor/huashu-derived/` when needed) = execution doctrine.

Interpretation rules:

- Retrieval evidence comes from `google-design-fusion` packets, not from ad-hoc stylistic guessing.
- `huashu-fusion-studio` is responsible for deterministic routing from packet to execution brief.
- The derived huashu subset contributes workflow/asset/export doctrine only; keep provenance and license boundaries explicit.
- The locally synced huashu-derived doctrine is a constrained upstream subset; some referenced upstream files may be intentionally absent in this repo snapshot.

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
  "principle_cluster": "",
  "style_seed_set": [],
  "motion_role": {
    "enabled": false
  },
  "brand_asset_requirements": {
    "require_logo": true,
    "require_product_images": true,
    "require_ui_screenshots": true
  },
  "layout_rules": [],
  "execution_rules": {
    "mode": "",
    "preserve_source_trail": true,
    "deterministic_routing": true
  },
  "verification_rules": {
    "require_source_evidence": true,
    "require_export_targets": true,
    "run_motion_checks": false
  },
  "export_targets": [],
  "evidence": []
}
```

`motion_role` may also carry packet-provided fields like `role`, `motion_kinds`, `evidence_count`, and `evidence_scope` when present.

## Core references

- `references/orchestration-workflow.md`
- `references/execution-brief-contract.md`
- `references/artifact-routing.md`
- `references/provenance-and-license.md`
- `references/asset-protocol.md`
