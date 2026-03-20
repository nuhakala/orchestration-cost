import sys
import os

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))
import tools.test_suite
import definitions


def run(scenario: int, parse: bool, multi: bool, dir = ""):
    STATS_DIR = f"wc-k3s-single{dir}"
    GO_SERVICE = ""
    RUST_SERVICE = ""
    AI_SERVICE = ""
    if scenario == 1 or scenario == 4:
        GO_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/go-deploy-rep1.yaml"
        RUST_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/rust-deploy-rep1.yaml"
        AI_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/ai-deploy-rep1.yaml"
    else:
        GO_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/go-deploy-rep10.yaml"
        RUST_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/rust-deploy-rep10.yaml"
        AI_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/ai-deploy-rep10.yaml"
    HOST_HEADER = "nuhakala.com"
    SC1_SLEEP = 10
    PID_KEYWORDS = ["k3s", "wasmcloud"]
    PID_AMOUNT = 3
    if multi:
        STATS_DIR = f"wc-k3s-multi{dir}"
        PID_KEYWORDS = ["k3s", "wasmcloud"]
        PID_AMOUNT = 3

    tools.test_suite.execute_scenario(
        STATS_DIR,
        PID_KEYWORDS,
        PID_AMOUNT,
        GO_SERVICE,
        RUST_SERVICE,
        AI_SERVICE,
        HOST_HEADER,
        SC1_SLEEP,
        scenario,
        parse,
        multi,
    )


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: <scenario num> <bool: parse> <bool: multi>")
    parse = False
    multi = False
    if sys.argv[2] == "true":
        parse = True
    if sys.argv[3] == "true":
        multi = True
    run(int(sys.argv[1]), parse, multi)
