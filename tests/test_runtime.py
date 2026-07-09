import json
from pathlib import Path

import pytest

from urirun_llm_runtime.executor import Executor
from urirun_llm_runtime.llm_context import build_first_system_prompt, docs_index
from urirun_llm_runtime.process import (
    UriProcess,
    parse_processes_block,
    topological_order,
    validate_processes,
)
from urirun_llm_runtime.validator import lint_python_source


class DummyResp:
    def __init__(self, status=200, json_data=None, text="ok"):
        self.status = status
        self._json = json_data or {"ok": True}
        self.text = text

    def raise_for_status(self):
        if self.status >= 400:
            raise Exception(f"HTTP {self.status}")

    def json(self):
        return self._json


def test_execute_posts(monkeypatch):
    calls = {}

    def fake_post(url, json=None, timeout=0):
        calls["url"] = url
        calls["json"] = json
        return DummyResp()

    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post", fake_post)
    e = Executor("http://example:8765")
    res = e.execute("kvm://host/doctor/query/report")
    assert res.get("ok") is True
    assert calls["url"].endswith("/run")
    assert calls["json"]["uri"] == "kvm://host/doctor/query/report"
    assert calls["json"]["mode"] == "execute"


def test_parse_processes_block():
    text = '''```urirun:processes
[{"id":"a","name":"A","actor":"script","uri":"kvm://host/env/query/profile","payload":{}}]
```'''
    procs = parse_processes_block(text)
    assert len(procs) == 1
    assert procs[0].id == "a"


def test_validate_processes_deps():
    procs = [
        UriProcess("b", "B", "script", "kvm://host/env/query/profile", depends_on=["a"]),
        UriProcess("a", "A", "script", "kvm://host/doctor/query/report"),
    ]
    assert validate_processes(procs) == []


def test_topological_order():
    procs = [
        UriProcess("b", "B", "script", "kvm://host/env/query/profile", depends_on=["a"]),
        UriProcess("a", "A", "script", "kvm://host/doctor/query/report"),
    ]
    order = [p.id for p in topological_order(procs)]
    assert order == ["a", "b"]


def test_lint_bans_subprocess():
    bad = "import subprocess\nsubprocess.run(['date'])"
    errs = lint_python_source(bad)
    assert any("subprocess" in e for e in errs)


def test_lint_allows_executor():
    good = (
        "from urirun_llm_runtime import Executor\n"
        "def run(ctx):\n"
        "    return Executor('http://x').execute('kvm://host/env/query/profile')\n"
    )
    assert lint_python_source(good) == []


def test_first_system_prompt_nonempty():
    prompt = build_first_system_prompt()
    assert "URI RUNTIME" in prompt
    assert "kvm://host" in prompt
    assert len(prompt) > 500


def test_docs_index_urls():
    idx = docs_index()
    assert "openapi" in idx
    assert idx["openapi"].startswith("https://")


def test_example_process_json_valid():
    path = Path(__file__).resolve().parents[1] / "examples" / "processes" / "smoke_diagnostic.json"
    data = json.loads(path.read_text())
    procs = [UriProcess(
        item["id"], item["name"], item["actor"], item["uri"],
        payload=item.get("payload") or {},
        depends_on=item.get("depends_on") or [],
    ) for item in data]
    assert validate_processes(procs) == []
