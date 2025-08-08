import subprocess
import hashlib
import csv
import os
from collections import defaultdict

# ====== CONFIG ======
FOLDER_TO_TRACK = "/drives/c/Users/prasin/OneDrive - Synaptics/Desktop/myproject"
OUTPUT_CSV = "function_modification_counts.csv"
MD5_CACHE = ".last_md5.csv"
# ====================

def run_ctags(file_path):
    """
    Runs ctags to extract function names and line numbers from a C file.
    Returns a list of tuples: (function_name, start_line, end_line)
    """
    # Generate tags in JSON for easier parsing
    result = subprocess.run(
        ["ctags", "-x", "--c-kinds=f", file_path],
        capture_output=True, text=True
    )

    functions = []
    lines = result.stdout.strip().split("\n")
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        # Format from `ctags -x`:
        # NAME KIND LINE FILE
        # Example: myfunc function 12 myfile.c
        if len(parts) >= 4:
            name = parts[0]
            line_num = int(parts[2])
            functions.append((name, line_num))
    return functions

def extract_functions_with_md5(file_path):
    """
    Uses ctags to get functions and calculates MD5 for each function body.
    """
    functions = run_ctags(file_path)
    md5_map = {}

    with open(file_path, "r", errors="ignore") as f:
        code_lines = f.readlines()

    for i, (name, start_line) in enumerate(functions):
        start_index = start_line - 1
        # End line = start of next function OR EOF
        end_index = functions[i + 1][1] - 1 if i + 1 < len(functions) else len(code_lines)
        func_body = "".join(code_lines[start_index:end_index])
        md5_map[f"{os.path.basename(file_path)}::{name}"] = hashlib.md5(func_body.encode()).hexdigest()

    return md5_map

def scan_all_files():
    md5s = {}
    for root, _, files in os.walk(FOLDER_TO_TRACK):
        for file in files:
            if file.endswith(".c") or file.endswith(".h"):
                file_path = os.path.join(root, file)
                md5s.update(extract_functions_with_md5(file_path))
    return md5s

def load_previous_md5():
    if not os.path.exists(MD5_CACHE):
        return {}
    with open(MD5_CACHE, "r") as f:
        return dict(line.strip().split(",") for line in f)

def load_counts():
    if not os.path.exists(OUTPUT_CSV):
        return defaultdict(int)
    counts = defaultdict(int)
    with open(OUTPUT_CSV, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            counts[row[0]] = int(row[1])
    return counts

def save_md5(md5s):
    with open(MD5_CACHE, "w") as f:
        for func, md5 in md5s.items():
            f.write(f"{func},{md5}\n")

def save_counts(counts):
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        for func, count in counts.items():
            writer.writerow([func, count])

def main():
    new_md5s = scan_all_files()
    old_md5s = load_previous_md5()
    counts = load_counts()

    for func, new_md5 in new_md5s.items():
        old_md5 = old_md5s.get(func)
        if old_md5 and old_md5 != new_md5:
            counts[func] += 1
        elif old_md5 is None:
            counts[func] = counts.get(func, 0)

    save_md5(new_md5s)
    save_counts(counts)

if __name__ == "__main__":
    main()
