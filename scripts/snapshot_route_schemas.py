#!/usr/bin/env python3
"""Snapshot GET /routes from execution node → docs/llm/route_schemas_{node}.json.

CI uses the committed snapshot offline; refresh before lenovo connector deploys:
  URIRUN_LENOVO_URL=http://192.168.188.201:8765 python scripts/snapshot_route_schemas.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "llm"

# Routes that must exist on lenovo for Signal E2E / IFURI-059
_REQUIRED_URIS = (
    "kvm://host/ui/command/type-verified",
    "kvm://host/ui/query/verify",
    "kvm://host/input/command/type",
    "app://host/desktop/command/launch",
)


def _fetch_routes(base_url: str) -> list[dict]:
    base = base_url.rstrip("/")
    for path in ("/routes", "/api/routes"):
        try:
            with urllib.request.urlopen(f"{base}{path}", timeout=12) as resp:  # noqa: S310
                data = json.loads(resp.read().decode())
                routes = data.get("routes", data)
                if isinstance(routes, dict):
                    routes = list(routes.values())
                if isinstance(routes, list):
                    return [r for r in routes if isinstance(r, dict) and r.get("uri")]
        except Exception:
            continue
    return []


def _slim_route(route: dict) -> dict:
    return {
        "uri": route.get("uri"),
        "title": route.get("title"),
        "effect": route.get("effect"),
        "safe": route.get("safe"),
        "kind": route.get("kind"),
        "inputSchema": route.get("inputSchema") or {},
    }


def snapshot(node: str = "lenovo", *, base_url: str = "") -> Path:
    env_key = f"URIRUN_{node.upper()}_URL"
    url = (base_url or os.environ.get(env_key) or os.environ.get("URIRUN_LENOVO_URL", "")).strip()
    if not url:
        raise SystemExit(f"Set {env_key} or URIRUN_LENOVO_URL")
    routes = _fetch_routes(url)
    if not routes:
        raise SystemExit(f"No routes from {url}")
    slim = [_slim_route(r) for r in sorted(routes, key=lambda x: str(x.get("uri", "")))]
    out = {
        "source": f"{url.rstrip('/')}/routes",
        "node": node,
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "routeCount": len(slim),
        "routes": slim,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"route_schemas_{node}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _check_required_uris(uris: set[str]) -> list[str]:
    return [f"required URI missing: {req}" for req in _REQUIRED_URIS if req not in uris]


def _check_type_verified(routes: list[dict]) -> list[str]:
    tv = next((r for r in routes if isinstance(r, dict) and r.get("uri") == "kvm://host/ui/command/type-verified"), None)
    if not tv:
        return []
    props = (tv.get("inputSchema") or {}).get("properties") or {}
    fields = ("text", "x", "y", "submit", "draft_expect")
    return [f"type-verified missing inputSchema property: {field}" for field in fields if field not in props]


def validate_snapshot(path: Path) -> list[str]:
    if not path.is_file():
        return [f"missing {path}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    routes = data.get("routes") or []
    if not routes:
        return ["routes array empty"]
    uris = {str(r.get("uri")) for r in routes if isinstance(r, dict)}
    return _check_required_uris(uris) + _check_type_verified(routes)


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    node = (argv[0] if argv else os.environ.get("URIRUN_SNAPSHOT_NODE", "lenovo")).strip()
    if "--validate-only" in sys.argv:
        path = OUT_DIR / f"route_schemas_{node}.json"
        errs = validate_snapshot(path)
        if errs:
            print("\n".join(errs), file=sys.stderr)
            return 1
        print(f"OK {path} ({json.loads(path.read_text())['routeCount']} routes)")
        return 0
    path = snapshot(node)
    errs = validate_snapshot(path)
    print(f"wrote {path} ({json.loads(path.read_text())['routeCount']} routes)")
    if errs:
        print("WARN:", "; ".join(errs), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
