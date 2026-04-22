# Provenance and License

## Provenance

- Derived from `alchaincyf/huashu-design`.
- Upstream repo: `https://github.com/alchaincyf/huashu-design`.
- Local derived subset is recorded in `vendor/huashu-derived/manifest.json`.
- Upstream license text is carried through verbatim at `vendor/huashu-derived/LICENSE.upstream.txt` (source: upstream `LICENSE`).
- `manifest.json` `source_ref` should be an immutable upstream commit SHA.
- This repository intentionally vendors a constrained doctrine subset, not a full mirror of upstream.
- Vendored doctrine docs can reference upstream-only files/tools that are not present in this repository snapshot.

## License Boundary

- Upstream license kind: `Personal Use License`.
- This derived skill must keep upstream attribution visible.
- The files under `vendor/huashu-derived/` are governed by upstream personal-use terms, not re-licensed to this repo's MIT license.
- This repository must not present the derived subset as commercially relicensed.
- Top-level exception ledger: `../../../THIRD_PARTY_LICENSES.md`.
