import argparse
import csv
import functools
import http.server
import json
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sweep Exquis Fingering Lab SSLI presets through the real Playwright UI."
    )
    parser.add_argument("--limit", type=int, default=0, help="Maximum presets to test. Default: 0 means full sweep.")
    parser.add_argument("--output-dir", default="tmp_preset_sweep", help="Directory for JSON/CSV results.")
    parser.add_argument("--no-build", action="store_true", help="Use the current root index.html without rebuilding.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible browser window.")
    parser.add_argument("--timeout-ms", type=int, default=2500, help="Per-preset wait budget after playback.")
    parser.add_argument("--settle-ms", type=int, default=250, help="Post-click settle time before reading diagnostics.")
    parser.add_argument("--audio-sample-ms", type=int, default=650, help="How long to sample SSLI analyser output after each playback.")
    parser.add_argument("--engine", default="", help="Only sweep engines whose value or label contains this text.")
    parser.add_argument("--category", default="", help="Only sweep categories whose value or label contains this text.")
    parser.add_argument("--preset-contains", default="", help="Only sweep presets whose value or label contains this text.")
    parser.add_argument("--preset-list-file", default="", help="JSON results/list file containing exact presets to rerun.")
    parser.add_argument(
        "--mature-engines-only",
        action="store_true",
        help="Sweep only Subtractive, FM, and Physical engines.",
    )
    parser.add_argument(
        "--one-per-category",
        action="store_true",
        help="Smoke mode: keep only the first live preset found for each engine/category pair. Do not use as full acceptance.",
    )
    parser.add_argument(
        "--trigger",
        choices=["preview", "six-note-midi"],
        default="preview",
        help="Use normal preview playback or a six-note Exquis-style MIDI pressure run.",
    )
    return parser.parse_args()


def option_values(page, selector):
    return page.locator(selector).evaluate_all(
        "els => els[0] ? [...els[0].options].map((o) => ({ value: o.value, label: o.textContent.trim() })) : []"
    )


def select_if_present(page, selector, value):
    page.locator(selector).select_option(value)
    page.wait_for_timeout(25)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - matches stdlib signature
        return


def start_public_server():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}/index.html"


def collect_presets(page):
    presets = []
    for engine in option_values(page, '[data-testid="sound-engine-select"]'):
        select_if_present(page, '[data-testid="sound-engine-select"]', engine["value"])
        for category in option_values(page, '[data-testid="sound-category-select"]'):
            select_if_present(page, '[data-testid="sound-category-select"]', category["value"])
            for preset in option_values(page, '[data-testid="sound-preset-select"]'):
                presets.append(
                    {
                        "engine": engine["value"],
                        "engineLabel": engine["label"],
                        "category": category["value"],
                        "categoryLabel": category["label"],
                        "preset": preset["value"],
                        "presetLabel": preset["label"],
                    }
                )
    return presets


def contains_text(row, fields, needle):
    if not needle:
        return True
    lowered = needle.lower()
    return any(lowered in str(row.get(field, "")).lower() for field in fields)


def filter_presets(presets, args):
    filtered = [
        preset
        for preset in presets
        if contains_text(preset, ("engine", "engineLabel"), args.engine)
        and contains_text(preset, ("category", "categoryLabel"), args.category)
        and contains_text(preset, ("preset", "presetLabel"), args.preset_contains)
    ]
    if args.mature_engines_only:
        mature = {"fm", "physical", "subtractive"}
        filtered = [preset for preset in filtered if str(preset["engine"]).lower() in mature or str(preset["engineLabel"]).lower() in mature]
    if args.preset_list_file:
        wanted = load_preset_list(args.preset_list_file)
        filtered = [preset for preset in filtered if preset_key(preset) in wanted]
    if args.one_per_category:
        groups = {}
        for preset in filtered:
            key = (preset["engine"], preset["category"])
            groups.setdefault(key, []).append(preset)
        filtered = [rows[0] for rows in groups.values()]
    return filtered


def preset_key(row):
    return (
        str(row.get("engine", "")),
        str(row.get("category", "")),
        str(row.get("preset", "")),
    )


