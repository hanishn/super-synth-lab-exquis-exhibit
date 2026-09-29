# Exquis Fingering Lab Capabilities

Version: `0.1.25`

This exhibit is a visual practice tool for the Intuitive Instruments Exquis. It is intentionally separated into versioned parts and built into standalone `index.html` and `dist/index.html` outputs by `build.py`.

## SSLI Reuse Policy

Before adding or changing a feature, check Super Synth Lab Instrument first. If SSLI already has a suitable implementation or data source, use that before writing new local logic.

Current SSLI-derived parts:

- `src/vendor/ssli/scales-modes.json` from `shared/assets/data/scales-modes.json`
- note naming and flat-key policy modeled from `shared/assets/constants.js`
- hex/isomorphic layout concepts drawn from `products/ssli/assets/ssli-ctrl-isogrid.js`
- SSLI preset libraries from `shared/assets/presets/*.json`
- SSLI FX preset chains from `shared/assets/data/fx-presets.json`

Local code is allowed only where Exquis-specific teaching behavior is not already present in SSLI.

## Current Capabilities

### Exquis Layout Model

Models the 61-key Exquis surface as an 11-row alternating 6/5 hex grid. The pitch model follows the documented Exquis concept: semitones move horizontally, and thirds move vertically through the grid.

This is a teaching model, not yet a hardware-calibrated dump from the firmware.

### Scale Path Visualizer

The exhibit recomputes scale membership when tonic or scale changes. This matters because the set of buttons available for a given key moves around the Exquis surface rather than behaving like a piano keyboard.

The current practice path is anchored to a selectable duplicate root button. By default, the exhibit chooses the most centered matching root for the selected tonic and physical orientation; the user can override it with the Center Root control.

The path starts on the selected root and ascends scale degrees to the next octave root. Fingering labels follow that root-to-octave order rather than labeling an arbitrary set of lit pads.

Octave labels are derived from the Exquis pitch propagation rule instead of note-name patches: each row is a chromatic semitone run, and row starts rise by alternating thirds from the bottom of the surface. The centered C on the Exquis model is `C3` (`r5c3`), so the default C-major practice path starts on `C3` and resolves to the virtual octave `C4`. All instances of the selected tonic pitch class are shown as tonic/root-colored keys; C major makes every C white, not only the selected practice root.

Supported scales in v0.1.0 are sourced from SSLI `scales-modes.json`:

- Major
- Minor
- Pent.Min
- Pent.Maj
- Chromatic
- Dorian
- Mixolydian
- Blues

### Left-Hand Fingering Overlay

The default view is left-hand practice. It offers three starter strategies:

- 4-finger ladder: `5-4-3-2`
- Thumb-assisted: `5-4-3-2-1`
- Position shift: `4-3-2-1`

The first goal is consistent physical motion, not a final universal fingering doctrine.

Right-hand mode is also selectable. It mirrors the starter finger patterns so the same centered-root practice path can be rehearsed with either hand.

The selected root keeps the first fingering assignment even when the virtual octave root is added to the practice path. This prevents octave bookkeeping from overwriting the visible root finger.

### Built-In Guide Audio

The exhibit includes a self-contained WebAudio guide tone fallback. SSLI sound presets are not approximated locally when SSLI is available; selected presets are applied through `SynthLab.presets.apply`, short guide notes use `SynthLab.audio.playNoteOnInstrument`, and Exquis MIDI performance uses `SynthLab.audio.startSustainedNote` / `stopSustainedNote`.

- Soft Wurli
- Round Sine
- Muted Pluck
- Test Tone with visible audio status
- SSLI preset selector with engine/category/preset selection delegated to the real SSLI preset/audio API for playback
- SSLI FX preset selector applying selected chains through the real SSLI `EffectChain` API when SSLI is available
- Filter type, cutoff, and resonance controls

SSLI preset selection is split into Engine, Category, and Preset controls. FX selection is split into FX Category and FX Preset controls.

Selected SSLI presets must change the actual generated sound, not just the UI label or diagnostic log. When the SSLI host is available, the Engine/Category/Preset selectors are populated from `SynthLab.presets.getEngines()`, `getCategoriesForEngine()`, and `getPresetsForEngineCategory()` instead of the exhibit's local preset bundle. Playback applies that runtime SSLI preset object through `SynthLab.presets.apply()` and verifies that playback sees the resulting instrument type/settings. The local preset bundle is only a fallback for no-SSLI/offline operation. The exhibit must not overwrite preset filter or effect settings with default local controls unless the user has explicitly changed those controls.

Some SSLI subtractive presets store filter cutoff values above the valid 0-1000 slider range. Before applying a runtime preset, the exhibit normalizes those cutoff values through SSLI `freqToSlider()` so WebAudio does not receive impossible multi-megahertz filter frequencies.

