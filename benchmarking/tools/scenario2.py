import datetime
import os
import subprocess
import requests
import time
import urllib.parse

import definitions
import tester
import print_utils


def benchmark(
    stats_dir: str,
    command: list[str],
    reset_command: list[str],
    pids: list[str],
    host_header,
):
    """
    Scenario 2 benchmark

    Makes a HTTP request to host, where ./host-server.py should be running. The
    host server will then run hey from the host, so that creating the requests
    don't clutter guest performance stats.

    NOTE! When running wasmCloud tests, the extra 60 second waiting time must
    be added by uncommenting line 73.

        stats_dir - directory to save stats to
        command - command to run when starting workload
        reset_command - command to run when deleting workload
        pids - list of strings which contain the pids to watch
        host_header - HTTP host header to use when pinging endpoint
    """
    folder = f"{definitions.SC2_PATH}/{stats_dir}"
    control_plane_ip = definitions.HEY_SERVER_IP
    host_server_port = definitions.HOST_SERVER_PORT
    ping_endpoint = definitions.PING_ENDPOINT
    interface = definitions.INTERFACE
    scaledown_delay = definitions.SCALEDOWN_DELAY
    service_endpoint = definitions.SERVICE_ENDPOINT

    if not os.path.isdir(folder):
        os.mkdir(folder)

    # Start benchmark
    print_utils.print_start(f"Starting scenario 2 benchmark with folder {folder}")
    print_utils.print_start(f"and pids {pids}")
    perf_file = f"{folder}/perf.csv"
    interface_file = f"{folder}/interface.csv"
    url_parameters = {
        "host_header": host_header,
        "folder": stats_dir,
        "ipaddress": service_endpoint,
        "endpoint": ping_endpoint,
    }
    encoded_url = urllib.parse.urlencode(url_parameters)
    url = f"http://{control_plane_ip}:{host_server_port}/?{encoded_url}"

    # Wrap only hey command inside tester, as it is the only thing we want to
    # benchmark
    def test():
        print("Waiting extra 20 seconds to capture more data before benchmark.")
        time.sleep(20)

        # Wasmcloud is too slow to deploy any instance in 30 seconds, I got
        # 503 for the first 2000 requests. Hence, add extra 60 seconds of wait
        # time to ensure that the workloads have been deployed. When testing
        # manually, all the workloads were ready in ~70s, so overall 90 second
        # waiting time should be enough.
        # print("Sleeping extra 60 seconds for wasmcloud")
        # time.sleep(60)

        print("Making request to host next to trigger hey.")
        try:
            requests.get(
                url,
                timeout=(5, 5 * 60),  # 5s to connect, 5 minutes to wait for response
            )
            print("Hey finished successfully")
        except Exception as e:
            print_utils.print_red(f"ERROR: making test request produced error: {e}")
            return

        # wait for some time to capture the scaledown resource usage
        print_utils.print_time_delay(
            f"Wait for {scaledown_delay}s to capture scaling down effect",
            datetime.timedelta(seconds=scaledown_delay),
        )
        time.sleep(scaledown_delay)

    # Deploy app
    try:
        subprocess.run(
            command,
            text=True,
            check=True,
            capture_output=True,
        )
        print("Deployed successfully")
    except Exception as e:
        print_utils.print_red(f"ERROR: running start command produced error: {e}")
        return

    # Run test
    tester.test(perf_file, pids, test, interface_file, interface)

    # Undeploy app
    try:
        subprocess.run(
            reset_command,
            text=True,
            check=True,
            capture_output=True,
        )
        print("Undeployed successfully")
    except Exception as e:
        print_utils.print_red(f"ERROR: running start command produced error: {e}")
        return

    # Finish
    print_utils.print_finish("Benchmark finished")
