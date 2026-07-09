"""Example: execute a composed urirun:processes plan via the HTTP runtime."""
from urirun_llm_runtime import Executor


def main():
    node = "http://host-node:8765"
    executor = Executor(node)
    plan = [
        {
            "id": "step-1",
            "name": "Query KVM diagnostics",
            "actor": "script",
            "uri": "kvm://host/doctor/query/report",
            "payload": {},
        },
        {
            "id": "step-2",
            "name": "Verify environment",
            "actor": "script",
            "uri": "kvm://host/env/query/profile",
            "payload": {},
            "depends_on": ["step-1"],
        },
    ]
    results = executor.execute_processes(plan)
    print(results)


if __name__ == "__main__":
    main()
