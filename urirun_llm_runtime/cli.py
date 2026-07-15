"""Command-line interface for urirun-llm-runtime.

Exposes the library's core capabilities without writing any glue by hand:

    urirun-llm health                      # GET {node}/health
    urirun-llm routes                      # GET {node}/routes
    urirun-llm execute <uri> [--payload J] # POST {node}/run for a single URI
    urirun-llm run <file|->                 # execute a urirun:processes plan
    urirun-llm validate <file|->            # parse + validate a plan (no execution)
    urirun-llm lint <path>                  # anti-subprocess CI gate over glue
    urirun-llm prompt [--ticket T]          # print the first LLM system prompt

The node URL comes from ``--node`` or ``URIRUN_NODE_URL`` (default
``http://localhost:8765``). ``execute``/``run`` default to ``--mode execute``;
pass ``--mode dry-run`` to preview without side effects.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _read_source(location: str) -> str:
    """Read a plan/glue source from a path or ``-`` (stdin)."""
    if location == "-":
        return sys.stdin.read()
    return Path(location).read_text(encoding="utf-8")


def _emit(obj: Any) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def _executor(args: argparse.Namespace):
    from urirun_llm_runtime.executor import Executor

    return Executor(args.node, timeout=args.timeout)


def _cmd_health(args: argparse.Namespace) -> int:
    _emit(_executor(args).health())
    return 0


def _cmd_routes(args: argparse.Namespace) -> int:
    _emit(_executor(args).routes())
    return 0


def _cmd_execute(args: argparse.Namespace) -> int:
    payload = json.loads(args.payload) if args.payload else None
    result = _executor(args).execute(args.uri, payload, mode=args.mode)
    _emit(result)
    return 0 if result.get("ok", True) else 1


def _cmd_run(args: argparse.Namespace) -> int:
    text = _read_source(args.source)
    results = _executor(args).execute_processes(text, stop_on_error=not args.keep_going)
    _emit(results)
    return 0 if all(r.get("ok", True) for r in results) else 1


def _cmd_validate(args: argparse.Namespace) -> int:
    from urirun_llm_runtime.process import parse_processes_block, validate_processes

    processes = parse_processes_block(_read_source(args.source))
    errors = validate_processes(processes)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1
    print(f"ok: {len(processes)} process(es) valid")
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    from urirun_llm_runtime.validator import lint_path, lint_tree

    target = Path(args.path)
    errors = lint_tree(target) if target.is_dir() else lint_path(target)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    print(f"ok: no anti-patterns in {target}")
    return 0


def _cmd_prompt(args: argparse.Namespace) -> int:
    from urirun_llm_runtime.llm_context import build_first_system_prompt

    print(build_first_system_prompt(ticket=args.ticket, max_chars=args.max_chars))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="urirun-llm", description=__doc__.splitlines()[0])
    parser.add_argument("--node", default=None, help="Node base URL (default: $URIRUN_NODE_URL or http://localhost:8765)")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds (default: 60)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="check node health").set_defaults(func=_cmd_health)
    sub.add_parser("routes", help="list node routes").set_defaults(func=_cmd_routes)

    p_exec = sub.add_parser("execute", help="execute a single URI")
    p_exec.add_argument("uri")
    p_exec.add_argument("--payload", help="JSON payload object")
    p_exec.add_argument("--mode", default="execute", choices=["execute", "dry-run"])
    p_exec.set_defaults(func=_cmd_execute)

    p_run = sub.add_parser("run", help="execute a urirun:processes plan from file or stdin")
    p_run.add_argument("source", help="path to a plan file, or '-' for stdin")
    p_run.add_argument("--keep-going", action="store_true", help="do not stop on the first failed step")
    p_run.set_defaults(func=_cmd_run)

    p_val = sub.add_parser("validate", help="parse and validate a plan without executing it")
    p_val.add_argument("source", help="path to a plan file, or '-' for stdin")
    p_val.set_defaults(func=_cmd_validate)

    p_lint = sub.add_parser("lint", help="check glue for banned subprocess/os anti-patterns")
    p_lint.add_argument("path", help="file or directory to lint")
    p_lint.set_defaults(func=_cmd_lint)

    p_prompt = sub.add_parser("prompt", help="print the first LLM system prompt")
    p_prompt.add_argument("--ticket", default="", help="ticket context to weave into the prompt")
    p_prompt.add_argument("--max-chars", type=int, default=24000)
    p_prompt.set_defaults(func=_cmd_prompt)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
