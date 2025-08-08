import subprocess
import hashlib
import re
import csv
import os
from collections import defaultdict

# ==============================
# CONFIGURATION
# ==============================
FOLDER_TO_TRACK = "."  # Folder to scan for .c files (use "." for current directory)
OUTPUT_CSV = "function_modification_counts.csv"  # Output file for modification counts
MD5_CACHE = ".last_md5.csv"  # Stores latest MD5 hash of each function per file


# ==============================
# FUNCTION: Extract functions from C code
# ==============================
def extract_functions(code):
    """
    Extracts function names and their full body from C source code.

    Parameters:
        code (str): Full text content of the C file.

    Returns:
        list: A list of tuples (function_name, function_body).
    """
    # Matches: return type (optional), function name, parameters, opening brace
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


# ==============================
# FUNCTION: Create MD5 checksum
# ==============================
def md5sum(text):
    """Returns MD5 checksum of the given text."""
    return hashlib.md5(text.encode()).hexdigest()


# ==============================
# FUNCTION: Get commit history for a file
# ==============================
def get_commits(file_path):
    """
    Gets a list of commit hashes for a specific file.

    Returns:
        list: Commit hashes sorted oldest → newest.
    """
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H", "--", file_path],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip().splitlines()[::-1]  # Reverse to get oldest first


# ==============================
# FUNCTION: Get file content at a specific commit
# ==============================
def get_file_at_commit(commit_hash, file_path):
    """
    Retrieves the file content at a specific commit hash.

    Returns:
        str: File content at that commit, or empty string if not found.
    """
    result = subprocess.run(
        ["git", "show", f"{commit_hash}:{file_path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    return result.stdout if result.returncode == 0 else ""


# ==============================
# FUNCTION: Find all .c files in directory
# ==============================
def find_c_files(folder):
    """Recursively finds all .c files starting from the given folder."""
    c_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".c"):
                rel_path = os.path.relpath(os.path.join(root, file))
                c_files.append(rel_path)
    return c_files


# ==============================
# FUNCTION: Save latest MD5s to cache
# ==============================
def save_current_md5(md5_map, path=MD5_CACHE):
    """Saves the latest MD5 checksums of each function per file."""
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        for (file, func), md5 in sorted(md5_map.items()):
            writer.writerow([file, func, md5])


# ==============================
# MAIN SCRIPT LOGIC
# ==============================
def main():
    # Step 1: Find all C files in the folder
    all_c_files = find_c_files(FOLDER_TO_TRACK)
    print(f"📁 Found {len(all_c_files)} C files to track.")

    overall_md5_prev = {}  # Stores final MD5s for all files
    modification_counts = defaultdict(int)  # Tracks change counts per (file, func)

    # Step 2: Process each file's commit history
    for file in all_c_files:
        print(f"🔍 Processing: {file}")
        commits = get_commits(file)
        function_md5_prev = {}  # Tracks previous MD5 for each function (per file)

        # Step 3: Check each commit for function changes
        for commit in commits:
            code = get_file_at_commit(commit, file)
            if not code:
                continue

            functions = extract_functions(code)
            current_md5s = {name: md5sum(body) for name, body in functions}

            for name, md5 in current_md5s.items():
                key = (file, name)  # Include file path to separate same-named functions in different files
                prev_md5 = function_md5_prev.get(name)

                if prev_md5 and prev_md5 != md5:
                    modification_counts[key] += 1
                elif key not in modification_counts:
                    modification_counts[key] = 0  # First time seen

            function_md5_prev = current_md5s

        # Step 4: Save latest MD5 for this file
        for name, md5 in function_md5_prev.items():
            overall_md5_prev[(file, name)] = md5

    # Step 5: Save modification counts to CSV
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", "Function", "ModificationCount"])
        for (file, func), count in sorted(modification_counts.items()):
            writer.writerow([file, func, count])

    # Step 6: Save current MD5 snapshot
    save_current_md5(overall_md5_prev)

    print(f"\n📄 Function modification data saved in: {OUTPUT_CSV}")
    print(f"📦 Final MD5 sum saved in: {MD5_CACHE}")


# ==============================
# RUN SCRIPT
# ==============================
if __name__ == "__main__":
    main()
