# LLM documentation index

Provide these files to the LLM as project context (entire repo or raw URLs).

| File | Role |
|------|------|
| [first_system_prompt.md](first_system_prompt.md) | **Start here** — assembled system prompt |
| [runtime_semantics.md](runtime_semantics.md) | POST /run contract |
| [process_contract.md](process_contract.md) | `urirun:processes` field reference |
| [process_schema.json](process_schema.json) | Machine validation schema |
| [environment_topology.yaml](environment_topology.yaml) | Where nodes/services live |
| [route_catalog.yaml](route_catalog.yaml) | Common URI routes |
| [../openapi.yaml](../openapi.yaml) | OpenAPI transport spec |

Regenerate `first_system_prompt.md`:

```bash
python scripts/assemble_llm_prompt.py
```
