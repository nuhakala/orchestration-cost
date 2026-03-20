import datetime
import sys
import time
import urllib.parse
import requests

from . import print_utils
from . import scenario1
from . import scenario2
from . import getpids

import definitions


def __get_pids(keywords, amount):
    PIDS = getpids.get_pids(keywords)
    # Simple sanity check
    if len(PIDS) != amount:
        print(PIDS)
        print(f"Got len(pids) != {amount} pids, check you stuff")
        sys.exit(0)
    if len(PIDS) == 0:
        print("No pids found, check your stuff")
        sys.exit(0)
    return PIDS


def __start_worker_measures(scenario, dir, i):
    if i == -1:
        url_parameters = {
            "scenario": scenario,
            "stats_dir": dir,
            "perf_file": f"worker-perf.csv",
            "int_file": f"worker-int.csv",
        }
    else:
        url_parameters = {
            "scenario": scenario,
            "stats_dir": dir,
            "perf_file": f"{i}-worker-perf.csv",
            "int_file": f"{i}-worker-int.csv",
        }
    encoded_url = urllib.parse.urlencode(url_parameters)
    address = f"http://{definitions.WORKER_ADDRESS}:{definitions.HOST_SERVER_PORT}/start?{encoded_url}"
    try:
        _ = requests.get(address, timeout=10)
    except Exception as e:
        print_utils.print_red(
            f"ERROR: making request to worker node produced error: {e}"
        )
        sys.exit(0)


def __stop_worker_measures():
    address = f"http://{definitions.WORKER_ADDRESS}:{definitions.HOST_SERVER_PORT}/stop"
    try:
        _ = requests.get(address, timeout=10)
    except Exception as e:
        print_utils.print_red(
            f"ERROR: making request to worker node produced error: {e}"
        )
        sys.exit(0)


