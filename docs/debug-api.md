# Debug and Test API Contract

The following `window.__exquis*` names are deliberately supported for browser
regression tests and local diagnosis. They are not a customer-facing SDK. A
production feature must not call them; change them only with a matching
Playwright/static test and this document in the same commit.

## Stability Tiers

- **Contract:** the name, input shape, and named output fields below are relied
  upon by tests and may change only as a coordinated breaking test change.
- **Diagnostic:** fields not listed below are observational and may be extended
  or removed. Callers must not mutate returned objects.
- **Test injection:** `__exquisLatencyProbe` and mock MIDI output are fixtures,
  not application APIs; they exist only before/inside a test.

## Contract Hooks

| Global | Input | Contractual result / purpose | Primary coverage |
| --- | --- | --- | --- |
| `__exquisDebugLog` | `(kind, message)` | Appends a diagnostic event; diagnostic-only side effect. | diagnostics/browser tests |
| `__exquisDebugSnapshot` | `()` | Snapshot with held notes, voices, last MIDI, selected preset, and pending release-strum commits. | voice-lifecycle regressions |
| `__exquisDebugBuildGripExerciseEvent` | exercise-event spec | A normalized grip event or invalid result. | exercise schema tests |
| `__exquisDebugBuildHarmonyGripFixture` | `{rootMidi, quality, noteCount, inversion, compactVoicing?}` | Exact physical harmony fixture or `null`. | harmony/progression tests |
| `__exquisDebugBuildProgressionFixture` | `(fixtureId, tonicPc?)` | Ordered, playable progression fixture transposed to the optional tonic PC, or `null`. | progression fixture tests |
| `__exquisDebugBuildSsliProgressionFixture` | `(genreIndex, progressionIndex, tonicPc?, scaleId?)` | SSLI-derived playable progression or `null`. | SSLI progression tests |
| `__exquisDebugPromptMidis` | `()` | Current expected prompt MIDI list. | prompt/playback tests |
| `__exquisDebugShouldUseSsliPlayback` | `(presetApplied, hasOutput)` | Boolean SSLI playback decision. | audio routing tests |
| `__exquisDebugStartAfterAudioResume` | `(audioContext, start)` | Promise resolving true only after the context can start; used to test gesture/audio sequencing. | audio-resume tests |
| `__exquisDebugBuildVoiceLeadingTransition` | `{from, to}` harmony-fixture spec | Transition plan with retained anchors and movement score. | voice-leading tests |
| `__exquisDebugBuildExerciseLifecycleEvents` | `()` | Stable reduced lifecycle-event sample: `type`, `valid`, `musicalIntent`, `cellId`, `midi`, `targets`, `fingering`, `timing`. | lifecycle schema test |
| `__exquisDebugEvaluateGrip` | `(event, attempts)` | `{accepted, outcome, missing, wrong, timingSpreadMs, toleranceMs}`. | simultaneous-grip scoring tests |

## Light and SysEx Objects

`__exquisLightDebug` is contract-tier for pure inspection:

- `currentFrame()` returns `{pads}` as copied semantic pad records.
- `hardwareFrame()` returns `{padId, midi, role, isTarget, paletteIndex}` per
  physical pad. It is the assertion surface for canonical duplicate selection.
- `paletteRgbFor(pad)` and `intervalHue(interval)` expose deterministic color
  conversion only.

`__exquisSysexDebug` is contract-tier protocol construction/parsing. It must not
send MIDI. Tests that need sends use the mock output and assert exact byte
sequences.

| Member | Input | Result |
| --- | --- | --- |
| `build` | `(command, payload?)` | Official Exquis SysEx byte array. |
| `parse` | `(bytes)` | `{command, payload, bytes}` or `null` for a non-official/invalid packet. |
| `degreesFor` | `(scaleId?)` | Twelve 0/1 custom-scale degree flags, defaulting to selected scale. |
| `scaleIndexFor` | `(scaleId)` | Internal selectable scale index, or `0` when unknown. |
| `scaleIdForIndex` | `(index)` | Scale ID or empty string. |
| `exquisScaleNumberFor` | `(scaleId)` | Official hardware scale number, or `0` when unmapped. |
| `scaleIdForExquisNumber` | `(scaleNumber)` | Scale ID or empty string. |
| `developerMask` | none | Pads-only Developer Mode bitmask scalar. |
| `legacy` | `(command, payload?)` | Legacy diagnostic SysEx byte array only; never normal sync. |

When adding a global, document its tier, input/output shape, and a named test.
When removing one, delete its callers and table row in the same change; silent
renames are forbidden because the browser suite otherwise fails late and
cryptically—software's preferred form of hide-and-seek.
