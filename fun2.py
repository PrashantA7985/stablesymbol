#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
import sys

def git_changed_c_files(repo_root: Path, base_ref: str = "HEAD~1", head_ref: str = "HEAD"):
    try:
        res = subprocess.run(
            ["git", "diff", "--name-only", base_ref, head_ref],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        files = []
        for line in res.stdout.splitlines():
            if line.endswith(".c"):
                files.append(line.strip())
        return files
    except Exception:
        return []

def main():
    ap = argparse.ArgumentParser(description="Run function MD5 tracker after a new commit.")
    ap.add_argument("--repo", type=str, default=".", help="Repo root.")
    ap.add_argument("--history", type=str, default="functions_history.csv", help="CSV path to store function history.")
    ap.add_argument("--base", type=str, default="HEAD~1", help="Base ref to compute changed files.")
    ap.add_argument("--head", type=str, default="HEAD", help="Head ref.")
    ap.add_argument("--full-scan", action="store_true", help="Force scan all .c files instead of only changed files.")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    history_csv = Path(args.history).resolve()

    only_files = []
    if not args.full_scan:
        only_files = git_changed_c_files(repo_root, args.base, args.head)

    cmd = [
        sys.executable,
        str((Path(__file__).parent / "extract_and_track_functions.py").resolve()),
        "--repo", str(repo_root),
        "--baseline", str(history_csv),
        "--output", str(history_csv),
    ]
    if only_files:
        cmd += ["--only-files"] + only_files

    print("Running:", " ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("Failed to update history:", e)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
