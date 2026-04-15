# Harness

## Current maturity

This skill ships a focused retrieval harness, not a full autonomous agent runtime.

That is intentional. The current maturity is:

- corpus build
- retrieval
- guardrail injection
- validation

This corresponds to a narrow Tier 2 harness that is strong enough for design research and prompt shaping without pretending to be a general multi-agent runtime.

## Current layers

### 1. Corpus layer

`scripts/build_design_fusion_vector_db.py`

Responsibilities:

- crawl `design.google`
- ingest `awesome-design-md`
- chunk content
- build sparse hashed vectors
- write local manifests and indexes

### 2. Retrieval layer

`scripts/design_harness.py`

Responsibilities:

- accept `query + phase`
- score chunks from the local vector library
- apply metadata boosts
- inject guardrails
- emit a retrieval packet

### 3. Safety layer

The safety layer is prompt-level rather than tool-level:

- anti-pattern rejection
- motion-purpose checks
- hierarchy checks
- contrast checks
- anti-dashboard-slop checks

This is documented in `references/anti-patterns.md`.

### 4. Verification layer

- `scripts/validate_harness.py`
- `scripts/validate_skill_contract.py`
- `scripts/run_full_validation.py`

Responsibilities:

- retrieval smoke tests
- skill-structure checks
- end-to-end validation flow

## Why this shape

For this workspace, the biggest risk is not missing orchestration features. The biggest risk is using weak references, fusing too many styles, or generating generic AI UI.

So the harness is optimized for:

- strong local retrieval
- strong preflight guardrails
- low-friction repeatability

## Next extensions

If the skill grows, add these in order:

1. saved golden queries and regression tests
2. explicit anti-pattern scoring
3. prompt pack generation per phase
4. persistent task state for long studies
5. optional subagent verifier pass

Do not add multi-agent orchestration before the retrieval and verification loops stop changing.