Physical-model presets must preserve their model parameters during preview. For example, `Physical / Plucked / Koto` must apply the runtime Koto settings (`model=pluck`, `damping=35`, `brightness=75`, `excitation=pick`, `bodySize=50`, `decayTime=60`) and one-shot preview/path playback must not force maximum global expression over the physical engine before the note is triggered.

The audio is for practice confirmation, not final performance tone. It lets the player hear the current target note and the full practice path without opening a DAW or plugin, while preserving SSLI preset identity when the SSLI engine is loaded.

Test Tone now bypasses SSLI and uses the boosted local output bus, so it remains a loud diagnostic reference and drives the local waveform display. The scope must show a non-flat waveform and retain a readable peak trace after playback instead of falling back to an invisible idle line. Preview and path playback can still exercise SSLI one-shot velocity/expression when SSLI is available.

Filter and FX controls now update the current SSLI instrument rather than only changing local labels or a fallback bus. The local WebAudio filter/FX path remains only for non-SSLI fallback audio.

Exquis touch pressure now maps to SSLI expression through `SynthLab.audio.setExpression`, using pressure to drive output gain and expression cutoff while the note is held.

The hidden SSLI host is now built with its app support files and audio worklet assets. SSLI engines are initialized before selected preset playback, and Exquis note-on velocity is floored to a stronger playable SSLI voice-start level so pressure-first MIDI messages do not create effectively silent notes.

When the Exquis reuses an MPE channel for a new note before a matching note-off arrives, the previous voice on that channel is explicitly stopped before the next note starts.

When the last Exquis-held MIDI voice is released, the exhibit also asks SSLI to stop all sustained notes. This is an idle-only cleanup pass, not a per-note panic button; it prevents stale SSLI runtime voices from accumulating after fast multi-key bursts.

Repeated Exquis note bursts must not reapply the selected SSLI preset for every incoming note, because preset application stops sustained SSLI voices. The exhibit caches the applied Engine/Category/Preset selection, invalidates that cache only when the user changes the sound selection, and prunes stale local MIDI voice bookkeeping when the active voice count exceeds the practice budget.

Stale note-off messages for voices that were already pruned are ignored with a diagnostic log entry instead of double-stopping SSLI voices or clearing the current touch state. While multiple notes are held, global SSLI expression follows the strongest currently held pressure. A pressure-zero packet for one note must not collapse output gain/cutoff while another note is still pressed.

For a single held note, pressure zero clears SSLI expression directly instead of falling back to the original note-on velocity. MIDI practice playback also normalizes the active SSLI instrument volume through `SynthLab.audio.setInstrumentVolume(inst, 100)` when a preset leaves the instrument volume lower, wraps `SynthLab.audio.getFinalDestination()` with a practice output boost for sustained-note voices, and logs the before/after volume plus boost gain so quiet-preset diagnosis is visible in the console.

When duplicate physical cells share the same exact MIDI note, incoming MIDI feedback highlights the centered matching cell by default. This keeps `C3` near the center (`r5c3`) instead of lighting an edge duplicate (`r4c0`) while still requiring an exact full MIDI note match.

### Repeatable Preset Sweep

Broad preset validation must use `tools/preset_sweep.py`, not inference from a few selected presets. The sweep builds/loads the standalone app with Playwright through a localhost HTTP server so the hidden SSLI frame is same-origin, enumerates the live Engine, Category, and Preset controls, can filter by engine/category/preset-name text for targeted checks, triggers playback for each selected preset, captures page errors and console errors, records SSLI instrument type/settings evidence after playback, samples the live SSLI analyser for waveform peak/RMS, spectrum peak/RMS, and waveform/spectrum hashes, and writes machine-readable JSON plus CSV results under `tmp_preset_sweep/`.

Useful commands:

```powershell
python tools/preset_sweep.py --limit 10
python tools/preset_sweep.py --engine Physical --category Plucked --preset-contains Koto
python tools/preset_sweep.py --output-dir tmp_preset_sweep_full
```

`--limit` is only for smoke/debug runs. Omitting it sweeps every preset visible through the UI.

### Responsive Practice Ergonomics

The page is designed around the Exquis surface first. Tonic, centered root, hand, fingering, orientation, and rotation stay in the top panel. SSLI preset, FX, and filter controls are visible in the right rail so sound design does not require opening a separate drawer.

Current ergonomic guarantees:

