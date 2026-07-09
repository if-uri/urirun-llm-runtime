"""Example: run a shell command via the runtime (shell:// URI).

This shows the canonical pattern LLMs should follow: build a URI and call
the runtime rather than using subprocess directly.
"""
from urirun_llm_runtime.executor import Executor


def main():
    e = Executor('http://192.168.188.201:8765')
    res = e.execute('shell://laptop/command/date')
    print('Date result:', res)


if __name__ == '__main__':
    main()
