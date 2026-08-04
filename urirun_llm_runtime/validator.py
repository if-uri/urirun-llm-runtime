"""CI gate: block anti-patterns in LLM-generated glue code."""
from __future__ import annotations

import ast
import re
from pathlib import Path

_BANNED_CALLS = frozenset({
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
    "os.system",
    "os.popen",
    "os.execv",
    "os.execve",
})

_BANNED_IMPORTS = frozenset({"subprocess"})

_URI_SCHEMES = re.compile(
    r"\b(kvm|shell|work|twin|signal-gui|marksync|markpact|router|gap|env|app|browser)://"
)


def _qualname(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _qualname(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


def _check_imports(node: ast.AST, path: str) -> list[str]:
    errors: list[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.split(".")[0] in _BANNED_IMPORTS:
                errors.append(f"{path}: banned import {alias.name}")
    elif isinstance(node, ast.ImportFrom):
        if node.module and node.module.split(".")[0] in _BANNED_IMPORTS:
            errors.append(f"{path}: banned import from {node.module}")
    return errors


def _check_call_node(node: ast.Call, path: str) -> tuple[list[str], bool]:
    errors: list[str] = []
    name = _qualname(node.func)
    if name in _BANNED_CALLS:
        errors.append(f"{path}: banned call {name} — use Executor.execute(uri)")
    has_uri = name in ("Executor.execute", "execute", "run_processes") or (
        isinstance(node.func, ast.Attribute) and node.func.attr in ("execute", "run_processes")
    )
    return errors, has_uri


def _check_node_for_run_uri(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute) and node.attr == "run_uri":
        return True
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if _URI_SCHEMES.search(node.value):
            return True
    return False


def lint_python_source(source: str, *, path: str = "<string>") -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        return [f"{path}: syntax error: {exc}"]

    has_run_uri = False
    for node in ast.walk(tree):
        errors.extend(_check_imports(node, path))
        if isinstance(node, ast.Call):
            call_errors, has_uri = _check_call_node(node, path)
            errors.extend(call_errors)
            if has_uri:
                has_run_uri = True
        if _check_node_for_run_uri(node):
            has_run_uri = True

    if "def run(" in source and not has_run_uri:
        errors.append(f"{path}: run(ctx) glue must call ctx.run_uri or contain URI literals")
    return errors


def lint_path(path: Path) -> list[str]:
    if path.suffix != ".py":
        return []
    return lint_python_source(path.read_text(encoding="utf-8"), path=str(path))


def lint_tree(root: Path) -> list[str]:
    errors: list[str] = []
    for py in sorted(root.rglob("*.py")):
        if ".pytest_cache" in py.parts or "__pycache__" in py.parts:
            continue
        errors.extend(lint_path(py))
    return errors
