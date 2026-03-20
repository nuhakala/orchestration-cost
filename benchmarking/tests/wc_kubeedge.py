import sys
import os
import time

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))
import tools.test_suite
import definitions


def run(scenario: int, parse: bool, multi: bool, dir = ""):
    STATS_DIR = f"wc-kubeedge-single{dir}"
    GO_SERVICE = ""
    RUST_SERVICE = ""
    AI_SERVICE = ""
    if scenario == 1 or scenario == 4:
        GO_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/go-kubeedge-rep1.yaml"
        RUST_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/rust-kubeedge-rep1.yaml"
        AI_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/ai-kubeedge-rep1.yaml"
    else:
        GO_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/go-kubeedge-rep10.yaml"
        RUST_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/rust-kubeedge-rep10.yaml"
        AI_SERVICE = f"{definitions.WORK_DIR}/wasmcloud-v2-infra/ai-kubeedge-rep10.yaml"
    HOST_HEADER = "nuhakala.com"
    SC1_SLEEP = 20
    PID_KEYWORDS = ["kubeedge", "wasmcloud"]
    PID_AMOUNT = 8
    if multi:
        STATS_DIR = f"wc-kubeedge-multi{dir}"
        PID_KEYWORDS = ["kubeedge", "wasmcloud"]
        PID_AMOUNT = 8

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
    scenario = int(sys.argv[1])
    if scenario < 1 or scenario > 2:
        print("Scenario must be 1 or 2, cannot run both at once due to manifests.")
        sys.exit(1)
    parse = False
    multi = False
    if sys.argv[2] == "true":
        parse = True
    if sys.argv[3] == "true":
        multi = True
    # Reminder for the special cases to take with wasmcloud
    if scenario == 2 and not parse:
        print("Before you begin, check that")
        print("1. You have added extra 60 seconds waiting to scenario 2")
        print("2. You have deployd the correct amount of wasmcloud hosts")
        print("3. Once workload is deployed, check that each host gets a workload")
        time.sleep(10)
    run(int(sys.argv[1]), parse, multi)
