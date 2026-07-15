# urirun-llm-runtime

Canonical **LLM-facing project** for the if-uri URI process execution runtime.

Repo: https://github.com/if-uri/urirun-llm-runtime

LLM clients should load this repository (or its raw docs) as project context so generated code uses `POST /run` with URI processes — never raw `subprocess` / GUI hacks.

## What this repo contains

| Path | Purpose |
|------|---------|
| `docs/llm/first_system_prompt.md` | Assembled system prompt (topology + routes + contract) |
| `docs/llm/runtime_semantics.md` | How `POST /run` works |
| `docs/llm/process_schema.json` | JSON Schema for `urirun:processes` blocks |
| `docs/openapi.yaml` | Transport API contract |
| `urirun_llm_runtime/` | Python executor, process runner, validators |
| `runtime/docker-compose.yml` | Real if-uri node (requires `if-uri` clone) |
| `docker/` | Lightweight mock node for offline CI |
| `.github/workflows/ci.yml` | **Blocking gates** — merge fails if any gate fails |

## LLM consumption (raw URLs)

```text
https://raw.githubusercontent.com/if-uri/urirun-llm-runtime/main/docs/llm/first_system_prompt.md
https://raw.githubusercontent.com/if-uri/urirun-llm-runtime/main/docs/llm/runtime_semantics.md
https://raw.githubusercontent.com/if-uri/urirun-llm-runtime/main/docs/llm/route_catalog.yaml
https://raw.githubusercontent.com/if-uri/urirun-llm-runtime/main/docs/openapi.yaml
```

Or in Python:

```python
from urirun_llm_runtime import build_first_system_prompt, docs_index
print(build_first_system_prompt())
print(docs_index())
```

## LLM output format

````markdown
```urirun:processes
[
  {
    "id": "step-1",
    "name": "Diagnose KVM",
    "actor": "script",
    "uri": "kvm://host/doctor/query/report",
    "payload": {},
    "depends_on": []
  }
]
```
````

## Glue code (allowed)

```python
from urirun_llm_runtime import Executor

def run(ctx=None):
    return Executor("http://host-node:8765").execute("kvm://host/env/query/profile")
```

## CLI

Installing the package provides a `urirun-llm` command (also `python -m urirun_llm_runtime`):

```bash
urirun-llm health                               # GET {node}/health
urirun-llm routes                               # GET {node}/routes
urirun-llm execute kvm://host/env/query/profile # POST {node}/run for one URI
urirun-llm run plan.json                         # execute a urirun:processes plan (file or -)
urirun-llm validate plan.json                    # parse + validate a plan, no execution
urirun-llm lint examples/glue                    # anti-subprocess CI gate over glue
urirun-llm prompt --ticket "check domains"       # print the first LLM system prompt
```

The node URL comes from `--node` or `$URIRUN_NODE_URL` (default `http://localhost:8765`).
`execute`/`run` default to `--mode execute`; pass `--mode dry-run` to preview.

## Local development

```bash
pip install -e ".[dev]"
python scripts/assemble_llm_prompt.py
pytest -q
python scripts/validate_examples.py
python scripts/validate_processes.py
```

### Mock runtime (no if-uri)

```bash
docker compose up -d --build urirun-mock
curl -sf http://127.0.0.1:8765/health
```

### Real runtime (if-uri monorepo)

```bash
git clone https://github.com/if-uri/if-uri ../if-uri   # sibling of this repo
echo "IF_URI_ROOT=../if-uri" > runtime/.env
docker compose -f runtime/docker-compose.yml up -d host-node
docker compose -f runtime/docker-compose.yml --profile smoke run --rm uri-smoke
```

## CI gates (blocking)

1. **unit-and-gates** — pytest, glue lint, process JSON schema, prompt artifact
2. **mock-runtime-smoke** — `POST /run` on mock node
3. **if-uri-runtime-smoke** — builds real if-uri `host-node`, runs URI smoke + live Executor

All three must pass on `main`.

## Related

- [if-uri](https://github.com/if-uri/if-uri) — monorepo with connectors and dashboard
- [markpact + marksync prompt](docs/markpact_marksync_prompt.md) — orchestration primitives
