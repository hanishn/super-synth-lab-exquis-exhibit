import argparse
import functools
import http.server
import json
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = [
    ("Subtractive", "Keys", "Wurlitzer EP", "subtractive"),
    ("Physical", "Plucked", "Koto", "physical"),
    ("FM", "Bass", "BASS 1", "fm"),
    ("Wavetable", "Pads", "Warm Analog Pad", "wavetable"),
]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002
        return


def parse_case(text):
    parts = [part.strip() for part in text.split("/", 3)]
    if len(parts) not in {3, 4}:
        raise argparse.ArgumentTypeError("case must be Engine/Category/Preset[/expectedEngineType]")
    if len(parts) == 3:
        parts.append("")
    return tuple(parts)


def parse_args():
    parser = argparse.ArgumentParser(description="Validate SSLI preset identity with runtime engine/settings and waveform evidence.")
    parser.add_argument("--case", action="append", type=parse_case, help="Engine/Category/Preset[/expectedEngineType]. Can be repeated.")
    parser.add_argument("--output", default="tmp_preset_signature_check/results.json")
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--sample-ms", type=int, default=900)
    parser.add_argument("--trigger", choices=["preview", "midi"], default="preview")
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


def start_server():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}/index.html"


def select_by_label(page, selector, label):
    page.locator(selector).select_option(label=label)
    page.wait_for_timeout(40)


def ensure_engine_visible(page, engine):
    options = page.locator('[data-testid="sound-engine-select"] option').evaluate_all("(opts) => opts.map((opt) => opt.textContent.trim())")
    values = page.locator('[data-testid="sound-engine-select"] option').evaluate_all("(opts) => opts.map((opt) => opt.value)")
    if engine in options or engine in values:
        return
    show_all = page.locator('[data-testid="show-all-engines"]')
    if show_all.count() and not show_all.is_checked():
        show_all.check()
        page.wait_for_timeout(40)


def prepare_signature_probe(page):
    return page.evaluate(
        """
        () => {
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow && frame.contentWindow.SynthLab ? frame.contentWindow : window;
          const SL = host.SynthLab;
          if (!SL || !SL.audio) return { available: false, error: 'missing SynthLab.audio' };
          const instId = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
          const instruments = SL.audio.getInstruments ? SL.audio.getInstruments() : [];
          const inst = instruments[instId] || {};
          const settings = inst.settings || {};
          const settingsJson = JSON.stringify(settings);
          let settingsHash = 0;
          for (let i = 0; i < settingsJson.length; i += 1) settingsHash = ((settingsHash << 5) - settingsHash + settingsJson.charCodeAt(i)) | 0;
          const engineSettingsKey = {
            fm: 'fmSettings',
            physical: 'physicalSettings',
            wavetable: 'wavetableSettings',
            additive: 'additiveSettings',
            granular: 'granularSettings',
            modal: 'modalSettings',
            ringmod: 'ringmodSettings',
            superwave: 'superwaveSettings',
            wavefolder: 'wavefoldSettings',
            formant: 'formantSettings',
            chord: 'chordSettings',
            phasedist: 'phasedistSettings',
            chip: 'chipSettings',
            vector: 'vectorSettings',
            drumsyn: 'drumsynSettings',
            pulsar: 'pulsarSettings',
            reed: 'reedSettings'
          }[inst.type || ''] || '';
          const engineSettings = engineSettingsKey ? (settings[engineSettingsKey] || {}) : {
            osc: settings.osc || null,
            filter: settings.filter || null,
            adsr: settings.adsr || null
          };
          const engineSettingsJson = JSON.stringify(engineSettings || {});
          let engineSettingsHash = 0;
          for (let i = 0; i < engineSettingsJson.length; i += 1) engineSettingsHash = ((engineSettingsHash << 5) - engineSettingsHash + engineSettingsJson.charCodeAt(i)) | 0;
          if (inst._analyserNode) {
            try { inst._analyserNode.disconnect(); } catch (err) {}
            inst._analyserNode = null;
          }
          let instrumentAnalyser = null;
          let masterAnalyser = null;
          if (SL.audio.getInstrumentAnalyser) instrumentAnalyser = SL.audio.getInstrumentAnalyser(instId);
          if (SL.audio.getAnalyser) masterAnalyser = SL.audio.getAnalyser();
          const analyser = instrumentAnalyser || masterAnalyser;
          window.__exquisPresetSignatureProbe = {
            available: !!analyser,
            instrumentAnalyser,
            masterAnalyser,
            instrumentType: inst.type || '',
            settingsHash: String(settingsHash),
            settingsKeys: Object.keys(settings).sort(),
            engineSettingsKey,
            engineSettingsHash: String(engineSettingsHash),
            engineSettingsKeys: Object.keys(engineSettings || {}).sort(),
            engineSettings,
            physicalSettings: settings.physicalSettings || null
          };
          if (!analyser) window.__exquisPresetSignatureProbe.error = 'missing analyser';
          return window.__exquisPresetSignatureProbe;
        }
        """
    )


