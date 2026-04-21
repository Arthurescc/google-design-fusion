# Galaxy Source Policy

## Role of galaxy-motion

`galaxy-motion` is not the principle layer and not the main surface-style layer.

It is a motion-reference layer derived from the vendored `uiverse-io/galaxy` snapshot.

Use it for:

- interaction references
- loading patterns
- hover feedback
- CTA polish
- transition examples

## Weighting rules

- `design.google` keeps authority on meaning, hierarchy, accessibility, and motion purpose
- `awesome-design-md` keeps authority on atmosphere, typography, geometry, and surface language
- `galaxy-motion` only joins when motion helps the request

## Anti-drift rule

If `galaxy-motion` starts to dominate a retrieval packet, reduce its weight until at least one principle or style source remains visible in the top evidence.

## Packaging rule

The full raw snapshot lives in `vendor/galaxy/`.

The retrieval harness should prefer the derived `skills/google-design-fusion/galaxy-motion/` layer, not the raw snapshot tree.
