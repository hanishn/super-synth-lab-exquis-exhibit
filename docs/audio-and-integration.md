# Audio and Integration Contract

## SSLI Boundary

The exhibit is an SSLI host, not a second synthesizer. `getSsliHost()` locates
the public `SynthLab` surface in the hidden iframe; readiness checks require the
particular APIs used by the operation. Preset selection delegates to SSLI first.
The local WebAudio path exists only so the teaching UI remains usable when the
iframe is unavailable.

The iframe source includes the build timestamp and the host removes stale SSLI
service-worker registrations. This is a correctness choice: audio runtime
patches must not be silently replaced by an old cached worklet. Do not turn this
into generic PWA caching without proving that the runtime and all worklets are
version-consistent.

## Voice Lifecycle

`midiVoices` is the ownership ledger. Each voice is keyed by input channel plus
display MIDI note, carries the selected articulation at onset, and is released
through the matching key. A duplicate note-on first releases its older logical
owner. Cleanup after note-off must clear both voice bookkeeping and expression
only when no SSLI voice remains.

Sustained instruments begin at note-on and receive live pressure. Physical
plucked/struck instruments are onset-decay interactions: pressure establishes
the excitation, then the voice decays. Release-strum is a short gesture
recognizer, not a delayed generic note-off; a new contact cancels a pending
release commitment and damps a committed tail. This preserves the physical
meaning of the gesture and avoids a prior release becoming a new press sound.

## Physical Voice Protection

Physical engines can become unusably loud when several voices begin together.
The velocity helper applies a bounded load scale, while deliberately treating a
tight simultaneous onset as a chord rather than already-held sustain. The floor
keeps quiet contacts playable; the cap protects later voices. Change these
constants only with multi-voice measurements and a regression covering both a
chord onset and genuinely sustained overlap.

## Presets and Effects

Vendored preset JSON is injected by `build.py` and gets a default articulation
only when the preset does not declare one. Keep behavioral overrides narrowly
identified and logged. An effect or normalization change must preserve the
selected preset's public identity and use AudioParam automation where available
to avoid gain discontinuities/clicks.

## Debug/Test Surfaces

The `window.__exquisDebug*` and `window.__exquisLightDebug` hooks are test
surfaces. Preserve their observable shapes unless the corresponding tests and
documentation change in the same patch. Browser tests validate routing and
lifecycle state; a preset sweep is required for broad audible behavior and a
human hearing check remains the final authority for timbre.
