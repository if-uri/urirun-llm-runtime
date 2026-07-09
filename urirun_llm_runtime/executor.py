import json
from typing import Any, Dict, Optional

import requests


class Executor:
    """Simple HTTP executor for URI processes.

    It POSTs JSON to the node's `/run` endpoint with the `uri` key and optional
    `payload` (dictionary). Returns the parsed JSON response or raises on HTTP error.
    """

    def __init__(self, node_url: str = "http://localhost:8765") -> None:
        self.node_url = node_url.rstrip("/")

    def execute(self, uri: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Dict[str, Any]:
        body = {"uri": uri, "payload": payload or {}}
        url = f"{self.node_url}/run"
        resp = requests.post(url, json=body, timeout=timeout)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {"ok": True, "raw": resp.text}
