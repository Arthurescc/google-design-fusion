# Asset Protocol

- Declare required input assets before execution starts.
- Track missing brand assets explicitly in `brand_asset_requirements`.
- Keep `brand_asset_requirements` deterministic:
- `require_logo`: false only for `critique` mode.
- `require_product_images`: true for `prototype`, `slides`, `motion`, and `infographic`.
- `require_ui_screenshots`: true for `prototype` and `slides`.
- Separate mandatory assets from optional enhancement assets.
- Document final export targets and file packaging expectations per mode.
