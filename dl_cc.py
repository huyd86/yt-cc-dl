import subprocess
import os
import re
import configparser
from datetime import timedelta
from pathlib import Path

config = configparser.ConfigParser()
config.read('config.ini')

COOKIES_FILE = config['DEFAULT'].get('COOKIES_FILE', "cookies.txt")
URL_LIST_FILE = config['DEFAULT'].get('URL_LIST_FILE', "tts_vid_infos.filtered.txt")
OUTPUT_DIR = config['DEFAULT'].get('OUTPUT_DIR', "tts_transcripts")
KEEP_VTT = False  # Set to True if you want to keep the .vtt file after conversion

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip()

def parse_vtt_time(vtt_time):
    h, m, s = vtt_time.split(":")
    seconds, ms = s.split(".")
    return timedelta(hours=int(h), minutes=int(m), seconds=int(seconds), milliseconds=int(ms))

def vtt_to_text(vtt_path):
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sentences = []
    current_sentence = ""
    sentence_start_time = None
    last_line = None  # <--- Added to track duplicates

    for i in range(len(lines)):
        line = lines[i].strip()

        # Parse timestamp line, e.g. "00:01:16.360 --> 00:01:18.320"
        if "-->" in line:
            time_start_str = line.split("-->")[0].strip()
            try:
                cur_time = parse_vtt_time(time_start_str)
            except Exception:
                cur_time = None
            if (sentence_start_time is not None and cur_time is not None and
                (cur_time - sentence_start_time) >= timedelta(minutes=0.5) and current_sentence):
                sentences.append(current_sentence.strip())
                current_sentence = ""
                sentence_start_time = cur_time
            elif sentence_start_time is None and cur_time is not None:
                sentence_start_time = cur_time
            continue

        if not line or line.startswith("WEBVTT") or "<" in line:
            continue
        if re.match(r"^\[.*\]$", line):
            continue

        # Deduplication: skip if exact match with last line appended
        if line == last_line:
            continue
        last_line = line

        current_sentence += (" " if current_sentence else "") + line
        while True:
            match = re.search(r"([.?!])(\s+|$)", current_sentence)
            if not match:
                break
            end = match.end()
            sentences.append(current_sentence[:end].strip())
            current_sentence = current_sentence[end:].lstrip()
            sentence_start_time = None

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
        "--write-auto-sub",
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
