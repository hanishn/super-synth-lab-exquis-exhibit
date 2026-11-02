# Unified Notation Theme System

## Goal

Every practice surface—the engraved score, piano roll, reference keyboard, and
Exquis pad map—must describe the same musical state through one semantic theme.
The default is the product's dark stage with light notation foreground. A later
theme switch must change the shared token set rather than require individual
renderer edits.

## Theme contract

The root element owns these semantic tokens:

| Token family | Meaning | Consumers |
| --- | --- | --- |
| `--notation-surface-*` | Notation rail/staff background, foreground, grid, border | engraved score, fallback/error states, piano roll |
| `--notation-pitch-*` | Default, completed, and active emphasis | score notes, roll notes, keyboard/pad state treatment |
| `--notation-current-*` | Non-semantic current-step glow/pulse | score, roll, reference keyboard, Exquis pads |
| `--instrument-*` | Shared dark physical-surface chrome | Exquis device and reference keyboard |

Pitch color remains data, not a theme override: renderer code exposes a pitch
hue/color per note. The active state may add motion, outline, or glow, but must
never replace that pitch color.

## Initial themes

- `dark` (default): near-black surface, white notation foreground, colored
  notes/pads, amber-white current glow.
- Future themes are a root attribute (`data-notation-theme`) that override the
  semantic tokens only. Renderer JavaScript must not branch on theme names.

## Acceptance criteria

1. A single root theme attribute changes score, roll, keyboard, and pad chrome
   without rewriting renderer output.
2. The engraved score uses the same dark surface and light foreground language
   as the rest of the practice stage.
3. Root/scale-degree colors remain identical across score, roll, reference
   keyboard, and Exquis pad map; current-step emphasis preserves them.
4. Tests verify token use, active-note color preservation, and a runtime theme
   switch across all four surfaces.
5. Desktop and tablet screenshots are visually inspected before review.

## Migration rule

New notation/UI color literals are prohibited unless they define a semantic
token. Existing literals are migrated surface-by-surface behind the contract,
starting with the active practice screen.
