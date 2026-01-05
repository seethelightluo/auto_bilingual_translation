import argparse
import os
import subprocess
import whisper
import edge_tts
import asyncio
import datetime
from transformers import pipeline
from tqdm import tqdm

def format_timestamp(seconds):
    """Converts seconds to SRT timestamp format."""
    td = datetime.timedelta(seconds=seconds)
    # Handle milliseconds properly
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt(segments, output_path):
    """Generates SRT file from Whisper segments."""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()
            f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")
    print(f"✅ Subtitles saved to: {output_path}")

_translation_pipeline = None


def translate_to_chinese(texts, batch_size=8):
    """Translates English text lines to Chinese using a Marian MT model."""
    global _translation_pipeline
    if _translation_pipeline is None:
        print("🌐 Loading translation model (en→zh)...")
        _translation_pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-en-zh")

    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        sanitized = [text if text.strip() else "." for text in batch]
        translations = _translation_pipeline(sanitized)
        results.extend(item["translation_text"].strip() for item in translations)
    return results

async def generate_audio(segments, output_audio_path):
    """Generates Chinese speech using Edge-TTS."""
    print("🔊 Generating dubbed audio (this may take time)...")
    
    # Chinese voice (Male: zh-CN-YunxiNeural, Female: zh-CN-XiaoxiaoNeural)
    VOICE = "zh-CN-YunxiNeural" 
    
    # We will create individual audio clips and merge them based on timestamps
    # For simplicity in this script, we concatenate TTS. 
    # Note: Perfect lip-sync is extremely hard. This creates a voiceover track.
    
    temp_files = []
    
    for i, segment in enumerate(tqdm(segments, desc="Synthesizing Audio")):
        text = segment['text']
        if not text.strip():
            continue
            
        temp_file = f"temp_{i}.mp3"
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(temp_file)
        
        # Calculate duration adjustments if needed (advanced logic omitted for stability)
        temp_files.append(temp_file)

    # Merge audio files (Simple concatenation for this demo version)
    # A production version would place audio at specific timestamps using ffmpeg filters
    
    # Create file list for ffmpeg
    with open("ffmpeg_list.txt", "w") as f:
        for tf in temp_files:
            f.write(f"file '{tf}'\n")
            
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", "ffmpeg_list.txt", 
        "-c", "copy", output_audio_path, "-y"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup
    for tf in temp_files:
        os.remove(tf)
    os.remove("ffmpeg_list.txt")
    print(f"✅ Dubbed audio saved to: {output_audio_path}")

def process_video(video_path, mode, model_size, bilingual=False):
    base_name = os.path.splitext(video_path)[0]
    output_video = f"{base_name}_zh.mp4"
    srt_path = f"{base_name}.srt"
    dub_audio_path = f"{base_name}_dub.mp3"

    # 1. Transcribe & Translate
    print(f"🎧 Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)
    
    print("🕵️ Transcribing English audio...")
    english_result = model.transcribe(video_path, task="transcribe", language="en")
    en_segments = english_result['segments']

    print("🌐 Translating subtitles to Chinese...")
    zh_texts = translate_to_chinese([seg['text'] for seg in en_segments])
    zh_segments = []
    for seg, zh_text in zip(en_segments, zh_texts):
        zh_segments.append({
            "start": seg['start'],
            "end": seg['end'],
            "text": zh_text
        })

    segments_for_srt = zh_segments

    if bilingual:
        print("📝 Combining English and Chinese lines for bilingual subtitles...")
        merged_segments = []
        for eng_seg, zh_seg in zip(en_segments, zh_segments):
            merged_segments.append({
                "start": eng_seg['start'],
                "end": eng_seg['end'],
                "text": f"{eng_seg['text'].strip()}\n{zh_seg['text'].strip()}"
            })
        segments_for_srt = merged_segments

    # 2. Generate Subtitles
    generate_srt(segments_for_srt, srt_path)

    if mode == "subs":
        # Burn subtitles only
        print("🎬 Merging subtitles into video...")
        # FFmpeg command to hardcode subtitles
        # Note: path formatting for subtitles in ffmpeg can be tricky on Windows
        srt_filename = os.path.basename(srt_path)
        cmd = [
            "ffmpeg", "-i", video_path, 
            "-vf", f"subtitles={srt_filename}", 
            "-c:a", "copy", output_video, "-y"
        ]
        subprocess.run(cmd)

    elif mode == "dub":
        # 3. Generate Audio
        asyncio.run(generate_audio(zh_segments, dub_audio_path))
        
        # 4. Merge Video + New Audio + Subtitles
        print("🎬 Merging video, dubbed audio, and subtitles...")
        # Reduce original audio volume, mix with new audio, add subtitles
        cmd = [
            "ffmpeg", "-i", video_path, "-i", dub_audio_path,
            "-filter_complex", 
            f"[0:a]volume=0.1[original];[original][1:a]amix=inputs=2:duration=longest[audio];[0:v]subtitles={os.path.basename(srt_path)}[video]",
            "-map", "[video]", "-map", "[audio]",
            "-c:v", "libx264", "-c:a", "aac", 
            output_video, "-y"
        ]
        subprocess.run(cmd)

    print(f"🎉 Done! Output file: {output_video}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate English Video to Chinese")
    parser.add_argument("video_path", help="Path to the input video file")
    parser.add_argument("--mode", choices=["subs", "dub"], default="subs", help="subs: subtitles only; dub: subtitles + voiceover")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("--bilingual", action="store_true", help="Include English lines above the Chinese translation in subtitles")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video_path):
        print("Error: File not found.")
    else:
        process_video(args.video_path, args.mode, args.model, args.bilingual)