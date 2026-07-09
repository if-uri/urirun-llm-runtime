import pytest

from urirun_llm_runtime.executor import Executor


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
        calls['url'] = url
        calls['json'] = json
        return DummyResp()

    monkeypatch.setattr('urirun_llm_runtime.executor.requests.post', fake_post)
    e = Executor('http://example:8765')
    res = e.execute('kvm://laptop/diag/query/which')
    assert res.get('ok') is True
    assert calls['url'].endswith('/run')
    assert calls['json']['uri'] == 'kvm://laptop/diag/query/which'


def test_examples_importable():
    # Ensure example scripts import runtime without side-effects
    import importlib.util
    from pathlib import Path
    base = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('example_kvm_diag',
                                                  str(base / 'examples' / 'example_kvm_diag.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
