# Vendored SSLI Runtime Patch Catalog

`build.py` applies named, text-anchored patches to the vendored SSLI runtime
copied from `external/SuperSynthLabInstrument`. This is a controlled compatibility
layer, not a place for anonymous production edits. The source provenance and
upstream location are recorded in [Source Provenance](source-provenance.md).

## Ownership and Upgrade Rule

Exhibit maintainers own the patch declarations and their tests; upstream owns
the unpatched runtime. Each patch has a unique `name`, exact `before` anchor,
and exact `after` replacement. `apply_required_text_patches()` accepts either
the before or after form (idempotence) and fails when neither is present
(upstream-anchor drift). Before an SSLI upgrade, run the static suite; resolve
every failed anchor by re-validating the upstream behavior rather than copying
old text until it happens to match.

## Catalog by Runtime Concern

| Prefix / count | Target | Intent | Verification |
| --- | --- | --- | --- |
| `disable-*` (2), `expression-*` (1) | SSLI page shell | Prevent stale service-worker audio and isolate the embedded host's MIDI ownership. | build-patch static tests; iframe cache regression |
| `voice-pool-*` (11) | page shell | Tokenize release cleanup so a reused voice cannot be released by an old timer. | patch-anchor test and voice lifecycle browser checks |
| `physical-note-on-*` (4), `physical-engine-*` (2) | page shell | Preserve owned one-shot voice IDs, bounded duration, pick position, and live pressure API. | physical runtime static tests |
| `physical-fallback-*` (14) | page shell fallback model | Deterministic excitation, smooth mute/duration, bounded decay, and physically meaningful pluck output. | physical source/worklet regression tests |
| `fm-fallback-*` (16) | page shell fallback FM | Correct DX7 operator routing, envelope/gain, feedback, and per-note frequency data. | DX7 patch/static tests |
| `fm-worklet-*` (16) | `assets/fm-worklet.js` | Apply the same DX7 correctness rules to the actual worklet. | ordered patch-name assertion plus worklet source checks |
| `physical-worklet-*` (29) | `assets/physical-worklet.js` | Keep physical-string, modal, bow, pressure, duration, owned note-off, and polyphony behavior aligned with the host API. | physical worklet static/audio tests |
| `subtractive-*` (3), `synth-worklet-*` (1) | page shell / synth worklet | Prevent low-level velocity/polyphony makeup regressions in sustained engines. | static runtime-patch tests |
| `phrase-audition-*` (12) | page shell / synth worklet | Use the real-time renderer and an audio-thread release deadline for dense authored songs, so UI work cannot make repeated notes stick. | browser dense-phrase timing and worklet-message regression |

The executable catalog is the named patch lists in `build.py`:
`SSLI_INDEX_PATCHES`, `SSLI_WORKLET_PATCHES`, `SSLI_FM_MIX_PATCHES`,
`SSLI_SYNTH_WORKLET_PATCHES`, and `SSLI_PHYSICAL_WORKLET_PATCHES`. The static
suite deliberately asserts required names and ordering for the DX7 worklet, then
verifies target source excerpts after a build. Add a patch by naming it for its
behavior, placing it in the narrowest applicable list, documenting its prefix
family above, and adding a test that fails on both missing anchor and lost
runtime behavior.

## Traceability Boundary

Patch names are the stable identifiers in code and test output. The upstream
runtime has no pinned package version in this repository; the reproducible
identity is the vendored source revision present at build time. Record an
upstream commit/tag in the change record whenever refreshing `external/
SuperSynthLabInstrument`; do not manufacture a version here. This makes the
absence of a pin explicit and auditable instead of quietly pretending one exists.

## Named Patch Inventory

The list below is intentionally exhaustive and is checked against build.py by
the static suite. Names are the cross-reference from an upgrade failure to the
concern and verification family above.

