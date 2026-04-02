import os
import time
import subprocess

import definitions
from . import endpoint
from . import writestats
from . import tester
from . import print_utils


def benchmark(
    folder: str,
    iter: int,
    pids: list[str],
    command: list[str],
    reset_command: list[str],
    host_header: str,
    ai_workload: bool,
):
    """
    Scenario 1 benchmark

    Measures how long it take for endpoint to be alive from running the given
    command.

        folder - directory to save stats to
        iter - iteration, just a number to track which iteration out of 10 is going
        pids - list of strings which contain the pids to watch
        command - command to run when starting workload
        reset_command - command to run when deleting workload
        host_header - HTTP host header to use when pinging endpoint
    """
    # folder = f"{definitions.SC1_PATH}/{stats_dir}"
    interface = definitions.INTERFACE
    timeout = definitions.TIMEOUT
    endpoints = [definitions.SERVICE_ENDPOINT]
    if ai_workload:
        endpoints = [definitions.AI_ENDPOINT]

    if not os.path.isdir(folder):
        os.mkdir(folder)

    print_utils.print_start(
        f"Starting scenario 1 iter {iter} with stats file folder {folder}"
    )
    print_utils.print_start(f"and pids {pids}")
    fpref = f"{folder}/{iter}"
    perf_file = f"{fpref}-perf.csv"
    stat_file = f"{fpref}-startup.txt"
    interface_file = f"{fpref}-interface.csv"
    writer = writestats.StatWriter(stat_file, "", 0)
    image_path = f"{definitions.WORK_DIR}/servers/fixture/images/dog.jpg"

    def test():
        start_time = time.time_ns()
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

        print(f"Pinging addresses http://{endpoints[0]} now")
        while True:
            delta_time = time.time_ns() - start_time

            for end in endpoints:
                address = f"http://{end}"
                success = False
                if ai_workload:
                    success = endpoint.recognize_image(
                        address, host_header, image_path, timeout
                    )
                else:
                    success = endpoint.ping_endpoint(address, host_header, 10)

                if success:
                    print_utils.print_green("Endpoint found")
                    writer.write_time(delta_time)
                    return

            if (time.time_ns() - start_time) / 1000 / 1000 > timeout:
                print_utils.print_red("Timeout hit, no endpoint found")
                writer.write_stat(f"Timeout {writer.get_time(delta_time)}")
                return
            time.sleep(0.002)

    tester.test(perf_file, pids, test, interface_file, interface)

    print("Undeploying app")
    try:
        _ = subprocess.run(
            reset_command,
            text=True,
            check=True,
            capture_output=True,
        )
        print("Undeployed successfully")
    except Exception as e:
        print_utils.print_red(f"ERROR: running reset command produced error: {e}")
        return False

    print_utils.print_finish("Benchmark finished")
    return True
