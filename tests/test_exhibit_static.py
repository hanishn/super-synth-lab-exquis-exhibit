import json
import re
import subprocess
import unittest
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]


def load_module(rel_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StaticExhibitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["python", "build.py"], cwd=ROOT, check=True)
        cls.bundle = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_standalone_build_shape(self):
        self.assertTrue((ROOT / "index.html").exists())
        self.assertTrue((ROOT / "dist/index.html").exists())
        self.assertIn("<!doctype html>", self.bundle.lower())
        self.assertRegex(self.bundle, r'src="ssli/index\.html\?v=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"')
        self.assertFalse((ROOT / "exhibit.json").exists())

    def test_versioned_parts_exist(self):
        expected = [
            "src/metadata.json",
            "src/capabilities.json",
            "src/parts/template.html",
            "src/parts/index.html",
            "src/parts/styles.css",
            "src/parts/app.js",
            "docs/capabilities.md",
            "tools/preset_sweep.py",
            "tools/preset_signature_check.py",
            "build.py"
        ]
        for rel in expected:
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_bundle_contains_core_ui(self):
        self.assertIn("Exquis Fingering Lab", self.bundle)
        self.assertIn('data-testid="build-version"', self.bundle)
        self.assertIn('data-testid="keyboard"', self.bundle)
        self.assertIn("EXQUIS_NOTE_ROWS", self.bundle)
        self.assertIn("Soft Wurli", self.bundle)
        self.assertIn('data-testid="mode-select"', self.bundle)
        self.assertIn('data-testid="mode-switch"', self.bundle)
        self.assertIn('data-testid="practice-mode"', self.bundle)
        self.assertIn('data-testid="play-mode"', self.bundle)
        self.assertIn("Practice", self.bundle)
        self.assertIn("Play", self.bundle)
        self.assertIn("function playNote", self.bundle)
        self.assertIn("SSLI_VENDOR", self.bundle)

    def test_build_version_is_generated_visible_and_used_for_cache_busting(self):
        match = re.search(r'data-testid="build-version"[^>]*title="Built ([^"]+)"[^>]*>\s*<span>Build</span>\s*<b>([^<]+)</b>', self.bundle)
        self.assertIsNotNone(match)
        timestamp = match.group(1)
        version = match.group(2)
        self.assertRegex(version, r"^Build \d+$")
        self.assertRegex(timestamp, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [AP]M ET$")
        utc_match = re.search(r'<meta name="ssli-exquis-build-timestamp-utc" content="([^"]+)">', self.bundle)
        self.assertIsNotNone(utc_match)
        utc_timestamp = utc_match.group(1)
        self.assertIn(f'<meta name="ssli-exquis-build-version" content="{version}">', self.bundle)
        self.assertIn(f'window.SSLI_EXQUIS_BUILD = {{"version":"{version}","timestamp":"{timestamp}","timestampUtc":"{utc_timestamp}"}};', self.bundle)
        self.assertIn(f'src="ssli/index.html?v={utc_timestamp}"', self.bundle)
        self.assertIn(f"var freshSrc = 'ssli/index.html?v={utc_timestamp}';", self.bundle)
        self.assertNotIn("{{BUILD_VERSION}}", self.bundle)
        self.assertNotIn("{{BUILD_TIMESTAMP}}", self.bundle)
        self.assertNotIn("{{BUILD_TIMESTAMP_UTC}}", self.bundle)

    def test_build_version_changes_on_each_build(self):
        import build

        first = build.build()
        second = build.build()
        self.assertEqual(second["buildNumber"], first["buildNumber"] + 1)
        self.assertNotEqual(first["buildVersion"], second["buildVersion"])
        rebuilt = (ROOT / "index.html").read_text(encoding="utf-8")
        rebuilt_dist = (ROOT / "dist/index.html").read_text(encoding="utf-8")
        self.assertIn('data-testid="build-version"', rebuilt)
        self.assertIn(second["buildVersion"], rebuilt)
        self.assertIn(second["buildVersion"], rebuilt_dist)

    def test_public_index_is_built(self):
        self.assertTrue((ROOT / "index.html").exists())
        self.assertTrue((ROOT / "dist/index.html").exists())

    def test_source_docs_and_manifest_are_plain_utf8_without_bom(self):
        for rel in ["src/capabilities.json", "docs/capabilities.md"]:
            data = (ROOT / rel).read_bytes()
            self.assertFalse(data.startswith(b"\xef\xbb\xbf"), rel)

    def test_public_build_includes_real_ssli_engine_host(self):
        ssli_index = ROOT / "ssli/index.html"
        self.assertTrue(ssli_index.exists())
        self.assertGreater(ssli_index.stat().st_size, 1_000_000)
        self.assertIn('id="ssliEngineFrame"', self.bundle)
        self.assertRegex(self.bundle, r'src="ssli/index\.html\?v=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"')
        self.assertIn("SL.presets.apply", self.bundle)
        self.assertIn("SL.audio.playNoteOnInstrument", self.bundle)

    def test_capability_docs_describe_play_and_practice_modes(self):
        docs = (ROOT / "docs/capabilities.md").read_text(encoding="utf-8")
        self.assertIn("### Play Mode and Practice Mode", docs)
        self.assertIn("Practice mode", docs)
        self.assertIn("Play mode", docs)
        self.assertIn("scoring", docs)

    def test_capability_docs_require_spec_test_implement_verify_order(self):
        docs = (ROOT / "docs/capabilities.md").read_text(encoding="utf-8")
        section = docs.split("New feature workflow invariant:", 1)[1].split("Stated failure workflow:", 1)[0]
        required_order = [
            "Update the durable spec first",
            "Update unit/static/Playwright tests second",
            "Verify the new or changed tests fail",
            "Implement only after the spec and tests",
            "Verify the targeted tests pass",
            "Run the full existing unit suite"
        ]
        positions = [section.index(item) for item in required_order]
        self.assertEqual(positions, sorted(positions))

    def test_regression_ssli_runtime_keeps_upstream_physical_pluck_level(self):
        ssli_text = (ROOT / "ssli/index.html").read_text(encoding="utf-8")
        dist_ssli_text = (ROOT / "dist/ssli/index.html").read_text(encoding="utf-8")
        self.assertIn("var PLUCK_VOICE_LEVEL  = 0.25;  // transient, slightly hotter OK", ssli_text)
        self.assertIn("var PLUCK_VOICE_LEVEL  = 0.25;  // transient, slightly hotter OK", dist_ssli_text)
        self.assertNotIn("Exquis exhibit: make physical plucks audible from MPE pads", ssli_text)
        self.assertNotIn("Exquis exhibit: make physical plucks audible from MPE pads", dist_ssli_text)

    def test_regression_ssli_runtime_patches_are_required_and_named(self):
        import build

        self.assertGreaterEqual(len(build.SSLI_INDEX_PATCHES), 4)
        self.assertTrue(all(patch.name and patch.before and patch.after for patch in build.SSLI_INDEX_PATCHES))
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "index.html"
            with self.assertRaisesRegex(RuntimeError, "Missing SSLI runtime patch target"):
                build.apply_required_text_patches("unrelated upstream file", build.SSLI_INDEX_PATCHES, target)

    def test_regression_ssli_physical_runtime_exposes_per_note_pressure_api(self):
        ssli_text = (ROOT / "ssli/index.html").read_text(encoding="utf-8")
        worklet_text = (ROOT / "ssli/assets/physical-worklet.js").read_text(encoding="utf-8")
        self.assertIn("function updateNotePressure(midi, pressure, instId)", ssli_text)
        self.assertIn("updateNotePressure: updateNotePressure", ssli_text)
        self.assertIn("type: 'notePressure'", ssli_text)
        self.assertIn("case 'notePressure':", worklet_text)
        self.assertIn("updateNotePressure(midiNote, pressure, instId)", worklet_text)
        self.assertIn("setPressure(pressure)", worklet_text)

    def test_regression_physical_pluck_aftertouch_does_not_add_energy_above_note_on(self):
        worklet_text = (ROOT / "ssli/assets/physical-worklet.js").read_text(encoding="utf-8")
        ssli_text = (ROOT / "ssli/index.html").read_text(encoding="utf-8")
        self.assertIn("this.modelType === 'pluck'", worklet_text)
        self.assertIn("this.targetPressureGain = 1.0;", worklet_text)
        self.assertIn("this.pressureGain = 1.0;", worklet_text)
        self.assertIn("this.targetPressureGain = 1.0;", ssli_text)
        self.assertIn("0.2 + normalized * 0.8", worklet_text)
        self.assertNotIn("0.95 + normalized * 0.05", worklet_text)
        self.assertNotIn("0.95 + normalized * 0.05", ssli_text)
        self.assertNotIn("normalized * 1.25", worklet_text)
        self.assertNotIn("1.35", worklet_text)

    def test_regression_plucked_midi_one_shots_do_not_schedule_helper_note_off(self):
        app = (ROOT / "src/parts/app.js").read_text(encoding="utf-8")
        match = re.search(r"function startPluckedOneShotWithSsli\(midi, velocity, options\) \{([\s\S]*?)\n  \}\n\n  function stopSustainedWithSsli", app)
        self.assertIsNotNone(match)
        body = match.group(1)
        self.assertIn("SL.physical.noteOn(midi, playableVelocity, inst);", body)
        self.assertIn("decay=natural", body)
        self.assertNotIn("playNoteOnInstrument", body)
        self.assertNotIn("physical.noteOff", body)

    def test_regression_physical_worklet_scales_six_voice_polyphony_headroom(self):
        worklet_text = (ROOT / "ssli/assets/physical-worklet.js").read_text(encoding="utf-8")
        self.assertIn("polyphonyMixGain", worklet_text)
        self.assertIn("numActive > 4 ? 4 / numActive : 1", worklet_text)
        self.assertIn("PHYS_VOICE_OUTPUT_GAIN * polyphonyMixGain", worklet_text)

    def test_regression_physical_voice_headroom_has_no_pitch_specific_pluck_hack(self):
        app_text = (ROOT / "src/parts/app.js").read_text(encoding="utf-8")
        worklet_text = (ROOT / "ssli/assets/physical-worklet.js").read_text(encoding="utf-8")
        ssli_text = (ROOT / "ssli/index.html").read_text(encoding="utf-8")
        self.assertNotIn("semitoneJamGuard", app_text)
        self.assertNotIn("hasRecentPhysicalSemitoneNeighbor", app_text)
        self.assertIn("var PLUCK_OUTPUT_SCALE = 1.0;", worklet_text)
        self.assertIn("var PLUCK_OUTPUT_SCALE = 1.0;", ssli_text)
        self.assertNotIn("var PLUCK_OUTPUT_SCALE = 1.5;", worklet_text)
        self.assertNotIn("var PLUCK_OUTPUT_SCALE = 1.5;", ssli_text)

    def test_regression_ssli_runtime_cannot_be_served_from_stale_service_worker(self):
        ssli_text = (ROOT / "ssli/index.html").read_text(encoding="utf-8")
        self.assertIn("service worker disabled for Exquis exhibit runtime", ssli_text)
        self.assertNotIn("navigator.serviceWorker.register('sw.js')", ssli_text)
        self.assertIn("ensureFreshSsliFrame", self.bundle)
        self.assertRegex(self.bundle, r"ssli/index\.html\?v=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
        self.assertIn("removed stale SSLI service worker cache", self.bundle)

    def test_public_build_includes_ssli_audio_worklet_assets(self):
        asset_dir = ROOT / "ssli/assets"
        expected = [
            "synth-worklet.js",
            "fm-worklet.js",
            "physical-worklet.js",
            "formant-worklet.js",
            "effects/grainfield-worklet.js",
        ]
        for rel in expected:
            asset = asset_dir / rel
            self.assertTrue(asset.exists(), rel)
            self.assertGreater(asset.stat().st_size, 500, rel)

    def test_public_build_includes_ssli_app_support_files(self):
        expected = ["manifest.json", "sw.js", "logo.png"]
        for rel in expected:
            support_file = ROOT / "ssli" / rel
            self.assertTrue(support_file.exists(), rel)
            self.assertGreater(support_file.stat().st_size, 100, rel)

    def test_vendored_ssli_parts_exist(self):
        self.assertTrue((ROOT / "src/vendor/ssli/scales-modes.json").exists())
        self.assertTrue((ROOT / "src/vendor/ssli/constants.js").exists())
        self.assertTrue((ROOT / "src/vendor/ssli/fx-presets.json").exists())
        preset_dir = ROOT / "src/vendor/ssli/presets"
        expected = {
            "additive-presets.json",
            "bytebeat-presets.json",
            "fm-presets.json",
            "formant-presets.json",
            "granular-presets.json",
            "modal-presets.json",
            "phasedist-presets.json",
            "physical-presets.json",
            "reed-presets.json",
            "subtractive-presets.json",
            "vector-presets.json",
            "vocoder-presets.json",
            "wavetable-synth-presets.json",
        }
        self.assertEqual({path.name for path in preset_dir.glob("*.json")}, expected)

    def test_ssli_preset_payload_is_bundled(self):
        self.assertIn('"presetLibraries"', self.bundle)
        self.assertIn('"subtractive"', self.bundle)
        self.assertIn('"Wurlitzer EP"', self.bundle)
        self.assertIn('"fxPresets"', self.bundle)
        self.assertIn('"lead-solo"', self.bundle)

    def test_ssli_vendor_data_has_expected_shape(self):
        subtractive = json.loads((ROOT / "src/vendor/ssli/presets/subtractive-presets.json").read_text(encoding="utf-8"))
        fx = json.loads((ROOT / "src/vendor/ssli/fx-presets.json").read_text(encoding="utf-8"))
        self.assertGreater(len(subtractive["presets"]), 50)
        self.assertTrue(any(preset["name"] == "Wurlitzer EP" for preset in subtractive["presets"]))
        self.assertIn("library", fx)
        self.assertTrue(any(preset["id"] == "lead-solo" for group in fx["library"].values() for preset in group))

    def test_every_bundled_preset_has_articulation_capability(self):
        import build

        preset_dir = ROOT / "src/vendor/ssli/presets"
        required = {"family", "onsetMode", "captureWindowMs", "minInterOnsetMs", "maxSpreadMs", "order", "pressurePolicy"}
        for path in sorted(preset_dir.glob("*-presets.json")):
            engine = path.stem.replace("-presets", "")
            library = build.with_articulation_defaults(engine, json.loads(path.read_text(encoding="utf-8")))
            for preset in library["presets"]:
                articulation = preset.get("articulation")
                self.assertIsInstance(articulation, dict, f"{engine}/{preset.get('category')}/{preset.get('name')}")
                self.assertTrue(required.issubset(articulation), f"{engine}/{preset.get('category')}/{preset.get('name')}: {articulation}")

    def test_plucked_physical_presets_use_strum_articulation_and_keys_remain_immediate(self):
        import build

        physical = build.with_articulation_defaults("physical", json.loads((ROOT / "src/vendor/ssli/presets/physical-presets.json").read_text(encoding="utf-8")))
        nylon = next(preset for preset in physical["presets"] if preset["name"] == "Nylon Guitar")
        self.assertEqual(nylon["articulation"]["family"], "plucked")
        self.assertEqual(nylon["articulation"]["onsetMode"], "strum")
        self.assertGreaterEqual(nylon["articulation"]["minInterOnsetMs"], 8)
        self.assertLessEqual(nylon["articulation"]["maxSpreadMs"], 55)
        self.assertEqual(nylon["articulation"]["pressurePolicy"], "onset-only")

        subtractive = build.with_articulation_defaults("subtractive", json.loads((ROOT / "src/vendor/ssli/presets/subtractive-presets.json").read_text(encoding="utf-8")))
        soft_piano = next(preset for preset in subtractive["presets"] if preset["name"] == "Soft EP")
        self.assertEqual(soft_piano["articulation"]["onsetMode"], "immediate")
        self.assertEqual(soft_piano["articulation"]["pressurePolicy"], "live")

    def test_repeatable_preset_sweep_harness_exists(self):
        script = ROOT / "tools/preset_sweep.py"
        text = script.read_text(encoding="utf-8")
        self.assertIn("sync_playwright", text)
        self.assertIn("collect_presets", text)
        self.assertIn("filter_presets", text)
        self.assertIn('[data-testid="sound-engine-select"]', text)
        self.assertIn('[data-testid="sound-category-select"]', text)
        self.assertIn('[data-testid="sound-preset-select"]', text)
        self.assertIn('[data-testid="play-step"]', text)
        self.assertIn("ssli_instrument_snapshot", text)
        self.assertIn("prepare_ssli_audio_probe", text)
        self.assertIn("capture_ssli_audio_signature", text)
        self.assertIn("analyserArmedBeforeTrigger", text)
        self.assertIn("__exquisDebugSnapshot", text)
        self.assertIn("instrumentSettingsHash", text)
        self.assertIn("audioPeak", text)
        self.assertIn("audioRms", text)
        self.assertIn("audioSpectrumPeak", text)
        self.assertIn("audioSpectrumRms", text)
        self.assertIn("__presetSweepAudioProbe", text)
        self.assertIn("audioWaveformHash", text)
        self.assertIn("audioSpectrumHash", text)
        self.assertIn("apply_duplicate_signature_failures", text)
        self.assertIn("duplicateSignatureGroups", text)
        self.assertIn("preset-sweep-results.json", text)
        self.assertIn("preset-sweep-results.csv", text)

    def test_preset_sweep_filter_one_per_category_uses_first_live_preset(self):
        sweep = load_module("tools/preset_sweep.py", "preset_sweep_for_filter_test")
        presets = [
            {"engine": "physical", "engineLabel": "Physical", "category": "plucked", "categoryLabel": "Plucked", "preset": "physical::A", "presetLabel": "A"},
            {"engine": "physical", "engineLabel": "Physical", "category": "plucked", "categoryLabel": "Plucked", "preset": "physical::B", "presetLabel": "B"},
            {"engine": "fm", "engineLabel": "FM", "category": "keys", "categoryLabel": "Keys", "preset": "fm::A", "presetLabel": "A"},
            {"engine": "granular", "engineLabel": "Granular", "category": "pads", "categoryLabel": "Pads", "preset": "granular::A", "presetLabel": "A"},
        ]
        args = SimpleNamespace(
            engine="",
            category="",
            preset_contains="",
            mature_engines_only=True,
            preset_list_file="",
            one_per_category=True,
        )
        filtered = sweep.filter_presets(presets, args)
        self.assertEqual([row["preset"] for row in filtered], ["physical::A", "fm::A"])

    def test_preset_sweep_validation_requires_current_voice_cleanup_snapshot(self):
        sweep = load_module("tools/preset_sweep.py", "preset_sweep_for_validation_test")
        base = {
            "engine": "physical",
            "engineLabel": "Physical",
            "audioSignature": {
                "available": True,
                "instrumentType": "physical",
                "engineSettingsKeys": ["model"],
                "peak": 0.2,
                "rms": 0.05,
                "spectrumPeak": 0.12,
                "clipRatio": 0.0,
                "diagnosticLog": "old run held=0 local=0 ssli=0",
            },
        }
        self.assertIn("missing MIDI voice cleanup snapshot", "; ".join(sweep.validate_audio_behavior(base, "six-note-midi")))
        stuck = json.loads(json.dumps(base))
        stuck["audioSignature"]["voiceCleanup"] = {"heldNotes": 0, "midiVoices": 1, "ssliActiveOscillators": 0}
        self.assertIn("MIDI voices not idle", "; ".join(sweep.validate_audio_behavior(stuck, "six-note-midi")))
        clean = json.loads(json.dumps(base))
        clean["audioSignature"]["voiceCleanup"] = {"heldNotes": 0, "midiVoices": 0, "ssliActiveOscillators": 0}
        clean["audioSignature"]["diagnosticLog"] = "current run held=0 local=0 ssli=0"
        self.assertEqual(sweep.validate_audio_behavior(clean, "six-note-midi"), [])

    def test_preset_sweep_duplicate_signature_detection_flags_same_category_presets(self):
        sweep = load_module("tools/preset_sweep.py", "preset_sweep_for_duplicate_test")
        rows = [
            {
                "status": "pass",
                "engine": "Subtractive",
                "category": "Keys",
                "preset": "subtractive::A",
                "presetLabel": "A",
                "instrumentType": "subtractive",
                "instrumentSettingsHash": "settings-a",
                "audioWaveformHash": "wave-a",
                "audioSpectrumHash": "spec-a",
                "audioSignature": {"engineSettingsHash": "engine-a"},
                "error": "",
            },
            {
                "status": "pass",
                "engine": "Subtractive",
                "category": "Keys",
                "preset": "subtractive::B",
                "presetLabel": "B",
                "instrumentType": "subtractive",
                "instrumentSettingsHash": "settings-a",
                "audioWaveformHash": "wave-a",
                "audioSpectrumHash": "spec-a",
                "audioSignature": {"engineSettingsHash": "engine-a"},
                "error": "",
            },
            {
                "status": "pass",
                "engine": "Subtractive",
                "category": "Pads",
                "preset": "subtractive::C",
                "presetLabel": "C",
                "instrumentType": "subtractive",
                "instrumentSettingsHash": "settings-a",
                "audioWaveformHash": "wave-a",
                "audioSpectrumHash": "spec-a",
                "audioSignature": {"engineSettingsHash": "engine-a"},
                "error": "",
            },
        ]
        self.assertEqual(sweep.apply_duplicate_signature_failures(rows), 1)
        self.assertEqual(rows[0]["status"], "fail")
        self.assertEqual(rows[1]["status"], "fail")
        self.assertEqual(rows[2]["status"], "pass")
        self.assertIn("duplicate preset signature group", rows[0]["error"])

    def test_repeatable_preset_sweep_cli_help(self):
        result = subprocess.run(
            ["python", "tools/preset_sweep.py", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("--limit", result.stdout)
        self.assertIn("--engine", result.stdout)
        self.assertIn("--category", result.stdout)
        self.assertIn("--preset-contains", result.stdout)
        self.assertIn("--preset-list-file", result.stdout)
        self.assertIn("--output-dir", result.stdout)
        self.assertIn("--no-build", result.stdout)

    def test_preset_signature_check_cli_help(self):
        result = subprocess.run(
            ["python", "tools/preset_signature_check.py", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("--case", result.stdout)
        self.assertIn("--sample-ms", result.stdout)
        self.assertIn("--trigger", result.stdout)
        self.assertIn("waveform", result.stdout.lower())

    def test_preset_signature_check_compares_runtime_engine_settings_and_audio(self):
        script = (ROOT / "tools/preset_signature_check.py").read_text(encoding="utf-8")
        self.assertIn("expectedInstrumentType", script)
        self.assertIn("settingsHash", script)
        self.assertIn("engineSettingsHash", script)
        self.assertIn("engineSettingsKeys", script)
        self.assertIn("waveformHash", script)
        self.assertIn("spectrumHash", script)
        self.assertIn("analyserArmedBeforeTrigger", script)
        self.assertIn("instrumentType", script)
        self.assertIn("Physical", script)
        self.assertIn("Koto", script)

    def test_capabilities_document_repeatable_preset_sweep(self):
        doc = (ROOT / "docs/capabilities.md").read_text(encoding="utf-8")
        self.assertIn("tools/preset_sweep.py", doc)
        self.assertIn("Omitting both sweeps every preset", doc)
        self.assertIn("--mature-engines-only --trigger six-note-midi", doc)
        self.assertIn("localhost HTTP server", doc)
        self.assertIn("same-origin", doc)
        self.assertIn("JSON plus CSV", doc)
        self.assertIn("final SSLI output path", doc)
        self.assertIn("engine mismatch", doc)
        self.assertIn("voice cleanup", doc)
        self.assertIn("not acceptance coverage", doc)
        self.assertNotIn("intentionally extreme or flaky", doc)
        self.assertNotIn("deterministic representative presets", doc)
        manifest = json.loads((ROOT / "src/capabilities.json").read_text(encoding="utf-8"))
        caps = {cap["id"]: cap for cap in manifest["capabilities"]}
        self.assertIn("repeatable_preset_sweep", caps)
        criteria = "\n".join(caps["repeatable_preset_sweep"]["acceptanceCriteria"])
        self.assertIn("JSON and CSV", criteria)
        self.assertIn("filter by engine", criteria)
        self.assertIn("instrument type/settings evidence", criteria)
        self.assertIn("live audio signature evidence", criteria)
        self.assertIn("spectrum peak/RMS", criteria)
        self.assertIn("waveform hash", criteria)
        self.assertIn("full mature-engine acceptance sweeps every live Subtractive, FM, and Physical preset", criteria)
        self.assertIn("one-per-category smoke mode must not skip hard presets", criteria)
        self.assertNotIn("intentionally extreme or flaky", criteria)
        self.assertNotIn("representative presets", criteria)

    def test_capabilities_document_maps_every_manifest_capability_to_heading(self):
        doc = (ROOT / "docs/capabilities.md").read_text(encoding="utf-8")
        headings = {
            match.group(1).strip().lower()
            for match in re.finditer(r"^###\s+(.+)$", doc, flags=re.MULTILINE)
        }
        manifest = json.loads((ROOT / "src/capabilities.json").read_text(encoding="utf-8"))
        for cap in manifest["capabilities"]:
            if cap["status"] == "planned":
                continue
            self.assertIn(cap["name"].lower(), headings, cap["id"])

    def test_named_regression_tests_are_registered_or_explicit_static_tripwires(self):
        playwright_module = load_module("tests/test_exhibit_playwright.py", "playwright_for_regression_audit")
        registered = set(playwright_module.PlaywrightExhibitTests.STATED_FAILURE_REGRESSIONS.values())
        static_tripwires = {
            "test_regression_ssli_runtime_keeps_upstream_physical_pluck_level",
            "test_regression_ssli_runtime_patches_are_required_and_named",
            "test_regression_ssli_physical_runtime_exposes_per_note_pressure_api",
            "test_regression_physical_pluck_aftertouch_does_not_add_energy_above_note_on",
            "test_regression_plucked_midi_one_shots_do_not_schedule_helper_note_off",
            "test_regression_physical_worklet_scales_six_voice_polyphony_headroom",
            "test_regression_physical_voice_headroom_has_no_pitch_specific_pluck_hack",
            "test_regression_ssli_runtime_cannot_be_served_from_stale_service_worker",
            "test_regression_preset_sweep_does_not_skip_known_hard_presets_by_preference_table",
        }
        playwright_regressions = {
            name for name in dir(playwright_module.PlaywrightExhibitTests)
            if name.startswith("test_regression_")
        }
        static_regressions = {
            name for name in dir(type(self))
            if name.startswith("test_regression_")
        }
        untracked = (playwright_regressions | static_regressions) - registered - static_tripwires
        self.assertEqual(untracked, set())

    def test_regression_preset_sweep_does_not_skip_known_hard_presets_by_preference_table(self):
        script = (ROOT / "tools/preset_sweep.py").read_text(encoding="utf-8")
        self.assertNotIn("CATEGORY_SAMPLE_PREFERENCES", script)
        self.assertNotIn("preferred_names", script)
        self.assertIn("Do not use as full acceptance", script)

    def test_midi_feedback_has_no_pitch_class_fallback_highlights(self):
        app = (ROOT / "src/parts/app.js").read_text(encoding="utf-8")
        self.assertNotIn("classes.push('midi-held-pitch')", app)
        self.assertNotIn("classes.push('midi-pitch')", app)
        self.assertNotIn("classes.push('midi-last-pitch')", app)
        doc = (ROOT / "docs/capabilities.md").read_text(encoding="utf-8")
        self.assertIn("exact full-MIDI-note matches", doc)

    def test_capability_manifest_is_complete(self):
        manifest = json.loads((ROOT / "src/capabilities.json").read_text(encoding="utf-8"))
        self.assertIn("capabilities", manifest)
        ids = set()
        for cap in manifest["capabilities"]:
            self.assertRegex(cap["id"], r"^[a-z][a-z0-9_]+$")
            self.assertNotIn(cap["id"], ids)
            ids.add(cap["id"])
            self.assertIn(cap["status"], {"planned", "prototype", "stable"})
            self.assertGreater(len(cap["description"]), 20)
            self.assertGreater(len(cap["userValue"]), 20)
            self.assertGreaterEqual(len(cap["acceptanceCriteria"]), 3)
            if cap["status"] != "planned":
                self.assertGreaterEqual(len(cap.get("testIds", [])), 1, cap["id"])

    def test_capability_manifest_test_ids_reference_real_tests(self):
        manifest = json.loads((ROOT / "src/capabilities.json").read_text(encoding="utf-8"))
        test_sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "tests/test_exhibit_static.py", ROOT / "tests/test_exhibit_playwright.py"]
        )
        for cap in manifest["capabilities"]:
            for test_id in cap.get("testIds", []):
                self.assertRegex(test_id, r"^test_[a-zA-Z0-9_]+$", (cap["id"], test_id))
                self.assertIn("def " + test_id + "(", test_sources, (cap["id"], test_id))

    def test_source_provenance_doc_exists(self):
        doc = ROOT / "docs/source-provenance.md"
        self.assertTrue(doc.exists())
        text = doc.read_text(encoding="utf-8")
        self.assertIn("SSLI-first", text)
        self.assertIn("shared/assets/presets/*.json", text)
        self.assertIn("fx-presets.json", text)

    def test_no_clairvoyance_exhibit_artifact_is_committed(self):
        self.assertFalse((ROOT / "exhibit.json").exists())


if __name__ == "__main__":
    unittest.main()
