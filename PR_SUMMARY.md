PR: Add OpenAPI spec, mock runtime, Docker and examples

This PR contains the following changes:
- `docs/openapi.yaml` — canonical OpenAPI for URI processes
- `docker/app.py`, `docker/Dockerfile`, `docker-compose.yml` — mock runtime and compose
- `examples/*` — example scripts using `Executor`
- `README.md` — docker / LLM usage instructions

This PR is created as a one-time merge per user request; future updates will be pushed
directly to `main` without opening PRs.
