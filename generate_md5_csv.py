import hashlib
import re
import csv
import sys
import os

def extract_functions(filename):
    with open(filename, 'r', errors='ignore') as f:
        code = f.read()

    # Basic regex for function extraction
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

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_md5_csv.py <input_file> <output_csv> [commit_sha]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_csv = sys.argv[2]
    commit_sha = sys.argv[3] if len(sys.argv) > 3 else ""

    functions = extract_functions(input_file)

    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", "Function", "MD5", "Commit"])
        for name, code in functions:
            writer.writerow([os.path.basename(input_file), name, md5sum(code), commit_sha])

if __name__ == "__main__":
    main()
