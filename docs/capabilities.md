# Exquis Fingering Lab Capabilities

Version: `0.1.26`

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

The current practice path is anchored to a selectable duplicate root button. Hand side and root-octave side are separate controls: Left/Right Hand changes the fingering scaffold, while Lower/Higher Root Octave chooses the one-octave practice range. By default, one-octave practice uses the higher valid range for the selected tonic; the user can switch to the lower range or override the exact physical root with the Start Button control.

The path starts on the selected root and ascends scale degrees to the next octave root. Fingering labels follow that root-to-octave order rather than labeling an arbitrary set of lit pads.

Octave labels are derived from the Exquis pitch propagation rule instead of note-name patches: each row is a chromatic semitone run, and row starts rise by alternating thirds from the bottom of the surface. The centered C on the Exquis model is `C3` (`r5c3`), so the default C-major practice path starts on `C3` and resolves to the virtual octave `C4`. All instances of the selected tonic pitch class are shown as tonic/root-colored keys; C major makes every C white, not only the selected practice root.

### Play Mode and Practice Mode

Practice mode is the guided coach. It shows the current target, upcoming path, explicit `Step` and `Finger` key labels, dimmed non-task keys, score, streak, and calibration/mismatch feedback. Practice-only controls such as Root Octave, Start Button, Hand, Exercise, Finger Pattern, Overlay, the target panel, drill panel, and stepper are visible only while practicing. Correct MIDI input can auto-advance the exercise; wrong input marks the miss without moving the step.

Play mode is the free instrument surface. It keeps all 61 Exquis keys visually available, shows physical note/octave labels, hides practice-only controls, preserves live MIDI highlighting and pressure visualization, and pauses scoring/auto-advance so sound, layout, and expressive poly-aftertouch can be tested without fighting the coach.

Play mode must preserve independent sustained-note ownership for chords: different MPE channels holding different MIDI notes remain active independently, releasing one note stops only that note, and scoring stays paused. Same-MIDI replacement is handled as explicit ownership transfer because SSLI's sustained-note API is MIDI-keyed rather than per-touch keyed.

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

The default view is left-hand practice using Natural clusters. It offers four starter strategies:

- 4-finger ladder: `5-4-3-2`
- Thumb-assisted: `5-4-3-2-1`
- Wrist-led pairs: `pinky-ring-ring-middle`
- Natural clusters: `pinky-ring-ring-middle-middle-index-index-index`
- Position shift: `4-3-2-1`

The first goal is consistent physical motion, not a final universal fingering doctrine.

Right-hand mode is also selectable. It mirrors the starter finger patterns so the same centered-root practice path can be rehearsed with either hand.

The selected root keeps the first fingering assignment even when the virtual octave root is added to the practice path. This prevents octave bookkeeping from overwriting the visible root finger.

### Fingering Exercises

Exercise mode is separate from hand, octave side, and fingering strategy so the same physical path can be practiced several ways:

- Root to octave: a straight, octave-aware scale ascent from the selected centered root.
- Two octaves: a full physical two-octave ascent. When the centered root cannot physically reach the second octave on the 61-key Exquis surface, practice mode selects a lower valid tonic root instead of reusing lower keys with fake octave labels.
- Inner-chain ladder: ascends the same inner two-chain path, then descends back to the selected root.
- Root returns: alternates each scale tone with the selected root to train a stable home reference.

All exercise modes reuse the selected Exquis root and the same octave/path-aware cells used by MIDI coaching and playback. Changing exercise mode changes the stepped practice path, not just the prompt text.

When the same pitch exists on multiple physical buttons, the practice path chooses the exact pitch first, keeps the two-chain path second, then favors the more centered duplicate. The target panel explains that choice for the current note. Finger numbers are presented as a strategy scaffold rather than piano law: the default Natural clusters strategy maps nearby notes to pinky, ring, middle, and index clusters, then explicitly cues a wrist/hand shift when the pattern repeats.

The target panel also reports a first-pass ergonomic movement load. The score is intentionally transparent: it combines physical button travel, a Fitts-style movement prior, repeated-finger movement, weak-finger pressure risk, and explicit hand-shift moments. It is not a universal truth engine; it is a tunable model based on the same research direction used by piano-fingering optimization and motor-control literature: Parncutt et al.'s ergonomic fingering model, Fitts' law for aimed movement, finger individuation/enslaving research, and MPE/continuous-control concerns around sustained pressure.

The ergonomic model is key/mode agnostic. It scores the current physical path after the tonic, scale/mode, root, and exercise have produced exact MIDI targets and Exquis button coordinates. Dorian, Mixolydian, Blues, two-octave, and future modes must keep the same movement-load features instead of falling back to C-major-specific presets.

