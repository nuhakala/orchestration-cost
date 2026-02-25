import sys
import os

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))

import tools.test_suite
import definitions


def run(scenario: int, parse: bool, multi: bool):
    STATS_DIR = "container-k3s-single"
    GO_SERVICE = f"{definitions.WORK_DIR}/native-infra/go-hpa-deploy.yaml"
    RUST_SERVICE = f"{definitions.WORK_DIR}/native-infra/rust-hpa-deploy.yaml"
    HOST_HEADER = "nuhakala.com"
    # It takes some time for knative to delete the pod, so have 40 second break
    SC1_SLEEP = 40
    PID_KEYWORDS = ["k3s"]
    PID_AMOUNT = 1
    if multi:
        STATS_DIR = "container-k3s-multi"
        PID_KEYWORDS = ["k3s"]
        PID_AMOUNT = 1

    tools.test_suite.execute_scenario(
        STATS_DIR,
        PID_KEYWORDS,
        PID_AMOUNT,
        GO_SERVICE,
        RUST_SERVICE,
        HOST_HEADER,
        SC1_SLEEP,
        scenario,
        parse,
        multi,
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Give scenario number and boolean (whether to parse data)")
    parse = False
    multi = False
    if sys.argv[2] == "true":
        parse = True
    if sys.argv[3] == "true":
        multi = True
    run(int(sys.argv[1]), parse, multi)
