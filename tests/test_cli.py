"""Tests for the urirun-llm CLI."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from urirun_llm_runtime import cli

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_validate_valid_plan(capsys):
    plan = EXAMPLES / "processes" / "smoke_diagnostic.json"
    rc = cli.main(["validate", str(plan)])
    assert rc == 0
    assert "valid" in capsys.readouterr().out


def test_validate_rejects_bad_uri(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"id": "a", "uri": "not-a-uri"}]))
    rc = cli.main(["validate", str(bad)])
    assert rc == 1
    assert "error" in capsys.readouterr().err


def test_lint_clean_glue(capsys):
    rc = cli.main(["lint", str(EXAMPLES / "glue")])
    assert rc == 0
    assert "no anti-patterns" in capsys.readouterr().out


def test_lint_flags_subprocess(tmp_path, capsys):
    offender = tmp_path / "glue.py"
    offender.write_text("import subprocess\ndef run(ctx=None):\n    subprocess.run(['ls'])\n")
    rc = cli.main(["lint", str(offender)])
    assert rc == 1
    assert capsys.readouterr().err.strip()


def test_prompt_prints_system_prompt(capsys):
    rc = cli.main(["prompt", "--ticket", "demo"])
    assert rc == 0
    assert capsys.readouterr().out.strip()


def test_missing_file_returns_code_2(capsys):
    rc = cli.main(["validate", "/no/such/plan.json"])
    assert rc == 2
    assert "error" in capsys.readouterr().err


def test_no_command_exits_nonzero():
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code != 0