### Built-In Guide Audio

The exhibit includes a self-contained WebAudio guide tone fallback. SSLI sound presets are not approximated locally when SSLI is available; selected presets are applied through `SynthLab.presets.apply`, short guide notes use `SynthLab.audio.playNoteOnInstrument`, plucked physical Exquis strums use onset-only physical model one-shots, and sustained Exquis MIDI performance uses `SynthLab.audio.startSustainedNote` / `stopSustainedNote`.

- Soft Wurli
- Round Sine
- Muted Pluck
- Test Tone with visible audio status
- SSLI preset selector with engine/category/preset selection delegated to the real SSLI preset/audio API for playback
- SSLI FX preset selector applying selected chains through the real SSLI `EffectChain` API when SSLI is available
- Filter type, cutoff, and resonance controls

SSLI preset selection is split into Engine, Category, and Preset controls. FX selection is split into FX Category and FX Preset controls, with both FX controls kept on the same visual row so the FX chain reads as one grouped decision.

Selected SSLI presets must change the actual generated sound, not just the UI label or diagnostic log. When the SSLI host is available, the Engine/Category/Preset selectors are populated from `SynthLab.presets.getEngines()`, `getCategoriesForEngine()`, and `getPresetsForEngineCategory()` instead of the exhibit's local preset bundle. Playback applies that runtime SSLI preset object through `SynthLab.presets.apply()` and verifies that playback sees the resulting instrument type/settings. The local preset bundle is only a fallback for no-SSLI/offline operation. The exhibit must not overwrite preset filter or effect settings with default local controls unless the user has explicitly changed those controls.

Some SSLI subtractive presets store filter cutoff values above the valid 0-1000 slider range. Before applying a runtime preset, the exhibit normalizes those cutoff values through SSLI `freqToSlider()` so WebAudio does not receive impossible multi-megahertz filter frequencies.

Physical-model presets must preserve their model parameters during preview. For example, `Physical / Plucked / Koto` must apply the runtime Koto settings (`model=pluck`, `damping=35`, `brightness=75`, `excitation=pick`, `bodySize=50`, `decayTime=60`) and one-shot preview/path playback must not force maximum global expression over the physical engine before the note is triggered.

The audio is for practice confirmation, not final performance tone. It lets the player hear the current target note and the full practice path without opening a DAW or plugin, while preserving SSLI preset identity when the SSLI engine is loaded.

Test Tone now bypasses SSLI and uses the boosted local output bus, so it remains a loud diagnostic reference and drives the local waveform display. The scope must show a non-flat waveform and retain a readable peak trace after playback instead of falling back to an invisible idle line. Preview and path playback can still exercise SSLI one-shot velocity/expression when SSLI is available.

Filter and FX controls now update the current SSLI instrument rather than only changing local labels or a fallback bus. The local WebAudio filter/FX path remains only for non-SSLI fallback audio.

For non-physical SSLI engines, Exquis touch pressure maps to SSLI expression through `SynthLab.audio.setExpression`, using pressure to drive output gain and expression cutoff while the note is held.

The hidden SSLI host is now built with its app support files and audio worklet assets. SSLI engines are initialized before selected preset playback, and Exquis note-on velocity is floored to a stronger playable SSLI voice-start level so pressure-first MIDI messages do not create effectively silent notes.

When the Exquis reuses an MPE channel for a new note before a matching note-off arrives, the previous voice on that channel is explicitly stopped before the next note starts.

Physical-model MIDI playback stays on SSLI sustained-note tracking, passes velocity into the physical engine, and scales new note velocity against the number of currently held physical voices. Three-note shapes must not force every physical note to maximum velocity or reapply the preset while independent voices are being added.

Physical-model MIDI poly-aftertouch is applied per held note through `SL.physical.updateNotePressure(midi, pressure, inst)`. It must not be collapsed into a shared global physical pressure value, because the Exquis is an expressive poly-aftertouch controller. SSLI Physical worklet voices maintain independent per-note pressure gain so pressure changes affect only the matching active note.

Plucked physical models route pressure per note for ownership and diagnostics, but continuous aftertouch does not modulate the Karplus-string amplitude after note-on. A plucked string receives its musical energy at the strummed onset; expressive pressure streams must not roughen the decaying resonator or reintroduce zipper/noise artifacts. Plucked strum groups use lower chord-specific output gain and velocity caps than sustained physical models, then trigger bounded SSLI one-shot physical notes through direct physical `noteOn` so held buttons do not behave like bowed/sustained instruments. Live plucked MIDI must not use helper playback that schedules a delayed physical `noteOff`, because that delayed release can sound like a second pluck while the finger is still held.

