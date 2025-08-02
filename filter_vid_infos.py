KEYWORDS = ['(teaser)', '(re-up)', '(reup)']

def should_filter(title):
    if not title:
        return False
    lower_title = title.lower()
    return any(keyword in lower_title for keyword in KEYWORDS)

def main():
    with open("vid_infos.txt", "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    filtered_lines = []
    for line in lines:
        # Expect: "NNN. title | url"
        parts = line.split('|', 1)
        if len(parts) != 2:
            continue  # skip malformed lines
        # Extract title (remove leading number and dot)
        title_part = parts[0]
        title = title_part.split('.', 1)[-1].strip()
        if not should_filter(title):
            filtered_lines.append(line)

    with open("vid_infos.filtered.txt", "w", encoding="utf-8") as outfile:
        outfile.writelines(filtered_lines)

if __name__ == "__main__":
    main()