# Huashu Fusion Studio Design

**Date:** 2026-04-22  
**Status:** Approved for planning  
**Host repository:** `E:\AI素材\前端设计\goole design`

## Goal

Create a new top-level skill in this repository that uses `huashu-design` as the execution-first design engine and uses `google-design-fusion` as the retrieval-first design intelligence layer.

The resulting skill should let an agent:

1. retrieve stronger design evidence before generating artifacts,
2. convert that evidence into a clear execution brief,
3. execute artifact production using `huashu-design`-style workflows,
4. stay portable across Codex, Claude Code, OpenClaw, and OpenCode.

## Why This Exists

The two systems solve different parts of the same problem:

- `google-design-fusion` is strong at principle retrieval, style seeding, motion references, and anti-AI-slop guardrails.
- `huashu-design` is strong at artifact execution: HTML-native prototypes, decks, motion pieces, expert critique, export chains, and staged design iteration.

Today they exist as separate systems. The desired new skill should combine them without flattening either one:

- `google-design-fusion` should remain the library and retrieval doctrine.
- `huashu-design` should become the execution doctrine.
- the new skill should act as the orchestrator between them.

## Decision Summary

The repository will keep the existing `google-design-fusion` skill intact and will add a new independent skill tentatively named:

`huashu-fusion-studio`

This new skill will:

- call into the existing `google-design-fusion` harness first,
- normalize the retrieved evidence into a `huashu execution brief`,
- apply a `huashu-design`-style delivery workflow,
- produce a portable, agent-agnostic output contract.

This is intentionally an additive architecture, not a rewrite of `google-design-fusion`.

## Source Boundary and License Constraint

`huashu-design` is not MIT. Its upstream `LICENSE` is a **Personal Use License** with explicit attribution requirements and explicit restrictions on company/team/commercial integration.

That changes the implementation boundary:

- This repository may derive a new skill from `alchaincyf/huashu-design` because it is a personal repository under the user's control and the upstream license explicitly allows personal derived skills with prominent attribution.
- The new skill must include **clear provenance and attribution** to `alchaincyf/huashu-design`.
- The new skill must **not** be documented as commercially safe or generally relicensable.
- The new skill should not silently present vendored `huashu-design` material as original work.

### Resulting design rule

The new skill will use a **controlled derivation model**:

- copy or derive only the execution-critical doctrine, scripts, and references needed for the fused workflow,
- record provenance in dedicated docs/manifests,
- avoid pretending that the upstream license became MIT by entering this repository.

## Scope

### In Scope

- Add a new orchestrator skill under `skills/huashu-fusion-studio/`
- Keep `skills/google-design-fusion/` unchanged as a reusable lower-level library
- Translate retrieval packets into a normalized execution brief
- Bring in `huashu-design` execution doctrine needed for:
  - prototype generation
  - slide/deck generation
  - motion/animation generation
  - infographic/data-viz generation
  - expert critique flow
- Add provenance and attribution docs
- Add validation coverage for the new skill
- Add user-facing README documentation for the new skill and its relationship to upstream systems

### Out of Scope

- Replacing `google-design-fusion`
- Rebuilding the whole repository around `huashu-design`
- Full upstream mirroring of `huashu-design` demos, gallery media, and large audio bundles
- Commercial licensing changes or relicensing
- Converting this repository into a generic website/app framework

## Architectural Model

The new skill will be a three-layer system.

### Layer 1: Retrieval Doctrine

Owner:

- `skills/google-design-fusion/`

Responsibility:

- retrieve principle evidence from `design.google`
- retrieve style seeds from `awesome-design-md`
- retrieve motion references from `galaxy-motion`
- apply phase-aware guardrails
- produce ranked evidence packets

The new skill must treat this layer as read-mostly infrastructure, not re-implement it.

### Layer 2: Execution Doctrine

Owner:

- derived from `huashu-design`

Responsibility:

- choose artifact mode: `prototype`, `slides`, `motion`, `infographic`, `critique`
- run staged design iteration:
  - assumptions
  - early draft
  - variations/tweaks
  - verification
  - export
- enforce asset-first design when a real brand/product is involved
- avoid generic web-dashboard tropes when producing non-web artifacts

This layer should inherit `huashu-design`'s worldview: HTML is the tool, not the visual endpoint.

### Layer 3: Orchestration Doctrine

Owner:

- `skills/huashu-fusion-studio/`

Responsibility:

- classify the user task
- decide which retrieval phase to run first
- convert retrieval output into execution input
- route to the correct artifact mode
- preserve source-backed rationale in the final output

This layer is the new product.

## User-Facing Workflow

The orchestrated flow should be:

1. **Task framing**
   Determine whether the request is primarily a prototype, deck, motion piece, infographic, or critique.

2. **Evidence retrieval**
   Run `google-design-fusion` against the right phase:
   - `research` for open-ended domain mapping
   - `concept` for design-direction branching
   - `ui` for surface language
   - `polish` for state/motion refinement
   - `audit` for critique

3. **Execution brief synthesis**
   Convert the retrieval packet into a `huashu execution brief` with:
   - dominant narrative or task
   - principle cluster
   - style seeds
   - motion role
   - anti-pattern guardrails
   - asset requirements
   - deliverable type
   - export targets

4. **Artifact execution**
   Follow `huashu-design` style workflow for the selected artifact type.

5. **Verification and export**
   Verify the artifact against the execution mode and return export instructions or export outputs.

6. **Final delivery**
   Return both:
   - design rationale
   - artifact production plan or artifact result

## Output Contract

The new skill should produce a stable four-part contract:

### 1. Task Framing

- task kind
- user objective
- core constraint
- success condition

### 2. Retrieved Design Packet

- phase used
- principle cluster
- style seeds
- motion strategy
- ranked source evidence
- explicit guardrails