Every bundled SSLI preset carries an articulation capability description. Sustained presets start notes immediately, struck physical presets may use a short roll, and plucked physical presets use a bounded strum scheduler: near-simultaneous note-ons are captured for a small window, ordered by Exquis physical position, and released into SSLI with a minimum inter-onset gap capped by the preset spread. This is a general per-preset behavior, not a Nylon Guitar or two-note exception. The whole plucked strum group uses chord-context output gain and velocity shaping from the first onset, so the first note cannot fire as an over-loud solo pluck before the rest of the group arrives. Pressure received while a note is waiting in the strum buffer is captured as onset energy, generated plucked preset metadata must use `pressurePolicy: onset-only`, plucked aftertouch is ignored after the one-shot starts, lone buffered notes released before a strum forms are cancelled, and notes that have joined a multi-note plucked strum remain committed even if the player releases before the delayed strum slot fires.

The SSLI Physical worklet also scales summed output once more than four physical voices are active. Six independent Exquis voices must preserve per-note pressure while reducing total mix energy enough to avoid riding the soft clipper continuously.

Physical per-note pressure updates are rate-limited per held note before being sent to SSLI. Tiny rapid aftertouch wiggles are skipped, while large changes and zero-pressure release updates remain immediate. This protects six independent voices from flooding the physical worklet without collapsing poly-aftertouch into one global value.

Six-note physical pressure regressions must be tested with Playwright-driven MIDI against the actual audible SSLI signal path. The test samples final audio output, not only SSLI's pre-output instrument analyser or mocked API calls. Physical-model output must satisfy measurable loudness/headroom thresholds: solo voices remain audible, dense independent voices avoid sustained clipping, and cleanup returns the engine to idle.

The exhibit may use a small adapter around SSLI's final output routing so every engine reaches the same audible diagnostic path. That adapter is tested by output metrics, not treated as the core sound architecture.

When the last Exquis-held MIDI voice is released, exact per-note ownership cleanup must already have stopped all voices started by the exhibit. As a final failsafe, the exhibit may ask SSLI to stop all sustained notes only after MIDI idle; tests must prove normal note-on/note-off ownership first so the idle failsafe cannot mask lifecycle bugs.

Repeated Exquis note bursts must not reapply the selected SSLI preset for every incoming note, because preset application stops sustained SSLI voices. The exhibit caches the applied Engine/Category/Preset selection, invalidates that cache only when the user changes the sound selection, and prunes stale local MIDI voice bookkeeping when the active voice count exceeds the practice budget.

Stale note-off messages for voices that were already pruned are ignored with a diagnostic log entry instead of double-stopping SSLI voices or clearing the current touch state. While multiple notes are held, global SSLI expression follows the strongest currently held pressure. A pressure-zero packet for one note must not collapse output gain/cutoff while another note is still pressed.

For a single held note, pressure zero clears SSLI expression directly instead of falling back to the original note-on velocity. MIDI practice playback also normalizes the active SSLI instrument volume through `SynthLab.audio.setInstrumentVolume(inst, 100)` when a preset leaves the instrument volume lower, wraps `SynthLab.audio.getFinalDestination()` with a practice output boost for sustained-note voices, and logs the before/after volume plus boost gain so quiet-preset diagnosis is visible in the console.

When duplicate physical cells share the same exact MIDI note, incoming MIDI feedback highlights the centered matching cell by default. This keeps `C3` near the center (`r5c3`) instead of lighting an edge duplicate (`r4c0`) while still requiring an exact full MIDI note match.

### Repeatable Preset Sweep

Broad preset validation must use `tools/preset_sweep.py`, not inference from a few selected presets. The sweep builds/loads the standalone app with Playwright through a localhost HTTP server so the hidden SSLI frame is same-origin, enumerates the live Engine, Category, and Preset controls, can filter by engine/category/preset-name text for targeted checks, triggers playback for each selected preset, captures page errors and console errors, records SSLI instrument type/settings evidence after playback, pre-arms the audio analyser before playback, samples the live SSLI analyser or final SSLI output path for waveform peak/RMS, spectrum peak/RMS, and waveform/spectrum hashes, and writes machine-readable JSON plus CSV results under `tmp_preset_sweep/`.

The required mature-engine poly-pressure procedure is:

