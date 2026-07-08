#!/usr/bin/env python3
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageFont


REQUIRED_FILES = [
    "SKILL.md",
    "requirements.txt",
    "assets/default-spec.json",
    "assets/previews/claude-loops.gif",
    "assets/previews/memory-pack.gif",
    "assets/fonts/PatrickHand-Regular.ttf",
    "assets/fonts/LXGWWenKai-Regular.ttf",
    "assets/fonts/LXGWWenKai-Medium.ttf",
    "assets/fonts/OFL-PatrickHand.txt",
    "assets/fonts/OFL-LXGWWenKai.txt",
    "scripts/render_animated_diagram.py",
    "references/spec-format.md",
]

def load_renderer(root):
    module_path = root / "scripts" / "render_animated_diagram.py"
    spec = importlib.util.spec_from_file_location("render_animated_diagram", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_required_files(root):
    missing = [path for path in REQUIRED_FILES if not (root / path).is_file()]
    empty = [path for path in REQUIRED_FILES if (root / path).is_file() and (root / path).stat().st_size == 0]
    return {
        "name": "required_files_exist",
        "ok": not missing and not empty,
        "missing": missing,
        "empty": empty,
    }


def check_font_assets(root):
    font_paths = [
        root / "assets" / "fonts" / "PatrickHand-Regular.ttf",
        root / "assets" / "fonts" / "LXGWWenKai-Regular.ttf",
        root / "assets" / "fonts" / "LXGWWenKai-Medium.ttf",
    ]
    failed = []
    for path in font_paths:
        try:
            ImageFont.truetype(str(path), 32)
        except OSError as exc:
            failed.append({"path": str(path.relative_to(root)), "error": str(exc)})
    return {"name": "font_assets_load", "ok": not failed, "failed": failed}


def check_preview_gifs(root):
    previews = [
        root / "assets" / "previews" / "claude-loops.gif",
        root / "assets" / "previews" / "memory-pack.gif",
    ]
    failed = []
    details = []
    for path in previews:
        try:
            with Image.open(path) as image:
                details.append(
                    {
                        "path": str(path.relative_to(root)),
                        "width": image.width,
                        "height": image.height,
                        "frames": getattr(image, "n_frames", 1),
                    }
                )
        except OSError as exc:
            failed.append({"path": str(path.relative_to(root)), "error": str(exc)})
    return {"name": "preview_gifs_load", "ok": not failed, "details": details, "failed": failed}


def check_default_spec(root):
    spec_path = root / "assets" / "default-spec.json"
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"name": "default_spec_loads", "ok": False, "error": str(exc)}
    required_keys = ["canvas", "title", "inputs", "core", "decision", "output"]
    missing = [key for key in required_keys if key not in spec]
    return {"name": "default_spec_loads", "ok": not missing, "missing": missing}


def check_python_dependencies(root):
    requirements = (root / "requirements.txt").read_text(encoding="utf-8").splitlines()
    has_pillow_requirement = any(line.strip().lower().startswith("pillow") for line in requirements)
    python_version_ok = sys.version_info >= (3, 9)
    try:
        import PIL

        pillow_version = PIL.__version__
    except Exception as exc:
        return {
            "name": "python_dependencies_available",
            "ok": False,
            "python_version": sys.version.split()[0],
            "python_version_ok": python_version_ok,
            "has_pillow_requirement": has_pillow_requirement,
            "error": str(exc),
        }
    return {
        "name": "python_dependencies_available",
        "ok": python_version_ok and has_pillow_requirement,
        "python_version": sys.version.split()[0],
        "python_version_ok": python_version_ok,
        "has_pillow_requirement": has_pillow_requirement,
        "pillow_version": pillow_version,
    }


def resolve_tool(name):
    executable = shutil.which(name)
    if executable:
        return executable
    candidates = []
    user_path = os.environ.get("Path", "")
    for entry in user_path.split(os.pathsep):
        if entry:
            candidates.append(Path(entry) / f"{name}.exe")
            candidates.append(Path(entry) / name)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        winget_packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        candidates.extend(winget_packages.glob(f"**/{name}.exe"))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def check_ffprobe_available(root):
    executable = resolve_tool("ffprobe")
    if not executable:
        return {"name": "ffprobe_available", "ok": False, "path": None}
    completed = subprocess.run([executable, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    first_line = completed.stdout.splitlines()[0] if completed.stdout else ""
    return {
        "name": "ffprobe_available",
        "ok": completed.returncode == 0,
        "path": executable,
        "version": first_line,
    }


def check_no_machine_local_paths(root):
    local_roots = {str(Path.home())}
    try:
        local_roots.add(str(Path.cwd()))
    except OSError:
        pass
    machine_local_patterns = [re.compile(re.escape(path), re.IGNORECASE) for path in local_roots if path]
    offenders = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".gif", ".png", ".jpg", ".jpeg", ".ttf", ".ttc", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in machine_local_patterns:
            if pattern.search(text):
                offenders.append(str(path.relative_to(root)))
                break
    return {"name": "no_machine_local_paths", "ok": not offenders, "offenders": offenders}


def check_font_candidates_start_with_bundled_assets(root):
    renderer = load_renderer(root)
    required_prefix = str((root / "assets" / "fonts").resolve())
    samples = [
        renderer.font_candidates(hand=True, bold=True),
        renderer.font_candidates(cjk=True, bold=False),
        renderer.font_candidates(cjk=True, bold=True),
        renderer.font_candidates(bold=False),
    ]
    failures = []
    for index, candidates in enumerate(samples):
        first = str(Path(candidates[0]).resolve()) if candidates else ""
        if not first.startswith(required_prefix):
            failures.append({"sample": index, "first": first})
    return {
        "name": "font_candidates_start_with_bundled_assets",
        "ok": not failures,
        "failures": failures,
    }


def run_checks(root):
    root = Path(root).resolve()
    checks = [
        check_required_files(root),
        check_font_assets(root),
        check_preview_gifs(root),
        check_default_spec(root),
        check_python_dependencies(root),
        check_ffprobe_available(root),
        check_no_machine_local_paths(root),
        check_font_candidates_start_with_bundled_assets(root),
    ]
    return {"ok": all(check["ok"] for check in checks), "checks": checks}


def main():
    parser = argparse.ArgumentParser(description="Check skill assets and dependencies for portable rendering.")
    parser.add_argument("skill_root", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = run_checks(Path(args.skill_root))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
