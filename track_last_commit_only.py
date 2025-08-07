# import subprocess
# import hashlib
# import re
# import csv
# import os
# from collections import defaultdict

# FILE_TO_TRACK = "myfile.c"  
# CSV_PATH = "function_modification_counts.csv"
# MD5_CACHE = ".last_md5.csv"

# def extract_functions(code):
#     pattern = re.compile(r'(?:\w[\w\s\*\(\)]+?\s+)?([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', re.M)
#     matches = list(pattern.finditer(code))
#     functions = []
#     for i in range(len(matches)):
#         start = matches[i].start()
#         end = matches[i + 1].start() if i + 1 < len(matches) else len(code)
#         body = code[start:end].strip()
#         name = matches[i].group(1)
#         functions.append((name, hashlib.md5(body.encode()).hexdigest()))
#     return functions

# def load_previous_md5():
#     if not os.path.exists(MD5_CACHE):
#         return {}
#     with open(MD5_CACHE) as f:
#         reader = csv.reader(f)
#         return {row[0]: row[1] for row in reader if row}

# def save_current_md5(md5_map):
#     with open(MD5_CACHE, 'w', newline='') as f:
#         writer = csv.writer(f)
#         for func, md5 in md5_map.items():
#             writer.writerow([func, md5])

# def load_counts():
#     counts = defaultdict(int)
#     if os.path.exists(CSV_PATH):
#         with open(CSV_PATH) as f:
#             reader = csv.reader(f)
#             next(reader, None)
#             for row in reader:
#                 if len(row) >= 2:
#                     counts[row[0]] = int(row[1])
#     return counts

# def save_counts(counts):
#     with open(CSV_PATH, 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow(["Function", "ModificationCount"])
#         for func, count in sorted(counts.items()):
#             writer.writerow([func, count])

# def main():
#     with open(FILE_TO_TRACK, 'r', errors='ignore') as f:
#         code = f.read()

#     new_md5s = dict(extract_functions(code))
#     old_md5s = load_previous_md5()
#     counts = load_counts()

#     for func, new_md5 in new_md5s.items():
#         old_md5 = old_md5s.get(func)
#         if old_md5 and old_md5 != new_md5:
#             counts[func] += 1
#         elif func not in counts:
#             counts[func] = 0

#     save_current_md5(new_md5s)
#     save_counts(counts)
#     print("✅ Function modification count updated after commit.")

# if __name__ == "__main__":
#     main()







import subprocess
import hashlib
import re
import csv
import os
from collections import defaultdict

FOLDER_TO_TRACK = "."  # Change this to your target folder (e.g., "src")
CSV_PATH = "function_modification_counts.csv"
MD5_CACHE = ".last_md5.csv"

def extract_functions(code):
    pattern = re.compile(r'(?:\w[\w\s\*\(\)]+?\s+)?([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', re.M)
    matches = list(pattern.finditer(code))
    functions = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(code)
        body = code[start:end].strip()
        name = matches[i].group(1)
        functions.append((name, hashlib.md5(body.encode()).hexdigest()))
    return functions

def find_c_files(folder):
    c_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".c"):
                full_path = os.path.join(root, file)
                c_files.append(os.path.relpath(full_path))
    return c_files

def load_previous_md5():
    if not os.path.exists(MD5_CACHE):
        return {}
    with open(MD5_CACHE) as f:
        reader = csv.reader(f)
        return {(row[0], row[1]): row[2] for row in reader if len(row) >= 3}

def save_current_md5(md5_map):
    with open(MD5_CACHE, 'w', newline='') as f:
        writer = csv.writer(f)
        for (file, func), md5 in md5_map.items():
            writer.writerow([file, func, md5])

def load_counts():
    counts = defaultdict(int)
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH) as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    counts[(row[0], row[1])] = int(row[2])
    return counts

def save_counts(counts):
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Function", "ModificationCount"])
        for (file, func), count in sorted(counts.items()):
            writer.writerow([file, func, count])

def main():
    all_c_files = find_c_files(FOLDER_TO_TRACK)
    print(f"🔍 Found {len(all_c_files)} .c files to scan in '{FOLDER_TO_TRACK}'")

    new_md5s = {}
    old_md5s = load_previous_md5()
    counts = load_counts()

    for file_path in all_c_files:
        try:
            with open(file_path, 'r', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            continue

        for func, md5 in extract_functions(code):
            key = (file_path, func)
            old_md5 = old_md5s.get(key)
            new_md5s[key] = md5

            if old_md5 and old_md5 != md5:
                counts[key] += 1
            elif key not in counts:
                counts[key] = 0

    save_current_md5(new_md5s)
    save_counts(counts)
    print("✅ Function modification counts updated for all .c files.")

if __name__ == "__main__":
    main()
