#!/usr/bin/env python3
"""Build Super Synth Lab Exquis Exhibit from versioned parts."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PARTS = SRC / "parts"
VENDOR = SRC / "vendor"
ROOT_INDEX = ROOT / "index.html"
DIST_DIR = ROOT / "dist"
DIST_INDEX = DIST_DIR / "index.html"
BUILD_COUNTER = ROOT / ".build-counter.json"
ROOT_SSLI_DIR = ROOT / "ssli"
DIST_SSLI_DIR = DIST_DIR / "ssli"
SSLI_ROOT = ROOT.parents[1] / "external" / "SuperSynthLabInstrument"
SSLI_SOURCE = SSLI_ROOT / "index.html"


@dataclass(frozen=True)
class TextPatch:
    name: str
    before: str
    after: str


SSLI_INDEX_PATCHES = [
    TextPatch(
        name="disable-stale-service-worker",
        before="<script>(function(){if('serviceWorker' in navigator){navigator.serviceWorker.register('sw.js').catch(function(e){console.warn('SW registration failed:',e);});}})();</script>",
        after="<script>console.info('[SSLI] service worker disabled for Exquis exhibit runtime');</script>",
    ),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def default_articulation(engine: str, preset: dict) -> dict:
    """Describe how simultaneous note-ons should be performed for this preset."""
    category = str(preset.get("category", ""))
    settings = preset.get("settings") or {}
    physical_model = str(settings.get("model") or settings.get("physicalSettings", {}).get("model") or "")
    if engine == "physical" and (category.lower() == "plucked" or physical_model == "pluck"):
        return {
            "family": "plucked",
            "onsetMode": "strum",
            "captureWindowMs": 18,
            "minInterOnsetMs": 11,
            "maxSpreadMs": 46,
            "order": "physical-low-to-high",
            "pressurePolicy": "onset-only"
        }
    if engine == "physical" and physical_model == "strike":
        return {
            "family": "struck",
            "onsetMode": "roll",
            "captureWindowMs": 10,
            "minInterOnsetMs": 5,
            "maxSpreadMs": 18,
            "order": "physical-low-to-high",
            "pressurePolicy": "capture-and-apply-at-onset"
        }
    return {
        "family": "sustained",
        "onsetMode": "immediate",
        "captureWindowMs": 0,
        "minInterOnsetMs": 0,
        "maxSpreadMs": 0,
        "order": "input",
        "pressurePolicy": "live"
    }


def with_articulation_defaults(engine: str, library: dict) -> dict:
    presets = []
    for preset in library.get("presets", []):
        enriched = dict(preset)
        enriched["articulation"] = dict(preset.get("articulation") or default_articulation(engine, preset))
        presets.append(enriched)
    return {**library, "presets": presets}


def next_build_info() -> dict:
    counter = 0
    if BUILD_COUNTER.exists():
        try:
            counter = int((json.loads(BUILD_COUNTER.read_text(encoding="utf-8")) or {}).get("build", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            counter = 0
    build_number = counter + 1
    utc_dt = datetime.now(timezone.utc)
    local_dt = utc_dt.astimezone(ZoneInfo("America/New_York"))
    info = {
        "build": build_number,
        "version": f"Build {build_number}",
        "timestamp": local_dt.strftime("%Y-%m-%d %I:%M:%S %p ET"),
        "timestampUtc": utc_dt.isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    BUILD_COUNTER.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    return info


def build_bundle(metadata: dict) -> str:
    template = read_text(PARTS / "template.html")
    preset_dir = VENDOR / "ssli" / "presets"
    preset_libraries = {
        path.stem.replace("-presets", ""): with_articulation_defaults(path.stem.replace("-presets", ""), read_json(path))
        for path in sorted(preset_dir.glob("*-presets.json"))
    }
    ssli_vendor = {
        "source": "SuperSynthLabInstrument",
        "sourceFiles": [
            "shared/assets/constants.js",
            "shared/assets/data/scales-modes.json",
            "shared/assets/presets/*.json",
            "shared/assets/data/fx-presets.json"
        ],
        "scalesModes": read_json(VENDOR / "ssli" / "scales-modes.json"),
        "presetLibraries": preset_libraries,
        "fxPresets": read_json(VENDOR / "ssli" / "fx-presets.json")
    }
    bundle = template.replace("{{TITLE}}", metadata["name"])
    bundle = bundle.replace("{{CSS}}", read_text(PARTS / "styles.css"))
    bundle = bundle.replace("{{HTML}}", read_text(PARTS / "index.html"))
    bundle = bundle.replace("{{SSLI_VENDOR_JSON}}", json.dumps(ssli_vendor, separators=(",", ":")))
    bundle = bundle.replace("{{JS}}", read_text(PARTS / "app.js"))
    bundle = bundle.replace("{{BUILD_VERSION}}", metadata["buildVersion"])
    bundle = bundle.replace("{{BUILD_TIMESTAMP}}", metadata["buildTimestamp"])
    bundle = bundle.replace("{{BUILD_TIMESTAMP_UTC}}", metadata["buildTimestampUtc"])
    return bundle


def sync_ssli_runtime(target: Path) -> None:
    target.mkdir(exist_ok=True)
    if SSLI_SOURCE.exists():
        shutil.copyfile(SSLI_SOURCE, target / "index.html")
        ssli_assets = SSLI_ROOT / "assets"
        if ssli_assets.exists():
            shutil.copytree(ssli_assets, target / "assets", dirs_exist_ok=True)
        for support_file in ("manifest.json", "sw.js", "logo.png"):
            source_file = SSLI_ROOT / support_file
            if source_file.exists():
                shutil.copyfile(source_file, target / support_file)
    elif target.resolve() != ROOT_SSLI_DIR.resolve() and ROOT_SSLI_DIR.exists() and (ROOT_SSLI_DIR / "index.html").exists():
        shutil.copytree(ROOT_SSLI_DIR, target, dirs_exist_ok=True)
    patch_ssli_runtime(target)


def patch_ssli_runtime(target: Path) -> None:
    """Apply exhibit-local SSLI runtime patches that are covered by tests."""
    index = target / "index.html"
    if not index.exists():
        return
    text = index.read_text(encoding="utf-8")
    patched = apply_required_text_patches(text, SSLI_INDEX_PATCHES, index)
    if patched != text:
        index.write_text(patched, encoding="utf-8")


def apply_required_text_patches(text: str, patches: list[TextPatch], target: Path) -> str:
    """Apply idempotent text patches and fail loudly when upstream drift breaks one."""
    patched = text
    for patch in patches:
        has_before = patch.before in patched
        has_after = patch.after in patched
        if not has_before and not has_after:
            raise RuntimeError(f"Missing SSLI runtime patch target '{patch.name}' in {target}")
        if has_before:
            patched = patched.replace(patch.before, patch.after)
    return patched


def build() -> dict:
    metadata_src = read_json(SRC / "metadata.json")
    build_info = next_build_info()
    metadata_src["buildNumber"] = build_info["build"]
    metadata_src["buildVersion"] = build_info["version"]
    metadata_src["buildTimestamp"] = build_info["timestamp"]
    metadata_src["buildTimestampUtc"] = build_info["timestampUtc"]
    bundle = build_bundle(metadata_src)
    DIST_DIR.mkdir(exist_ok=True)
    ROOT_INDEX.write_text(bundle, encoding="utf-8")
    DIST_INDEX.write_text(bundle, encoding="utf-8")
    sync_ssli_runtime(ROOT_SSLI_DIR)
    sync_ssli_runtime(DIST_SSLI_DIR)
    return {
        "name": metadata_src["name"],
        "buildNumber": metadata_src["buildNumber"],
        "buildVersion": metadata_src["buildVersion"],
        "buildTimestamp": metadata_src["buildTimestamp"],
        "buildTimestampUtc": metadata_src["buildTimestampUtc"],
        "rootIndex": str(ROOT_INDEX),
        "distIndex": str(DIST_INDEX),
        "ssliRuntime": str(ROOT_SSLI_DIR),
    }


if __name__ == "__main__":
    result = build()
    print(f"Built {result['rootIndex']}")
    print(f"Built {result['distIndex']}")
    print(f"Synced SSLI runtime: {result['ssliRuntime']}")
