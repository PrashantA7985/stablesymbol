import hashlib
import re
import csv
import os
from collections import defaultdict

# ==============================
# CONFIGURATION
# ==============================
FOLDER_TO_TRACK = "."  # "." means track the current directory
CSV_PATH = "function_modification_counts.csv"  # Stores modification counts
MD5_CACHE = ".last_md5.csv"  # Stores last known MD5 hashes per function per file


# ==============================
# FUNCTION: Extract Functions & MD5
# ==============================
def extract_functions(code):
    """
    Extracts function names and MD5 hash of their body from C code.

    Parameters:
        code (str): The content of the C source file.

    Returns:
        list: A list of tuples (function_name, md5_hash).
    """
    # Regex to match C function definitions
    pattern = re.compile(
        r'(?:\w[\w\s\*\(\)]+?\s+)?([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', re.M
    )

    matches = list(pattern.finditer(code))
    functions = []

    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(code)

        # Extract function body
        body = code[start:end].strip()
        name = matches[i].group(1)

        # Create MD5 hash of the function body
        md5_hash = hashlib.md5(body.encode()).hexdigest()

        functions.append((name, md5_hash))

    return functions


# ==============================
# FUNCTION: Find all .c files recursively
# ==============================
def find_c_files(folder):
    """
    Recursively finds all .c files in the given folder.

    Returns:
        list: A list of relative file paths for all found .c files.
    """
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
    """
    Loads the last known MD5 hash of each function from cache.

    Returns:
        dict: {(file, function): md5_hash}
    """
    if not os.path.exists(MD5_CACHE):
        return {}
    with open(MD5_CACHE) as f:
        reader = csv.reader(f)
        return {(row[0], row[1]): row[2] for row in reader if len(row) >= 3}


# ==============================
# FUNCTION: Save current MD5 snapshot
# ==============================
def save_current_md5(md5_map):
    """
    Saves the current MD5 hashes to cache.

    Parameters:
        md5_map (dict): {(file, function): md5_hash}
    """
    with open(MD5_CACHE, 'w', newline='') as f:
        writer = csv.writer(f)
        for (file, func), md5 in md5_map.items():
            writer.writerow([file, func, md5])


# ==============================
# FUNCTION: Load modification counts
# ==============================
def load_counts():
    """
    Loads the function modification counts from CSV.

    Returns:
        dict: {(file, function): count}
    """
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
    """
    Saves the modification counts to CSV.

    Parameters:
        counts (dict): {(file, function): count}
    """
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Function", "ModificationCount"])
        for (file, func), count in sorted(counts.items()):
            writer.writerow([file, func, count])


# ==============================
# MAIN LOGIC
# ==============================
def main():
    # 1️⃣ Find all .c files in the folder (including subfolders)
    all_c_files = find_c_files(FOLDER_TO_TRACK)
    print(f"🔍 Found {len(all_c_files)} .c files under '{FOLDER_TO_TRACK}'")

    # 2️⃣ Load previous MD5 hashes & counts
    new_md5s = {}
    old_md5s = load_previous_md5()
    counts = load_counts()

    # 3️⃣ Loop through each C file
    for file_path in all_c_files:
        try:
            with open(os.path.join(FOLDER_TO_TRACK, file_path), 'r', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            continue

        # Extract functions and their MD5 hashes
        for func, md5 in extract_functions(code):
            key = (file_path, func)  # File path + Function name = Unique key
            old_md5 = old_md5s.get(key)
            new_md5s[key] = md5

            # If MD5 has changed, increment modification count
            if old_md5 and old_md5 != md5:
                counts[key] += 1
            elif key not in counts:
                counts[key] = 0  # First time seeing this function

    # 4️⃣ Save updated MD5 hashes & counts
    save_current_md5(new_md5s)
    save_counts(counts)

    print(f"✅ Modification counts updated. Saved to '{CSV_PATH}'.")


# ==============================
# RUN THE SCRIPT
# ==============================
if __name__ == "__main__":
    main()
