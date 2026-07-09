# Runtime stack (real if-uri connectors)

This directory runs the **production URI runtime** from the [if-uri](https://github.com/if-uri/if-uri) monorepo.

## Prerequisites

```bash
git clone https://github.com/if-uri/if-uri /path/to/if-uri
export IF_URI_ROOT=/path/to/if-uri
```

Default sibling path: `../if-uri` (set in `.env`).

## Quick start

```bash
cd urirun-llm-runtime
cp runtime/.env.example runtime/.env
docker compose -f runtime/docker-compose.yml up -d host-node
curl -sf http://127.0.0.1:18765/health
```

## URI smoke (inside compose network)

```bash
docker compose -f runtime/docker-compose.yml --profile smoke run --rm uri-smoke
```

## Full stack (dashboard + node)

```bash
docker compose -f runtime/docker-compose.yml --profile full up -d
```

## LLM context

After stack is up, point LLM clients at:

- `docs/llm/first_system_prompt.md` — assembled system prompt
- `docs/llm/route_catalog.yaml` — common routes
- `GET http://host-node:8765/routes` — live registry

## Ports

| Service | Host port | Internal |
|---------|-----------|----------|
| host-node | 18765 | 8765 |
| host-dashboard | 18797 | 8797 |

Avoids conflict with bare-metal koru on 8765/8797.
