# Huashu Fusion Three-Layer Architecture

## Purpose

This repository now operates as a three-layer fusion system:

1. `google-design-fusion` provides retrieval-grounded design evidence.
2. `huashu-fusion-studio` translates that evidence into deterministic execution briefs.
3. Huashu-derived content provides execution doctrine for concrete artifact production.

The goal is to keep design reasoning source-backed while making delivery mode-specific and executable.

## Layer 1: Retrieval Engine (`google-design-fusion`)

Primary responsibility:

- Build/query the local fused corpus and return retrieval packets by phase (`research|concept|wireframe|ui|polish|audit`).

Primary outputs:

- Retrieval-backed packet JSON with ranked evidence and guardrails.
- Traceable sources from the checked-in local vector corpus.

Boundary:

- Does not decide final artifact production workflow.

## Layer 2: Orchestrator (`huashu-fusion-studio`)

Primary responsibility:

- Act as an execution-first orchestrator that converts retrieval packets into execution briefs.

Primary outputs:

- Deterministic execution brief contract fields (`artifact_mode`, execution rules, verification rules, export targets, evidence mapping).
- Mode routing for downstream execution (`prototype`, `slides`, `motion`, etc.).

Boundary:

- Does not replace retrieval logic from `google-design-fusion`.
- Does not claim ownership of upstream huashu doctrine content.

## Layer 3: Execution Doctrine (huashu-derived subset)

Primary responsibility:

- Provide derived workflow doctrine and production conventions for asset handling, export paths, and execution behavior.

Source and location:

- Derived from `alchaincyf/huashu-design` ([upstream repository](https://github.com/alchaincyf/huashu-design)).
- Can be synced locally into `skills/huashu-fusion-studio/vendor/huashu-derived/` when execution doctrine is needed.

Boundary:

- Doctrine guides execution behavior but does not override retrieval provenance requirements.

## End-to-End Flow

1. A task request enters with a design intent and target artifact mode.
2. `google-design-fusion` returns retrieval evidence packet(s).
3. `huashu-fusion-studio` compiles packet -> execution brief.
4. The orchestrator routes by `artifact_mode` and applies huashu-derived doctrine.
5. Verification checks ensure evidence coverage and export readiness.

## Provenance and License Boundary

- Repository-wide MIT licensing in this repo does not relicense upstream huashu-derived materials.
- Huashu-derived subset from `alchaincyf/huashu-design` remains governed by upstream `Personal Use License` constraints whenever it is generated locally.
- Attribution and source linkage must remain visible in docs and manifests.
- Exact local constraints are documented in `skills/huashu-fusion-studio/references/provenance-and-license.md`.
