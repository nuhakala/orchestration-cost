"""
This script starts an HTTP server which will start/stop node and process
specific measurements on request. The following query parameters must be
specified:

- scenario  & which scenario to use, affects the save location
- stats_dir & which dir to save data (under save location)
- perf_file & name of performance stats file
- int_file  & name of interface stats file

The base save location is definitions.SC2_PATH

Furthermore, the script takes process specifiers as command line parameters,
the available specifiers are in tools.getpids
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import threading
import time
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.abspath("./tools"))
from tools import interface, monitor, getpids
from tools.print_utils import print_red, print_start, print_finish
import definitions


stop_thread = False
start_time = time.time_ns()
threads = []
pids = []


def on_start(scenario, stats_dir, perf_file, int_file):
    # Start benchmark
    folder = ""
    if scenario == 1:
        folder = f"{definitions.SC1_PATH}/{stats_dir}"
    elif scenario == 2:
        folder = f"{definitions.SC2_PATH}/{stats_dir}"
    elif scenario == 4:
        folder = f"{definitions.AI_SC1}/{stats_dir}"
    elif scenario == 5:
        folder = f"{definitions.AI_SC2}/{stats_dir}"
    if not os.path.isdir(folder):
        os.mkdir(folder)

    perf_file = f"{folder}/{perf_file}"
    interface_file = f"{folder}/{int_file}"
    print_start(f"Starting worker node measures, logging to {perf_file}.")

    global start_time
    global threads
    global stop_thread
    global pids

    start_time = time.time_ns()

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
                definitions.INTERFACE,
                lambda: stop_thread,
                interface_file,
                start_time,
            ),
        )
    )

    for thread in threads:
        thread.start()


def on_stop():
    stop_time = time.time_ns()
    delta_time = stop_time - start_time
    global stop_thread
    stop_thread = True
    global threads
    for thread in threads:
        thread.join()
    threads = []
    stop_thread = False
    print_finish(
        f"Threads stopped, monitoring took {round(delta_time / 1000 / 1000 / 1000, 2)}s"
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/start"):
            # Parse query parameters
            query = urlparse(self.path).query
            params = parse_qs(query)

            scenario = int(params.get("scenario", [""])[0])
            stats_dir = params.get("stats_dir", [""])[0]
            perf_file = params.get("perf_file", [""])[0]
            int_file = params.get("int_file", [""])[0]

            on_start(scenario, stats_dir, perf_file, int_file)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK\n")

            # Finish
            print_finish("Threads started")
        elif self.path.startswith("/stop"):
            on_stop()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK\n")

    def log_message(self, format, *args):
        pass  # silence default logging


def run_server():
    pid_identifiers = sys.argv[1:]
    if len(pid_identifiers) == 0:
        print_red("No pid identifiers given, aborting.")
        sys.exit(0)
    global pids
    pids = getpids.get_pids(pid_identifiers)
    if len(pids) == 0:
        print_red("Zero pids found, aborting.")
        sys.exit(0)
    server = HTTPServer(("0.0.0.0", definitions.HOST_SERVER_PORT), Handler)
    print(f"Listening on http://0.0.0.0:{definitions.HOST_SERVER_PORT}")
    print(f"Watching pids {pids}")
    try:
        print("Server running. Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    run_server()
