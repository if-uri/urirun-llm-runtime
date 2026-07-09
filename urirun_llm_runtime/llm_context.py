"""Assemble first-system prompt for LLM from bundled docs."""
from __future__ import annotations

from pathlib import Path

_PKG = Path(__file__).resolve().parent
_DOCS = _PKG.parent / "docs" / "llm"

_ROLE = """\
Jesteś executorem automatyzacji IF-URI. Działasz W ŚRODOWISKU URI RUNTIME.

**Zasady:**
1. Każda akcja = URI proces: `scheme://target/path` + JSON payload.
2. Dispatch: POST {node_base_url}/run → {"uri":"...", "mode":"execute", "payload":{...}}.
3. Segment `host` w kvm://host/... to alias węzła (URIRUN_KVM_URI_HOST), nie hostname kontenera.
4. Plan = lista kroków w bloku ```urirun:processes``` (JSON) lub `def run(ctx): ctx.run_uri(...)`.
5. Python = tylko cienki glue; NIE zastępuj URI subprocess/os.system.
6. Przed keyboard/HID: router://host/plan/query/diagnose; po mutacji: kvm://host/ui/query/verify.
"""


def _read(name: str) -> str:
    path = _DOCS / name
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def build_first_system_prompt(*, ticket: str = "", max_chars: int = 24000) -> str:
    parts = [
        _ROLE,
        "",
        _read("runtime_semantics.md"),
        "",
        _read("environment_topology.yaml"),
        "",
        _read("route_catalog.yaml"),
        "",
        _read("process_contract.md"),
    ]
    if ticket:
        parts.extend(["", "**TICKET:**", ticket.strip()])
    text = "\n".join(p for p in parts if p)
    if len(text) > max_chars:
        return text[: max_chars - 80] + "\n\n…(truncated; see docs/llm/ in urirun-llm-runtime repo)"
    return text


def docs_index() -> dict[str, str]:
    """Paths LLM clients should fetch (raw GitHub URLs)."""
    base = "https://raw.githubusercontent.com/if-uri/urirun-llm-runtime/main/docs/llm"
    return {
        "first_system_prompt": f"{base}/first_system_prompt.md",
        "runtime_semantics": f"{base}/runtime_semantics.md",
        "environment_topology": f"{base}/environment_topology.yaml",
        "route_catalog": f"{base}/route_catalog.yaml",
        "process_schema": f"{base}/process_schema.json",
        "openapi": "https://raw.githubusercontent.com/if-uri/urirun-llm-runtime/main/docs/openapi.yaml",
    }
