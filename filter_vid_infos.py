import configparser

config = configparser.ConfigParser()
config.read('config.ini')

VID_INFOS_FILE = config['DEFAULT'].get('VID_INFOS_FILE', "vid_infos.txt")
VID_INFOS_FILE_FILTERED = config['DEFAULT'].get('VID_INFOS_FILE_FILTERED', "vid_infos.filtered.txt")
KEYWORDS = [kw.strip() for kw in config['DEFAULT'].get('KEYWORDS', '').split(',') if kw.strip()]

def should_filter(title):
    if not title:
        return False
    lower_title = title.lower()
    return any(keyword in lower_title for keyword in KEYWORDS)

def main():
    with open(VID_INFOS_FILE, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    filtered_lines = []
    for line in lines:
        parts = line.split('|', 1)
        if len(parts) != 2:
            continue  # skip malformed lines
        title_part = parts[0]
        title = title_part.split('.', 1)[-1].strip()
        if not should_filter(title):
            filtered_lines.append(line)

    with open(VID_INFOS_FILE_FILTERED, "w", encoding="utf-8") as outfile:
        outfile.writelines(filtered_lines)

if __name__ == "__main__":
    main()