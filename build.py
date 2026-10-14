"""Copies the shared Python core and the brand icon into the plugin, so the
directory packages on its own with `dify plugin package`."""

import shutil
from pathlib import Path

root = Path(__file__).resolve().parent
packages = (root / "shared")

target = root / "modelflare_core"
shutil.rmtree(target, ignore_errors=True)
shutil.copytree(packages / "core-py" / "modelflare_core", target, ignore=shutil.ignore_patterns("__pycache__"))

assets = root / "_assets"
assets.mkdir(exist_ok=True)
shutil.copyfile(packages / "brand" / "logo.svg", assets / "icon.svg")
print(f"Prepared {root.name}: modelflare_core/, _assets/icon.svg")