def execute_scenario(
    stats_dir: str,
    pid_keywords: list[str],
    pid_amount: int,
    go_service: str,
    rust_service: str,
    ai_service: str,
    host_header: str,
    sleep: int,
    scenario: int,
    parse: bool,
    multi_device: bool,
):
    """
    Executes given scenario with given parameters. Possible scenario identifiers:
        1 -> scenario 1
        2 -> scenario 2
        3 -> both scenario 1 and 2
        4 -> scenario 1 with AI workload

        stats_dir - stats dir prefix to save data to (for sc1 and sc2)
        pid_keywords - keywords by which get the pids to watch, see tools.getpids
        pid_amount - number of pids to sanity check that correct amount of pids is being watched
        go_service - go deployment file path
        rust_service - rust deployment file path
        host_header - host header to use for HTTP request
        sleep - time to wait between each iteration in sc1
        scenario - which scenario to operate, 3 = both
        parse - parse data instead of running tests
        multi_device - multi-device test or not
    """
    # Must push the full path expansion to scenarios because scenario 2 will
    # send the directory to the host-server, and host server must be able to
    # resolve its own path to the data directory. The home directories
    # between the two machines are not necessarily the same.
    go_dir = f"{stats_dir}-go"
    rust_dir = f"{stats_dir}-rust"
    ai_dir = stats_dir
    go_command = ["kubectl", "apply", "-f", go_service]
    go_reset_command = ["kubectl", "delete", "-f", go_service]
    rust_command = ["kubectl", "apply", "-f", rust_service]
    rust_reset_command = ["kubectl", "delete", "-f", rust_service]
    ai_command = ["kubectl", "apply", "-f", ai_service]
    ai_reset_command = ["kubectl", "delete", "-f", ai_service]
    minutes = definitions.SC2_MINUTES

    def execute_sc2(sc_num, base_dir, dir, com, reset_com):
        if multi_device:
            __start_worker_measures(sc_num, dir, -1)
        scenario2.benchmark(base_dir, dir, com, reset_com, pids, host_header)
        if multi_device:
            __stop_worker_measures()

    def execute_sc1(sc_num, dir, com, reset_com, ai):
        # go deployment
        for i in range(0, definitions.NUM_ITERS):
            if multi_device:
                __start_worker_measures(sc_num, ai_dir, i)
            success = scenario1.benchmark(
                dir,
                i,
                pids,
                com,
                reset_com,
                host_header,
                ai,
            )
            if not success:
                print("Undeploying failed, aborting benchmark.")
                break
            if multi_device:
                __stop_worker_measures()
            # sleep for few seconds so that system can calm down.
            # the deployment is deleted, so next iteration should start from similar
            # setup.
            time.sleep(sleep)

    # Parse data and exit
    def parse_data():
        from . import read_data_sc1
        from . import read_data_sc2

        GO_DIR = f"{stats_dir}-go"
        RUST_DIR = f"{stats_dir}-rust"
        if scenario in [1, 2, 3]:
            for dir in [GO_DIR, RUST_DIR]:
                if scenario == 1 or scenario == 3:
                    read_data_sc1.create_curves(definitions.SC1_PATH, dir, multi_device)
                    read_data_sc1.parse_stats(definitions.SC1_PATH, dir, multi_device)
                elif scenario == 2 or scenario == 3:
                    read_data_sc2.create_curves(definitions.SC2_PATH, dir, multi_device)
                    read_data_sc2.parse_stats(definitions.SC2_PATH, dir, multi_device)
        elif scenario == 4:
            read_data_sc1.create_curves(definitions.AI_SC1, ai_dir, multi_device)
            read_data_sc1.parse_stats(definitions.AI_SC1, ai_dir, multi_device)
        elif scenario == 5:
            read_data_sc2.create_curves(definitions.AI_SC2, ai_dir, multi_device)
            read_data_sc2.parse_stats(definitions.AI_SC2, ai_dir, multi_device)
        else:
            print("Choose scenario 1-5.")
        sys.exit(0)

    if parse:
        parse_data()

    # Run scenario
    if not parse:
        # Parse pids here to avoid interrupting execution in pid check in case
        # we are parsing data.
        pids = __get_pids(pid_keywords, pid_amount)

        # ***** SCENARIO 1 *****
        if scenario == 1 or scenario == 3:
            execute_sc1(
                1,
                f"{definitions.SC1_PATH}/{go_dir}",
                go_command,
                go_reset_command,
                False,
            )
            execute_sc1(
                1,
                f"{definitions.SC1_PATH}/{rust_dir}",
                rust_command,
                rust_reset_command,
                False,
            )

        # ***** Running both, so sleep in between *****
        if scenario == 3:
            # sleep for a while so that knative scale back to zero
            print_utils.print_time_delay(
                f"sleeping for {minutes} minutes to let system scale down",
                datetime.timedelta(minutes=minutes),
            )
            time.sleep(minutes * 60)

        # ***** SCENARIO 2 *****
        if scenario == 2 or scenario == 3:
            execute_sc2(2, definitions.SC2_PATH, go_dir, go_command, go_reset_command)
            # sleep for a while so that knative scale back to zero
            print_utils.print_time_delay(
                f"sleeping for {minutes} minutes to let system scale down",
                datetime.timedelta(minutes=minutes),
            )
            time.sleep(minutes * 60)
            execute_sc2(
                2, definitions.SC2_PATH, rust_dir, rust_command, rust_reset_command
            )

        # ***** AI WORKLOAD *****
        if scenario == 4:
            execute_sc1(
                4, f"{definitions.AI_SC1}/{ai_dir}", ai_command, ai_reset_command, True
            )

        if scenario == 5:
            execute_sc2(5, definitions.AI_SC2, ai_dir, ai_command, ai_reset_command)

        if scenario < 1 or scenario > 5:
            print("Choose either scenario 1, 2, 3 (both), or 4 (AI SC1) or 5 (AI SC2)")