```powershell
python tools/preset_sweep.py --mature-engines-only --trigger six-note-midi --audio-sample-ms 900 --output-dir tmp_preset_sweep_mature_poly_full
```

That command sweeps every live UI preset under Subtractive, FM, and Physical, drives six Exquis-style MIDI notes on independent channels, continuously varies their channel pressure, samples the actual audible SSLI output, and fails on silence, engine mismatch, duplicate signatures within the same engine/category, clipping, browser errors, stale-log-only cleanup, or missing current voice cleanup from the app's diagnostic state snapshot.

The diagnostic console remains reachable at all times. Its collapsed state is a compact action strip, and Audio Diag opens a right-side console drawer on desktop/laptop viewports so logs can be read while the keyboard remains visible.

`--one-per-category` is a smoke/debug shortcut only. It selects the first live UI preset from each category so a quick run can confirm that every category is reachable, but it is not acceptance coverage and must not be used to skip hard presets.

Dense MIDI voice stacks use general runtime headroom protection. Subtractive/FM voices scale later independent note-on velocity and expression gain as held voice count rises, physical models scale output based on active voice count, and low-register filtered subtractive stacks preserve instrument volume so dense bass/drone voicings remain audible. The required behavior is user-facing: simultaneous and sequential independent notes must preserve pitch identity, remain audible, avoid extra tones/noise, and avoid sustained clipping. Implementation must not use note-name, interval, or preset-specific exceptions.

Hot resonant subtractive presets receive structural dense-poly headroom based on filter/Q/envelope/oscillator load. The exhibit caps expression gain before SSLI's internal synth path and uses a lower practice output gain for that class, so sweep-style transition presets avoid internal clipping without relying on preset-name exceptions.

Physical plucked-string presets must stay stable when two nearby buttons are pressed together under pressure. The pluck model uses band-limited/string-shaped noise excitation, picked plucks have enough solo energy to satisfy MIDI signature checks, and physical output gain steps down starting at the second held voice so Nylon Guitar-style adjacent plucks avoid harsh summed transients without muting dense polyphony.

Useful commands:

```powershell
python tools/preset_sweep.py --limit 10
python tools/preset_sweep.py --engine Physical --category Plucked --preset-contains Koto
python tools/preset_sweep.py --output-dir tmp_preset_sweep_full
python tools/preset_sweep.py --mature-engines-only --trigger six-note-midi --audio-sample-ms 900 --output-dir tmp_preset_sweep_mature_poly_full
python tools/preset_sweep.py --mature-engines-only --one-per-category --trigger six-note-midi --audio-sample-ms 900 --output-dir tmp_preset_sweep_mature_poly_smoke
```

`--limit` and `--one-per-category` are only for smoke/debug runs. Omitting both sweeps every preset visible through the selected UI filters.

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
- MIDI enablement is the first prominent side-rail action because connecting the Exquis is the first required user step.
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

### Exquis Key/Mode Sync

The exhibit can opt into Exquis key/mode synchronization through the official Developer Mode MIDI API. Web MIDI is requested with SysEx permission first; if SysEx is denied, the app falls back to input-only MIDI coaching and leaves Exquis sync disabled instead of breaking practice mode.

When Sync Key/Mode is enabled, the app sends official Exquis SysEx messages in the form `F0 00 21 7E 7F id ... F7`: setup Developer Mode with the Pads mask `01h`, root note command `06h`, scale-number command `07h`, refresh command `03h`, then Developer Mode off (`00h`). Tonic changes in the UI send root-note updates; scale/mode changes send the selected scale index, a refresh, and root/scale readback requests. Incoming Exquis root (`06h`) and scale (`07h`) messages update the UI without echoing the change back to the hardware.

Native key/mode sync follows the Exquis Developer Mode manual and the Loopy Pro/Patchstorage root-scale action pattern: briefly enter Developer Mode for Pads (`01h`), send Root Note (`06h`) or Scale Number (`07h`), then leave Developer Mode (`00h`). This avoids holding the Settings/Sound or encoder zones hostage while still driving the same native root/scale state that the physical dials edit. The MIDI Coach also has a Dial Listen button, which intentionally holds Pads + Encoders + Settings/Sound Developer Mode (`13h`) so Exquis can emit official root/scale SysEx, channel-16 encoder activity, or raw fallback MIDI while the user turns physical settings dials; this mode may affect normal pad/encoder/settings behavior and should be used only for calibration/debugging.

