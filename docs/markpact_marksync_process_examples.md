<!--
This file contains realistic prompt examples and the expected `urirun:processes`
output that an LLM should produce when asked to solve specific tasks using the
markpact/marksync + urirun runtime contract.
-->

# markpact / marksync — LLM process examples

## Example 1: Build and deploy a Flask blog app with Docker

Prompt:

"""
You are an assistant that generates executable URI process plans for the
`urirun` runtime. The target environment supports `markpact` for contract-based
project generation and `marksync` for syncing projects into a live orchestration
server. Produce only a single JSON array inside a fenced code block labeled
`urirun:processes`.

Task: Generate a Flask blog application, package it with Docker support,
validate the generated contract, sync it to the marksync server, and run the
build in a Docker-enabled runtime.

Constraints:
- Use `work://` for project generation and review orchestration.
- Use `markpact://` for validation and runtime execution.
- Use `marksync://` for syncing contract state.
- Include clear dependencies and human approval where deployment risk exists.
"""

Result:

```urirun:processes
[
  {
    "id": "generate-flask-blog",
    "name": "Generate Flask blog markpact contract",
    "actor": "llm",
    "uri": "work://llm/generate/markpact-contract",
    "payload": {
      "prompt": "Create a markpact README for a Flask blog application with Docker support, SQLite storage, and a simple admin editor. Include dependencies, Dockerfile, and a runtime command."
    },
    "depends_on": [],
    "human_approval": false,
    "timeout_seconds": 420,
    "retries": 1
  },
  {
    "id": "validate-flask-blog",
    "name": "Validate generated Flask blog contract",
    "actor": "script",
    "uri": "markpact://local/validate",
    "payload": {
      "contract_path": "generated/flask-blog/README.md"
    },
    "depends_on": ["generate-flask-blog"],
    "human_approval": false,
    "timeout_seconds": 180,
    "retries": 1
  },
  {
    "id": "sync-flask-blog",
    "name": "Sync Flask blog contract to marksync server",
    "actor": "script",
    "uri": "marksync://sync-server/push",
    "payload": {
      "contract_path": "generated/flask-blog/README.md",
      "server_uri": "ws://localhost:8765"
    },
    "depends_on": ["validate-flask-blog"],
    "human_approval": false,
    "timeout_seconds": 120,
    "retries": 1
  },
  {
    "id": "run-flask-blog-docker",
    "name": "Run Flask blog contract in Docker runtime",
    "actor": "script",
    "uri": "markpact://local/run",
    "payload": {
      "contract_path": "generated/flask-blog/README.md",
      "docker": true
    },
    "depends_on": ["sync-flask-blog"],
    "human_approval": false,
    "timeout_seconds": 600,
    "retries": 2
  },
  {
    "id": "approve-production-blog",
    "name": "Human review and approve production deployment",
    "actor": "human",
    "uri": "work://human/review/approve",
    "payload": {
      "summary": "Review the Flask blog project and approve the Docker deployment to production."
    },
    "depends_on": ["run-flask-blog-docker"],
    "human_approval": true,
    "timeout_seconds": 3600,
    "retries": 0
  }
]
```

## Example 2: Generate an automation plan for KVM-based desktop messaging

Prompt:

"""
You are an LLM tasked with producing a process plan in `urirun:processes` format.
The user needs a desktop automation flow that opens Signal on a remote KVM target,
verifies the window, types a message, and confirms completion. Use KVM and
markpact/marksync primitives where appropriate.
"""

Result:

```urirun:processes
[
  {
    "id": "prepare-signal-kvm",
    "name": "Fetch remote KVM and Signal desktop status",
    "actor": "script",
    "uri": "kvm://laptop/diag/query/signal-status",
    "payload": {
      "verify_window": true,
      "expected_title": "Signal"
    },
    "depends_on": [],
    "human_approval": false,
    "timeout_seconds": 120,
    "retries": 1
  },
  {
    "id": "focus-signal-window",
    "name": "Focus Signal desktop window via KVM",
    "actor": "script",
    "uri": "kvm://laptop/gui/focus",
    "payload": {
      "window_title": "Signal"
    },
    "depends_on": ["prepare-signal-kvm"],
    "human_approval": false,
    "timeout_seconds": 90,
    "retries": 2
  },
  {
    "id": "type-signal-message",
    "name": "Type message into Signal using KVM automation",
    "actor": "script",
    "uri": "kvm://laptop/gui/type",
    "payload": {
      "text": "Hello from the urirun automation flow. This message was sent by KVM desktop control."
    },
    "depends_on": ["focus-signal-window"],
    "human_approval": false,
    "timeout_seconds": 120,
    "retries": 2
  },
  {
    "id": "confirm-message-sent",
    "name": "Confirm the message was sent successfully",
    "actor": "script",
    "uri": "kvm://laptop/gui/confirm",
    "payload": {
      "verification": "message-delivered"
    },
    "depends_on": ["type-signal-message"],
    "human_approval": false,
    "timeout_seconds": 90,
    "retries": 1
  }
]
```

## Example 3: Sync a repo and execute a maintenance workflow

Prompt:

"""
Generate a URI process plan for a maintenance workflow that syncs a repository
contract into marksync, validates it with markpact, and runs a maintenance script.
The plan should be explicit about dependencies and include a human approval
step before the final maintenance execution.
"""

Result:

```urirun:processes
[
  {
    "id": "sync-repo-contract",
    "name": "Sync repository README contract to marksync",
    "actor": "script",
    "uri": "marksync://sync-server/push",
    "payload": {
      "contract_path": "repos/maintenance/README.md",
      "server_uri": "ws://localhost:8765"
    },
    "depends_on": [],
    "human_approval": false,
    "timeout_seconds": 120,
    "retries": 1
  },
  {
    "id": "validate-maintenance-contract",
    "name": "Validate maintenance contract with markpact",
    "actor": "script",
    "uri": "markpact://local/validate",
    "payload": {
      "contract_path": "repos/maintenance/README.md"
    },
    "depends_on": ["sync-repo-contract"],
    "human_approval": false,
    "timeout_seconds": 180,
    "retries": 1
  },
  {
    "id": "review-maintenance-plan",
    "name": "Human review maintenance workflow",
    "actor": "human",
    "uri": "work://human/review/maintenance-plan",
    "payload": {
      "summary": "Review the maintenance workflow and approve execution."
    },
    "depends_on": ["validate-maintenance-contract"],
    "human_approval": true,
    "timeout_seconds": 3600,
    "retries": 0
  },
  {
    "id": "execute-maintenance-script",
    "name": "Run maintenance script through the runtime",
    "actor": "script",
    "uri": "shell://maintenance-host/command/run",
    "payload": {
      "command": "./scripts/maintenance.sh",
      "cwd": "/workspace/repos/maintenance"
    },
    "depends_on": ["review-maintenance-plan"],
    "human_approval": false,
    "timeout_seconds": 600,
    "retries": 2
  }
]
```
