# Architecture Guide

This is the ownership map for a change to the exhibit. It deliberately describes
the source tree, not a particular generated build number.

## Source Ownership

Edit `src/parts/` and `src/vendor/`. `build.py` assembles those sources into the committed root and `dist` bundles, increments build metadata, and syncs the vendored SSLI runtime. Generated `index.html`, `dist/index.html`, `ssli/`, and `dist/ssli/` are build outputs. A direct edit to a generated bundle is intentionally disposable: make the equivalent source edit and rebuild instead.

`build.py` patches a small, named set of upstream SSLI runtime seams. Those patches are not general forks: each must be idempotent, fail loudly when its upstream anchor drifts, and have a regression test. See [Source Provenance](source-provenance.md) before changing a patch or upgrading the vendored runtime.

## Runtime Boundaries

- `src/parts/index.html`: semantic shell and stable `data-testid` interface.
- `src/parts/styles.css`: responsive/touch layout and light-language presentation.
- `src/parts/app.js`: state, rendering, practice evaluation, audio bridge, Web MIDI, diagnostics.
- `src/vendor/ssli/`: build-injected scale, preset, progression, and FX data.
- hidden `ssli/index.html` iframe: SSLI audio runtime; local WebAudio is fallback only.

The host is responsible for learner state, routing Web MIDI, and choosing presets.
The iframe owns SSLI instrument instances and WebAudio worklets. The host must
feature-detect the iframe API and degrade to its local guide-audio fallback;
never reach into SSLI internals as though they were a stable public API.

## Rendering Contract

`state` is the application model. `render()` derives DOM and `currentLightFrame`; do not use DOM as a second source of truth. `buildPadLightFrame()` is the shared UI/hardware light model. It resolves duplicate MIDI pitches to the cell nearest the vertical meridian before assigning hue, role, palette, and target effect.

The renderer is allowed to replace visual nodes. Event handlers and tests must
therefore target the documented `data-testid` hooks rather than cache DOM nodes
or infer application state from CSS classes. `currentLightFrame` is the output
contract for both the visual keyboard and Exquis lighting; changing it requires
checking both paths.

## Safety Invariants

- One MIDI pitch has one illuminated physical representation.
- UI key/mode changes render before hardware sync.
- Normal Exquis sync owns pads only; edge controls remain native.
- Every reproduced failure receives a narrow Playwright regression.

## Change Boundaries

| Change | Primary source | Required companion check |
| --- | --- | --- |
| UI/control/teaching state | `src/parts/app.js`, `src/parts/index.html`, `src/parts/styles.css` | Preserve `data-testid`; add a user-visible regression. |
| Layout or pitch geometry | `src/parts/app.js` | Verify duplicate-note canonicalization and all supported viewport/orientation tests. |
| SSLI preset/data selection | `src/vendor/ssli/` | Keep source provenance accurate and run the targeted preset/static tests. |
| SSLI runtime behavior | `build.py` patch table | Add an idempotence/upstream-anchor regression before rebuilding. |
| Exquis hardware behavior | `src/parts/app.js`, `docs/exquis-midi.md` | Test ordering and keep normal sync pads-only. |
| Public developer/debug surface | `src/parts/app.js` | Treat `window.__exquis*` hooks and `data-testid` values as test contracts. |

## Iteration Loop

1. State the behavior and invariant in `docs/capabilities.md` (and
   `src/capabilities.json` when it is manifest-backed).
2. Add the smallest static or Playwright regression that would have caught the
   failure. Confirm it exercises the intended source/build boundary.
3. Change versioned source only, run `python build.py`, and inspect the
   generated files rather than hand-editing them.
4. Run the focused test first, then the complete test command in the README.
5. Hardware-affecting changes also run the applicable manual script in
   `docs/uat-expressive-lighting.md`; browser evidence does not prove firmware
   behavior.

## Validation

`tests/test_exhibit_playwright.py` protects user-visible flows through the built
page. `tests/test_exhibit_static.py` protects source, build, and data contracts.
Start narrow, then run broader suites. `tools/preset_sweep.py` is a separate
audio/preset harness; smoke limits are diagnostic only and never acceptance
evidence.
