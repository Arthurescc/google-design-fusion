# Orchestration Workflow

Scope note: `vendor/huashu-derived/` is a constrained upstream subset. Some referenced upstream files are intentionally not vendored here.

1. If `--packet-in` is provided, load that retrieval packet fixture directly.
2. Otherwise run `skills/google-design-fusion/scripts/design_harness.py` with `--format json`.
3. Translate the packet into the execution-brief contract fields.
4. Route execution by deterministic `artifact_mode`.
5. Verify evidence coverage and export readiness before final output.

Minimal export-tool prerequisites for huashu-derived scripts:

- Node.js runtime with dependencies installed for the vendored script workspace.
- `ffmpeg` available on `PATH` when the routed export target includes motion/video formats (`mp4`/`gif`).
- Missing external tools should fail fast (or explicitly skip export) while preserving execution-brief provenance output.
