import hashlib
import re
import csv
import os
import subprocess
from collections import defaultdict

# ==============================
# CONFIGURATION
# ==============================
FOLDER_TO_TRACK = "."  # "." means track the current directory
CSV_PATH = "function_modification_counts.csv"  # Stores modification counts
MD5_CACHE = ".last_md5.csv"  # Stores last known MD5 hashes per function per file


# ==============================
# FUNCTION: Extract Functions & MD5 using ctags
# ==============================
def extract_functions(code, file_path=None):
    """
    Extracts function names and MD5 hash of their body from a C file using ctags.
    `file_path` must be the actual file on disk (ctags works on files, not strings).
    Returns: list of (function_name, md5_hash)
    """
    if not file_path:
        return []

    # Run ctags to get function name + line number
    result = subprocess.run(
        ["ctags", "-x", "--c-kinds=f", file_path],
        capture_output=True, text=True
    )

    functions = []
    if result.returncode != 0:
        return functions

    lines = result.stdout.strip().split("\n")
    if not lines or lines == ['']:
        return functions

    # Load file content once
    with open(file_path, "r", errors="ignore") as f:
        code_lines = f.readlines()

    # Parse ctags output and extract body
    parsed_funcs = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            name = parts[0]
            try:
                start_line = int(parts[2])
                parsed_funcs.append((name, start_line))
            except ValueError:
                continue

    # Sort by start line so we can find body ranges
    parsed_funcs.sort(key=lambda x: x[1])

    for i, (name, start_line) in enumerate(parsed_funcs):
        start_idx = start_line - 1
        end_idx = parsed_funcs[i + 1][1] - 1 if i + 1 < len(parsed_funcs) else len(code_lines)
        body = "".join(code_lines[start_idx:end_idx]).strip()
        md5_hash = hashlib.md5(body.encode()).hexdigest()
        functions.append((name, md5_hash))

    return functions


# ==============================
# FUNCTION: Find all .c files recursively
# ==============================
def find_c_files(folder):
    c_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".c"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=FOLDER_TO_TRACK)
                c_files.append(rel_path)
    return c_files


# ==============================
# FUNCTION: Load last MD5 snapshot
# ==============================
def load_previous_md5():
    if not os.path.exists(MD5_CACHE):
        return {}
    with open(MD5_CACHE) as f:
        reader = csv.reader(f)
        return {(row[0], row[1]): row[2] for row in reader if len(row) >= 3}


# ==============================
# FUNCTION: Save current MD5 snapshot
# ==============================
def save_current_md5(md5_map):
    with open(MD5_CACHE, 'w', newline='') as f:
        writer = csv.writer(f)
        for (file, func), md5 in md5_map.items():
            writer.writerow([file, func, md5])


# ==============================
# FUNCTION: Load modification counts
# ==============================
def load_counts():
    counts = defaultdict(int)
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 3:
                    counts[(row[0], row[1])] = int(row[2])
    return counts


# ==============================
# FUNCTION: Save modification counts
# ==============================
def save_counts(counts):
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Function", "ModificationCount"])
        for (file, func), count in sorted(counts.items()):
            writer.writerow([file, func, count])


# ==============================
# MAIN LOGIC
# ==============================
def main():
    all_c_files = find_c_files(FOLDER_TO_TRACK)
    print(f"🔍 Found {len(all_c_files)} .c files under '{FOLDER_TO_TRACK}'")

    new_md5s = {}
    old_md5s = load_previous_md5()
    counts = load_counts()

    for file_path in all_c_files:
        abs_path = os.path.join(FOLDER_TO_TRACK, file_path)
        try:
            with open(abs_path, 'r', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            continue

        for func, md5 in extract_functions(code, file_path=abs_path):
            key = (file_path, func)
            old_md5 = old_md5s.get(key)
            new_md5s[key] = md5

            if old_md5 and old_md5 != md5:
                counts[key] += 1
            elif key not in counts:
                counts[key] = 0

    save_current_md5(new_md5s)
    save_counts(counts)

    print(f"✅ Modification counts updated. Saved to '{CSV_PATH}'.")


if __name__ == "__main__":
    main()
