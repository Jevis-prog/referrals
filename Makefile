ruff_lint_check:
	ruff check app tests main.py

ruff_lint_fix:
	ruff check app tests main.py --fix

ruff_format_check:
	ruff format app tests main.py --check

ruff_format_fix:
	ruff format app tests main.py

ruff_sort_imports:
	ruff check app tests main.py --fix --select I

ruff: ruff_format_check ruff_lint_check

mypy_check:
	mypy app tests main.py --explicit-package-bases

fmt: ruff_format_fix ruff_sort_imports

lint: mypy_check ruff_format_check ruff_lint_check

test:
	set PYTHONPATH=. && pytest tests

all: fmt lint test