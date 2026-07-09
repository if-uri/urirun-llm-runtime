# URIRUN LLM Runtime — Minimal Runtime Spec

This file describes the canonical runtime contract that LLMs should target when generating code that executes "URI processes" in the ifURI ecosystem.

1) Execution endpoint

- POST {node}/run
- Request JSON: { "uri": "kvm://laptop/diag/query/which", "payload": { ... } }
- Response JSON: arbitrary result object; success convention: { "ok": true, ... }

2) Semantic guarantees

- The runtime SHALL interpret `uri` as a single atomic step: query vs command vs metadata as encoded by scheme and path.
- The runtime SHOULD return `ok: true` on successful execution and include `via`/`action` details where applicable.

3) Security

- Hosts may require `URIRUN_NODE_TOKEN` or similar to authenticate POST /run. Clients SHOULD support sending tokens via HTTP headers `Authorization: Bearer <TOKEN>`.

4) LLM integration

- When synthesizing code that performs actions, the LLM should prefer constructing URIs and calling the runtime endpoint instead of shelling out or calling OS-level subprocesses.
