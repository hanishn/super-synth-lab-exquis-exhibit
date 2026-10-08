#!/usr/bin/env python3
"""Compare exhibit FM output against a DX7/Dexed sysex reference."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import resample_poly

from preset_sweep import (
    ROOT,
    clear_diagnostics,
    enable_mock_midi,
    select_if_present,
    set_performance_volume,
    start_public_server,
)


REFERENCE_BANK = ROOT / "tests" / "fixtures" / "dx7" / "rom1a.syx"


def parse_args():
    parser = argparse.ArgumentParser(description="Compare an exhibit FM preset to a DX7/Dexed reference render.")
    parser.add_argument("--engine", default="FM")
    parser.add_argument("--category", default="Keys")
    parser.add_argument("--preset", default="FM::DX RHODES")
    parser.add_argument("--reference-bank", default=str(REFERENCE_BANK))
    parser.add_argument("--reference-voice", default="E.PIANO 1")
    parser.add_argument("--output", default="tmp_fm_reference_compare/result.json")
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--min-log-spectrum-cosine", type=float, default=0.74)
    parser.add_argument("--max-centroid-ratio-delta", type=float, default=0.5)
    parser.add_argument("--max-high-ratio-delta", type=float, default=0.18)
    return parser.parse_args()


def rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(audio))) if audio.size else 0.0)


def normalize(audio: np.ndarray) -> np.ndarray:
    audio = np.asarray(audio, dtype=np.float64)
    audio = audio - float(np.mean(audio))
    value = rms(audio)
    if value <= 1e-9:
        return audio
    return audio / value


def render_dexed_reference(bank_path: Path, voice_name: str, sample_rate: int = 44100) -> np.ndarray:
    from dexed import DexedSynth, Patch

    wanted = voice_name.strip().upper()
    bank = Patch.load_bank(str(bank_path))
    patch = next((patch for patch in bank if patch.name.strip().upper() == wanted), None)
    if patch is None:
        names = [patch.name.strip() for patch in bank]
        raise SystemExit(f"Reference voice {voice_name!r} not found in {bank_path}; available={names}")

    synth = DexedSynth(sample_rate)
    synth.load_patch(patch)
    notes = [
        (48, 104, 0.000),
        (50, 108, 0.038),
        (52, 96, 0.046),
        (53, 116, 0.054),
        (55, 92, 0.062),
        (57, 122, 0.070),
    ]
    total = int(sample_rate * 1.2)
    mix = np.zeros(total, dtype=np.float64)
    for midi, velocity, offset in notes:
        rendered = synth.render(midi_note=midi, velocity=velocity, note_duration=0.52, render_duration=1.2)
        start = int(round(offset * sample_rate))
        end = min(total, start + len(rendered))
        mix[start:end] += np.asarray(rendered[: end - start], dtype=np.float64)
    peak = float(np.max(np.abs(mix))) if mix.size else 0.0
    if peak > 0:
        mix = mix / peak * 0.95
    return mix.astype(np.float32)


def capture_exhibit_pcm(args) -> tuple[np.ndarray, int, str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit(f"Python Playwright is required: {exc}") from exc

    server, url = start_public_server()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--autoplay-policy=no-user-gesture-required"],
            )
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(url)
                page.wait_for_selector('[data-testid="sound-engine-select"]')
                enable_mock_midi(page)
                set_performance_volume(page, 80)
                select_if_present(page, '[data-testid="sound-engine-select"]', args.engine)
                select_if_present(page, '[data-testid="sound-category-select"]', args.category)
                select_if_present(page, '[data-testid="sound-preset-select"]', args.preset)
                clear_diagnostics(page)
                payload = page.evaluate(
                    """
                    async ({ captureMs }) => {
                      const input = window.__presetSweepMidiInput;
                      if (!input || !input.onmidimessage) return { error: 'missing mock MIDI input' };
                      const send = (data) => input.onmidimessage({ data });
                      const frame = document.getElementById('ssliEngineFrame');
                      const host = frame && frame.contentWindow && frame.contentWindow.SynthLab ? frame.contentWindow : window;
                      const SL = host.SynthLab;
                      if (!SL || !SL.audio) return { error: 'missing SynthLab.audio' };
                      if (SL.audio.getCtx) SL.audio.getCtx();
                      if (SL.audio.initEffectChain) {
                        const inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
                        const instruments = SL.audio.getInstruments ? SL.audio.getInstruments() : [];
                        if (!(instruments[inst] && instruments[inst].masterOutput)) SL.audio.initEffectChain();
                      }
                      const ctx = SL.audio.getCtx ? SL.audio.getCtx() : null;
                      if (!ctx) return { error: 'missing audio context' };
                      if (ctx.state === 'suspended' && ctx.resume) await ctx.resume();
                      const analyser = SL.audio.getAnalyser ? SL.audio.getAnalyser() : null;
                      if (!analyser) return { error: 'missing analyser' };
                      const processor = ctx.createScriptProcessor(2048, 1, 1);
                      const samples = [];
                      processor.onaudioprocess = (event) => {
                        const inputBuffer = event.inputBuffer.getChannelData(0);
                        for (let i = 0; i < inputBuffer.length; i += 1) samples.push(inputBuffer[i]);
                      };
                      analyser.connect(processor);
                      processor.connect(ctx.destination);
                      const notes = [
                        { midi: 48, channel: 7, velocity: 104, delay: 0 },
                        { midi: 50, channel: 13, velocity: 108, delay: 38 },
                        { midi: 52, channel: 9, velocity: 96, delay: 46 },
                        { midi: 53, channel: 2, velocity: 116, delay: 54 },
                        { midi: 55, channel: 15, velocity: 92, delay: 62 },
                        { midi: 57, channel: 5, velocity: 122, delay: 70 }
                      ];
                      notes.forEach(note => setTimeout(() => send([0x90 | note.channel, note.midi, note.velocity]), note.delay));
                      notes.forEach((note, index) => setTimeout(() => {
                        send([0xD0 | note.channel, 0]);
                        send([0x80 | note.channel, note.midi, 0]);
                      }, 520 + index * 12));
                      await new Promise(resolve => setTimeout(resolve, captureMs));
                      try { analyser.disconnect(processor); } catch (e) {}
                      try { processor.disconnect(); } catch (e) {}
                      const logEl = document.querySelector('[data-testid="diagnostic-log"]');
                      return { sampleRate: ctx.sampleRate, samples, diagnosticLog: logEl ? logEl.textContent : '' };
                    }
                    """,
                    {"captureMs": 1350},
                )
                if payload.get("error"):
                    raise SystemExit(payload["error"])
                return np.asarray(payload["samples"], dtype=np.float32), int(payload["sampleRate"]), payload.get("diagnosticLog", "")
            finally:
                browser.close()
    finally:
        server.shutdown()


def spectral_features(audio: np.ndarray, sample_rate: int) -> dict:
    audio = normalize(audio)
    if sample_rate != 44100:
        common = math.gcd(sample_rate, 44100)
        audio = resample_poly(audio, 44100 // common, sample_rate // common)
        sample_rate = 44100
    n_fft = 4096
    hop = 1024
    if audio.size < n_fft:
        audio = np.pad(audio, (0, n_fft - audio.size))
    window = np.hanning(n_fft)
    frames = []
    for start in range(0, max(1, audio.size - n_fft + 1), hop):
        frame = audio[start : start + n_fft]
        if frame.size < n_fft:
            frame = np.pad(frame, (0, n_fft - frame.size))
        frames.append(np.abs(np.fft.rfft(frame * window)) + 1e-9)
    spectrum = np.mean(np.stack(frames), axis=0)
    freqs = np.fft.rfftfreq(n_fft, 1 / sample_rate)
    energy = spectrum * spectrum
    centroid = float(np.sum(freqs * energy) / np.sum(energy))
    high_ratio = float(np.sum(energy[freqs >= 4000]) / np.sum(energy))
    bell_ratio = float(np.sum(energy[(freqs >= 2500) & (freqs <= 10000)]) / np.sum(energy))
    log_spec = np.log1p(spectrum)
    log_spec = log_spec / max(1e-9, float(np.linalg.norm(log_spec)))
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    value_rms = rms(audio)
    return {
        "sampleRate": sample_rate,
        "samples": int(audio.size),
        "rms": value_rms,
        "peak": peak,
        "peakToRms": peak / max(1e-9, value_rms),
        "centroidHz": centroid,
        "highRatio": high_ratio,
        "bellRatio": bell_ratio,
        "logSpectrum": log_spec,
    }


def comparable_summary(features: dict) -> dict:
    return {
        key: round(float(value), 6) if isinstance(value, (float, np.floating)) else value
        for key, value in features.items()
        if key != "logSpectrum"
    }


def main():
    args = parse_args()
    if not args.no_build:
        subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)

    reference_audio = render_dexed_reference(Path(args.reference_bank), args.reference_voice)
    exhibit_audio, exhibit_rate, diagnostic_log = capture_exhibit_pcm(args)

    reference = spectral_features(reference_audio, 44100)
    exhibit = spectral_features(exhibit_audio, exhibit_rate)
    log_spectrum_cosine = float(np.dot(reference["logSpectrum"], exhibit["logSpectrum"]))
    centroid_ratio_delta = abs(exhibit["centroidHz"] - reference["centroidHz"]) / max(1.0, reference["centroidHz"])
    high_ratio_delta = abs(exhibit["highRatio"] - reference["highRatio"])

    errors = []
    if log_spectrum_cosine < args.min_log_spectrum_cosine:
        errors.append(f"log spectrum cosine too low ({log_spectrum_cosine:.4f})")
    if centroid_ratio_delta > args.max_centroid_ratio_delta:
        errors.append(f"centroid ratio delta too high ({centroid_ratio_delta:.4f})")
    if high_ratio_delta > args.max_high_ratio_delta:
        errors.append(f"high ratio delta too high ({high_ratio_delta:.4f})")

    result = {
        "status": "fail" if errors else "pass",
        "errors": errors,
        "preset": args.preset,
        "referenceVoice": args.reference_voice,
        "referenceBank": str(args.reference_bank),
        "metrics": {
            "logSpectrumCosine": round(log_spectrum_cosine, 6),
            "centroidRatioDelta": round(float(centroid_ratio_delta), 6),
            "highRatioDelta": round(float(high_ratio_delta), 6),
        },
        "reference": comparable_summary(reference),
        "exhibit": comparable_summary(exhibit),
        "diagnosticLogTail": diagnostic_log.splitlines()[-20:],
    }

    output = (ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
