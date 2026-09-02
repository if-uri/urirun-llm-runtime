.PHONY: help install install-dev test doctor-test doctor-health lint validate-examples clean

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

help:
	@echo "Targets:"
	@echo "  install           Install runtime dependencies"
	@echo "  install-dev       Install development dependencies (pytest, ruff, ...)"
	@echo "  test              Run the test suite with pytest"
	@echo "  doctor-test       Run the test gate used by Doctor/OneDev"
	@echo "  doctor-health     Verify the installed runtime imports"
	@echo "  lint              Run ruff lint checks"
	@echo "  validate-examples Validate example plans with urirun-llm CLI"
	@echo "  clean             Remove build and cache artifacts"

install:
	$(PIP) install .

install-dev:
	$(PIP) install -e ".[dev]"

doctor-test:
	$(PYTHON) -m pytest

doctor-health:
	$(PYTHON) -c "import urirun_llm_runtime"

test: doctor-test

lint:
	$(PYTHON) -m ruff check .

validate-examples:
	$(PYTHON) -m urirun_llm_runtime.cli validate examples/processes/smoke_diagnostic.json

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
