# URI Runtime Semantics (LLM contract)

## Transport

Every external action goes through a running **urirun node**:

```http
POST {node_base_url}/run
Content-Type: application/json

{
  "uri": "kvm://host/doctor/query/report",
  "mode": "execute",
  "payload": {}
}
```

Response envelope:

```json
{
  "ok": true,
  "uri": "kvm://host/doctor/query/report",
  "result": { "type": "function-subprocess", "value": { "ok": true, ... } },
  "_meta": { "servedBy": "host", "ranOn": "host-node" }
}
```

## URI shape

`{scheme}://{target}/{package}/{resource}/{operation}`

| Part | Meaning |
|------|---------|
| `scheme` | Connector family: `kvm`, `twin`, `work`, `shell`, `router`, … |
| `target` | Logical node alias in that node's registry (`host`, `laptop`, …) |
| `package/resource/operation` | Route inside the connector |

**Critical:** `kvm://host/...` on lenovo means POST to lenovo's `/run`, not to dashboard.

## Layers

| Layer | Service | Port | Role |
|-------|---------|------|------|
| Control plane | `host-dashboard` | 8797 | Tickets, loop, koru, LLM orchestration |
| Execution node | `host-node` | 8765 | `POST /run` — real connector handlers |
| Bare-metal | `lenovo` | 8765 | Signal Desktop, real KVM/Wayland |

Inside Docker Compose network use DNS: `http://host-node:8765/run`.

## Process plan format

LLM output MUST include a fenced block:

````markdown
```urirun:processes
[
  {
    "id": "step-1",
    "name": "Diagnose environment",
    "actor": "script",
    "uri": "kvm://host/doctor/query/report",
    "payload": {},
    "depends_on": [],
    "human_approval": false
  }
]
```
````

## Desktop-GUI grounding (kvm) — verify BEFORE injection, not only after

Learned live from a Signal-Desktop E2E on `lenovo` (GNOME-Wayland): typing first and checking
afterward lets a wrong-window mistake actually happen before it's caught. Ground the target
first.

- **`window/query/list` and `window/command/focus` are BLIND to Electron/Flatpak windows on
  GNOME-Wayland** (atspi only sees gnome-shell/XWayland apps; `wmctrl` can't reach Wayland-native
  surfaces either). Signal Desktop, and apps like it, will not appear in the window list even
  while genuinely open and visible. **`screen/query/capture` is the only ground truth** for
  whether such an app is open/foreground — never conclude "not open" from an empty window list.
- **`window/command/focus` / `window/command/maximize` are fire-and-forget**: the underlying
  `wmctrl -a`/`-r` calls do NOT error when the title matches nothing. `ok:true` only means the
  command was dispatched, not that it landed — always read the response's `verify` field
  (`{trusted, verified/fullscreen, title}`) before trusting a focus/maximize call.
- **Prefer `task/command/run` with a leading `{op:"focus", title:"…"}` step** over raw
  `input/command/type`/`input/command/key`. That step auto-maximizes the window (skip with
  `fullscreen:false`) and every `type`/`key`/`click`/`move`/`scroll` step that follows in the
  SAME batch is re-gated against a live probe of window identity + fullscreen state — the whole
  task is refused (nothing is sent) if a TRUSTED probe shows the wrong window focused or a
  resized/un-maximized window, instead of only discovering the mistake after text already
  landed. `input/command/type`/`input/command/key` also take an optional `expect_window` (+
  `require_fullscreen`) for the same grounding outside a batch.
- **`trusted:false` (pure Wayland, no active-window query) is "unverifiable", not "pass"** — the
  guard degrades to best-effort in that case. Always follow with `kvm://host/ui/command/type-verified`
  or a `screen/query/capture` + `ui/query/verify` check before any irreversible next step.
- **The final outbound/destructive action (e.g. pressing Enter to send a message) is a genuine
  human action** — build the flow up to "typed + verified, ready to send" and stop there; do not
  self-approve the send step.

## Screenshots are multimodal, not text

A screenshot does **not** fit this system prompt's budget: one plain 1920×1080 PNG alone runs
to roughly 200K base64 characters — about 8x the ENTIRE 24K-char `build_first_system_prompt()`
budget, and `screen/query/capture`'s `pngBase64` field is never concatenated into it. Do not
paste base64 image data into a text prompt or a `urirun:processes` payload.

- Use `Executor.capture_for_llm(uri, payload)` (not a raw `execute("kvm://.../screen/query/capture")`
  call) when a screenshot needs to reach the LLM. It requests a server-side `max_width` downscale
  AND enforces the same cap client-side (some capture backends ignore `max_width` and return
  full resolution regardless — a documented "cold path" behavior of `urirun-connector-kvm`), plus
  a byte ceiling with a JPEG-quality fallback if a downscaled PNG is still too large.
- The result (`{mimeType, base64, width, height, ...}`) is meant to be attached as a **separate
  multimodal image content block** in the LLM API call — never inlined into
  `build_first_system_prompt()` or any other text field.
- Configurable via `.env` (see `.env.example`): `URIRUN_LLM_SCREENSHOT_MAX_WIDTH` (default 1280),
  `URIRUN_LLM_SCREENSHOT_MAX_BYTES` (default 400000).
- Without Pillow installed, the client-side safety net is skipped (the call still succeeds,
  just may return whatever size the node sent) — install the `llm-vision` extra
  (`pip install urirun-llm-runtime[llm-vision]`) for the size guarantee.

## Glue code (Python)

Allowed pattern only:

```python
from urirun_llm_runtime import Executor

def run(ctx=None):
    e = Executor("http://host-node:8765")
    return e.execute("kvm://host/env/query/profile")
```

Forbidden: `subprocess`, `os.system`, direct GUI automation libraries.

## CI blocking

This repo's CI rejects examples that bypass URI runtime. Merge is blocked until gates pass.
