"""HTTP executor for URI processes — POST {node}/run."""
from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
import requests

load_dotenv()


class Executor:
    """Execute atomic URI steps on a running urirun node."""

    def __init__(self, node_url: str | None = None, *, timeout: int = 60) -> None:
        url = node_url or os.environ.get("URIRUN_NODE_URL") or "http://localhost:8765"
        self.node_url = url.rstrip("/")
        self.timeout = timeout

    def health(self) -> dict[str, Any]:
        resp = requests.get(f"{self.node_url}/health", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def execute(
        self,
        uri: str,
        payload: dict[str, Any] | None = None,
        *,
        mode: str = "execute",
    ) -> dict[str, Any]:
        body = {"uri": uri, "mode": mode, "payload": payload or {}}
        resp = requests.post(f"{self.node_url}/run", json=body, timeout=self.timeout)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {"ok": True, "raw": resp.text}

    def routes(self) -> list[str]:
        resp = requests.get(f"{self.node_url}/routes", timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("routes", data.get("items", []))
        out: list[str] = []
        for item in items:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                u = item.get("uri") or item.get("path")
                if u:
                    out.append(str(u))
        return out