def capture_signature(page, sample_ms):
    return page.evaluate(
        """
        async (sampleMs) => {
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow && frame.contentWindow.SynthLab ? frame.contentWindow : window;
          const SL = host.SynthLab;
          if (!SL || !SL.audio) return { available: false, error: 'missing SynthLab.audio' };
          const probe = window.__exquisPresetSignatureProbe || {};
          const analysers = [probe.instrumentAnalyser, probe.masterAnalyser || (SL.audio.getAnalyser ? SL.audio.getAnalyser() : null)].filter(Boolean);
          if (!analysers.length) return { available: false, error: probe.error || 'missing analyser', instrumentType: probe.instrumentType || '', settingsHash: probe.settingsHash || '' };
          const buffers = analysers.map(analyser => ({
            analyser,
            wave: new Uint8Array(analyser.fftSize || 256),
            spectrum: new Uint8Array(analyser.frequencyBinCount || 128),
            peak: 0,
            rmsSum: 0,
            rmsCount: 0,
            spectrumPeak: 0,
            spectrumSum: 0,
            spectrumCount: 0,
            waveHash: 0,
            spectrumHash: 0
          }));
          let waveHash = 0;
          let spectrumHash = 0;
          let peak = 0;
          let rmsSum = 0;
          let rmsCount = 0;
          let spectrumPeak = 0;
          let spectrumSum = 0;
          let spectrumCount = 0;
          const start = Date.now();
          while (Date.now() - start < sampleMs) {
            buffers.forEach((buffer, analyserIndex) => {
              buffer.analyser.getByteTimeDomainData(buffer.wave);
              if (buffer.analyser.getByteFrequencyData) buffer.analyser.getByteFrequencyData(buffer.spectrum);
              for (let i = 0; i < buffer.wave.length; i += 1) {
                const n = (buffer.wave[i] - 128) / 128;
                peak = Math.max(peak, Math.abs(n));
                buffer.peak = Math.max(buffer.peak, Math.abs(n));
                rmsSum += n * n;
                rmsCount += 1;
                buffer.rmsSum += n * n;
                buffer.rmsCount += 1;
                if (i % 8 === 0) {
                  waveHash = ((waveHash << 5) - waveHash + buffer.wave[i] + analyserIndex) | 0;
                  buffer.waveHash = ((buffer.waveHash << 5) - buffer.waveHash + buffer.wave[i]) | 0;
                }
              }
              for (let j = 0; j < buffer.spectrum.length; j += 8) {
                const n = buffer.spectrum[j] / 255;
                spectrumPeak = Math.max(spectrumPeak, n);
                buffer.spectrumPeak = Math.max(buffer.spectrumPeak, n);
                spectrumSum += n * n;
                spectrumCount += 1;
                buffer.spectrumSum += n * n;
                buffer.spectrumCount += 1;
                spectrumHash = ((spectrumHash << 5) - spectrumHash + buffer.spectrum[j] + analyserIndex) | 0;
                buffer.spectrumHash = ((buffer.spectrumHash << 5) - buffer.spectrumHash + buffer.spectrum[j]) | 0;
              }
            });
            await new Promise(resolve => setTimeout(resolve, 40));
          }
          const analyserPeaks = buffers.map(buffer => ({
            peak: Number(buffer.peak.toFixed(5)),
            rms: Number(Math.sqrt(buffer.rmsSum / Math.max(1, buffer.rmsCount)).toFixed(5)),
            spectrumPeak: Number(buffer.spectrumPeak.toFixed(5)),
            spectrumRms: Number(Math.sqrt(buffer.spectrumSum / Math.max(1, buffer.spectrumCount)).toFixed(5)),
            waveformHash: String(buffer.waveHash),
            spectrumHash: String(buffer.spectrumHash)
          }));
          const aggregateRms = Number(Math.sqrt(rmsSum / Math.max(1, rmsCount)).toFixed(5));
          const strongestAnalyserRms = Math.max(aggregateRms, ...analyserPeaks.map(row => row.rms || 0));
          return {
            available: true,
            instrumentType: probe.instrumentType || '',
            settingsHash: probe.settingsHash || '',
            settingsKeys: probe.settingsKeys || [],
            engineSettingsKey: probe.engineSettingsKey || '',
            engineSettingsHash: probe.engineSettingsHash || '',
            engineSettingsKeys: probe.engineSettingsKeys || [],
            engineSettings: probe.engineSettings || null,
            physicalSettings: probe.physicalSettings || null,
            analyserArmedBeforeTrigger: true,
            analyserCount: buffers.length,
            analyserPeaks,
            peak: Number(peak.toFixed(5)),
            rms: Number(strongestAnalyserRms.toFixed(5)),
            aggregateRms,
            spectrumPeak: Number(spectrumPeak.toFixed(5)),
            spectrumRms: Number(Math.sqrt(spectrumSum / Math.max(1, spectrumCount)).toFixed(5)),
            waveformHash: String(waveHash),
            spectrumHash: String(spectrumHash)
          };
        }
        """,
        sample_ms,
    )


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