def load_preset_list(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("results", payload) if isinstance(payload, dict) else payload
    wanted = set()
    for row in rows:
        if str(row.get("status", "")).lower() == "pass":
            continue
        wanted.add(preset_key(row))
    return wanted


def diagnostic_snapshot(page):
    return page.evaluate(
        """
        () => {
          const log = document.querySelector('[data-testid="diagnostic-log"]');
          return log ? log.textContent.length : 0;
        }
        """
    )


def diagnostic_tail(page, since_length=0):
    text = page.evaluate(
        """
        () => {
          const log = document.querySelector('[data-testid="diagnostic-log"]');
          return log ? log.textContent : '';
        }
        """
    )
    if since_length:
        text = text[since_length:]
    return text.splitlines()[-12:]


def clear_diagnostics(page):
    page.locator('[data-testid="reset-console"]').click(timeout=1000)
    page.wait_for_timeout(25)


def is_benign_console_message(text):
    known = [
        "AudioWorklet not supported, using ScriptProcessor fallback",
        "The ScriptProcessorNode is deprecated. Use AudioWorkletNode instead.",
    ]
    return any(fragment in text for fragment in known)


def ssli_instrument_snapshot(page):
    return page.evaluate(
        """
        () => {
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow && frame.contentWindow.SynthLab
            ? frame.contentWindow
            : window;
          const SL = host.SynthLab;
          if (!SL || !SL.audio || !SL.audio.getInstruments) {
            return { available: false, instrumentType: '', settingsHash: '', settingsKeys: [] };
          }
          const instruments = SL.audio.getInstruments() || [];
          const index = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
          const inst = instruments[index] || {};
          const settings = inst.settings || {};
          const settingsJson = JSON.stringify(settings);
          let hash = 0;
          for (let i = 0; i < settingsJson.length; i += 1) {
            hash = ((hash << 5) - hash + settingsJson.charCodeAt(i)) | 0;
          }
          return {
            available: true,
            instrumentIndex: index,
            instrumentType: inst.type || '',
            settingsHash: String(hash),
            settingsKeys: Object.keys(settings).sort()
          };
        }
        """
    )


def prepare_ssli_audio_probe(page):
    return page.evaluate(
        """
        () => {
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow && frame.contentWindow.SynthLab
            ? frame.contentWindow
            : window;
          const SL = host.SynthLab;
          if (!SL || !SL.audio) {
            window.__presetSweepAudioProbe = { available: false, error: 'missing SynthLab.audio' };
            return window.__presetSweepAudioProbe;
          }
          const inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
          let analyser = null;
          if (SL.audio.getInstrumentAnalyser) analyser = SL.audio.getInstrumentAnalyser(inst);
          if (!analyser && SL.audio.getAnalyser) analyser = SL.audio.getAnalyser();
          if (!analyser) {
            window.__presetSweepAudioProbe = { available: false, error: 'missing analyser' };
            return window.__presetSweepAudioProbe;
          }
          window.__presetSweepAudioProbe = { available: true, analyser, armedAt: performance.now() };
          return { available: true, armedAt: window.__presetSweepAudioProbe.armedAt };
        }
        """
    )


def capture_ssli_audio_signature(page, sample_ms):
    return page.evaluate(
        """
        async (sampleMs) => {
          const probe = window.__presetSweepAudioProbe || {};
          const analyser = probe.analyser;
          if (!analyser) {
            return { available: false, error: probe.error || 'audio probe was not armed', peak: 0, rms: 0, spectrumPeak: 0, spectrumRms: 0, waveformHash: '', spectrumHash: '', samples: 0 };
          }
          const wave = new Uint8Array(analyser.fftSize || 256);
          const spectrum = new Uint8Array(analyser.frequencyBinCount || 128);
          let peak = 0;
          let sumSq = 0;
          let count = 0;
          let spectrumPeak = 0;
          let spectrumSumSq = 0;
          let spectrumCount = 0;
          let samples = 0;
          let waveHash = 0;
          let spectrumHash = 0;
          const started = Date.now();
          while (Date.now() - started < sampleMs) {
            analyser.getByteTimeDomainData(wave);
            if (analyser.getByteFrequencyData) analyser.getByteFrequencyData(spectrum);
            samples += 1;
            for (let i = 0; i < wave.length; i += 1) {
              const normalized = (wave[i] - 128) / 128;
              const abs = Math.abs(normalized);
              if (abs > peak) peak = abs;
              sumSq += normalized * normalized;
              count += 1;
              if (i % 8 === 0) waveHash = ((waveHash << 5) - waveHash + wave[i]) | 0;
            }
            for (let j = 0; j < spectrum.length; j += 8) {
              const spectrumLevel = spectrum[j] / 255;
              if (spectrumLevel > spectrumPeak) spectrumPeak = spectrumLevel;
              spectrumSumSq += spectrumLevel * spectrumLevel;
              spectrumCount += 1;
              spectrumHash = ((spectrumHash << 5) - spectrumHash + spectrum[j]) | 0;
            }
            await new Promise((resolve) => setTimeout(resolve, 40));
          }
          const rms = count ? Math.sqrt(sumSq / count) : 0;
          const spectrumRms = spectrumCount ? Math.sqrt(spectrumSumSq / spectrumCount) : 0;
          return {
            available: true,
            peak: Number(peak.toFixed(5)),
            rms: Number(rms.toFixed(5)),
            spectrumPeak: Number(spectrumPeak.toFixed(5)),
            spectrumRms: Number(spectrumRms.toFixed(5)),
            waveformHash: String(waveHash),
            spectrumHash: String(spectrumHash),
            analyserArmedBeforeTrigger: true,
            armedAt: probe.armedAt || 0,
            samples
          };
        }
        """,
        sample_ms,
    )


def ssli_audio_signature(page, sample_ms):
    prepare_ssli_audio_probe(page)
    return capture_ssli_audio_signature(page, sample_ms)


def reset_runtime_audio(page):
    page.evaluate(
        """
        () => {
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow && frame.contentWindow.SynthLab ? frame.contentWindow : window;
          const SL = host.SynthLab;
          if (!SL || !SL.audio) return;
          try { if (SL.audio.stopAllSustained) SL.audio.stopAllSustained(); } catch (err) {}
          try { if (SL.audio.clearExpression) SL.audio.clearExpression(); } catch (err) {}
          try {
            const inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
            [
              'fm', 'physical', 'additive', 'granular', 'vocoderSynth',
              'wavefolder', 'formant', 'modal', 'ringmod', 'chord',
              'superwave', 'wavetableSynth', 'phasedist', 'chip',
              'bytebeat', 'vector', 'drumsyn', 'pulsar', 'bodyResonance', 'reed'
            ].forEach((engineName) => {
              const engine = SL[engineName];
              if (engine && engine.allNotesOff) engine.allNotesOff(inst);
            });
          } catch (err) {}
        }
        """
    )
    page.wait_for_timeout(80)


def enable_mock_midi(page):
    page.evaluate(
        """
        () => {
          window.__presetSweepMidiInput = { id: 'preset-sweep-exquis', name: 'Exquis Preset Sweep', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__presetSweepMidiInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """
    )
    page.locator('[data-testid="enable-midi"]').click()
    page.wait_for_function("() => window.__presetSweepMidiInput && window.__presetSweepMidiInput.onmidimessage")


def ssli_six_note_midi_signature(page, sample_ms):
    return page.evaluate(
        """
        async (sampleMs) => {
          const input = window.__presetSweepMidiInput;
          if (!input || !input.onmidimessage) return { available: false, error: 'missing mock MIDI input' };
          const send = (data) => input.onmidimessage({ data });
          const logEl = document.querySelector('[data-testid="diagnostic-log"]');
          const diagnosticStartLength = logEl ? logEl.textContent.length : 0;
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow && frame.contentWindow.SynthLab ? frame.contentWindow : window;
          const SL = host.SynthLab;
          if (!SL || !SL.audio) return { available: false, error: 'missing SynthLab.audio' };
          const inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
          const instruments = SL.audio.getInstruments ? SL.audio.getInstruments() : [];
          const instrument = instruments[inst] || {};
          const settings = instrument.settings || {};
          const settingsJson = JSON.stringify(settings);
          let settingsHash = 0;
          for (let i = 0; i < settingsJson.length; i += 1) settingsHash = ((settingsHash << 5) - settingsHash + settingsJson.charCodeAt(i)) | 0;
          const engineSettingsKey = {
            fm: 'fmSettings',
            physical: 'physicalSettings'
          }[instrument.type || ''] || '';
          const engineSettings = engineSettingsKey ? (settings[engineSettingsKey] || {}) : {
            osc: settings.osc || null,
            filter: settings.filter || null,
            adsr: settings.adsr || null
          };
          const engineSettingsJson = JSON.stringify(engineSettings || {});
          let engineSettingsHash = 0;
          for (let i = 0; i < engineSettingsJson.length; i += 1) engineSettingsHash = ((engineSettingsHash << 5) - engineSettingsHash + engineSettingsJson.charCodeAt(i)) | 0;

          const ctx = SL.audio.getCtx ? SL.audio.getCtx() : null;
          if (window.__exquisPrepareSsliOutputBoost) window.__exquisPrepareSsliOutputBoost();
          const boost = SL.__exquisPracticeOutputBoost;
          if (!ctx || !boost) return { available: false, error: 'missing final SSLI boost path' };
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 2048;
          boost.connect(analyser);
          const wave = new Uint8Array(analyser.fftSize);
          const spectrum = new Uint8Array(analyser.frequencyBinCount);
          const first = { midi: 48, channel: 7, velocity: 104 };
          send([0x90 | first.channel, first.midi, first.velocity]);
          await new Promise(resolve => setTimeout(resolve, 30));
          const notes = [
            first,
            { midi: 50, channel: 13, velocity: 108 },
            { midi: 52, channel: 9, velocity: 96 },
            { midi: 53, channel: 2, velocity: 116 },
            { midi: 55, channel: 15, velocity: 92 },
            { midi: 57, channel: 5, velocity: 122 }
          ];
          notes.slice(1).forEach((note, index) => setTimeout(() => send([0x90 | note.channel, note.midi, note.velocity]), 8 + index * 8));
          const pressureFrames = [
            [102, 108, 95, 116, 91, 123],
            [112, 118, 104, 125, 99, 127],
            [120, 126, 111, 127, 107, 124],
            [116, 121, 106, 119, 101, 116],
            [94, 104, 88, 106, 73, 98],
            [68, 82, 51, 83, 38, 67],
            [21, 44, 0, 37, 0, 29],
            [0, 0, 0, 0, 0, 0]
          ];
          pressureFrames.forEach((frameValues, frameIndex) => {
            frameValues.forEach((pressure, noteIndex) => {
              const note = notes[noteIndex];
              setTimeout(() => send([0xD0 | note.channel, pressure]), 80 + frameIndex * 45 + noteIndex * 5);
            });
          });
          notes.forEach((note, index) => {
            setTimeout(() => {
              send([0xD0 | note.channel, 0]);
              send([0x80 | note.channel, note.midi, 0]);
            }, 480 + index * 12);
          });

          let peak = 0;
          let rmsSum = 0;
          let count = 0;
          let clipped = 0;
          let spectrumPeak = 0;
          let spectrumSum = 0;
          let spectrumCount = 0;
          let waveHash = 0;
          let spectrumHash = 0;
          const framePeaks = [];
          const started = Date.now();
          while (Date.now() - started < sampleMs) {
            analyser.getByteTimeDomainData(wave);
            analyser.getByteFrequencyData(spectrum);
            let framePeak = 0;
            for (let i = 0; i < wave.length; i += 1) {
              const normalized = (wave[i] - 128) / 128;
              const abs = Math.abs(normalized);
              peak = Math.max(peak, abs);
              framePeak = Math.max(framePeak, abs);
              rmsSum += normalized * normalized;
              count += 1;
              if (wave[i] <= 2 || wave[i] >= 253) clipped += 1;
              if (i % 8 === 0) waveHash = ((waveHash << 5) - waveHash + wave[i]) | 0;
            }
            framePeaks.push(framePeak);
            for (let j = 0; j < spectrum.length; j += 1) {
              const level = spectrum[j] / 255;
              spectrumPeak = Math.max(spectrumPeak, level);
              spectrumSum += level * level;
              spectrumCount += 1;
              if (j % 8 === 0) spectrumHash = ((spectrumHash << 5) - spectrumHash + spectrum[j]) | 0;
            }
            await new Promise(resolve => setTimeout(resolve, 16));
          }
          try { boost.disconnect(analyser); } catch (err) {}
          await new Promise(resolve => setTimeout(resolve, 120));
          framePeaks.sort((a, b) => a - b);
          const diagnosticLog = logEl ? logEl.textContent.slice(diagnosticStartLength) : '';
          const voiceCleanup = window.__exquisDebugSnapshot ? window.__exquisDebugSnapshot() : null;
          return {
            available: true,
            trigger: 'six-note-midi',
            instrumentType: instrument.type || '',
            settingsHash: String(settingsHash),
            settingsKeys: Object.keys(settings).sort(),
            engineSettingsKey,
            engineSettingsHash: String(engineSettingsHash),
            engineSettingsKeys: Object.keys(engineSettings || {}).sort(),
            physicalSettings: settings.physicalSettings || null,
            peak: Number(peak.toFixed(5)),
            rms: Number(Math.sqrt(rmsSum / Math.max(1, count)).toFixed(5)),
            p95Peak: Number((framePeaks[Math.floor(framePeaks.length * 0.95)] || 0).toFixed(5)),
            clipRatio: Number((clipped / Math.max(1, count)).toFixed(6)),
            spectrumPeak: Number(spectrumPeak.toFixed(5)),
            spectrumRms: Number(Math.sqrt(spectrumSum / Math.max(1, spectrumCount)).toFixed(5)),
            waveformHash: String(waveHash),
            spectrumHash: String(spectrumHash),
            finalBoostGain: Number(boost.gain.value.toFixed(2)),
            analyserArmedBeforeTrigger: true,
            diagnosticLog,
            diagnosticStartLength,
            voiceCleanup
          };
        }
        """,
        sample_ms,
    )


def expected_type_for_engine(row):
    engine = str(row.get("engine", "")).lower()
    label = str(row.get("engineLabel", "")).lower()
    if "physical" in {engine, label} or engine == "physical":
        return "physical"
    if engine == "fm" or label == "fm":
        return "fm"
    if engine == "subtractive" or label == "subtractive":
        return "subtractive"
    return ""


def validate_audio_behavior(row, trigger):
    errors = []
    signature = row.get("audioSignature") or {}
    expected_type = expected_type_for_engine(row)
    if not signature.get("available"):
        errors.append(f"audio unavailable: {signature.get('error', '')}")
    if expected_type and signature.get("instrumentType") and signature.get("instrumentType") != expected_type:
        errors.append(f"expected engine {expected_type}, got {signature.get('instrumentType')}")
    if expected_type and expected_type != "subtractive" and not signature.get("engineSettingsKeys"):
        errors.append(f"missing {expected_type} parameter block")
    if max(signature.get("peak", 0), signature.get("spectrumPeak", 0)) < 0.015 or signature.get("rms", 0) < 0.003:
        errors.append("audio energy too low")
    if trigger == "six-note-midi":
        if signature.get("clipRatio", 0) > 0.03:
            errors.append(f"clipping ratio too high ({signature.get('clipRatio')})")
        log = signature.get("diagnosticLog", "")
        cleanup = signature.get("voiceCleanup") or {}
        if cleanup:
            held = cleanup.get("heldNotes")
            local = cleanup.get("midiVoices")
            ssli = cleanup.get("ssliActiveOscillators")
            if held != 0 or local != 0 or (ssli is not None and ssli != 0):
                errors.append(f"MIDI voices not idle after run (held={held} local={local} ssli={ssli})")
        else:
            errors.append("missing MIDI voice cleanup snapshot")
        if "held=0 local=0 ssli=0" not in log:
            errors.append("current MIDI run did not report clean idle cleanup")
    return errors


def audio_signature_identity(row):
    signature = row.get("audioSignature") or {}
    settings_hash = str(row.get("instrumentSettingsHash") or signature.get("settingsHash") or "")
    engine_settings_hash = str(signature.get("engineSettingsHash") or "")
    waveform_hash = str(row.get("audioWaveformHash") or signature.get("waveformHash") or "")
    spectrum_hash = str(row.get("audioSpectrumHash") or signature.get("spectrumHash") or "")
    if not settings_hash or not waveform_hash or not spectrum_hash:
        return None
    return (
        str(row.get("engine", "")),
        str(row.get("category", "")),
        str(row.get("instrumentType") or signature.get("instrumentType") or ""),
        settings_hash,
        engine_settings_hash,
        waveform_hash,
        spectrum_hash,
    )


def find_duplicate_signature_groups(results):
    groups = {}
    for row in results:
        if row.get("status") != "pass":
            continue
        identity = audio_signature_identity(row)
        if identity is None:
            continue
        groups.setdefault(identity, []).append(row)
    return [rows for rows in groups.values() if len({preset_key(row) for row in rows}) > 1]


def apply_duplicate_signature_failures(results):
    duplicate_groups = find_duplicate_signature_groups(results)
    for group_index, rows in enumerate(duplicate_groups, start=1):
        names = ", ".join(row.get("presetLabel") or row.get("preset", "") for row in rows)
        message = f"duplicate preset signature group {group_index}: {names}"
        for row in rows:
            row["status"] = "fail"
            row["duplicateSignatureGroup"] = group_index
            row["error"] = "; ".join(part for part in [row.get("error", ""), message] if part)
    return len(duplicate_groups)


def run_sweep(args):
    if not args.no_build:
        subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit(f"Python Playwright is required for preset sweep: {exc}") from exc

    output_dir = (ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    server, url = start_public_server()
    results = []
    started_at = time.time()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=not args.headed,
            args=["--autoplay-policy=no-user-gesture-required"],
        )
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page_errors = []
            console_errors = []
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text)
                if msg.type in {"error", "warning"} and not is_benign_console_message(msg.text)
                else None,
            )
            page.goto(url)
            page.wait_for_selector('[data-testid="sound-engine-select"]')
            if args.trigger == "six-note-midi":
                enable_mock_midi(page)
            presets = collect_presets(page)
            total = len(presets)
            presets = filter_presets(presets, args)
            if args.limit and args.limit > 0:
                presets = presets[: args.limit]

            for index, preset in enumerate(presets, start=1):
                before_page_errors = len(page_errors)
                before_console_errors = len(console_errors)
                status = "pass"
                error = ""
                log_tail = []
                instrument = {}
                audio_signature = {}
                try:
                    reset_runtime_audio(page)
                    select_if_present(page, '[data-testid="sound-engine-select"]', preset["engine"])
                    select_if_present(page, '[data-testid="sound-category-select"]', preset["category"])
                    select_if_present(page, '[data-testid="sound-preset-select"]', preset["preset"])
                    clear_diagnostics(page)
                    log_start = diagnostic_snapshot(page)
                    if args.trigger == "six-note-midi":
                        audio_signature = ssli_six_note_midi_signature(page, max(args.audio_sample_ms, 900))
                    else:
                        probe = prepare_ssli_audio_probe(page)
                        page.locator('[data-testid="play-step"]').click(timeout=args.timeout_ms)
                        audio_signature = capture_ssli_audio_signature(page, args.audio_sample_ms)
                        if probe and not probe.get("available"):
                            audio_signature["available"] = False
                            audio_signature["error"] = probe.get("error", "audio probe unavailable")
                    page.wait_for_timeout(args.settle_ms)
                    log_tail = diagnostic_tail(page, log_start)
                    instrument = ssli_instrument_snapshot(page)
                    joined = "\n".join(log_tail)
                    validation_errors = validate_audio_behavior({**preset, "audioSignature": audio_signature}, args.trigger)
                    if validation_errors:
                        status = "fail"
                        error = "; ".join(validation_errors)
                    elif args.trigger == "preview" and "SSLI play" not in joined and "playing C" not in joined and "playing " not in joined:
                        status = "fail"
                        error = "No playback log found after preset play."
                except Exception as exc:
                    status = "fail"
                    error = str(exc)
                    try:
                        log_tail = diagnostic_tail(page)
                    except Exception:
                        log_tail = []

                new_page_errors = page_errors[before_page_errors:]
                new_console_errors = console_errors[before_console_errors:]
                if new_page_errors or new_console_errors:
                    status = "fail"
                    error = "; ".join([error] + new_page_errors + new_console_errors).strip("; ")

                row = {
                    **preset,
                    "index": index,
                    "sweepCount": len(presets),
                    "availablePresetCount": total,
                    "status": status,
                    "error": error,
                    "diagnosticTail": log_tail,
                    "pageErrors": new_page_errors,
                    "consoleErrors": new_console_errors,
                    "instrument": instrument,
                    "audioSignature": audio_signature,
                    "instrumentType": instrument.get("instrumentType", ""),
                    "instrumentSettingsHash": instrument.get("settingsHash", ""),
                    "instrumentSettingsKeys": ",".join(instrument.get("settingsKeys", [])),
                    "audioPeak": audio_signature.get("peak", 0),
                    "audioRms": audio_signature.get("rms", 0),
                    "audioSpectrumPeak": audio_signature.get("spectrumPeak", 0),
                    "audioSpectrumRms": audio_signature.get("spectrumRms", 0),
                    "audioEnergy": max(audio_signature.get("peak", 0), audio_signature.get("spectrumPeak", 0)),
                    "audioWaveformHash": audio_signature.get("waveformHash", ""),
                    "audioSpectrumHash": audio_signature.get("spectrumHash", ""),
                    "audioSamples": audio_signature.get("samples", 0),
                    "audioSignatureAvailable": audio_signature.get("available", False),
                    "audioP95Peak": audio_signature.get("p95Peak", ""),
                    "audioClipRatio": audio_signature.get("clipRatio", ""),
                    "finalBoostGain": audio_signature.get("finalBoostGain", ""),
                    "trigger": args.trigger,
                }
                results.append(row)
                print(f"[{index}/{len(presets)}] {status.upper()} {preset['engine']} / {preset['categoryLabel']} / {preset['presetLabel']}")
        finally:
            browser.close()
            server.shutdown()

    duplicate_signature_groups = apply_duplicate_signature_failures(results)
    summary = {
        "url": url,
        "startedAt": started_at,
        "elapsedSeconds": round(time.time() - started_at, 3),
        "availablePresetCount": total,
        "sweptPresetCount": len(results),
        "duplicateSignatureGroups": duplicate_signature_groups,
        "passed": sum(1 for row in results if row["status"] == "pass"),
        "failed": sum(1 for row in results if row["status"] == "fail"),
    }
    json_path = output_dir / "preset-sweep-results.json"
    csv_path = output_dir / "preset-sweep-results.csv"
    json_path.write_text(json.dumps({"summary": summary, "results": results}, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "index",
                "status",
                "engine",
                "categoryLabel",
                "presetLabel",
                "preset",
                "instrumentType",
                "instrumentSettingsHash",
                "instrumentSettingsKeys",
                "audioSignatureAvailable",
                "audioPeak",
                "audioRms",
                "audioSpectrumPeak",
                "audioSpectrumRms",
                "audioEnergy",
                "audioWaveformHash",
                "audioSpectrumHash",
                "audioSamples",
                "audioP95Peak",
                "audioClipRatio",
                "finalBoostGain",
                "duplicateSignatureGroup",
                "trigger",
                "error",
                "availablePresetCount",
                "sweepCount",
            ],
        )
        writer.writeheader()
        for row in results:
            writer.writerow({field: row.get(field, "") for field in writer.fieldnames})

    print(json.dumps(summary, indent=2))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(run_sweep(parse_args()))
