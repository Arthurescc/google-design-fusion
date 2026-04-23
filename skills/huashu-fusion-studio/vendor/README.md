# Local Vendor Outputs

`huashu-derived/` is intentionally not checked into the default repository state.

Generate it locally only when you need execution doctrine from `alchaincyf/huashu-design`:

```bash
python skills/huashu-fusion-studio/scripts/sync_huashu_subset.py \
  --source-root ../huashu-design-upstream \
  --output-root skills/huashu-fusion-studio/vendor/huashu-derived \
  --source-ref <40-char-upstream-sha>
```

When present locally, `huashu-derived/` remains governed by upstream terms and is not relicensed to MIT by this repository.
