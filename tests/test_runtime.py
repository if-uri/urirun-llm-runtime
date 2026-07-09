import base64
import io
import json
from pathlib import Path

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
        if isinstance(self.status, int) and self.status >= 400:
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


def test_execute_processes_with_dict_plan(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=0):
        calls.append((url, json, timeout))
        return DummyResp({"ok": True, "uri": json["uri"]})

    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post", fake_post)
    e = Executor("http://example:8765")
    plan = [
        {"id": "step-1", "name": "Step 1", "actor": "script", "uri": "kvm://host/diag/query/one", "payload": {"x": 1}},
        {"id": "step-2", "name": "Step 2", "actor": "script", "uri": "kvm://host/diag/query/two",
         "payload": {"y": 2}, "depends_on": ["step-1"]},
    ]
    results = e.execute_processes(plan)
    assert len(results) == 2
    assert results[0]["id"] == "step-1"
    assert results[1]["id"] == "step-2"
    assert calls[0][1]["uri"] == "kvm://host/diag/query/one"
    assert calls[1][1]["uri"] == "kvm://host/diag/query/two"


def test_execute_processes_with_block_string(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=0):
        calls.append((url, json, timeout))
        return DummyResp({"ok": True, "uri": json["uri"]})

    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post", fake_post)
    e = Executor("http://example:8765")
    block = '''```urirun:processes
[{
  "id": "step-1",
  "name": "Step 1",
  "actor": "script",
  "uri": "kvm://host/diag/query/one",
  "payload": {"x": 1}
}]
```'''
    results = e.execute_processes(block)
    assert len(results) == 1
    assert results[0]["id"] == "step-1"
    assert calls[0][1]["uri"] == "kvm://host/diag/query/one"


def _png_bytes(width, height, *, noise=False):
    from PIL import Image
    if noise:
        import os as _os
        im = Image.frombytes("RGB", (width, height), _os.urandom(width * height * 3))
    else:
        im = Image.new("RGB", (width, height), color=(80, 120, 200))
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def _capture_response(png_bytes, **extra):
    value = {"ok": True, "pngBase64": base64.b64encode(png_bytes).decode(), "path": "/tmp/shot.png"}
    value.update(extra)
    return DummyResp(json_data={"result": {"value": value}})


def test_capture_for_llm_passes_through_small_image(monkeypatch):
    png = _png_bytes(200, 100)

    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post",
                         lambda url, json=None, timeout=0: _capture_response(png))
    e = Executor("http://example:8765")
    out = e.capture_for_llm()
    assert out["ok"] is True
    assert out["mimeType"] == "image/png"
    assert out["resizedClientSide"] is False
    assert out["width"] == 200


def test_capture_for_llm_downscales_oversized_width(monkeypatch):
    png = _png_bytes(2560, 1440)

    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post",
                         lambda url, json=None, timeout=0: _capture_response(png))
    e = Executor("http://example:8765")
    out = e.capture_for_llm()
    assert out["ok"] is True
    assert out["resizedClientSide"] is True
    assert out["width"] <= 1280
    assert len(out["base64"]) < len(base64.b64encode(png).decode())


def test_capture_for_llm_falls_back_to_jpeg_when_still_too_big(monkeypatch):
    # Random noise near the width cap barely compresses as PNG — forces the byte-ceiling
    # fallback to JPEG even though no width resize was needed.
    png = _png_bytes(1280, 720, noise=True)
    assert len(png) > 400_000  # sanity: the fixture actually exercises the fallback

    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post",
                         lambda url, json=None, timeout=0: _capture_response(png))
    e = Executor("http://example:8765")
    out = e.capture_for_llm()
    assert out["ok"] is True
    assert out["mimeType"] == "image/jpeg"
    assert out["bytes"] <= 400_000
    assert out["resizedClientSide"] is True


def test_capture_for_llm_respects_env_override(monkeypatch):
    png = _png_bytes(2000, 1000)
    seen = {}

    def fake_post(url, json=None, timeout=0):
        seen["payload"] = json["payload"]
        return _capture_response(png)

    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post", fake_post)
    monkeypatch.setenv("URIRUN_LLM_SCREENSHOT_MAX_WIDTH", "640")
    e = Executor("http://example:8765")
    out = e.capture_for_llm()
    assert seen["payload"]["max_width"] == 640
    assert out["width"] <= 640


def test_capture_for_llm_reports_missing_base64(monkeypatch):
    monkeypatch.setattr(
        "urirun_llm_runtime.executor.requests.post",
        lambda url, json=None, timeout=0: DummyResp(json_data={"result": {"value": {"ok": True}}}),
    )
    e = Executor("http://example:8765")
    out = e.capture_for_llm()
    assert out["ok"] is False
    assert "pngBase64" in out["error"]


def test_capture_for_llm_degrades_gracefully_without_pillow(monkeypatch):
    # Pillow is an optional dependency (llm-vision extra) — simulate it being absent so this
    # runs the same in CI regardless of whether it happens to be installed, instead of needing
    # a second, Pillow-free install matrix just to exercise this one path.
    png = _png_bytes(2560, 1440)  # built BEFORE the patch below — the fixture itself needs PIL

    import builtins

    real_import = builtins.__import__

    def no_pil(name, *args, **kwargs):
        if name == "PIL" or name.startswith("PIL."):
            raise ImportError("simulated: Pillow not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_pil)
    monkeypatch.setattr("urirun_llm_runtime.executor.requests.post",
                         lambda url, json=None, timeout=0: _capture_response(png))
    e = Executor("http://example:8765")
    out = e.capture_for_llm()

    assert out["ok"] is True
    assert out["resizedClientSide"] is False  # no PIL to resize with — passed through as-is
    assert out["mimeType"] == "image/png"
    assert base64.b64decode(out["base64"]) == png


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


def test_route_schemas_lenovo_snapshot():
    path = Path(__file__).resolve().parents[1] / "docs" / "llm" / "route_schemas_lenovo.json"
    assert path.is_file(), "run scripts/snapshot_route_schemas.py to refresh"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("routeCount", 0) >= 10
    uris = {r["uri"] for r in data.get("routes", []) if r.get("uri")}
    assert "kvm://host/ui/command/type-verified" in uris
    tv = next(r for r in data["routes"] if r["uri"] == "kvm://host/ui/command/type-verified")
    props = (tv.get("inputSchema") or {}).get("properties") or {}
    assert "text" in props and "x" in props and "submit" in props


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
