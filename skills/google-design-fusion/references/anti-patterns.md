# Anti-Patterns

Use this file before generating UI, prompts, or critiques.

## Hard rejects

- Do not use helper text, tooltip text, or popovers to patch unclear labels, vague icons, or weak hierarchy.
- Do not put semantic text in low-contrast gray on gradients, glass, or colorful fills.
- Do not add tiny decorative captions, badges, or labels that do not explain a real rule, risk, or state.
- Do not create fake KPI cards, gauges, rings, or charts without real metric semantics.
- Do not ship a default component-library dashboard stack as if it were a finished design system.
- Do not hide core actions in icon-only controls, hover-only affordances, transient UI, or tiny hit targets.
- Do not add motion without causality, focus guidance, or state feedback.

## High-risk symptoms

- purple-blue gradients carrying the entire identity
- glowing numbers with no semantic emphasis
- cards nested inside cards
- meaningless badges
- tiny captions
- progress rings for trivial metrics
- unclear selection states
- low-contrast sidebars
- ornamental glass with no information role

## Source-backed cues

The guardrails above are grounded in:

- Apple UI design tips
- Material accessibility, selection, motion, snackbar, error, responsive UI, and color guidance
- PatternFly form/help, popover, and dashboard guidelines
- NN/g visual design and image-usage guidance
- Stacey Barr on useless KPI gauges
- GitHub discussions and issues on low-contrast states and poor mobile affordances

See `references/anti-pattern-sources.md` for the fuller source list that backs these guardrails.
