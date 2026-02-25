import datetime
import sys
import time
import urllib.parse

import requests
from tools import print_utils
import tools.scenario1
import tools.scenario2
import tools.getpids
import definitions


def __get_pids(keywords, amount):
    PIDS = tools.getpids.get_pids(keywords)
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
    host_header: str,
    sleep: int,
    scenario: int,
    parse: bool,
    multi_device: bool,
):
    """
    Executes given scenario with given parameters.

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
    go_command = ["kubectl", "apply", "-f", go_service]
    go_reset_command = ["kubectl", "delete", "-f", go_service]
    rust_command = ["kubectl", "apply", "-f", rust_service]
    rust_reset_command = ["kubectl", "delete", "-f", rust_service]
    minutes = definitions.SC2_MINUTES

    # Parse data and exit
    if parse:
        import read_data_sc1
        import read_data_sc2

        GO_DIR = f"{stats_dir}-go"
        RUST_DIR = f"{stats_dir}-rust"
        for dir in [GO_DIR, RUST_DIR]:
            if scenario == 1 or scenario == 3:
                read_data_sc1.create_curves(dir, multi_device)
                read_data_sc1.parse_stats(dir, multi_device)
            elif scenario == 2 or scenario == 3:
                read_data_sc2.create_curves(dir, multi_device)
                read_data_sc2.parse_stats(dir, multi_device)
            else:
                print("Choose either scenario 1, 2, or 3 (both).")
        sys.exit(0)

    # Parse data before getting pids to do the pid check after that if necessary
    pids = __get_pids(pid_keywords, pid_amount)

    # Run scenario
    if not parse:
        # ***** SCENARIO 1 *****
        if scenario == 1 or scenario == 3:
            # go deployment
            for i in range(0, definitions.NUM_ITERS):
                if multi_device:
                    __start_worker_measures(1, go_dir, i)
                res = tools.scenario1.benchmark(
                    go_dir,
                    i,
                    pids,
                    go_command,
                    go_reset_command,
                    host_header,
                )
                if not res:
                    break
                # sleep for few seconds so that system can calm down.
                # the deployment is deleted, so next iteration should start from similar
                # setup.
                if multi_device:
                    __stop_worker_measures()
                time.sleep(sleep)

            # rust deployment
            for i in range(0, definitions.NUM_ITERS):
                if multi_device:
                    __start_worker_measures(1, rust_dir, i)
                res = tools.scenario1.benchmark(
                    rust_dir,
                    i,
                    pids,
                    rust_command,
                    rust_reset_command,
                    host_header,
                )
                if not res:
                    break
                if multi_device:
                    __stop_worker_measures()
                time.sleep(sleep)

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
            if multi_device:
                __start_worker_measures(2, go_dir, -1)
            tools.scenario2.benchmark(
                go_dir, go_command, go_reset_command, pids, host_header
            )
            if multi_device:
                __stop_worker_measures()

            # sleep for a while so that knative scale back to zero
            print_utils.print_time_delay(
                f"sleeping for {minutes} minutes to let system scale down",
                datetime.timedelta(minutes=minutes),
            )
            time.sleep(minutes * 60)

            if multi_device:
                __start_worker_measures(2, rust_dir, -1)
            tools.scenario2.benchmark(
                rust_dir, rust_command, rust_reset_command, pids, host_header
            )
            if multi_device:
                __stop_worker_measures()

        if scenario < 1 or scenario > 3:
            print("Choose either scenario 1, 2, or 3 (both).")
