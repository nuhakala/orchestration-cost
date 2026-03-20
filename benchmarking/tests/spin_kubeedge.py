import sys
import os

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))
import tools.test_suite
import definitions


def run(scenario: int, parse: bool, multi: bool, dir = ""):
    STATS_DIR = f"spin-kubeedge-single-container{dir}"
    GO_SERVICE = f"{definitions.WORK_DIR}/spin-infra/go-kubeedge-deploy.yaml"
    RUST_SERVICE = f"{definitions.WORK_DIR}/spin-infra/rust-kubeedge-deploy.yaml"
    AI_SERVICE = f"{definitions.WORK_DIR}/spin-infra/ai-kubeedge-deploy.yaml"
    HOST_HEADER = "nuhakala.com"
    SC1_SLEEP = 10
    PID_KEYWORDS = ["kubeedge", "spin"]
    PID_AMOUNT = 7
    if multi:
        STATS_DIR = f"spin-kubeedge-multi-container{dir}"
        PID_KEYWORDS = ["kubeedge", "spin"]  # spin operator running in worker node
        PID_AMOUNT = 7

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
