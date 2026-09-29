# Source Provenance

Version: `0.1.1`

This standalone exhibit follows an SSLI-first reuse policy.

## Vendored SSLI Sources

The following files are copied from:

`C:/Users/hanis/AppData/Roaming/clairvoyance/external/SuperSynthLabInstrument`

| Exhibit Path | SSLI Source | Purpose |
|---|---|---|
| `src/vendor/ssli/scales-modes.json` | `shared/assets/data/scales-modes.json` | Scale/mode intervals and labels |
| `src/vendor/ssli/constants.js` | `shared/assets/constants.js` | Reference for note names, flat-key policy, and shared constants |
| `src/vendor/ssli/presets/*.json` | `shared/assets/presets/*.json` | SSLI sound preset libraries |
| `src/vendor/ssli/fx-presets.json` | `shared/assets/data/fx-presets.json` | SSLI FX preset chains |
| `ssli/index.html` | `index.html` | Vendored SSLI runtime host used by the hidden synth frame |
| `ssli/assets/**` | `assets/**` | SSLI audio worklets and runtime support scripts |
| `ssli/manifest.json`, `ssli/sw.js`, `ssli/logo.png` | root SSLI support files | App support files for the vendored runtime |

## Reuse Decisions

- Scale definitions are injected from SSLI at build time.
- Note naming follows SSLI's `NOTES`, `NOTES_FLAT`, and flat-key-root policy.
- Hex/isomorphic layout design is informed by `products/ssli/assets/ssli-ctrl-isogrid.js`.
- SSLI preset and FX preset libraries are injected at build time. Runtime preset playback delegates to SSLI's `SynthLab.presets.apply` and `SynthLab.audio.playNoteOnInstrument` when the SSLI engine is available. Exquis MIDI performance delegates to SSLI's sustained-note and expression APIs (`startSustainedNote`, `stopSustainedNote`, `setExpression`). FX presets delegate to SSLI's `EffectChain` (`getInstrumentChain`, `setOrder`, `getEffect`, `setEnabled`, `setParam`). Filter controls update the current SSLI instrument filter settings. The local WebAudio path is fallback guide audio only.
- The committed `ssli/` directory is an intentional vendored runtime dependency so `index.html` can run as a standalone public app. It is copied to `dist/ssli/` by `build.py`.

## Exquis Documentation Sources

- Exquis User Guide V2.1.0: documents 61 hex keys, default horizontal semitone movement, vertical thirds, and C major startup display.
- Intuitive Instruments Help/FAQ: documents isomorphic versus free layouts, stored hardware layouts, and the fact that only isomorphic layouts react to scale display.

## Local Exquis-Specific Code

The Exquis fingering model, drill scoring, MIDI diagnostics, and calibration workflow are local because SSLI does not yet contain Exquis-specific hardware pedagogy.
