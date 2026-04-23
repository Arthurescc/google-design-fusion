# Orchestration Workflow

Scope note: `vendor/huashu-derived/` is an optional local sync target for a constrained upstream subset. Some referenced upstream files are intentionally not copied into this repo by default.

1. If `--packet-in` is provided, load that retrieval packet fixture directly.
2. Otherwise run `skills/google-design-fusion/scripts/design_harness.py` with `--format json`.
3. Translate the packet into the execution-brief contract fields.
4. Route execution by deterministic `artifact_mode`.
5. Verify evidence coverage and export readiness before final output.

Minimal export-tool prerequisites for huashu-derived scripts after local sync:

- Node.js runtime with vendored dependencies installed from `vendor/huashu-derived/package.json` (`playwright@1.59.1`, `sharp@0.34.5`), e.g. `cd vendor/huashu-derived && npm install`.
- `ffmpeg` available on `PATH` when the routed export target includes motion/video formats (`mp4`/`gif`).
- Missing external tools should fail fast (or explicitly skip export) while preserving execution-brief provenance output.