### 3. Execution Brief

- artifact type
- information hierarchy
- brand/asset protocol
- layout direction
- component language
- interaction rules
- motion role
- export targets

### 4. Artifact / Export Plan

- implementation mode
- verification steps
- export steps
- optional critique pass

This contract must remain agent-agnostic so the skill can work across Codex, Claude Code, OpenClaw, and OpenCode.

## Repository Layout

Recommended new structure:

```text
skills/
  google-design-fusion/
  huashu-fusion-studio/
    SKILL.md
    references/
      orchestration-workflow.md
      execution-brief-contract.md
      artifact-routing.md
      provenance-and-license.md
      asset-protocol.md
    scripts/
      build_execution_brief.py
      validate_skill_contract.py
      validate_orchestration.py
      run_full_validation.py
    vendor/
      huashu-derived/
        manifest.json
        references/
        scripts/
        assets/
research/
  huashu-fusion-architecture.md
```

### Important boundary

The `vendor/huashu-derived/` directory should be a **curated subset**, not a blind mirror of the whole upstream repository.

## What Should Be Derived from `huashu-design`

The first implementation should bring in the execution-critical subset only.

### References to derive or adapt

- workflow
- verification
- critique guidance
- animation guidance
- slide/deck guidance
- editable PPTX guidance
- video export guidance
- tweaks system guidance
- design styles guidance where it materially helps artifact production

### Scripts to derive or adapt

- `render-video.js`
- `convert-formats.sh`
- `add-music.sh`
- `export_deck_pdf.mjs`
- `export_deck_pptx.mjs`
- `html2pptx.js`
- `verify.py`

### Assets to derive or adapt

- `animations.jsx`
- device/browser frame components
- `deck_stage.js`
- `deck_index.html`
- `design_canvas.jsx`

### What not to bring in initially

- large demo galleries
- bulky release media
- full BGM libraries unless they are required for a tested export path

This keeps the first fused skill focused, reviewable, and lighter to maintain.

## Core Translation Contract

The main new technical seam is the translation step between systems.

### Input

`google-design-fusion` packet:

- `phase`
- `phase_goal`
- `guardrails`
- `motion_strategy`
- `motion_guardrails`
- `evidence[]`

### Output

`huashu execution brief`:

- `artifact_mode`
- `dominant_story`
- `principle_cluster`
- `style_seed_set`
- `motion_role`
- `brand_asset_requirements`
- `layout_rules`
- `execution_rules`
- `verification_rules`
- `export_targets`

This translation layer is where the new skill differentiates itself. It should be deterministic enough to test.

## Validation Strategy

The new skill needs its own validation stack, separate from but compatible with `google-design-fusion`.

### Validation targets

1. **Skill contract validation**
   Ensure `SKILL.md`, references, and declared scripts are internally consistent.

2. **Orchestration validation**
   Ensure representative prompts map to the right:
   - artifact mode
   - retrieval phase
   - execution brief shape

3. **Provenance validation**
   Ensure attribution, upstream SHA/source metadata, and license notes are present and synchronized.

4. **Workspace validation**
   Ensure the new docs agree with the real file layout and the actual derived subset.

### Representative smoke cases

- app prototype request
- keynote/deck request
- launch animation request
- infographic request
- critique request
- vague request that must trigger design-direction advising before execution

## Risks and Mitigations

### Risk 1: License confusion

If upstream `huashu-design` material is copied without clear provenance, users may assume this repository remains entirely MIT-safe.

Mitigation:

- explicit provenance docs
- explicit derived manifest
- explicit README attribution
- no silent copying

### Risk 2: Collapsing retrieval and execution into one muddy prompt

If the new skill only pastes both doctrines together, it will become harder to test and easier for the agent to ignore the retrieval layer.

Mitigation:

- use the execution brief as a hard seam
- keep retrieval packet and execution brief distinct in output

### Risk 3: Repository bloat

Blindly mirroring `huashu-design` will inflate maintenance cost and review difficulty.

Mitigation:

- curated subset only in phase 1
- no full demo/media import in the first pass

### Risk 4: Motion over-application

Combining `galaxy-motion` with `huashu-design` animation/export tools could push the system toward ornamental motion.

Mitigation:

- preserve `google-design-fusion` motion guardrails
- keep motion role explicit in the execution brief
- forbid motion-by-default in non-motion tasks

## Alternatives Considered

### Alternative A: Replace `google-design-fusion`

Rejected because it destroys the current library role and makes migration harder.

### Alternative B: Fork `huashu-design` and move everything there

Rejected because it demotes the current repository into a source dump and increases maintenance complexity.

### Alternative C: Create a third separate repository

Rejected for now because it creates unnecessary packaging, sync, and release overhead before the new orchestration model is proven.

## Success Criteria

This design is successful if the implemented skill:

1. exists as a new top-level skill in this repository,
2. keeps `google-design-fusion` usable on its own,
3. exposes `huashu-design`-style execution through a source-backed execution brief,
4. documents and validates provenance clearly,
5. works as a portable agent workflow, not a Codex-only surface.

## Spec Self-Review

### Placeholder scan

No `TODO`, `TBD`, or empty sections remain.

### Internal consistency

The document consistently treats:

- `google-design-fusion` as the retrieval layer,
- `huashu-design` as the execution layer,
- `huashu-fusion-studio` as the orchestrator.

### Scope check

The scope is intentionally limited to:

- one new top-level skill,
- one translation seam,
- one curated derived execution subset,
- one validation stack.

This is focused enough for a single implementation plan.

### Ambiguity check

The main ambiguity was whether to fully mirror `huashu-design` or derive a controlled subset. This spec makes the decision explicit: **controlled subset first, with provenance and attribution as hard requirements**.
