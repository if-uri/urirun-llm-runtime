# Integration with if-uri tickets

This repo is the **canonical LLM ↔ ticket communication standard** for if-uri.

## Wired in if-uri

| Component | Role |
|-----------|------|
| `urirun_runtime/process_standard.py` | Parse/validate/execute `urirun:processes` |
| `urirun_runtime/llm_runtime_loop.py` | **LLM pętla** — gap, dogrywanie, retry na każdej turze |
| `urirun_runtime/ticket_llm_context.py` | First system prompt + examples + history |
| `urirun_connector_work/goal.py` | `send_via_kvm` → `LlmRuntimeLoop` (default) |
| `urirun_twin_human/core.py` | Twin human — same output standard |

## Environment

```bash
# LLM kontroluje wykonanie (domyślnie włączone)
export URIRUN_LLM_RUNTIME_CONTROL=1
export URIRUN_LLM_MAX_STEPS=40

# Fallback na scripted Python (tylko gdy LLM wyłączony)
export URIRUN_LLM_RUNTIME_CONTROL=0

# Opcjonalnie: triple-LLM prep jako initial_plan, potem pętla LLM
export SIGNAL_KVM_PREP=1
```

## LLM must output

````markdown
```urirun:processes
[{ "id": "...", "name": "...", "actor": "script", "uri": "kvm://host/...", "payload": {} }]
```
````

See [markpact_marksync_process_examples.md](markpact_marksync_process_examples.md) for realistic prompt/response pairs.
