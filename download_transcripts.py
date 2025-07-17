
import subprocess
import os
from pathlib import Path

COOKIES_FILE = "cookies.txt"
URL_LIST_FILE = "video_urls.txt"
OUTPUT_DIR = "transcripts"

def vtt_to_text(vtt_path):
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_lines = []
    last_line = None
    for line in lines:
        line = line.strip()
        if not line or "-->" in line or "<" in line:
            continue
        if line == last_line:
            continue
        cleaned_lines.append(line)
        last_line = line

    return "\n".join(cleaned_lines)

def sanitize_filename(title):
    import re
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip()

def download_and_convert(url, custom_title):
    print(f"Processing: {url}")
    safe_title = sanitize_filename(custom_title)

    # Download subtitles
    result = subprocess.run([
        "yt-dlp",
        "--cookies", COOKIES_FILE,
        "--write-auto-sub",
        "--skip-download",
        "--sub-lang", "vi",
        "--output", f"{safe_title}.%(ext)s",
        url
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error downloading subtitles for {url}:\n{result.stderr}")
        return

    vtt_file = f"{safe_title}.vi.vtt"
    if not os.path.exists(vtt_file):
        print(f"Subtitle file not found: {vtt_file}")
        return

    # Convert and save
    text = vtt_to_text(vtt_file)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{safe_title}.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Transcript saved to {output_file}")
    os.remove(vtt_file)

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
            download_and_convert(url, title)

if __name__ == "__main__":
    main()
