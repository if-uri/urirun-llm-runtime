"""urirun-llm-runtime — canonical LLM-facing URI process execution library."""
__version__ = "0.2.2"

from urirun_llm_runtime.cli import main as cli_main
from urirun_llm_runtime.executor import Executor
from urirun_llm_runtime.llm_context import build_first_system_prompt, docs_index
from urirun_llm_runtime.process import (
    UriProcess,
    from_dict,
    parse_processes_block,
    run_processes,
    validate_processes,
)
from urirun_llm_runtime.validator import lint_path, lint_tree

__all__ = [
    "__version__",
    "cli_main",
    "Executor",
    "UriProcess",
    "from_dict",
    "build_first_system_prompt",
    "docs_index",
    "lint_path",
    "lint_tree",
    "parse_processes_block",
    "run_processes",
    "validate_processes",
]
