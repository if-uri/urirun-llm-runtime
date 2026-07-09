# urirun-llm-runtime

This repository contains a minimal runtime library and spec for executing "URI processes" in the ifURI ecosystem. The goal is to provide a canonical runtime description and a small HTTP executor library that LLMs can target when producing code that runs tasks via `kvm://`, `app://`, `shell://`, `work://` and other URI schemes.

It also includes a CI workflow that runs tests to ensure the runtime is stable and examples follow the URI-driven execution model.

Key parts:

- `urirun_llm_runtime/executor.py` — an HTTP-based executor that talks to a running node's `/run` endpoint and executes a URI.
- `docs/spec.md` — a concise machine-readable description of the runtime semantics for LLM consumption.
- `.github/workflows/ci.yml` — runs tests on each push and pull request.

Usage example (from host machine):

```bash
python -c "from urirun_llm_runtime.executor import Executor; e=Executor('http://192.168.188.201:8765'); print(e.execute('kvm://laptop/diag/query/which'))"
```
Docker / LLM usage
------------------

Run a lightweight mock runtime in Docker Compose (useful for local LLM testing):

```bash
cd urirun-llm-runtime
docker compose up --build
```

LLMs should fetch the OpenAPI spec at `/docs/openapi.yaml` (or the raw file in the repo)
and generate code that posts to `/run` with JSON `{ "uri": "...", "payload": {...} }`.

The repository includes a mock service at `docker/app.py` that simulates responses.

CI enforces that examples/flows adopt URI-based execution patterns by running repository-level checks.
