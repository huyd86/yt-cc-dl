import subprocess
import os
import re
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
    # Merge lines into a single paragraph while preserving sentence flow
    paragraph = ' '.join(lines).strip()
    paragraph = re.sub(r'\s+', ' ', paragraph)  # collapse extra spaces
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
            # Try to avoid speaker tags or formatting
            if re.match(r"^\[.*\]$", line):
                continue
            current_lines.append(line)

    if current_lines:
        paragraphs.append(clean_and_merge_lines(current_lines))

    return "\n\n".join(paragraphs)

def sanitize_filename(title):
    """Sanitize filename to remove/replace illegal characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip()


def download_and_convert(url, custom_title):
    """Download .vtt subtitle for a YouTube video and convert to readable text."""
    print(f"Processing: {url}")
    safe_title = sanitize_filename(custom_title)

    # Download subtitles only
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

    # Convert VTT to paragraph text
    text = vtt_to_text(vtt_file, group_minutes=1)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{safe_title}.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Transcript saved to {output_file}")

    if not KEEP_VTT:
        os.remove(vtt_file)
        print(f"Deleted VTT file: {vtt_file}")


def main():
    """Main entry point: process each video URL and title from the list."""
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
            download_and_convert(url.strip(), title.strip())


if __name__ == "__main__":
    main()
