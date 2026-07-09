# LLM documentation index

Provide these files to the LLM as project context (entire repo or raw URLs).

| File | Role |
|------|------|
| [first_system_prompt.md](first_system_prompt.md) | **Start here** — assembled system prompt |
| [runtime_semantics.md](runtime_semantics.md) | POST /run contract |
| [process_contract.md](process_contract.md) | `urirun:processes` field reference |
| [process_schema.json](process_schema.json) | Machine validation schema |
| [environment_topology.yaml](environment_topology.yaml) | Where nodes/services live |
| [route_catalog.yaml](route_catalog.yaml) | Common URI routes (curated examples) |
| [route_schemas_lenovo.json](route_schemas_lenovo.json) | **Full inputSchema per URI** (lenovo snapshot for offline CI) |
| [../openapi.yaml](../openapi.yaml) | OpenAPI transport spec |

Regenerate `first_system_prompt.md`:

```bash
python scripts/assemble_llm_prompt.py
```

Refresh lenovo route schema snapshot (after connector deploy on node):

```bash
URIRUN_LENOVO_URL=http://192.168.188.201:8765 python scripts/snapshot_route_schemas.py
python scripts/snapshot_route_schemas.py --validate-only
```
