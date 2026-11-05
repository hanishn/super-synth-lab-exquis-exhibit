# UI Layout Templates

The app has two deliberate desktop layout templates.  Reuse them instead of
inventing a screen-specific header or card geometry.

## 1. Workbench

Use for destinations where the player configures something before returning to
the instrument: **Session** and **Hardware & Diagnostics**.

- An editorial header is always stacked in this order: eyebrow, title, deck.
- The header and control canvas share one left gutter.
- Related controls live in bordered work cards using the shared panel radius,
  background, spacing, labels, and primary-action treatment.
- Peer cards always have a direct title in the same position and type scale.
  Never leave a settings card to imply its purpose from its first field label.
- Status color belongs to the narrow status/action that needs it; it must not
  turn a whole workbench into a separate visual system.

The markup contract is `data-layout-template="workbench"`.  The Playwright
regression `test_regression_workbench_screens_share_header_hierarchy_and_content_gutter`
checks the visible hierarchy and shared gutter at laptop size.

## 2. Playfield

Use for active performance and learning: **Practice**.

- Keep the same application shell, navigation, typography, color tokens, and
  control treatment as a workbench.
- Give most of the canvas to the Exquis surface and notation rather than to a
  settings-form header.
- Put session editing behind the Session destination; active play controls stay
  in the transport/header around the instrument.

The markup contract is `data-layout-template="playfield"` on the stage.

## Change Checklist

Before adding a screen or changing a workspace layout:

1. Choose one of these two templates.
2. Add/adjust a semantic `data-testid` for the primary region.
3. Extend a viewport regression before implementing geometry changes.
4. Capture and inspect Practice, Session, and Hardware at the same laptop
   viewport; a local improvement that changes their shared scan order is a
   regression.
