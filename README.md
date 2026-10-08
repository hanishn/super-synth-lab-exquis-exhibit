<p align="center">
  <img src="ssli/logo.png" alt="Super Synth Lab" width="160">
</p>

# Super Synth Lab Exquis Exhibit

Standalone browser-based practice exhibit for the Intuitive Instruments Exquis, built on Super Synth Lab Instrument (SSLI) audio runtime and preset data.

## What It Does

- Models the 61-key Exquis hex layout with compact honeycomb geometry.
- Shows key, scale, root, and fingering paths for one-hand scale practice.
- Connects to Exquis over Web MIDI in Chrome/Edge and highlights exact MIDI notes.
- Uses SSLI presets, FX chains, filters, sustained voices, and expression APIs for guide audio.
- Includes diagnostics, waveform display, and repeatable Playwright-based regression tests.

## Running

Open `index.html` in a modern browser, or host the repository root with any static web server.

For Web MIDI and the hidden SSLI runtime, Chrome/Edge over localhost is the most reliable local path:

```powershell
python -m http.server 8767
```

Then open:

```text
http://127.0.0.1:8767/index.html
```

## Building from Source

Requires Python 3.6+.

```powershell
python build.py
```

This rebuilds:

- `index.html`
- `dist/index.html`
- `dist/ssli/`

`exhibit.json` is a Clairvoyance build side effect and is intentionally not part of this repository.

## Testing

Install the Python test dependencies once:

```powershell
python -m pip install -r requirements.txt
```

```powershell
python -m unittest tests.test_exhibit_static tests.test_exhibit_playwright
```

The preset sweep harness can check SSLI preset behavior through the real UI and audio path:

```powershell
python tools/preset_sweep.py --engine Physical --category Plucked --preset-contains Koto
python tools/preset_sweep.py --mature-engines-only --trigger six-note-midi --audio-sample-ms 900 --output-dir tmp_preset_sweep_mature_poly_full
```

For quick smoke/debug runs only:

```powershell
python tools/preset_sweep.py --limit 10
python tools/preset_sweep.py --mature-engines-only --one-per-category --trigger six-note-midi --audio-sample-ms 900 --output-dir tmp_preset_sweep_mature_poly_smoke
```

Omit `--limit` and `--one-per-category` for acceptance sweeps.

## Repository Shape

- `src/parts/` contains the versioned HTML, CSS, and JavaScript source parts.
- `src/vendor/ssli/` contains vendored SSLI data used to populate fallback preset, scale, and FX controls.
- `ssli/` contains the vendored SSLI runtime required by the standalone app.
- `docs/` records capabilities and source provenance.
- `tests/` contains static and Playwright regression coverage.
- `tools/` contains repeatable validation utilities.
- `index.html` follows SSLI's root-runnable app convention.

## Provenance

This project is standalone, but intentionally SSLI-first. Existing SSLI implementations and data are reused before local Exquis-specific code is added. See `docs/source-provenance.md`.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`.

"Super Synth Lab", "SSLI", and "Super Synth Lab - Instrument" are names reserved by the creator. See `NOTICE`.
