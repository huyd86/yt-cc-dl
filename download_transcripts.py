import subprocess
import os
import re
import glob
from datetime import timedelta
from pathlib import Path

COOKIES_FILE = "cookies.txt"
URL_LIST_FILE = "video_urls.txt"
OUTPUT_DIR = "transcripts"
KEEP_VTT = False  # Set to True if you want to keep the .vtt file after conversion

def parse_vtt_timestamp(ts):
    h, m, s = ts.split(":")
    s, ms = s.split(".")
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms))

def clean_and_merge_lines(lines):
    paragraph = ' '.join(lines).strip()
    paragraph = re.sub(r'\s+', ' ', paragraph)
    return paragraph

def vtt_to_text(vtt_path, group_minutes=2):
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    paragraphs = []
    current_lines = []
    current_start = None

    for i in range(len(lines)):
        line = lines[i].strip()

        if "-->" in line:
            start_ts = line.split(" --> ")[0]
            start_time = parse_vtt_timestamp(start_ts)

            if current_start is None:
                current_start = start_time
            elif start_time - current_start >= timedelta(minutes=group_minutes):
                if current_lines:
                    paragraphs.append(clean_and_merge_lines(current_lines))
                current_lines = []
                current_start = start_time
        elif line and not line.startswith("WEBVTT") and "<" not in line:
            if re.match(r"^\[.*\]$", line):
                continue
            current_lines.append(line)

    if current_lines:
        paragraphs.append(clean_and_merge_lines(current_lines))

    return "\n\n".join(paragraphs)

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip()

def download_and_convert(url, custom_title, lang):
    print(f"Processing: {url} (lang: {lang})")
    safe_title = sanitize_filename(custom_title)
    result = subprocess.run([
        "yt-dlp",
        "--cookies", COOKIES_FILE,
        "--write-subs",
        "--sub-lang", lang,
        "--skip-download",
        "--output", f"{safe_title}.%(ext)s",
        url
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error downloading subtitles for {url}:\n{result.stderr}")
        return False
    vtt_candidate = f"{safe_title}.{lang}.vtt"
    if not os.path.exists(vtt_candidate):
        print(f"No subtitle file found for: {vtt_candidate}")
        return False

    text = vtt_to_text(vtt_candidate, group_minutes=1)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{safe_title}.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Transcript saved to {output_file}")

    if not KEEP_VTT:
        os.remove(vtt_candidate)
        print(f"Deleted VTT file: {vtt_candidate}")

    return True

def main():
    if not os.path.exists(COOKIES_FILE):
        print("Missing cookies.txt.")
        return
    if not os.path.exists(URL_LIST_FILE):
        print(f"Missing {URL_LIST_FILE}.")
        return

    with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != 2:
                print(f"Skipping malformed line: {line.strip()}")
                continue
            url, title = parts
            for lang in ["vi", "en"]:
                success = download_and_convert(url.strip(), title.strip(), lang)
                if success:
                    break

if __name__ == "__main__":
    main()
