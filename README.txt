✅ Overview
We'll build a tool that:
- Authenticates your YouTube session (via cookies).
- Accesses the video using yt-dlp (a powerful YouTube downloading tool).
- Extracts transcript/subtitles if available.
- Saves the transcript to a .txt or .json file.

🛠 Requirements
Install the following:
pip install yt-dlp

🔐 Step 1: Get Your YouTube Cookies
YouTube member videos require your login. You’ll need to export your cookies from your browser:
Install the Get cookies.txt extension for Chrome.
Visit the YouTube page where you're logged in.
Click the extension > “Export cookies.txt”
Save it as cookies.txt.

🧪 Step 2: Test yt-dlp Can Access the Video
Open a terminal and run:
yt-dlp --cookies cookies.txt "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
If this works, yt-dlp can access your member-only content.

📜 Step 3: Download Transcript/Subtitles
Run this command to list all available subtitles:
yt-dlp --cookies cookies.txt --list-subs "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"

Then download the subtitles in English (or your preferred language):
yt-dlp --cookies cookies.txt --write-auto-sub --sub-lang "en" --skip-download "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
This creates a .vtt or .webvtt subtitle file.

📄 Step 4: Convert .vtt to Plain Text (Optional)
