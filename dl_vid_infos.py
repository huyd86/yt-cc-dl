import yt_dlp
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

CHANNEL_URL = config['DEFAULT'].get('CHANNEL_URL', "https://www.youtube.com/@tungtungsoong/videos")
COOKIES_FILE = config['DEFAULT'].get('COOKIES_FILE', "cookies.txt")
VID_INFOS_FILE = config['DEFAULT'].get('VID_INFOS_FILE', "vid_infos.txt")

def main():
    ydl_opts = {
        'cookiefile': COOKIES_FILE,
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(CHANNEL_URL, download=False)
        entries = results['entries']

        # Reverse list so oldest is first
        entries = entries[::-1]

        lines = []
        for idx, video in enumerate(entries, start=1):
            url = f"https://www.youtube.com/watch?v={video['id']}"
            title = video.get('title')
            line = f"{idx:03d}. {title} | {url}"
            lines.append(line)

        with open(VID_INFOS_FILE, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

if __name__ == "__main__":
    main()