YouTube Subtitle Downloader & Converter
=======================================

This script downloads subtitles (preferably uploaded ones, falling back to auto-generated if needed) from YouTube videos in Vietnamese or English, then converts them from `.vtt` to clean paragraph-style `.txt` files.

Features
--------

- Downloads **only subtitles** (no video).
- Supports **both uploaded and auto-generated** subs.
- Prefers **Vietnamese** subtitles, falls back to **English**.
- Converts `.vtt` subtitle format into clean paragraph text.
- Outputs transcript to `transcripts/` folder.
- Cleans up temporary `.vtt` files unless configured otherwise.

Setup
-----

### 1. Create and activate virtual environment

    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate

### 2. Install requirements

    pip install -r requirements.txt

Usage
-----

### 1. Prepare `video_urls.txt`

This file should contain YouTube URLs and custom titles, **one per line**, comma-separated:

    https://www.youtube.com/watch?v=dQw4w9WgXcQ,My Custom Title
    https://www.youtube.com/watch?v=abc123xyz,Another Title

### 2. Make sure you have `cookies.txt`

- Export cookies from your browser (e.g. using "Get cookies.txt" browser extension).
- Save as `cookies.txt` in the same directory as the script.

### 3. Run the script

    python your_script.py

This will:
- Download available subtitles.
- Convert them to text.
- Save `.txt` files to the `transcripts/` directory.

Configuration
-------------

- `KEEP_VTT = False` — change to `True` in the script if you want to keep the `.vtt` files after conversion.

Notes
-----

- Make sure the `cookies.txt` file is up to date if subtitles fail to download (especially for members-only, age-restricted, or private videos).
- This script uses `yt-dlp`, an actively maintained `youtube-dl` fork.

Output
------

The transcript files will be saved to:

    transcripts/My Custom Title.txt

Troubleshooting
---------------

- **No subtitles found?**
  - Check if the video actually has `vi` or `en` subtitles.
  - Auto-generated subs may not be available for every video.
- **Getting 403/401 errors?**
  - Your `cookies.txt` might be invalid or expired.

Example
-------

    $ python your_script.py
    Processing: https://www.youtube.com/watch?v=dQw4w9WgXcQ
    Transcript saved to transcripts/My Custom Title.txt
    Deleted VTT file: My Custom Title.en.vtt

License
-------

MIT
