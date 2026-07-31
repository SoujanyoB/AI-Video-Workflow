#!/usr/bin/env python3
"""
install.py

Install project dependencies declared in dependencies.json.

Python 3.10+ is a prerequisite and must be installed manually. This script
installs Python packages into the current interpreter, then downloads models
and FFmpeg / FFprobe binaries into modules/.

Usage:
    python install.py
    python install.py --skip-python
    python install.py --skip-binaries
    python install.py --skip-models
    python install.py --force
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEPENDENCIES_FILE = PROJECT_ROOT / "dependencies.json"


def load_manifest() -> dict:
    if not DEPENDENCIES_FILE.exists():
        raise FileNotFoundError(f"Dependency manifest not found: {DEPENDENCIES_FILE}")
    with open(DEPENDENCIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def _pip_specs(packages: dict) -> list[str]:
    specs = []
    for name, version in packages.items():
        if version:
            specs.append(f"{name}=={version}")
        else:
            specs.append(name)
    return specs


def install_python_deps(manifest: dict, force: bool = False) -> None:
    python = manifest.get("python", {})
    packages = python.get("packages", {})
    extra = python.get("extra", {})

    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("WARNING: you are not inside a virtual environment.")
        print("It is recommended to activate one before installing packages.\n")

    if not packages:
        raise RuntimeError(
            "No packages configured in dependencies.json -> python.packages"
        )

    def _pip(specs: list[str], extra_args: list[str] | None = None) -> None:
        cmd = [sys.executable, "-m", "pip", "install"]
        if extra_args:
            cmd.extend(extra_args)
        cmd.extend(specs)
        run_command(cmd)

    print("Installing Python packages from dependencies.json.")
    _pip(_pip_specs(packages))

    if extra:
        print("\nInstalling extra Python packages:")

    for group_name, group in extra.items():
        group_packages = group.get("packages", {})
        if not group_packages:
            continue

        platform_args = group.get("pip_args", {}).get(sys.platform, [])
        note = group.get("note", "")

        print(f"  {group_name}: {note}")
        _pip(_pip_specs(group_packages), platform_args)


def install_models(manifest: dict, force: bool = False) -> None:
    config = manifest.get("models", {})
    install_dir = PROJECT_ROOT / config.get("install_dir", "modules/models")
    files = config.get("files", {})

    if not files:
        print("No models configured. Skipping.")
        return

    install_dir.mkdir(parents=True, exist_ok=True)

    for filename, meta in files.items():
        if not meta.get("enabled", True):
            print(f"Skipping {filename} (disabled).")
            continue

        url = meta["url"]
        destination = install_dir / filename

        if not force and destination.exists():
            print(f"Model already present: {destination}")
            continue

        download_file(url, destination, filename)
        print(f"Saved model to {destination}")


def get_ffbinaries_url(version: str, platform_code: str, component: str) -> str:
    url = f"https://ffbinaries.com/api/v1/version/{version}"
    print(f"Fetching FFmpeg metadata: {url}")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Video-Workflow installer"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    try:
        return data["bin"][platform_code][component]
    except KeyError as exc:
        raise RuntimeError(
            f"FFbinaries did not return a URL for {component} on {platform_code}. "
            f"Response: {data}"
        ) from exc


def download_file(url: str, destination: Path, label: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {label} from {url}")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AI-Video-Workflow installer"},
    )

    with urllib.request.urlopen(request, timeout=300) as response:
        total = response.headers.get("Content-Length")
        if total:
            total = int(total)

        downloaded = 0
        chunk_size = 1024 * 1024
        with open(destination, "wb") as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(f"\r{label}: {pct}% ({downloaded}/{total} bytes)", end="")
        print()

    print(f"Saved to {destination}")


def extract_component(archive: Path, bin_dir: Path, component: str) -> Path:
    """Extract a single FFmpeg component archive and place the binary in bin_dir."""

    extract_dir = archive.parent / f".extract_{component}"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)

    try:
        if zipfile.is_zipfile(archive):
            with zipfile.ZipFile(archive, "r") as zf:
                zf.extractall(extract_dir)
        elif tarfile.is_tarfile(archive):
            with tarfile.open(archive, "r:*") as tf:
                tf.extractall(extract_dir)
        else:
            raise RuntimeError(
                f"Unsupported archive format for {component}: {archive}"
            )

        target_name = f"{component}.exe" if sys.platform == "win32" else component
        found: Path | None = None
        for path in extract_dir.rglob("*"):
            if path.is_file() and path.name == target_name:
                found = path
                break

        if not found:
            raise FileNotFoundError(
                f"Could not find {target_name} inside {archive}. "
                "The archive layout may have changed."
            )

        dest = bin_dir / target_name
        shutil.copy2(found, dest)
        if sys.platform != "win32":
            mode = os.stat(dest).st_mode
            os.chmod(dest, mode | 0o111)

        return dest
    finally:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)


def install_ffmpeg(manifest: dict, force: bool = False) -> None:
    config = manifest.get("binaries", {}).get("ffmpeg")
    if not config:
        print("No FFmpeg binary configuration found. Skipping binary install.")
        return

    version = config["version"]
    platform_map = config["platform_map"]
    install_dir = PROJECT_ROOT / config["install_dir"]
    bin_dir = PROJECT_ROOT / config["bin_dir"]
    components = config["components"]

    platform = sys.platform
    if platform not in platform_map:
        supported = ", ".join(platform_map.keys())
        raise RuntimeError(
            f"Unsupported platform: {platform}. Supported: {supported}"
        )
    platform_code = platform_map[platform]

    version_file = bin_dir / ".version"
    if not force and version_file.exists() and version_file.read_text().strip() == version:
        print(f"FFmpeg {version} already installed in {bin_dir}")
        return

    if force and bin_dir.exists():
        print(f"Removing existing binaries in {bin_dir}")
        shutil.rmtree(bin_dir)

    bin_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir = install_dir / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    archive_extension = ".zip" if sys.platform == "win32" else ".tar.gz"

    for component in components:
        url = get_ffbinaries_url(version, platform_code, component)
        archive = downloads_dir / f"{component}-{version}-{platform_code}{archive_extension}"
        download_file(url, archive, component)
        print(f"Extracting {component} ...")
        extract_component(archive, bin_dir, component)
        archive.unlink()

    version_file.write_text(version)
    print(f"FFmpeg {version} installed to {bin_dir}\n")


def verify_binaries(bin_dir: Path) -> None:
    binary_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    ffmpeg = bin_dir / binary_name
    if not ffmpeg.exists():
        ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        print("Verifying FFmpeg installation:")
        subprocess.run([str(ffmpeg), "-version"], check=False)
    else:
        print("WARNING: could not find ffmpeg to verify.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install dependencies for AI-Video-Workflow"
    )
    parser.add_argument(
        "--skip-python",
        action="store_true",
        help="Do not install Python packages",
    )
    parser.add_argument(
        "--skip-binaries",
        action="store_true",
        help="Do not download FFmpeg binaries",
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Do not download model files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download dependencies even if they are already present",
    )
    args = parser.parse_args()

    manifest = load_manifest()

    if not args.skip_python:
        install_python_deps(manifest, force=args.force)

    if not args.skip_models:
        install_models(manifest, force=args.force)

    if not args.skip_binaries:
        install_ffmpeg(manifest, force=args.force)
        bin_dir = PROJECT_ROOT / manifest["binaries"]["ffmpeg"]["bin_dir"]
        verify_binaries(bin_dir)

    print("\nInstall complete.")


if __name__ == "__main__":
    main()
