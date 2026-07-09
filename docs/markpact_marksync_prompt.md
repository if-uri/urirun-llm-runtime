<!--
This file is generated from local repos:
 - /home/tom/github/markpact/markpact
 - /home/tom/github/markpact/marksync

It is intended to be provided as a single prompt artifact for an LLM so the
model can produce a sequence of URI-based processes (the `urirun` runtime
contract) to realize a requested task.
-->

# markpact + marksync — LLM Prompt Summary

Purpose
- `markpact`: executable README runtime. Generate projects and run codeblocks
  `markpact:*` from a single README.md. Supports `markpact:bootstrap`, `markpact:deps`,
  `markpact:file`, `markpact:run` and run in sandbox/docker.
- `marksync`: multi-agent CRDT sync + orchestrator. Provides DSL, agents, pipelines,
  WebSocket sync server and REST/WS API for coordinating LLM/script/human steps.

Key local commands (representative)
- `markpact -p "PROMPT" -o out/README.md --run` — generate & run project from prompt
- `markpact sync README.md --check` — ensure files match README contract
- `marksync orchestrate -c agents.yml` — run agents per `agents.yml`
- `marksync server README.md` — start sync server (WS hub)

What the LLM must produce
- A single Markdown (or JSON) document that encodes an ordered list of processes
  to execute using the `urirun` runtime contract (POST /run with `{uri,payload}`).
- Each process item MUST include these fields:
  - `id` (string): stable identifier
  - `name` (string): human readable name
  - `actor` (one of: `llm`, `script`, `human`, `system`)
  - `uri` (string): the URI to execute (scheme://host/path[/action])
  - `payload` (object): optional JSON payload for the URI
  - `depends_on` (array of ids): optional dependencies
  - `human_approval` (bool): whether to pause for human approval
  - `timeout_seconds` (int): optional per-step timeout
  - `retries` (int): optional retry count

Format requirements
- Primary output MUST be a fenced code block labeled `urirun:processes` containing
  a single JSON array of process objects. Example:

```urirun:processes
[
  {
    "id": "step-1-generate-contract",
    "name": "Generate project contract README",
    "actor": "llm",
    "uri": "work://llm/generate/markpact-contract",
    "payload": {"prompt": "Create a todo API with FastAPI and SQLite"},
    "depends_on": [],
    "human_approval": false,
    "timeout_seconds": 300,
    "retries": 1
  },
  {
    "id": "step-2-sync",
    "name": "Sync generated README to sync server",
    "actor": "script",
    "uri": "marksync://sync-server/push",
    "payload": {"contract_path": "generated/README.md"},
    "depends_on": ["step-1-generate-contract"],
    "human_approval": false
  }
]
```

Guidance for URI schemes (suggested mapping)
- `kvm://host/...` — actions on a remote desktop via KVM (capture, focus, type)
- `shell://host/command/...` — run a shell command on node
- `work://service/action` — internal orchestrator actions (generate, validate)
- `marksync://sync-server/push` — push contract to marksync sync-server
- `markpact://local/run` — run markpact on generated README

Operational constraints
- Prefer `work://` or `marksync://` calls for code-generation and orchestration steps.
- Use `kvm://` only when GUI automation is required and a KVM target is available.
- Avoid direct `subprocess` or `shell` calls from LLM unless wrapped by a runtime URI.

Example LLM prompt wrapper (supply this whole file as context):

"""
You are given the following project runtime primitives (markpact + marksync).
Produce a sequence of URI processes (JSON array, see format) that will achieve
the user goal: <USER_GOAL_HERE>. Ensure dependencies and human approvals are
explicit. Output ONLY the `urirun:processes` code block containing the JSON.
"""

Notes / References
- markpact README: `/home/tom/github/markpact/markpact/README.md`
- marksync README: `/home/tom/github/markpact/marksync/README.md`
