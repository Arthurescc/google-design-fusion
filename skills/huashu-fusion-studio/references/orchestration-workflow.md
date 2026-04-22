# Orchestration Workflow

1. If `--packet-in` is provided, load that retrieval packet fixture directly.
2. Otherwise run `skills/google-design-fusion/scripts/design_harness.py` with `--format json`.
3. Translate the packet into the execution-brief contract fields.
4. Route execution by deterministic `artifact_mode`.
5. Verify evidence coverage and export readiness before final output.
