# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `urirun-llm` console CLI (`urirun_llm_runtime.cli`) plus
  `python -m urirun_llm_runtime`, exposing `health`, `routes`, `execute`,
  `run`, `validate`, `lint` and `prompt` over the existing library — no
  hand-written glue required. Registered as a `project.scripts` entry point.
- Export `urirun_llm_runtime.__version__` and `cli_main`.
- CLI test suite (`tests/test_cli.py`).

### Changed
- README documents the new CLI.

## [0.2.0]

- Canonical LLM-facing URI process runtime: spec, executor, process runner,
  validators and CI gates.
