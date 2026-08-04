"""URI process list — parse, validate, execute urirun:processes blocks."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from urirun_llm_runtime.executor import Executor

_PROCESS_BLOCK = re.compile(
    r"```urirun:processes\s*\n(.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)

_ALLOWED_ACTORS = frozenset({"llm", "script", "human", "system"})
_URI_RE = re.compile(r"^[a-z][a-z0-9+.-]*://[^/\s]+/.+")


@dataclass
class UriProcess:
    id: str
    name: str
    actor: str
    uri: str
    payload: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    human_approval: bool = False
    timeout_seconds: int | None = None
    retries: int = 0

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "actor": self.actor,
            "uri": self.uri,
            "payload": self.payload,
            "depends_on": list(self.depends_on),
            "human_approval": self.human_approval,
        }
        if self.timeout_seconds is not None:
            out["timeout_seconds"] = self.timeout_seconds
        if self.retries:
            out["retries"] = self.retries
        return out


def parse_processes_block(text: str) -> list[UriProcess]:
    match = _PROCESS_BLOCK.search(text)
    raw = match.group(1) if match else text.strip()
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("urirun:processes must be a JSON array")
    return [from_dict(item) for item in data]


def from_dict(item: dict[str, Any]) -> UriProcess:
    return UriProcess(
        id=str(item["id"]),
        name=str(item.get("name") or item["id"]),
        actor=str(item.get("actor") or "script"),
        uri=str(item["uri"]),
        payload=dict(item.get("payload") or {}),
        depends_on=[str(x) for x in (item.get("depends_on") or [])],
        human_approval=bool(item.get("human_approval")),
        timeout_seconds=item.get("timeout_seconds"),
        retries=int(item.get("retries") or 0),
    )


def _validate_process_fields(proc: UriProcess, seen: set[str]) -> list[str]:
    errors: list[str] = []
    if not proc.id:
        return ["process missing id"]
    if proc.id in seen:
        errors.append(f"duplicate id: {proc.id}")
    seen.add(proc.id)
    if proc.actor not in _ALLOWED_ACTORS:
        errors.append(f"{proc.id}: invalid actor {proc.actor!r}")
    if not _URI_RE.match(proc.uri):
        errors.append(f"{proc.id}: invalid uri {proc.uri!r}")
    return errors


def _validate_process_dependencies(processes: list[UriProcess]) -> list[str]:
    ids = {p.id for p in processes}
    errors: list[str] = []
    for proc in processes:
        for dep in proc.depends_on:
            if dep not in ids:
                errors.append(f"{proc.id}: unknown depends_on {dep!r}")
    return errors


def validate_processes(processes: list[UriProcess]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for proc in processes:
        errors.extend(_validate_process_fields(proc, seen))
    errors.extend(_validate_process_dependencies(processes))
    if not errors:
        try:
            topological_order(processes)
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def topological_order(processes: list[UriProcess]) -> list[UriProcess]:
    by_id = {p.id: p for p in processes}
    order: list[UriProcess] = []
    done: set[str] = set()
    visiting: list[str] = []

    def visit(pid: str) -> None:
        if pid in done:
            return
        if pid in visiting:
            cycle = visiting[visiting.index(pid):] + [pid]
            raise ValueError("dependency cycle: " + " -> ".join(cycle))
        visiting.append(pid)
        proc = by_id[pid]
        for dep in proc.depends_on:
            visit(dep)
        visiting.pop()
        done.add(pid)
        order.append(proc)

    for proc in processes:
        visit(proc.id)
    return order


def run_processes(
    executor: Executor,
    processes: list[UriProcess],
    *,
    stop_on_error: bool = True,
) -> list[dict[str, Any]]:
    errors = validate_processes(processes)
    if errors:
        raise ValueError("invalid processes: " + "; ".join(errors))
    results: list[dict[str, Any]] = []
    for proc in topological_order(processes):
        if proc.human_approval:
            results.append({"id": proc.id, "skipped": True, "reason": "human_approval"})
            continue
        attempt = 0
        last: dict[str, Any] = {}
        while attempt <= proc.retries:
            timeout = proc.timeout_seconds or executor.timeout
            old_timeout = executor.timeout
            executor.timeout = timeout
            try:
                last = executor.execute(proc.uri, proc.payload)
            finally:
                executor.timeout = old_timeout
            if last.get("ok", True) is not False and not last.get("error"):
                break
            attempt += 1
        entry = {"id": proc.id, "uri": proc.uri, "result": last}
        results.append(entry)
        if stop_on_error and (last.get("ok") is False or last.get("error")):
            break
    return results
