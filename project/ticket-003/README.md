# Ticket 003: Reconcile ruff linter configuration and snapshot line length

- **ID**: ticket-003
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Created**: 2026-10-15

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: user requested ongoing repository health repair, testing, and ticket execution.
1. Add `extend-exclude = [".governance"]` to `[tool.ruff]` in `pyproject.toml` to prevent linter recursion into governance framework files.
2. Reconcile line length in `scripts/snapshot_route_schemas.py:82` to conform to 120 character limit.
3. Validate `ruff check .` passes with 0 errors across the repository.

## Acceptance criteria

- [x] AC-01: `pyproject.toml` excludes `.governance` from ruff linting.
- [x] AC-02: `scripts/snapshot_route_schemas.py` line length is <= 120 characters.
- [x] AC-03: `ruff check .` passes cleanly with 0 errors.
- [x] AC-04: Governance check `./project/governance-check.sh` passes cleanly with 0 errors.

## Validation

- Linter: `ruff check .` reports `All checks passed!`.
- Governance: `./project/governance-check.sh` reports `GOV-PASS: passed (0 errors, 0 warnings)`.
- Tests: `pytest` passes cleanly.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
