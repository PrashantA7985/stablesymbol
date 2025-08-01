# Makefile for tracking function-level changes using md5 across Git commits

PYTHON := python3
TARGET_FILE := myfile.c  # <-- Replace with your file name
HISTORY_SCRIPT := track_function_changes.py
COMMIT_SCRIPT := track_last_commit_only.py

.PHONY: all run commit-setup reset clean

# Run full Git history analysis and generate CSV
run:
	$(PYTHON) $(HISTORY_SCRIPT) $(TARGET_FILE)

# Run only on last commit (used after each commit)
last:
	$(PYTHON) $(COMMIT_SCRIPT)

# Setup git post-commit hook to auto-run after commit
commit-setup:
	echo "#!/bin/bash\n$(PYTHON) $(COMMIT_SCRIPT)" > .git/hooks/post-commit
	chmod +x .git/hooks/post-commit
	echo "✅ Git post-commit hook installed."

# Clean generated files
clean:
	rm -f function_modification_counts.csv .last_md5.csv

# Start fresh (delete CSVs and rerun full history)
reset: clean
	$(MAKE) run
