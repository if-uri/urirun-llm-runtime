"""Example: query KVM diagnostic using the urirun-llm-runtime Executor.

This script demonstrates how LLM-generated code should call the runtime
endpoint instead of invoking subprocesses.
"""
from urirun_llm_runtime.executor import Executor


def main():
    e = Executor('http://192.168.188.201:8765')
    res = e.execute('kvm://laptop/diag/query/which')
    print('Result:', res)


if __name__ == '__main__':
    main()
