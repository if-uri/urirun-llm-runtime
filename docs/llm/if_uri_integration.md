# Integration with if-uri tickets

This repo is the **canonical LLM ↔ ticket communication standard** for if-uri.

## Wired in if-uri

| Component | Role |
|-----------|------|
| `urirun_runtime/process_standard.py` | Parse/validate/execute `urirun:processes` |
| `urirun_runtime/ticket_llm_context.py` | First system prompt + examples + history |
| `urirun_connector_work/goal.py` | Signal/KVM tickets — extract & run plans |
| `urirun_twin_human/core.py` | Twin human — same output standard |

## Environment

```bash
# Optional: override examples file (default: bundled llm_standard/process_examples.md)
export URIRUN_LLM_EXAMPLES_FILE=/path/to/markpact_marksync_process_examples.md
export URIRUN_LLM_RUNTIME_REPO=https://github.com/if-uri/urirun-llm-runtime
```

## LLM must output

````markdown
```urirun:processes
[{ "id": "...", "name": "...", "actor": "script", "uri": "kvm://host/...", "payload": {} }]
```
````

See [markpact_marksync_process_examples.md](markpact_marksync_process_examples.md) for realistic prompt/response pairs.