- `disable-stale-service-worker`
- `expression-gain-range-supports-aftertouch-swells`
- `disable-embedded-ssli-web-midi-in-exhibit-host`
- `voice-pool-release-queue-skips-stale-reused-voices`
- `voice-pool-release-cleanup-token-guard`
- `voice-pool-release-queue-stores-token`
- `voice-pool-release-cleanup-uses-hidden-frame-safe-timer`
- `voice-pool-release-cleanup-reschedules-deadline-timer`
- `voice-pool-release-enqueue-schedules-deadline-timer`
- `voice-pool-release-token-on-voice`
- `voice-pool-acquire-invalidates-stale-release-cleanup`
- `voice-pool-release-cleanup-requeues-all-allocated-voices-once`
- `voice-pool-acquire-skips-stale-free-stack-entries-and-reclaims-available-voices`
- `voice-pool-stats-report-free-stack-depth`
- `physical-note-on-accepts-bounded-one-shot-options`
- `physical-note-on-passes-pick-position-and-max-duration`
- `physical-note-on-returns-owned-voice-id-fallback`
- `physical-note-on-returns-owned-voice-id-worklet`
- `physical-fallback-pluck-deterministic-excitation-noise`
- `physical-fallback-pluck-loop-filter-brightness-range`
- `physical-fallback-pluck-smooth-mute-state`
- `physical-fallback-picked-string-triangular-displacement-derivative`
- `physical-fallback-pluck-noise-source-deterministic`
- `physical-fallback-pluck-reset-smooth-mute-on-note-on`
- `physical-fallback-pluck-note-off-is-smooth-finger-mute`
- `physical-fallback-pluck-apply-smooth-mute-envelope`
- `physical-fallback-voice-duration-state`
- `physical-fallback-voice-reset-duration`
- `physical-fallback-voice-applies-bounded-one-shot-duration`
- `physical-fallback-voice-silent-retire`
- `physical-fallback-pluck-output-tap-before-loop-damping`
- `physical-fallback-pluck-decaytime-controls-t60-round-trip-loss`
- `physical-engine-export-live-note-pressure`
- `physical-engine-api-live-note-pressure`
- `fm-engine-requires-instrument-output`
- `fm-fallback-active-voice-makeup-gain`
- `subtractive-direct-midi-linear-velocity-amplitude`
- `subtractive-sustained-linear-velocity-amplitude`
- `subtractive-fallback-active-voice-rms-makeup`
- `fm-fallback-dx7-matrix-routing`
- `fm-fallback-dx7-routing-phase-units`
- `fm-fallback-dx7-two-sample-feedback-state`
- `fm-fallback-dx7-two-sample-feedback-reset`
- `fm-fallback-dx7-two-sample-feedback-routing`
- `fm-fallback-dx7-algorithm-matrix`
- `fm-fallback-dx7-operator-source-fields`
- `fm-fallback-dx7-operator-source-params`
- `fm-fallback-dx7-keyon-gain-and-frequency`
- `fm-fallback-dx7-envelope-qrate-and-log-gain`
- `fm-fallback-dx7-ratio-fine-multiplicative-source-comment`
- `fm-fallback-dx7-combined-log-domain-gain`
- `fm-fallback-dx7-release-finished-actual-level`
- `fm-fallback-dx7-feedback-scale`
- `fm-fallback-pass-midi-note-to-operators`
- `fm-worklet-dx7-gain-lookup`
- `fm-worklet-dx7-detune-frequency`
- `fm-worklet-dx7-envelope-level-curve`
- `fm-worklet-dx7-envelope-rate-scaling-state`
- `fm-worklet-dx7-envelope-qrate`
- `fm-worklet-dx7-operator-level-curve`
- `fm-worklet-dx7-operator-kls-state`
- `fm-worklet-dx7-operator-kls-params`
- `fm-worklet-dx7-velocity-scaling`
- `fm-worklet-dx7-combined-log-domain-gain`
- `fm-worklet-dx7-operator-rate-scaling`
- `fm-worklet-dx7-pass-midi-note-to-operators`
- `fm-worklet-dx7-feedback-scale`
- `fm-worklet-dx7-bus-algorithm-routing`
- `fm-worklet-remove-non-dx7-per-voice-soft-clipper`
- `fm-worklet-active-voice-makeup-gain`
- `synth-worklet-active-voice-makeup-gain`
- `phrase-audition-uses-realtime-ssli-renderer`
- `phrase-audition-is-treated-as-sequence-for-visual-work`
- `phrase-audition-forces-realtime-renderer`
- `phrase-audition-passes-bounded-release-to-worklet`
- `phrase-audition-includes-bounded-release-in-worklet-message`
- `phrase-audition-releases-on-the-audio-clock`
- `phrase-audition-worklet-stores-audio-clock-release`
- `phrase-audition-worklet-reads-bounded-release`
- `phrase-audition-worklet-reads-audio-clock-release`
- `phrase-audition-worklet-sets-audio-clock-release`
- `phrase-audition-worklet-clamps-release-tail`
- `phrase-audition-worklet-releases-on-audio-clock`
- `physical-worklet-pluck-output-family-scale`
- `physical-worklet-deterministic-pluck-excitation-noise`
- `physical-worklet-bow-pressure-slope-direction`
- `physical-worklet-pluck-excitation-noise-source`
- `physical-worklet-pluck-shaped-noise-source`
- `physical-worklet-picked-string-triangular-displacement-derivative`
- `physical-worklet-pluck-output-tap-before-loop-damping`
- `physical-worklet-pick-position-independent-from-body-size`
- `physical-worklet-default-off-center-pick-position`
- `physical-worklet-pluck-smooth-mute-state`
- `physical-worklet-pluck-reset-smooth-mute-on-note-on`
- `physical-worklet-voice-duration-state`
- `physical-worklet-voice-reset-duration`
- `physical-worklet-pluck-note-off-is-smooth-finger-mute`
- `physical-worklet-pluck-apply-smooth-mute-envelope`
- `physical-worklet-pluck-settings-include-pick-position`
- `physical-worklet-voice-applies-bounded-one-shot-duration`
- `physical-worklet-voice-silent-retire`
- `physical-worklet-brightness-controls-ks-averaging-loss`
- `physical-worklet-pluck-loop-filter-brightness-range`
- `physical-worklet-pluck-pressure-update-brightness-range`
- `physical-worklet-marimba-tuned-bar-ratios`
- `physical-worklet-marimba-mode-decay-ratios`
- `physical-worklet-marimba-modal-output-headroom`
- `physical-worklet-marimba-modal-amplitude-falloff`
- `physical-worklet-polyphony-mix-gain`
- `physical-worklet-live-note-pressure-message`
- `physical-worklet-note-off-owned-voice-id`
- `physical-worklet-live-note-pressure-params`
