"""urirun-llm-runtime — canonical LLM-facing URI process execution library."""
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
    "Executor",
    "UriProcess",
    "from_dict",
    "build_first_system_prompt",
    "docs_index",
    "docs_index",
    "lint_path",
    "lint_tree",
    "parse_processes_block",
    "run_processes",
    "validate_processes",
]
