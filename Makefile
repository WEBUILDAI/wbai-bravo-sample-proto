# Alle Befehle laufen headless (CI, Cloud session, lokal).
PYTHON ?= $(shell command -v python3.12 || command -v python3)
VENV ?= .venv
BIN := $(VENV)/bin

.PHONY: venv install compile setup lint format test verify run

venv:
	test -x $(BIN)/python || $(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install -q --upgrade pip

install: venv
	$(BIN)/pip install -q -r requirements.txt -r requirements-dev.txt

compile: venv
	$(BIN)/pip install -q pip-tools==7.7.0
	$(BIN)/pip-compile -q --strip-extras --output-file requirements.txt requirements.in
	$(BIN)/pip-compile -q --strip-extras --output-file requirements-dev.txt requirements-dev.in

setup: install
	if [ -e .git ]; then $(BIN)/pre-commit install >/dev/null; fi

lint:
	$(BIN)/black --check .
	$(BIN)/ruff check .

format:
	$(BIN)/black .
	$(BIN)/ruff check --fix .

test:
	$(BIN)/pytest

verify: lint test

run:
	$(BIN)/uvicorn app.main:app --reload
