# Exquis MIDI Contract

Normal sync uses official Developer Mode over USB MIDI. Legacy packets are
diagnostic-only and must never drive normal sync. The implementation lives in
`src/parts/app.js`; this document is the behavioral contract for changing it.

## Transaction

1. Enable Developer Mode for pads only: `F0 00 21 7E 7F 00 01 F7`.
2. Send root, custom-scale-list, scale index, and custom-scale degrees.
3. Write the official RGB palette with command `02`.
4. Set pad palette entries with channel-16 CC: `BF <pad-id> <palette-index>`.
5. Set effects with channel-16 poly aftertouch: `AF <pad-id> <effect>`.

The implementation schedules these messages instead of sending a burst. It
cancels an unfinished transaction before starting another, clears its hardware
frame cache, then sends palette assignments before effects. That order prevents
an old pulse from surviving a new root/scale or practice step. Readbacks occur
only after the LED frame, so their diagnostics describe the transaction that was
actually sent.

Pads are `0..60`, bottom-left to top-right. Palette index `1` is off; `16..27` are root-relative note hues; `28` is the brighter root. Current targets use `3F` (pulsate to black). Every practice transition rewrites all pad effects so stale pulses cannot persist.

Keep pad Developer Mode active while sync is on; turning it off lets firmware overwrite the custom colors. Normal sync must not capture Settings, Sound, or transport zones.

## Ownership and Recovery

- **Normal mode:** only the pads Developer-Mode mask is enabled. The app owns
  pad colors/effects and the device keeps ownership of all edge controls.
- **UI root or mode change:** `render()` computes the new frame first, then the
  full key/mode transaction synchronizes it. Do not reverse this order.
- **Practice step change:** use the coalesced pad-frame path. It may refresh
  every effect to clear stale target pulses, but must not replay the full
  root/scale transaction.
- **Disconnect/error:** outbound sends are guarded; the page remains playable
  and diagnostics record the failed operation. Do not mutate learner state just
  because a device is unavailable.
- **Diagnostics/probes:** may send legacy or broader Developer-Mode packets
  solely on explicit user action. They are deliberately separated from normal
  sync and must leave Developer Mode off when their probe ends.

## Compatibility Rules

Pad IDs are physical `0..60`, ordered bottom-left to top-right. A rendered
MIDI pitch can appear in multiple cells; lighting chooses one canonical cell
before the pad frame is written. Never add a second physical LED for a duplicate
pitch as a shortcut—one MIDI pitch has one hardware representation.

Treat command bytes and timing constants as hardware protocol, not visual
styling. A new effect, mask, or packet must have: a cited source or recorded
hardware observation, a static sequence assertion, and a manual UAT result on
the target firmware.
