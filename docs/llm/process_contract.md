# Process contract — fields every LLM step must include

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable step identifier |
| `name` | string | Human-readable label |
| `actor` | enum | `llm`, `script`, `human`, `system` |
| `uri` | string | Full URI to POST to `/run` |
| `payload` | object | JSON payload per route schema |

## Optional fields

| Field | Type | Default |
|-------|------|---------|
| `depends_on` | string[] | `[]` |
| `human_approval` | bool | `false` |
| `timeout_seconds` | int | node default |
| `retries` | int | `0` |

## Execution order

Steps run in topological order of `depends_on`. Dependency cycles and self-dependencies are invalid and rejected before execution. Steps with `human_approval: true` pause until approved.

The `uri` field must always be a concrete executable address. Wildcards such as
`youtube://*` belong in an authorization contract; they are not executable
process addresses.

## Validation

Use `urirun_llm_runtime.validate_processes()` or CI script `scripts/validate_processes.py`.

JSON Schema: `docs/llm/process_schema.json`
