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
