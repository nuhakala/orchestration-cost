import threading
import time

from . import monitor
from . import interface


def test(
    perf_file,
    pids,
    test_function,
    interface_file,
    interface_to_watch,
):
    """
    Very simple wrapper for autocollecting perf-stats. Starts monitoring threads
    10 seconds before test and then calls the test function and stops monitoring
    10 seconds after test.

        perf_file - file to save perf stats
        pids - pids to watch for perf data
        test_function - function to test
        interface_file - file to save interface stats
        interface_to_watch - name of system network interface to watch
    """

    # Start recording stats
    start_time = time.time_ns()
    stop_thread = False
    threads = []

    # Stats thread
    threads.append(
        threading.Thread(
            target=monitor.record_stats,
            args=(
                pids,
                lambda: stop_thread,
                perf_file,
                start_time,
            ),
        )
    )

    # Interface thread
    threads.append(
        threading.Thread(
            target=interface.watch_interface,
            args=(
                interface_to_watch,
                lambda: stop_thread,
                interface_file,
                start_time,
            ),
        )
    )

    for t in threads:
        t.start()
    time.sleep(0.5)  # so that the following print is later than the prints in threads
    print("Wait 10 seconds to get some performance statistics before actual test.")
    time.sleep(9.5)  # sleep for a while to get some stats

    test_start_time = time.time_ns()
    test_function()
    test_stop_time = time.time_ns()

    # Wrap up and stop statistic measuring
    delta_time = test_stop_time - test_start_time
    print("Wait 10 seconds to get some performance statistics after actual test.")
    time.sleep(10)
    stop_thread = True
    for thread in threads:
        thread.join()
    print(f"Tester executed in {round(delta_time / 1000 / 1000 / 1000, 2)}s")
