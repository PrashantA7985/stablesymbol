import subprocess
import hashlib
import re
import csv
from collections import defaultdict

FILE_TO_TRACK = "myfile.c"  # <--- Replace with your actual file name
OUTPUT_CSV = "function_modification_counts.csv"

def extract_functions(code):
    pattern = re.compile(
        r'(?:\w[\w\s\*\(\)]+?\s+)?([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', re.M
    )
    matches = list(pattern.finditer(code))

    functions = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(code)
        func_code = code[start:end].strip()
        func_name = matches[i].group(1)
        functions.append((func_name, func_code))

    return functions

def md5sum(text):
    return hashlib.md5(text.encode()).hexdigest()

def get_commits(file_path):
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H", "--", file_path],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip().splitlines()[::-1]  # oldest to newest

def get_file_at_commit(commit_hash, file_path):
    result = subprocess.run(
        ["git", "show", f"{commit_hash}:{file_path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    return result.stdout if result.returncode == 0 else ""

def main():
    commits = get_commits(FILE_TO_TRACK)
    print(f"Found {len(commits)} commits for file: {FILE_TO_TRACK}")

    function_md5_prev = {}
    modification_counts = defaultdict(int)

    for commit in commits:
        code = get_file_at_commit(commit, FILE_TO_TRACK)
        if not code:
            continue

        functions = extract_functions(code)
        current_md5s = {name: md5sum(body) for name, body in functions}

        for name, md5 in current_md5s.items():
            prev_md5 = function_md5_prev.get(name)
            if prev_md5 and prev_md5 != md5:
                modification_counts[name] += 1
            elif name not in function_md5_prev:
                modification_counts[name] = modification_counts.get(name, 0)

        function_md5_prev = current_md5s  # Replace with new snapshot

    # Write to CSV
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Function", "ModificationCount"])
        for func, count in sorted(modification_counts.items()):
            writer.writerow([func, count])

    print(f"\n✅ Function modification data saved in: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
