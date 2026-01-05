"""
Refactored video processing with explicit output directory support.
This module is imported by the MCP server tools.
"""
from __future__ import annotations

import asyncio
import datetime
import os
import sys
import subprocess
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import edge_tts
import whisper
from tqdm import tqdm
from transformers import pipeline

# Global translation pipeline (loaded once)
_translation_pipeline = None


def format_timestamp(seconds: float) -> str:
    """Converts seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def generate_srt(segments: list[dict], output_path: Path) -> None:
    """Generates SRT file from Whisper segments."""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")
    print(f"[OK] Subtitles saved to: {output_path}")


def translate_to_chinese(texts: list[str], batch_size: int = 8) -> list[str]:
    """Translates English text lines to Chinese using Helsinki-NLP/opus-mt-en-zh."""
    global _translation_pipeline
    if _translation_pipeline is None:
        print("[LOAD] Loading translation model (en->zh)...")
        _translation_pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-en-zh")

    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        sanitized = [text if text.strip() else "." for text in batch]
        translations = _translation_pipeline(sanitized)
        results.extend(item["translation_text"].strip() for item in translations)
    return results


async def generate_audio(segments: list[dict], output_audio_path: Path, temp_dir: Path) -> None:
    """Generates Chinese speech using Edge-TTS."""
    print("[AUDIO] Generating dubbed audio (this may take time)...")

    VOICE = "zh-CN-YunxiNeural"
    temp_files = []

    for i, segment in enumerate(tqdm(segments, desc="Synthesizing Audio")):
        text = segment["text"]
        if not text.strip():
            continue

        temp_file = temp_dir / f"temp_{i}.mp3"
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(str(temp_file))
        temp_files.append(temp_file)

    # Merge audio files using ffmpeg concat
    list_file = temp_dir / "ffmpeg_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for tf in temp_files:
            # Use forward slashes and escape for ffmpeg
            safe_path = str(tf).replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    subprocess.run(
        [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c", "copy", str(output_audio_path), "-y"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    # Cleanup temp files
    for tf in temp_files:
        tf.unlink()
    list_file.unlink()
    print(f"[OK] Dubbed audio saved to: {output_audio_path}")


def _escape_ffmpeg_path(path: Path) -> str:
    """
    Escape a path for use in ffmpeg subtitles filter on Windows.
    FFmpeg subtitles filter needs special escaping for Windows paths.
    """
    path_str = str(path.resolve()).replace("\\", "/")
    path_str = path_str.replace(":", "\\:")
    path_str = path_str.replace("'", "\\'")
    return path_str


def process_video_to_dirs(
    video_path: Path,
    video_output_dir: Path,
    srt_output_dir: Path,
    mode: str = "subs",
    model_size: str = "base",
    bilingual: bool = True,
) -> dict:
    """
    Process a video file with explicit output directories.
    
    Args:
        video_path: Path to input video file
        video_output_dir: Directory to save output video
        srt_output_dir: Directory to save SRT subtitle file
        mode: "subs" for subtitles only, "dub" for subtitles + voiceover
        model_size: Whisper model size
        bilingual: If True, include both English and Chinese in subtitles
    
    Returns:
        dict with video_output, srt_output, and optionally dub_audio paths
    """
    video_path = Path(video_path).resolve()
    video_output_dir = Path(video_output_dir).resolve()
    srt_output_dir = Path(srt_output_dir).resolve()
    
    # Ensure output directories exist
    video_output_dir.mkdir(parents=True, exist_ok=True)
    srt_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define output paths
    base_name = video_path.stem
    output_video = video_output_dir / f"{base_name}_bilingual.mp4"
    srt_path = srt_output_dir / f"{base_name}_bilingual.srt"
    dub_audio_path = video_output_dir / f"{base_name}_dub.mp3"
    
    # 1. Transcribe with Whisper
    print(f"[LOAD] Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)
    
    print("[TRANSCRIBE] Transcribing English audio...")
    english_result = model.transcribe(str(video_path), task="transcribe", language="en")
    en_segments = english_result["segments"]

    # 2. Translate to Chinese
    print("[TRANSLATE] Translating subtitles to Chinese...")
    zh_texts = translate_to_chinese([seg["text"] for seg in en_segments])
    zh_segments = []
    for seg, zh_text in zip(en_segments, zh_texts):
        zh_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": zh_text,
        })

    # 3. Prepare final subtitle segments
    if bilingual:
        print("[COMBINE] Combining English and Chinese lines for bilingual subtitles...")
        segments_for_srt = []
        for eng_seg, zh_seg in zip(en_segments, zh_segments):
            segments_for_srt.append({
                "start": eng_seg["start"],
                "end": eng_seg["end"],
                "text": f"{eng_seg['text'].strip()}\n{zh_seg['text'].strip()}",
            })
    else:
        segments_for_srt = zh_segments

    # 4. Generate SRT file
    generate_srt(segments_for_srt, srt_path)
    
    # 5. Build output video with burned-in subtitles
    escaped_srt = _escape_ffmpeg_path(srt_path)
    subtitle_filter = f"subtitles='{escaped_srt}'"
    
    result = {
        "video_output": output_video,
        "srt_output": srt_path,
    }

    if mode == "subs":
        print("[MERGE] Merging subtitles into video...")
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vf", subtitle_filter,
            "-c:a", "copy",
            str(output_video), "-y"
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    elif mode == "dub":
        # Generate dubbed audio
        temp_dir = video_output_dir / ".temp"
        temp_dir.mkdir(exist_ok=True)
        asyncio.run(generate_audio(zh_segments, dub_audio_path, temp_dir))
        
        # Clean up temp dir
        try:
            temp_dir.rmdir()
        except OSError:
            pass
        
        print("[MERGE] Merging video, dubbed audio, and subtitles...")
        cmd = [
            "ffmpeg", "-i", str(video_path), "-i", str(dub_audio_path),
            "-filter_complex",
            f"[0:a]volume=0.1[original];[original][1:a]amix=inputs=2:duration=longest[audio];[0:v]{subtitle_filter}[video]",
            "-map", "[video]", "-map", "[audio]",
            "-c:v", "libx264", "-c:a", "aac",
            str(output_video), "-y"
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        result["dub_audio"] = dub_audio_path

    print(f"[DONE] Done! Output file: {output_video}")
    return result
