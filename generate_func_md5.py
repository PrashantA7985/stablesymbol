import hashlib
import re
import csv
import os
import sys

def extract_functions(content):
    functions = {}
    func_pattern = re.compile(r'^[\w\s\*]+?\s+(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE)
    matches = list(func_pattern.finditer(content))

    for i, match in enumerate(matches):
        func_name = match.group(1)
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        func_body = content[start:end].strip()
        func_md5 = hashlib.md5(func_body.encode()).hexdigest()
        functions[func_name] = func_md5
    return functions

def save_to_csv(func_md5s, out_csv):
    with open(out_csv, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Function Name", "MD5 Hash"])
        for func, md5 in func_md5s.items():
            writer.writerow([func, md5])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generate_func_md5.py myfile.c")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print("File not found:", file_path)
        sys.exit(1)

    with open(file_path, 'r') as f:
        content = f.read()

    func_md5s = extract_functions(content)
    output_csv = file_path + "_func_md5.csv"
    save_to_csv(func_md5s, output_csv)

    print(f"✅ MD5 per function saved to: {output_csv}")