Hardware testing showed the physical Settings dials also emit channel-1 CC messages while Dial Listen is active: encoder rotations use CC `41..44`, and encoder clicks use CC `21..24`. The Exquis user guide states that holding Settings and turning encoder 2 changes the root note, while encoder 3 changes the scale. The app therefore treats raw CC `42` values `0..11` as hardware root notes and updates the UI tonic immediately. Raw CC `43` is interpreted through the Exquis scale-number table where known: `0` Major, `1` Dorian, `4` Mixolydian, and `5` Natural minor. Unsupported Exquis scale numbers such as Phrygian/Lydian remain logged as hardware scale numbers until the app supports those modes; the UI does not coerce them into the wrong local scale.

The MIDI Coach also includes a Probe action for hardware diagnosis. Probe sends a universal MIDI identity request, official Developer Mode setup/readback/refresh messages for masks `20h` and `3Fh`, legacy Exquis keepalive/header messages observed in older community tooling, and a final Developer Mode off command. Any incoming SysEx is logged as raw bytes before parsing so hardware/firmware protocol mismatches are visible in the console.

Native Probe is a narrower write diagnostic for root/scale sync. It sends the current UI root and scale as official Root Note (`06h`) and Scale Number (`07h`) writes under four labeled Developer Mode masks: Pads (`01h`), Settings/Sound (`10h`), Pads + Settings/Sound (`11h`), and Pads + Encoders + Settings/Sound (`13h`). The probes are spaced apart so the user can watch the hardware and report which mask, if any, changes the native Exquis key/mode display. Normal Sync remains conservative until that hardware behavior is verified.

The stage includes an Exquis edge-control map so hardware zones are visible in the UI with the same physical placement as the device, not merely as an inventory. In vertical/portrait layout, Encoder 1-4 are rendered above the hex keybed; Down/Up, the six-zone Slider, Undo/Redo, and the Settings/Sound/Record/Loop/Clips/Play-Stop action row are rendered below the keybed and remain visible above fixed build/console overlays. In horizontal layout, the edge-control map rotates with the physical surface: the bottom-control deck becomes the left side rail and the encoder edge becomes the right side rail, so the controls do not remain incorrectly above/below a landscape keybed or mirror the device. Horizontal mode must fit without clipping the practice stepper or pushing the hardware halfway down the stage; the rotated device should begin near the practice path strip. Horizontal hardware labels sit beside the controls rather than below them so the knob/button shapes remain visually primary. Labels follow the Exquis user guide and Developer Mode identifiers: Settings (`100`), Sound (`101`), Record (`102`), Loop (`103`), Clips (`104`), Play/Stop (`105`), Down (`106`), Up (`107`), Undo (`108`), Redo (`109`), Encoder 1-4 (`110..113`, play-mode CC `41..44`, clicks `21..24`), and Slider (`90`, portions `80..85`). When Developer Mode takes over a zone, the matching edge controls are marked as captured; incoming encoder/button/slider activity marks the most recent control active. This makes visible that masks such as `13h` intentionally turn off/take over edge controls while probing.

On the tested hardware, Probe produced a visible light change and an echoed legacy keepalive (`F0 00 21 7E F7`) while the official Developer Mode root/scale readback commands produced no response. Sync therefore also sends a legacy backend update: keepalive, per-pad MIDI note mapping (`F0 00 21 7E 04 pad note F7`), and legacy LED colors generated from the current UI tonic and mode. Legacy command `03h` targets note-color LEDs; command `07h` targets button-color LEDs and is the normal Sync default after hardware testing showed `03h` changed a different light set than the playable button lights. Normal Sync logs one compact summary per hardware update, sends note mapping once per sync session, debounces root/scale changes, and suppresses routine keepalive echo spam; Probe remains verbose for diagnostics. Because legacy pad numbering is not documented in the official API and may vary by firmware/orientation, the MIDI Coach exposes Legacy Map and Legacy Lights selectors for calibration.

Diagnostic fields are intentionally visible:

- MIDI status
- MIDI input selector
- visible device list
- Exquis key/mode sync status
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

New feature workflow invariant:

1. Update the durable spec first: `docs/capabilities.md` and, when behavior is tracked in the manifest, `src/capabilities.json`.
2. Update unit/static/Playwright tests second, including stated-failure regression tests when the work comes from a reported failure.
3. Verify the new or changed tests fail against the old behavior before implementation whenever the failure can be reproduced locally.
4. Implement only after the spec and tests describe the intended behavior.
5. Verify the targeted tests pass.
6. Run the full existing unit suite to verify no regressions.
7. Hand the page to human review with the build number and any residual test caveats.

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
- Start Button and Hand selectors update the practice path and fingering overlay.
- Practice-path notes stay on the two inner chains nearest the centered root.
