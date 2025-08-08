import csv
import sys
import hashlib
import re
from collections import defaultdict

MD5_CACHE = ".last_md5.csv"
OUTPUT_CSV = "function_modification_counts.csv"

def extract_functions(code):
    pattern = re.compile(r'^[\w\s\*\(\)]+?\s+(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE)
    functions = {}
    for match in pattern.finditer(code):
        func_name = match.group(1)
        start = match.start()
        brace_count = 0
        end = start
        for i in range(start, len(code)):
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        func_body = code[start:end]
        md5_hash = hashlib.md5(func_body.encode()).hexdigest()
        functions[func_name] = md5_hash
    return functions

def load_previous_md5():
    try:
        with open(MD5_CACHE, 'r') as f:
            reader = csv.reader(f)
            return {rows[0]: rows[1] for rows in reader}
    except FileNotFoundError:
        return {}

def load_counts():
    try:
        with open(OUTPUT_CSV, 'r') as f:
            reader = csv.reader(f)
            return defaultdict(int, {rows[0]: int(rows[1]) for rows in reader})
    except FileNotFoundError:
        return defaultdict(int)

def save_counts(counts):
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        for func, count in counts.items():
            writer.writerow([func, count])

def save_md5s(md5s):
    with open(MD5_CACHE, 'w', newline='') as f:
        writer = csv.writer(f)
        for func, md5 in md5s.items():
            writer.writerow([func, md5])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compare_md5_changes.py <file.c>")
        sys.exit(1)

    with open(sys.argv[1], 'r', errors='ignore') as f:
        code = f.read()

    new_md5s = extract_functions(code)
    old_md5s = load_previous_md5()
    counts = load_counts()

    for func, new_md5 in new_md5s.items():
        old_md5 = old_md5s.get(func)
        if old_md5 and old_md5 != new_md5:
            counts[func] += 1
        elif old_md5 is None:
            counts[func] += 0  # new function — no change count

    save_counts(counts)
    save_md5s(new_md5s)
    print("Function change comparison complete.")
