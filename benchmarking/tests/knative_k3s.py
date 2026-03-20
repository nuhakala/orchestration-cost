import sys
import os

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))
import tools.test_suite
import definitions


def run(scenario: int, parse: bool, multi, dir = ""):
    STATS_DIR = f"knative-k3s-single{dir}"
    GO_SERVICE = f"{definitions.WORK_DIR}/knative-infra/go-service.yaml"
    RUST_SERVICE = f"{definitions.WORK_DIR}/knative-infra/rust-service.yaml"
    AI_SERVICE = f"{definitions.WORK_DIR}/knative-infra/ai-service.yaml"
    HOST_HEADER = "knative-test.default.nuhakala.com"
    SC1_SLEEP = 60
    PID_KEYWORDS = ["k3s", "knative"]
    PID_AMOUNT = 7
    if multi:
        STATS_DIR = f"knative-k3s-multi{dir}"
        PID_KEYWORDS = ["k3s"]  # knative stuff is at worker
        PID_AMOUNT = 1

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