- Desktop and laptop layouts avoid document-level scrolling for the main practice workflow without masking or clipping the right rail.
- Horizontal orientation defaults to the corrected physical-facing view; the rotation control initially offers `Rotate 180` as the alternate view.
- Horizontal orientation rotates the physical key shapes with the surface instead of drawing upright hexes in a transposed grid.
- Desktop keeps the practice surface content-sized instead of stretching to the diagnostics sidebar.
- The keyboard viewport stays tight around the physical 61-key surface instead of showing a large empty grid.
- The rendered key field uses a tall compact Exquis-like silhouette, with six-key and five-key rows centered against each other instead of reading as a loose generic hex board.
- Adjacent keys now use regular-hex honeycomb math: all six sides match, and same-row/adjacent-row neighbors share edges without geometric gaps or overlap.
- Rotation toggles only between the two visually correct hardware views whose buttons read `Rotate 180` and `Rotate 0`; the broken `Rotate 90` / `Rotate 270` states are not exposed.
- The Exquis key field is scaled up to use available stage space on desktop and after viewport resize, while preserving the locked regular-hex geometry.
- Practice mode lights two in-scale pads per row. The C-major practice path is separately marked and fingered, while the broader purple key LEDs remain in-key rather than random physical lanes.
- Hardware-lit scale pads stay visibly lit in both horizontal and vertical practice views, even when they are not part of the current fingering path.
- Guide Tone selection is visually separate from the SSLI engine/category/preset and FX controls.
- The keyboard surface uses a plain controller pad field, not a cartesian background grid.
- Primary practice, sound, preset, FX, and filter controls remain visible at laptop size without relying on page clipping or document scrolling.
- The diagnostic console is visible during practice as a dock with Reset, Copy, and Exit controls.
- Mobile keeps the overall document width stable and makes the Exquis surface intentionally pannable.
- Tonic, in-scale, practice-path, current-step, and MIDI touch states use distinct visual treatments.
- Cutoff and resonance sliders expose live numeric values.
- Verbose diagnostics, calibration, and explanatory legend text are demoted from the always-visible no-scroll view.

## Planned Capabilities

### Hardware Calibration

Use real Exquis MIDI note output or the official developer layout data to confirm every physical key's MIDI pitch in the selected layout.

### Key Comparison

Compare two key/scale states side by side or as overlays, making key-dependent layout shifts obvious.

### Web MIDI Feedback

Incoming MIDI note highlights are exact full-MIDI-note matches. Pressing `C4` lights only keys whose `data-midi` is `60`; it must not light `C2`, `C3`, `C5`, or any other octave duplicate through pitch-class fallback.

The user can enable Web MIDI. The exhibit lists every MIDI input visible to Chrome/Edge, selects an Exquis/Intuitive Instruments input when available, lets the user manually switch inputs, listens for note-on messages, and highlights the nearest virtual cell.

Diagnostic fields are intentionally visible:

- MIDI status
- MIDI input selector
- visible device list
- activity/readout for the most recent note-on

### Hardware Calibration

Calibration is the feature that will move this from useful to trustworthy. The current build records in-session correct/mismatched target presses. Persistence/export is not implemented yet.

The current flow:

1. Exhibit highlights one virtual button.
2. User presses the corresponding physical Exquis button.
3. Exhibit records received MIDI note.
4. Matching pitch classes are marked verified.
5. Mismatches are marked for later map correction.

### Practice Coach

The MIDI coach now behaves like a basic drill teacher:

- Correct target notes increment correct count and streak.
- Wrong notes increment misses and reset streak.
- Auto advance moves to the next target after a correct note.
- Clearing the calibration session also resets drill score.

## Test Expectations

New feature workflow:

1. Add or update the capability description and acceptance criteria.
2. Add the unit or Playwright test for that behavior.
3. Verify the new test fails before implementation.
4. Implement the feature.
5. Iterate until the new test passes.
6. Run the full existing unit suite to verify no regressions.
7. Hand the page to human review.

Stated failure workflow:

Every stated failure from review must be added to `PlaywrightExhibitTests.STATED_FAILURE_REGRESSIONS` with a named `test_regression_*` method. The suite includes a meta-test that fails if a listed failure does not have a corresponding regression test.

Playwright tests should cover:

- 61 virtual keys render.
- Changing tonic changes the practice map.
- Changing scale changes the practice path.
- Stepper advances current note.
- Strategy changes update finger guidance.
- Guide audio controls are present and callable in browser tests.
- MIDI diagnostics list and switch visible inputs.
- Calibration preview mode changes UI guidance.
- MIDI coach tracks correct/missed/streak scoring.
- Mobile viewport keeps controls and keyboard usable.
- Desktop and medium-width layouts avoid avoidable empty space and horizontal overflow.
- Color states remain distinguishable for tonic, scale, path, current note, and MIDI touch feedback.
- Physical Exquis spacing stays compact, staggered, and close to the hardware-like honeycomb model.
- Hex neighbor geometry fails tests if gaps or overlap return in any supported orientation/rotation state.
- Center Root and Hand selectors update the practice path and fingering overlay.
- Practice-path notes stay on the two inner chains nearest the centered root.
