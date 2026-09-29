import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StaticExhibitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["python", "build.py"], cwd=ROOT, check=True)
        cls.bundle = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_standalone_build_shape(self):
        self.assertTrue((ROOT / "index.html").exists())
        self.assertTrue((ROOT / "dist/index.html").exists())
        self.assertIn("<!doctype html>", self.bundle.lower())
        self.assertIn('src="ssli/index.html"', self.bundle)
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
            "build.py"
        ]
        for rel in expected:
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_bundle_contains_core_ui(self):
        self.assertIn("Exquis Fingering Lab", self.bundle)
        self.assertIn('data-testid="keyboard"', self.bundle)
        self.assertIn("EXQUIS_NOTE_ROWS", self.bundle)
        self.assertIn("Soft Wurli", self.bundle)
        self.assertIn("function playNote", self.bundle)
        self.assertIn("SSLI_VENDOR", self.bundle)

    def test_public_index_is_built(self):
        self.assertTrue((ROOT / "index.html").exists())
        self.assertTrue((ROOT / "dist/index.html").exists())

    def test_public_build_includes_real_ssli_engine_host(self):
        ssli_index = ROOT / "ssli/index.html"
        self.assertTrue(ssli_index.exists())
        self.assertGreater(ssli_index.stat().st_size, 1_000_000)
        self.assertIn('id="ssliEngineFrame"', self.bundle)
        self.assertIn('src="ssli/index.html"', self.bundle)
        self.assertIn("SL.presets.apply", self.bundle)
        self.assertIn("SL.audio.playNoteOnInstrument", self.bundle)

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
        self.assertIn("ssli_audio_signature", text)
        self.assertIn("instrumentSettingsHash", text)
        self.assertIn("audioPeak", text)
        self.assertIn("audioRms", text)
        self.assertIn("audioSpectrumPeak", text)
        self.assertIn("audioSpectrumRms", text)
        self.assertIn("_analyserNode", text)
        self.assertIn("audioWaveformHash", text)
        self.assertIn("audioSpectrumHash", text)
        self.assertIn("preset-sweep-results.json", text)
        self.assertIn("preset-sweep-results.csv", text)

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
        self.assertIn("--output-dir", result.stdout)
        self.assertIn("--no-build", result.stdout)

    def test_capabilities_document_repeatable_preset_sweep(self):
        doc = (ROOT / "docs/capabilities.md").read_text(encoding="utf-8")
        self.assertIn("tools/preset_sweep.py", doc)
        self.assertIn("Omitting it sweeps every preset", doc)
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
