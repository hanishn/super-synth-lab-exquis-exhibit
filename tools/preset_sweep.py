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
    return [
        preset
        for preset in presets
        if contains_text(preset, ("engine", "engineLabel"), args.engine)
        and contains_text(preset, ("category", "categoryLabel"), args.category)
        and contains_text(preset, ("preset", "presetLabel"), args.preset_contains)
    ]


def diagnostic_tail(page):
    text = page.locator('[data-testid="diagnostic-log"]').inner_text(timeout=1000)
    return text.splitlines()[-12:]


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


def ssli_audio_signature(page, sample_ms):
    return page.evaluate(
        """
        async (sampleMs) => {
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow && frame.contentWindow.SynthLab
            ? frame.contentWindow
            : window;
          const SL = host.SynthLab;
          if (!SL || !SL.audio) {
            return { available: false, peak: 0, rms: 0, spectrumPeak: 0, spectrumRms: 0, waveformHash: '', spectrumHash: '', samples: 0 };
          }
          const inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
          const instruments = SL.audio.getInstruments ? SL.audio.getInstruments() : [];
          if (instruments && instruments[inst] && instruments[inst]._analyserNode) {
            try { instruments[inst]._analyserNode.disconnect(); } catch (err) {}
            instruments[inst]._analyserNode = null;
          }
          let analyser = null;
          if (SL.audio.getInstrumentAnalyser) analyser = SL.audio.getInstrumentAnalyser(inst);
          if (!analyser && SL.audio.getAnalyser) analyser = SL.audio.getAnalyser();
          if (!analyser) {
            return { available: false, peak: 0, rms: 0, spectrumPeak: 0, spectrumRms: 0, waveformHash: '', spectrumHash: '', samples: 0 };
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
            samples
          };
        }
        """,
        sample_ms,
    )


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
                    select_if_present(page, '[data-testid="sound-engine-select"]', preset["engine"])
                    select_if_present(page, '[data-testid="sound-category-select"]', preset["category"])
                    select_if_present(page, '[data-testid="sound-preset-select"]', preset["preset"])
                    page.locator('[data-testid="play-step"]').click(timeout=args.timeout_ms)
                    audio_signature = ssli_audio_signature(page, args.audio_sample_ms)
                    page.wait_for_timeout(args.settle_ms)
                    log_tail = diagnostic_tail(page)
                    instrument = ssli_instrument_snapshot(page)
                    joined = "\n".join(log_tail)
                    if "SSLI play" not in joined and "playing C" not in joined and "playing " not in joined:
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
                }
                results.append(row)
                print(f"[{index}/{len(presets)}] {status.upper()} {preset['engine']} / {preset['categoryLabel']} / {preset['presetLabel']}")
        finally:
            browser.close()
            server.shutdown()

    summary = {
        "url": url,
        "startedAt": started_at,
        "elapsedSeconds": round(time.time() - started_at, 3),
        "availablePresetCount": total,
        "sweptPresetCount": len(results),
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
