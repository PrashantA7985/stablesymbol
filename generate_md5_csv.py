import hashlib
import re
import csv

def extract_functions(filename):
    with open(filename, 'r') as f:
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

def main():
    input_file = "myfile.c"
    output_csv = "md5_current.csv"

    functions = extract_functions(input_file)

    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Function", "MD5"])
        for name, code in functions:
            writer.writerow([name, md5sum(code)])

if __name__ == "__main__":
    main()