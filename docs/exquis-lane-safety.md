# Exquis Practice Lane Safety

## Scope

This contract governs every rendered and synced practice sequence on the Exquis hex surface. It is deliberately about **physical pads**, not just MIDI pitches: the lattice contains duplicate pitches and a safe MIDI list can still be an unsafe visual or hardware map.

## Acceptance criteria

1. Practice always lights the complete Exquis tonic/key map, matching the default Exquis scale layout: two in-key pads in each of the eleven displayed columns (22 physical pads).
2. The exercise sequence is an overlay on that complete key map: Root to octave contains eight targets; Two octaves contains fifteen. It must never replace or reduce the lit key map.
3. Every rendered lit scale pad and every hardware-synced lit scale pad identifies the same physical cell ID. Every exercise target must be one of those lit scale pads.
4. No displayed vertical pad column contains more than two lit sequence pads. A column is measured from the rendered pad `left` position, not inferred from a MIDI pitch, a duplicate-pitch canonicalization rule, or a diagonal lattice axis.
5. A path that cannot satisfy criterion 4 is not silently replaced with an unsafe fallback. The planner must choose another valid root/layout or report no safe path.
6. Regression coverage must automate the real Session controls, count the visible colored pads, verify the expected total, test all three axes, and capture a screenshot for human inspection.

## Required regression examples

- Session -> Tonic Db -> Scale Minor -> Root to octave: 22 lit key-map pads and 8 targets; each displayed vertical column has 2 pads.
- Session -> Tonic Db -> Scale Minor -> Two octaves: 22 lit key-map pads and 15 targets; each displayed vertical column has 2 pads.
- Every tonic in Major and Minor, for both Root to octave and Two octaves: 22 lit key-map pads; 8 or 15 targets respectively; every target is lit. The regression captures one rendered Practice screenshot per key and exercise for manual visual inspection.
