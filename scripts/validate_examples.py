#!/usr/bin/env python3
"""CI gate: validate examples/*.py and examples/glue/*.py follow URI-only patterns."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from urirun_llm_runtime.validator import lint_path, lint_tree


def main() -> int:
    errors: list[str] = []
    examples = ROOT / "examples"
    glue = ROOT / "examples" / "glue"
    if examples.is_dir():
        for py in sorted(examples.glob("*.py")):
            errors.extend(lint_path(py))
    if glue.is_dir():
        errors.extend(lint_tree(glue))
    if errors:
        print("URI glue validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("URI glue validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
