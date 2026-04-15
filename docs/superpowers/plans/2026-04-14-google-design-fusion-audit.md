# Google Design Fusion Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Audit the `google-design-fusion` skill end-to-end, fix real defects, improve source recovery, and re-verify the whole workflow.

**Architecture:** Use the local spec as the source of truth, run parallel read-only audit passes for findings, then apply bounded fixes to the crawler, harness, validation chain, and docs. Rebuild the vector DB and rerun the full validation stack after each meaningful repair.

**Tech Stack:** Python 3.9 scripts, markdown docs, local JSON/JSONL vector artifacts, subagent review workflow

---

### Task 1: Run Parallel Audit Passes

**Files:**
- Read: `docs/superpowers/specs/2026-04-14-google-design-fusion-audit-design.md`
- Read: `skills/google-design-fusion/**/*.py`
- Read: `skills/google-design-fusion/**/*.md`
- Read: `research/*.md`
- Read: `google-design-vector-db/manifest.json`

- [ ] **Step 1: Dispatch read-only audit subagents**

Goal:
- one subagent audits crawler/source coverage
- one subagent audits skill contract + docs
- one subagent audits harness retrieval quality

Expected output:
- concise findings with severity
- explicit file targets
- suggested fixes only where confidence is high

- [ ] **Step 2: Collect findings and collapse them into a unified checklist**

Expected:
- duplicate findings merged
- only actionable issues retained
- issues grouped into crawler / harness / docs / hygiene

- [ ] **Step 3: Record the execution checklist in the controller context**

Expected:
- ordered list of fix tasks
- high-priority issues first

### Task 2: Improve Source Recovery and Failure Reporting

**Files:**
- Modify: `skills/google-design-fusion/scripts/build_design_fusion_vector_db.py`
- Modify: `research/validation-report.md`
- Modify: `google-design-vector-db/README.md`

- [ ] **Step 1: Write or update a failing recovery expectation**

Target behavior:
- redirected or legacy pages should either be ingested through a stable fallback or reported as unrecoverable external links with clear counts

Verification approach:
- rebuild vector DB and compare recovered vs unrecoverable counts

- [ ] **Step 2: Implement minimal crawler improvements**

Focus:
- relative redirects
- non-Next fallback pages
- short-link and external-link classification
- clearer warning buckets

- [ ] **Step 3: Rebuild the vector DB**

Run:

```bash
python skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
```

Expected:
- command exits `0`
- vector DB files are regenerated
- unresolved pages are explicitly enumerated

- [ ] **Step 4: Update validation/reporting docs**

Expected:
- counts and unresolved-page explanations match the fresh build output

### Task 3: Fix Skill and Harness Review Findings

**Files:**
- Modify: `skills/google-design-fusion/SKILL.md`
- Modify: `skills/google-design-fusion/agents/openai.yaml`
- Modify: `skills/google-design-fusion/references/*.md`
- Modify: `skills/google-design-fusion/scripts/design_harness.py`
- Modify: `skills/google-design-fusion/scripts/validate_harness.py`
- Modify: `skills/google-design-fusion/scripts/validate_skill_contract.py`
- Modify: `README.md`
- Modify: `research/*.md`

- [ ] **Step 1: Apply the smallest high-confidence fix set first**

Priority order:
- broken references
- misleading counts or claims
- harness ranking / duplication issues
- validation blind spots
- workspace hygiene issues

- [ ] **Step 2: Remove or prevent non-deliverable artifacts**

Expected:
- no stray cache directories inside the skill
- no empty asset directory unless justified

- [ ] **Step 3: Re-run targeted validations after each logical fix**

Run:

```bash
python skills/google-design-fusion/scripts/validate_skill_contract.py
python skills/google-design-fusion/scripts/validate_harness.py
```

Expected:
- both commands exit `0`

### Task 4: Re-verify the Full Skill

**Files:**
- Modify if needed: `research/validation-report.md`

- [ ] **Step 1: Run upstream structural validation**

```bash
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/google-design-fusion
```

Expected:
- `Skill is valid!`

- [ ] **Step 2: Run the full local validation stack**

```bash
python skills/google-design-fusion/scripts/run_full_validation.py
```

Expected:
- `Full validation passed.`

- [ ] **Step 3: Sanity-check retrieval outputs**

Run:

```bash
python skills/google-design-fusion/scripts/design_harness.py "AI glasses notification motion on transparent screens" --phase research --top-k 5
python skills/google-design-fusion/scripts/design_harness.py "brand-forward premium landing page typography" --phase ui --top-k 5
python skills/google-design-fusion/scripts/design_harness.py "audit generic AI dashboard anti-patterns" --phase audit --top-k 5
```

Expected:
- returned evidence is not obviously duplicated
- source family weighting matches the phase intent

- [ ] **Step 4: Update the validation report with fresh evidence**

Expected:
- report includes current counts
- report explains the remaining unresolved pages truthfully
