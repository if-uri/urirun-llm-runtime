"""HTTP executor for URI processes — POST {node}/run."""
from __future__ import annotations

import base64
import io
import json
import os
from typing import Any

from dotenv import load_dotenv
import requests

load_dotenv()

# A screenshot is a MULTIMODAL artifact, never text: one plain 1920x1080 PNG alone runs to
# ~200K base64 chars — ~8x the ENTIRE 24K-char first_system_prompt() budget (see
# docs/llm/runtime_semantics.md "Screenshots are multimodal, not text"). These bound what
# capture_for_llm() returns; override per-deployment via .env (see .env.example).
_DEFAULT_SCREENSHOT_MAX_WIDTH = 1280
_DEFAULT_SCREENSHOT_MAX_BYTES = 400_000


def _screenshot_limits() -> tuple[int, int]:
    max_width = int(os.environ.get("URIRUN_LLM_SCREENSHOT_MAX_WIDTH", _DEFAULT_SCREENSHOT_MAX_WIDTH))
    max_bytes = int(os.environ.get("URIRUN_LLM_SCREENSHOT_MAX_BYTES", _DEFAULT_SCREENSHOT_MAX_BYTES))
    return max_width, max_bytes


def _downscale_for_llm(raw: bytes, max_width: int, max_bytes: int) -> tuple[bytes, str, int, int, bool]:
    """Best-effort client-side safety net: the node was ASKED to downscale (max_width in the
    payload) but some capture backends silently ignore it — a "cold" (non-warmed) capture path
    returns full resolution regardless (see urirun-connector-kvm core.py capture()). Returns
    (bytes, mime_type, width, height, resized). Never raises: without Pillow installed, returns
    the input unchanged (resized=False) — the caller still gets an image, just a bigger one."""
    try:
        from PIL import Image
    except ImportError:
        return raw, "image/png", 0, 0, False

    im = Image.open(io.BytesIO(raw))
    im.load()
    resized = False
    if im.width > max_width:
        ratio = max_width / im.width
        im = im.resize((max_width, max(1, round(im.height * ratio))))
        resized = True

    def _encode(fmt: str, quality: int | None = None) -> bytes:
        buf = io.BytesIO()
        if fmt == "JPEG":
            im.convert("RGB").save(buf, format="JPEG", quality=quality or 85)
        else:
            im.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    out, mime = _encode("PNG"), "image/png"
    if len(out) > max_bytes:
        resized = True
        for quality in (85, 70, 55, 40):
            out, mime = _encode("JPEG", quality), "image/jpeg"
            if len(out) <= max_bytes:
                break
    return out, mime, im.width, im.height, resized


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

    def execute_processes(
        self,
        processes: list[dict[str, Any]] | str,
        *,
        stop_on_error: bool = True,
    ) -> list[dict[str, Any]]:
        """Execute a composed URI process plan on the node via POST /run steps."""
        from urirun_llm_runtime.process import UriProcess, from_dict, parse_processes_block, run_processes

        if isinstance(processes, str):
            processes = parse_processes_block(processes)
        if not isinstance(processes, list):
            raise TypeError("processes must be a list of process dicts or a urirun:processes block string")

        items: list[UriProcess] = []
        for item in processes:
            if isinstance(item, UriProcess):
                items.append(item)
            elif isinstance(item, dict):
                items.append(from_dict(item))
            else:
                raise TypeError("each process must be a dict or UriProcess instance")
        return run_processes(self, items, stop_on_error=stop_on_error)

    def capture_for_llm(
        self,
        uri: str = "kvm://host/screen/query/capture",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Capture a screenshot SIZED FOR MULTIMODAL LLM INPUT.

        Never inline the result into build_first_system_prompt() or any text prompt — attach
        ``base64``/``mimeType`` as a SEPARATE image content block in the LLM API call instead
        (see docs/llm/runtime_semantics.md "Screenshots are multimodal, not text").

        Requests ``max_width`` from the node (cheap server-side downscale), then enforces the
        SAME cap client-side as a safety net, because some capture backends ignore it and
        return full resolution anyway. Also enforces a byte ceiling, falling back to JPEG at
        decreasing quality if a downscaled PNG is still too large.

        Config (see .env.example): ``URIRUN_LLM_SCREENSHOT_MAX_WIDTH`` (default 1280),
        ``URIRUN_LLM_SCREENSHOT_MAX_BYTES`` (default 400000).
        """
        max_width, max_bytes = _screenshot_limits()
        body = dict(payload or {})
        body.setdefault("max_width", max_width)
        body.setdefault("base64", True)
        resp = self.execute(uri, body)
        result = resp.get("result")
        value = result.get("value", result) if isinstance(result, dict) else resp
        if not isinstance(value, dict) or value.get("ok") is False:
            err = value.get("error") if isinstance(value, dict) else None
            return {"ok": False, "error": err or "capture failed", "raw": resp}
        b64 = value.get("pngBase64")
        if not b64:
            return {"ok": False, "error": "capture response has no pngBase64 (pass base64=true)", "raw": resp}
        raw = base64.b64decode(b64)
        out_bytes, mime, width, height, resized = _downscale_for_llm(raw, max_width, max_bytes)
        return {
            "ok": True,
            "mimeType": mime,
            "base64": base64.b64encode(out_bytes).decode(),
            "bytes": len(out_bytes),
            "width": width or value.get("width"),
            "height": height or value.get("height"),
            "resizedClientSide": resized,
            "sourceBytes": len(raw),
            "path": value.get("path"),
        }

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
