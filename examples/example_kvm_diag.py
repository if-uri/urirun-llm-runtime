"""Example: query KVM diagnostic using the urirun-llm-runtime Executor."""
from urirun_llm_runtime import Executor


def main():
    node = "http://host-node:8765"  # compose network; use 127.0.0.1:18765 from host
    e = Executor(node)
    res = e.execute("kvm://host/doctor/query/report")
    print("ok:", res.get("ok"), "uri:", res.get("uri"))


if __name__ == "__main__":
    main()
