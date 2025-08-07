import subprocess
import hashlib
import re
import csv
import os
from collections import defaultdict

FOLDER_TO_TRACK = "."  # or "." for current directory
OUTPUT_CSV = "function_modification_counts.csv"
MD5_CACHE = ".last_md5.csv"

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
    return result.stdout.strip().splitlines()[::-1]  # Oldest to newest

def get_file_at_commit(commit_hash, file_path):
    result = subprocess.run(
        ["git", "show", f"{commit_hash}:{file_path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    return result.stdout if result.returncode == 0 else ""

def find_c_files(folder):
    c_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".c"):
                full_path = os.path.relpath(os.path.join(root, file))
                c_files.append(full_path)
    return c_files

def save_current_md5(md5_map, path=MD5_CACHE):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        for (file, func), md5 in sorted(md5_map.items()):
            writer.writerow([file, func, md5])

def main():
    all_c_files = find_c_files(FOLDER_TO_TRACK)
    print(f"📁 Found {len(all_c_files)} C files to track.")

    overall_md5_prev = {}
    modification_counts = defaultdict(int)

    for file in all_c_files:
        print(f"🔍 Processing: {file}")
        commits = get_commits(file)
        function_md5_prev = {}

        for commit in commits:
            code = get_file_at_commit(commit, file)
            if not code:
                continue

            functions = extract_functions(code)
            current_md5s = {name: md5sum(body) for name, body in functions}

            for name, md5 in current_md5s.items():
                prev_md5 = function_md5_prev.get(name)
                key = (file, name)

                if prev_md5 and prev_md5 != md5:
                    modification_counts[key] += 1
                elif key not in modification_counts:
                    modification_counts[key] = modification_counts.get(key, 0)

            function_md5_prev = current_md5s

        # Save the final MD5s for this file
        for name, md5 in function_md5_prev.items():
            overall_md5_prev[(file, name)] = md5

    # Write final CSV
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", "Function", "ModificationCount"])
        for (file, func), count in sorted(modification_counts.items()):
            writer.writerow([file, func, count])

    save_current_md5(overall_md5_prev)

    print(f"\n📄 Function modification data saved in: {OUTPUT_CSV}")
    print(f"📦 Final MD5 sum saved in: {MD5_CACHE}")

if __name__ == "__main__":
    main()
