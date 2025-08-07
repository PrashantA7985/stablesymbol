# Makefile for tracking function-level changes using md5 across Git commits
# Run full Git history analysis and generate CSV
run:
	python3 track_function_changes.py myfile.c

# Run only on last commit (used after each commit)
last:
	python3 track_last_commit_only.py

# Clean generated files
clean:
	rm -f function_modification_counts.csv .last_md5.csv