def trigger_note(page, trigger):
    if trigger == "midi":
        page.evaluate(
            """
            () => {
              window.__presetSweepMidiInput.onmidimessage({ data: [0x9E, 48, 96] });
              setTimeout(() => window.__presetSweepMidiInput.onmidimessage({ data: [0xDE, 127] }), 80);
              setTimeout(() => window.__presetSweepMidiInput.onmidimessage({ data: [0x8E, 48, 0] }), 700);
            }
            """
        )
    else:
        page.locator('[data-testid="play-step"]').click()


def run(args):
    if not args.no_build:
        subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit(f"Python Playwright is required: {exc}") from exc

    cases = args.case or DEFAULT_CASES
    output = (ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    server, url = start_server()
    results = []
    errors = []
    started = time.time()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed, args=["--autoplay-policy=no-user-gesture-required"])
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(url)
            page.wait_for_selector('[data-testid="sound-engine-select"]')
            if args.trigger == "midi":
                enable_mock_midi(page)
            for engine, category, preset, expected_type in cases:
                ensure_engine_visible(page, engine)
                select_by_label(page, '[data-testid="sound-engine-select"]', engine)
                select_by_label(page, '[data-testid="sound-category-select"]', category)
                select_by_label(page, '[data-testid="sound-preset-select"]', preset)
                page.locator('[data-testid="play-step"]').click()
                page.wait_for_timeout(850)
                prepare_signature_probe(page)
                trigger_note(page, args.trigger)
                signature = capture_signature(page, args.sample_ms)
                row = {
                    "engine": engine,
                    "category": category,
                    "preset": preset,
                    "trigger": args.trigger,
                    "expectedInstrumentType": expected_type,
                    **signature,
                }
                if not signature.get("available"):
                    errors.append(f"{engine}/{category}/{preset}: no audio signature ({signature.get('error', '')})")
                if expected_type and signature.get("instrumentType") != expected_type:
                    errors.append(f"{engine}/{category}/{preset}: expected engine {expected_type}, got {signature.get('instrumentType')}")
                if expected_type and expected_type != "subtractive" and not signature.get("engineSettingsKeys"):
                    errors.append(f"{engine}/{category}/{preset}: missing {expected_type} parameter block")
                if max(signature.get("peak", 0), signature.get("spectrumPeak", 0)) < 0.015:
                    errors.append(f"{engine}/{category}/{preset}: audio energy too low")
                results.append(row)
        finally:
            browser.close()
            server.shutdown()

    seen = {}
    for row in results:
        identity = (row.get("instrumentType"), row.get("settingsHash"), row.get("engineSettingsHash"), row.get("waveformHash"), row.get("spectrumHash"))
        if identity in seen:
            other = seen[identity]
            errors.append(f"{row['engine']}/{row['category']}/{row['preset']} matches default/other signature {other}")
        seen[identity] = f"{row['engine']}/{row['category']}/{row['preset']}"

    payload = {
        "summary": {
            "url": url,
            "elapsedSeconds": round(time.time() - started, 3),
            "caseCount": len(results),
            "failed": len(errors),
        },
        "errors": errors,
        "results": results,
    }
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    if errors:
        print("\n".join(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
