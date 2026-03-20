import sys
import os

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))
import tools.test_suite
import definitions


def run(scenario: int, parse: bool, multi: bool, dir = ""):
    STATS_DIR = f"spin-k3s-single-native{dir}"
    GO_SERVICE = f"{definitions.WORK_DIR}/spin-infra/go-native-deploy.yaml"
    RUST_SERVICE = f"{definitions.WORK_DIR}/spin-infra/rust-native-deploy.yaml"
    AI_SERVICE = f"{definitions.WORK_DIR}/spin-infra/ai-native-deploy.yaml"
    HOST_HEADER = "nuhakala.com"
    SC1_SLEEP = 10
    PID_KEYWORDS = ["k3s", "spin"]
    PID_AMOUNT = 2
    if multi:
        STATS_DIR = f"spin-k3s-multi-native{dir}"
        PID_KEYWORDS = ["k3s", "spin"]  # depends where spin operator running
        PID_AMOUNT = 2

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
