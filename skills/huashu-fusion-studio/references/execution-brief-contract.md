# Execution Brief Contract

Required keys in every execution brief:

- `query`
- `phase`
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
- `evidence`

Type contract (matches `scripts/build_execution_brief.py` output):

| Key | Type | Notes |
| --- | --- | --- |
| `query` | `string` | Original user query (or empty string fallback). |
| `phase` | `string` | Packet phase (`ui`, `concept`, `polish`, etc.). |
| `artifact_mode` | `string` | Deterministic mode (`prototype`, `slides`, `motion`, `infographic`, `critique`). |
| `dominant_story` | `string` | Sourced from packet `phase_goal`. |
| `principle_cluster` | `string` | Primary `design.google` title when available, otherwise fallback sentence. |
| `style_seed_set` | `string[]` | Stable `awesome-design-md` (or fallback) title list. |
| `motion_role` | `object` | Packet motion strategy object. `enabled:boolean` is expected for normal harness packets; `role`, `motion_kinds`, `evidence_count`, `evidence_scope` are optional but typed when present. |
| `brand_asset_requirements` | `object` | Booleans: `require_logo`, `require_product_images`, `require_ui_screenshots`. |
| `layout_rules` | `array` | Guardrail list from packet (default empty array). |
| `execution_rules` | `object` | Includes `mode:string`, `preserve_source_trail:boolean`, `deterministic_routing:boolean`. |
| `verification_rules` | `object` | Includes `require_source_evidence:boolean`, `require_export_targets:boolean`, `run_motion_checks:boolean`. |
| `export_targets` | `string[]` | Export list by `artifact_mode`. |
| `evidence` | `object[]` | Dict-only evidence entries after normalization. |
