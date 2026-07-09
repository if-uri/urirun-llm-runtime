"""Glue: run diagnostic process list via URI runtime only."""
from __future__ import annotations

import json
from pathlib import Path

from urirun_llm_runtime import Executor, from_dict, run_processes

NODE = "http://host-node:8765"


def run(ctx=None):
    executor = Executor(NODE)
    data = json.loads(
        (Path(__file__).resolve().parents[1] / "processes" / "smoke_diagnostic.json").read_text()
    )
    processes = [from_dict(item) for item in data]
    return run_processes(executor, processes)


if __name__ == "__main__":
    print(run())
