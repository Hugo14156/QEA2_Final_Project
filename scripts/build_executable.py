"""Build a distributable executable for this project using PyInstaller.

Usage examples:
  python scripts/build_executable.py
  python scripts/build_executable.py --name FourierSketcher --onedir
  python scripts/build_executable.py --target windows

Note:
  Native executable builds are platform-specific. To support all platforms,
  run this script once on each target OS (Windows, macOS, Linux) or use CI.
"""

from __future__ import annotations

import argparse
import platform
import shlex
import subprocess
import sys
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


def data_separator(target: str) -> str:
    return ";" if target == "windows" else ":"


def data_arg(source: Path, destination: str, sep: str) -> str:
    return f"{source.resolve()}{sep}{destination}"


def quote_cmd(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def run_command(command: list[str], cwd: Path) -> None:
    print(f"\nRunning:\n  {quote_cmd(command)}\n")
    subprocess.run(command, cwd=str(cwd), check=True)


def ensure_pyinstaller(project_root: Path) -> None:
    check_cmd = [sys.executable, "-m", "PyInstaller", "--version"]
    try:
        subprocess.run(
            check_cmd,
            cwd=str(project_root),
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "PyInstaller is not available in this Python environment. "
            "Install it with: pip install pyinstaller"
        ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build executable with PyInstaller")
    parser.add_argument(
        "--name",
        default="QEA2_Fourier_Sketcher",
        help="Output executable name",
    )
    parser.add_argument(
        "--target",
        choices=sorted(SUPPORTED_TARGETS),
        default=current_target(),
        help=(
            "Target platform. This must match the OS where the script runs "
            "because PyInstaller does not produce native cross-platform binaries."
        ),
    )
    parser.add_argument(
        "--entry",
        default="main.py",
        help="Entry-point Python file relative to the repository root",
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build a single-file executable",
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Build a one-directory app bundle",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Show terminal/console window when running",
    )
    parser.add_argument(
        "--icon",
        default=None,
        help="Optional icon file path (.ico on Windows, .icns on macOS)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean PyInstaller cache and temporary files before building",
    )
    parser.add_argument(
        "--install-pyinstaller",
        action="store_true",
        help="Install/upgrade PyInstaller automatically before build",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.onefile and args.onedir:
        print("Error: choose only one of --onefile or --onedir")
        return 2

    build_mode = "--onefile" if args.onefile or not args.onedir else "--onedir"

    project_root = Path(__file__).resolve().parents[1]
    entry_path = (project_root / args.entry).resolve()

    if not entry_path.exists():
        print(f"Error: entry file not found: {entry_path}")
        return 2

    host = current_target()
    if args.target != host:
        print(
            f"Error: requested target '{args.target}' but current OS is '{host}'.\n"
            "PyInstaller cannot cross-compile native executables between these OS targets."
        )
        return 2

    if args.install_pyinstaller:
        run_command(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"],
            cwd=project_root,
        )
    else:
        ensure_pyinstaller(project_root)

    platform_dist = project_root / "dist" / host
    platform_build = project_root / "build" / host
    platform_dist.mkdir(parents=True, exist_ok=True)
    platform_build.mkdir(parents=True, exist_ok=True)

    sep = data_separator(host)
    app_dir = project_root / "app"
    file_types_dir = project_root / "file_types"
    saved_series_dir = project_root / "saved_series"

    for required_dir in (app_dir, file_types_dir, saved_series_dir):
        if not required_dir.exists():
            print(f"Error: required folder not found: {required_dir}")
            return 2

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(entry_path),
        "--name",
        args.name,
        build_mode,
        "--noconfirm",
        "--distpath",
        str(platform_dist),
        "--workpath",
        str(platform_build),
        "--specpath",
        str(platform_build),
        "--add-data",
        data_arg(app_dir, "app", sep),
        "--add-data",
        data_arg(file_types_dir, "file_types", sep),
        "--add-data",
        data_arg(saved_series_dir, "saved_series", sep),
    ]

    if not args.console:
        command.append("--windowed")

    if args.clean:
        command.append("--clean")

    if args.icon:
        icon_path = (project_root / args.icon).resolve()
        if not icon_path.exists():
            print(f"Error: icon file not found: {icon_path}")
            return 2
        command.extend(["--icon", str(icon_path)])

    try:
        run_command(command, cwd=project_root)
    except subprocess.CalledProcessError as exc:
        print(f"Build failed with exit code {exc.returncode}")
        return exc.returncode

    print("Build completed successfully.")
    print(f"Target platform: {host}")
    print(f"Output folder: {platform_dist}")
    print(
        "To build for all platforms, run this script separately on "
        "Windows, macOS, and Linux."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
