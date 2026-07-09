#!/usr/bin/env python3
"""CI gate: validate examples/processes/*.json against process schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from urirun_llm_runtime.process import from_dict, validate_processes

try:
    import jsonschema
except ImportError:
    jsonschema = None  # type: ignore


def main() -> int:
    schema_path = ROOT / "docs" / "llm" / "process_schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    proc_dir = ROOT / "examples" / "processes"
    if not proc_dir.is_dir():
        print("no examples/processes — skip")
        return 0

    errors: list[str] = []
    for path in sorted(proc_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if jsonschema:
            try:
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as exc:
                errors.append(f"{path.name}: schema: {exc.message}")
                continue
        procs = [from_dict(item) for item in data]
        for msg in validate_processes(procs):
            errors.append(f"{path.name}: {msg}")

    if errors:
        print("process validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"process validation OK ({len(list(proc_dir.glob('*.json')))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
