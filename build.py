#!/usr/bin/env python3
"""Build Super Synth Lab Exquis Exhibit from versioned parts."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PARTS = SRC / "parts"
VENDOR = SRC / "vendor"
ROOT_INDEX = ROOT / "index.html"
DIST_DIR = ROOT / "dist"
DIST_INDEX = DIST_DIR / "index.html"
ROOT_SSLI_DIR = ROOT / "ssli"
DIST_SSLI_DIR = DIST_DIR / "ssli"
SSLI_ROOT = ROOT.parents[1] / "external" / "SuperSynthLabInstrument"
SSLI_SOURCE = SSLI_ROOT / "index.html"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle(metadata: dict) -> str:
    template = read_text(PARTS / "template.html")
    preset_dir = VENDOR / "ssli" / "presets"
    preset_libraries = {
        path.stem.replace("-presets", ""): read_json(path)
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
    return bundle


def sync_ssli_runtime(target: Path) -> None:
    if target.resolve() == ROOT_SSLI_DIR.resolve() and (ROOT_SSLI_DIR / "index.html").exists():
        return
    target.mkdir(exist_ok=True)
    if ROOT_SSLI_DIR.exists() and (ROOT_SSLI_DIR / "index.html").exists():
        shutil.copytree(ROOT_SSLI_DIR, target, dirs_exist_ok=True)
        return
    if SSLI_SOURCE.exists():
        shutil.copyfile(SSLI_SOURCE, target / "index.html")
        ssli_assets = SSLI_ROOT / "assets"
        if ssli_assets.exists():
            shutil.copytree(ssli_assets, target / "assets", dirs_exist_ok=True)
        for support_file in ("manifest.json", "sw.js", "logo.png"):
            source_file = SSLI_ROOT / support_file
            if source_file.exists():
                shutil.copyfile(source_file, target / support_file)


def build() -> dict:
    metadata_src = read_json(SRC / "metadata.json")
    bundle = build_bundle(metadata_src)
    DIST_DIR.mkdir(exist_ok=True)
    ROOT_INDEX.write_text(bundle, encoding="utf-8")
    DIST_INDEX.write_text(bundle, encoding="utf-8")
    sync_ssli_runtime(ROOT_SSLI_DIR)
    sync_ssli_runtime(DIST_SSLI_DIR)
    return {
        "name": metadata_src["name"],
        "rootIndex": str(ROOT_INDEX),
        "distIndex": str(DIST_INDEX),
        "ssliRuntime": str(ROOT_SSLI_DIR),
    }


if __name__ == "__main__":
    result = build()
    print(f"Built {result['rootIndex']}")
    print(f"Built {result['distIndex']}")
    print(f"Synced SSLI runtime: {result['ssliRuntime']}")
