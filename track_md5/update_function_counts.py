import os
import csv
import hashlib
import re
from collections import defaultdict

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATH = os.path.join(REPO_PATH, "track_md5/function_modification_counts.csv")
MD5_DIR = os.path.join(REPO_PATH, "track_md5/md5_store")
TARGET_FILE = "myfile.c"  # Replace with your actual C source file name

os.makedirs(MD5_DIR, exist_ok=True)

def extract_functions(filename):
    with open(filename, 'r', errors='ignore') as f:
        code = f.read()
    pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s+\**([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{', re.M)
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

def load_previous_md5s():
    latest = os.path.join(MD5_DIR, "latest.csv")
    if not os.path.exists(latest):
        return {}
    prev_md5s = {}
    with open(latest) as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                prev_md5s[row[0]] = row[1]
    return prev_md5s

def save_current_md5s(md5_map):
    latest = os.path.join(MD5_DIR, "latest.csv")
    with open(latest, 'w', newline='') as f:
        writer = csv.writer(f)
        for func, md5 in md5_map.items():
            writer.writerow([func, md5])

def load_counts():
    counts = defaultdict(int)
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH) as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    counts[row[0]] = int(row[1])
    return counts

def save_counts(counts):
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Function Name", "Modification Count"])
        for func, count in sorted(counts.items()):
            writer.writerow([func, count])

def main():
    file_path = os.path.join(REPO_PATH, TARGET_FILE)
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return
    functions = extract_functions(file_path)
    current_md5 = {name: md5sum(code) for name, code in functions}
    previous_md5 = load_previous_md5s()
    counts = load_counts()

    for func, new_md5 in current_md5.items():
        old_md5 = previous_md5.get(func)
        if old_md5 and old_md5 != new_md5:
            counts[func] += 1
        elif func not in counts:
            counts[func] = 0  # First time seen

    save_counts(counts)
    save_current_md5s(current_md5)

if __name__ == "__main__":
    main()
