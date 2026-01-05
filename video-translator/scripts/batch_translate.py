"""Batch helper to process every video in video_input and place bilingual outputs in video-output."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm"}


def collect_videos(folder: Path) -> list[Path]:
    items = []
    for candidate in folder.iterdir():
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() not in VIDEO_EXTENSIONS:
            continue
        if candidate.stem.endswith("_zh"):
            continue
        items.append(candidate)
    return sorted(items, key=lambda p: p.name)


def run_translation(video: Path, process_script: Path) -> int:
    """Invoke process_video.py with bilingual subtitles enabled."""
    cmd = [
        sys.executable,
        str(process_script),
        video.name,
        "--mode",
        "subs",
        "--model",
        "base",
        "--bilingual",
    ]
    completed = subprocess.run(cmd, cwd=video.parent)
    return completed.returncode


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    input_dir = project_root / "video_input"
    output_dir = project_root / "video-output"
    process_script = project_root / "video-translator" / "scripts" / "process_video.py"

    if not input_dir.exists():
        raise SystemExit("video_input folder not found")

    output_dir.mkdir(parents=True, exist_ok=True)

    videos = collect_videos(input_dir)
    if not videos:
        raise SystemExit("video_input contains no supported video files")

    for idx, video in enumerate(videos, start=1):
        print(f"Processing {video.name} -> videoout{idx}.mp4")
        exit_code = run_translation(video, process_script)
        if exit_code != 0:
            print(f"  ❌ Failed with exit code {exit_code}, skipping rename")
            continue

        temp_output = video.with_name(f"{video.stem}_zh.mp4")
        if not temp_output.exists():
            print("  ⚠️ Expected output not found; skipping")
            continue

        final_output = output_dir / f"videoout{idx}.mp4"
        if final_output.exists():
            final_output.unlink()
        temp_output.replace(final_output)
        print(f"  ✅ Saved {final_output.relative_to(project_root)}")


if __name__ == "__main__":
    main()
