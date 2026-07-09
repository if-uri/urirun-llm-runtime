<!--
This example file shows a concrete LLM output format for the markpact/marksync
runtime prompt. It contains a single `urirun:processes` code block with a
JSON array of process descriptions that can be executed by the urirun runtime.
-->

# Example: markpact + marksync process sequence

Goal: Build a TODO API with FastAPI and SQLite, validate it, sync it to marksync,
and run it inside a Docker-enabled runtime.

Output format: a single fenced code block labeled `urirun:processes`.

```urirun:processes
[
  {
    "id": "generate-todo-contract",
    "name": "Generate markpact contract for TODO API",
    "actor": "llm",
    "uri": "work://llm/generate/markpact-contract",
    "payload": {
      "prompt": "Generate a markpact README for a FastAPI TODO API backed by SQLite and Docker deployment. Include dependencies, file layout, and a run command."
    },
    "depends_on": [],
    "human_approval": false,
    "timeout_seconds": 300,
    "retries": 1
  },
  {
    "id": "validate-contract",
    "name": "Validate generated markpact contract",
    "actor": "script",
    "uri": "markpact://local/validate",
    "payload": {
      "contract_path": "generated/todo/README.md"
    },
    "depends_on": ["generate-todo-contract"],
    "human_approval": false,
    "timeout_seconds": 120,
    "retries": 1
  },
  {
    "id": "sync-contract",
    "name": "Sync README contract to marksync server",
    "actor": "script",
    "uri": "marksync://sync-server/push",
    "payload": {
      "contract_path": "generated/todo/README.md",
      "server_uri": "ws://localhost:8765"
    },
    "depends_on": ["validate-contract"],
    "human_approval": false,
    "timeout_seconds": 120,
    "retries": 1
  },
  {
    "id": "run-markpact",
    "name": "Run markpact on the generated TODO API contract",
    "actor": "script",
    "uri": "markpact://local/run",
    "payload": {
      "contract_path": "generated/todo/README.md",
      "docker": true
    },
    "depends_on": ["sync-contract"],
    "human_approval": false,
    "timeout_seconds": 600,
    "retries": 1
  },
  {
    "id": "review-deployment",
    "name": "Human review deployment and approve production push",
    "actor": "human",
    "uri": "work://human/review/approve",
    "payload": {
      "summary": "Inspect generated TODO API project and approve deployment to Docker."
    },
    "depends_on": ["run-markpact"],
    "human_approval": true,
    "timeout_seconds": 3600,
    "retries": 0
  }
]
```

This example demonstrates:

- `work://` for LLM generation and human review orchestration
- `markpact://` for validating and running generated README contracts
- `marksync://` for syncing contract state into a sync server
- Separate `actor` values for `llm`, `script`, and `human`
- Clear dependencies and timeouts per step
