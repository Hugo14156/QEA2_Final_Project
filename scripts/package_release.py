"""Build and package a release archive for the current platform.

This script wraps scripts/build_executable.py and then archives the result into
an easy-to-share release file, with checksum and JSON manifest.

To produce releases for all platforms, run this script on each target OS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED_TARGETS = {"windows", "macos", "linux"}


def current_target() -> str:
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    if system == "darwin":
        return "macos"
    if system == "linux":
        return "linux"
    return system


def normalize_arch(machine: str) -> str:
    value = machine.lower()
    mapping = {
        "amd64": "x64",
        "x86_64": "x64",
        "x64": "x64",
        "arm64": "arm64",
        "aarch64": "arm64",
        "armv7l": "armv7",
        "armv8": "arm64",
    }
    return mapping.get(value, value or "unknown")


def quote(parts: list[str]) -> str:
    return " ".join(f'"{part}"' if " " in part else part for part in parts)


def run_command(command: list[str], cwd: Path) -> None:
    print(f"\nRunning:\n  {quote(command)}\n")
    subprocess.run(command, cwd=str(cwd), check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and package a release archive")
    parser.add_argument("--name", default="QEA2_Fourier_Sketcher", help="App name")
    parser.add_argument(
        "--version",
        default="dev",
        help="Release version label used in archive names (for example: v1.0.0)",
    )
    parser.add_argument(
        "--target",
        choices=sorted(SUPPORTED_TARGETS),
        default=current_target(),
        help="Target platform (must match host OS)",
    )
    parser.add_argument("--entry", default="main.py", help="Entry point for builder")
    parser.add_argument("--onefile", action="store_true", help="Use onefile build mode")
    parser.add_argument("--onedir", action="store_true", help="Use onedir build mode")
    parser.add_argument(
        "--console", action="store_true", help="Show console in built executable"
    )
    parser.add_argument("--icon", default=None, help="Optional icon passed to builder")
    parser.add_argument("--clean", action="store_true", help="Clean build cache first")
    parser.add_argument(
        "--install-pyinstaller",
        action="store_true",
        help="Install/upgrade PyInstaller before build",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip build step and package current dist output",
    )
    parser.add_argument(
        "--format",
        choices=["auto", "zip", "tar.gz"],
        default="auto",
        help="Archive format; auto=zip on Windows, tar.gz elsewhere",
    )
    parser.add_argument(
        "--output-dir",
        default="releases",
        help="Output folder for release archives and metadata",
    )
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Do not include README.md and LICENSE in the package",
    )
    return parser.parse_args()


def choose_build_mode(args: argparse.Namespace) -> str:
    if args.onefile and args.onedir:
        raise ValueError("Choose only one of --onefile or --onedir")
    return "onefile" if args.onefile or not args.onedir else "onedir"


def choose_archive_format(target: str, user_format: str) -> str:
    if user_format != "auto":
        return user_format
    return "zip" if target == "windows" else "tar.gz"


def artifact_path(project_root: Path, target: str, name: str, mode: str) -> Path:
    dist_dir = project_root / "dist" / target
    if mode == "onefile":
        suffix = ".exe" if target == "windows" else ""
        return dist_dir / f"{name}{suffix}"
    return dist_dir / name


def build_project(project_root: Path, args: argparse.Namespace, mode: str) -> None:
    command = [
        sys.executable,
        str(project_root / "scripts" / "build_executable.py"),
        "--name",
        args.name,
        "--target",
        args.target,
        "--entry",
        args.entry,
    ]

    if mode == "onefile":
        command.append("--onefile")
    else:
        command.append("--onedir")

    if args.console:
        command.append("--console")
    if args.icon:
        command.extend(["--icon", args.icon])
    if args.clean:
        command.append("--clean")
    if args.install_pyinstaller:
        command.append("--install-pyinstaller")

    run_command(command, cwd=project_root)


def copy_into_stage(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def add_docs(project_root: Path, payload_dir: Path) -> list[str]:
    included = []
    for doc_name in ("README.md", "LICENSE"):
        doc_path = project_root / doc_name
        if doc_path.exists():
            shutil.copy2(doc_path, payload_dir / doc_name)
            included.append(doc_name)
    return included


def create_zip(archive_path: Path, source_dir: Path) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(source_dir))


def create_tar_gz(archive_path: Path, source_dir: Path) -> None:
    with tarfile.open(archive_path, "w:gz") as tf:
        tf.add(source_dir, arcname=".")


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    mode = choose_build_mode(args)

    project_root = Path(__file__).resolve().parents[1]
    host_target = current_target()
    if args.target != host_target:
        print(
            f"Error: target '{args.target}' does not match current OS '{host_target}'."
        )
        return 2

    if not args.skip_build:
        try:
            build_project(project_root, args, mode)
        except subprocess.CalledProcessError as exc:
            print(f"Build failed with exit code {exc.returncode}")
            return exc.returncode

    artifact = artifact_path(project_root, args.target, args.name, mode)
    if not artifact.exists():
        print(f"Error: build artifact not found: {artifact}")
        return 2

    archive_format = choose_archive_format(args.target, args.format)
    arch = normalize_arch(platform.machine())
    safe_version = args.version.strip() or "dev"
    base_name = f"{args.name}-{safe_version}-{args.target}-{arch}"

    output_dir = (project_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_root = project_root / "build" / "release_stage" / base_name
    if stage_root.exists():
        shutil.rmtree(stage_root)
    payload_dir = stage_root / base_name
    payload_dir.mkdir(parents=True, exist_ok=True)

    if mode == "onefile":
        copy_into_stage(artifact, payload_dir / artifact.name)
    else:
        copy_into_stage(artifact, payload_dir / artifact.name)

    included_docs = []
    if not args.no_docs:
        included_docs = add_docs(project_root, payload_dir)

    if archive_format == "zip":
        archive_path = output_dir / f"{base_name}.zip"
        create_zip(archive_path, stage_root)
    else:
        archive_path = output_dir / f"{base_name}.tar.gz"
        create_tar_gz(archive_path, stage_root)

    digest = sha256_of_file(archive_path)
    checksum_path = output_dir / f"{archive_path.name}.sha256"
    checksum_path.write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")

    manifest = {
        "name": args.name,
        "version": safe_version,
        "target": args.target,
        "architecture": arch,
        "build_mode": mode,
        "archive_format": archive_format,
        "archive_file": archive_path.name,
        "archive_sha256": digest,
        "artifact_source": str(artifact.relative_to(project_root)),
        "included_docs": included_docs,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = output_dir / f"{base_name}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Release package created successfully.")
    print(f"Archive: {archive_path}")
    print(f"Checksum: {checksum_path}")
    print(f"Manifest: {manifest_path}")
    print(
        "Run this script on each OS (Windows, macOS, Linux) to produce all platform releases."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
