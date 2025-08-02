import subprocess
import os
import re
from datetime import timedelta
from pathlib import Path

COOKIES_FILE = "cookies.txt"
URL_LIST_FILE = "vid_infos.filtered.txt"
OUTPUT_DIR = "transcripts"
KEEP_VTT = False  # Set to True if you want to keep the .vtt file after conversion

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip()

def vtt_to_text(vtt_path):
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sentences = []
    current_sentence = ""

    for i in range(len(lines)):
        line = lines[i].strip()
        if "-->" in line or not line or line.startswith("WEBVTT") or "<" in line:
            continue
        if re.match(r"^\[.*\]$", line):
            continue

        # Merge lines and split at sentence boundary
        current_sentence += (" " if current_sentence else "") + line
        while True:
            match = re.search(r"([.?!])(\s+|$)", current_sentence)
            if not match:
                break
            end = match.end()
            sentences.append(current_sentence[:end].strip())
            current_sentence = current_sentence[end:].lstrip()

    if current_sentence:
        sentences.append(current_sentence.strip())

    return "\n".join(sentences)

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

    text = vtt_to_text(vtt_candidate)
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

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if '|' not in line:
                print(f"Skipping malformed line: {line.strip()}")
                continue
            title, url = line.strip().split('|', 1)
            title = title.strip()
            url = url.strip()
            safe_title = sanitize_filename(title)
            output_file = os.path.join(OUTPUT_DIR, f"{safe_title}.txt")
            if os.path.exists(output_file):
                print(f"Transcript already exists for '{title}' ({output_file}), skipping.")
                continue
            for lang in ["vi", "en"]:
                success = download_and_convert(url, title, lang)
                if success:
                    break

if __name__ == "__main__":
    main()
