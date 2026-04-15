# Contributing

Thanks for your interest in improving `google-design-fusion`.

## Scope

This repository contains:

- the publishable skill package in `skills/google-design-fusion/`
- the generated local vector library in `google-design-vector-db/`
- supporting research and audit docs in `research/` and `docs/`

## Before Opening Changes

Please keep changes focused and explain which of these areas you touched:

- source ingestion
- retrieval / ranking
- anti-pattern guardrails
- skill contract / docs
- validation pipeline

## Validation

Run the full local validation stack before opening a PR:

```bash
python skills/google-design-fusion/scripts/run_full_validation.py
```

If you changed ingestion or retrieval logic, rebuild the local corpus first:

```bash
python skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
```

## Contribution Guidelines

- Prefer small, reviewable changes.
- Keep the skill package portable.
- Do not add cache artifacts or temporary outputs.
- Treat external design references conservatively: only ingest sources with clear design-learning value.
