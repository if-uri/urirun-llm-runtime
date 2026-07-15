"""Enable ``python -m urirun_llm_runtime`` as an alias for the CLI."""
from urirun_llm_runtime.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
