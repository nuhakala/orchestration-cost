"""
This script starts an HTTP server which will start hey load generator on request.
The HTTP request must specify the following query parameters:

- host_header & HTTP host header to use for generated requests
- folder      & folder to save the data to
- ipaddress   & IP address and port to make the requests to
- endpoint    & HTTP request endpoint, for example /wait
"""
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
from urllib.parse import urlparse, parse_qs

from tools.print_utils import print_start, print_red, print_finish, print_time_delay
from tools.writestats import StatWriter
import definitions


def on_request(host_header, stats_dir, ip_address, endpoint):
    # Start benchmark
    hey_dir = f"{definitions.SC2_PATH}/{stats_dir}"
    hey_file = f"{hey_dir}/hey.csv"
    if not os.path.isdir(hey_dir):
        os.mkdir(hey_dir)

    print_start(f"Starting to test orchestrator with hey and logging to {hey_file}")
    writer = StatWriter(hey_file, "", 0)

    TEST_LENGTH = 90  # seconds
    CPUS = "4"
    # Total RPS (or QPS) = CONCURRENT_WORKERS * QPS_WORKER
    CONCURRENT_WORKERS = "10"
    QPS_WORKER = "10"
    COMMAND = [
        "hey",
        "-z",
        f"{TEST_LENGTH}s",
        "-c",
        CONCURRENT_WORKERS,
        "-cpus",
        CPUS,
        "-q",
        QPS_WORKER,
        "-disable-keepalive",
        "-host",
        host_header,
        "-o=csv",
        f"http://{ip_address}{endpoint}",
    ]

    try:
        print(f"Starting command '{COMMAND}'")
        print_time_delay(
            f"will run for {TEST_LENGTH} seconds",
            datetime.timedelta(seconds=TEST_LENGTH),
        )
        res = subprocess.run(
            COMMAND,
            text=True,
            check=True,
            capture_output=True,
        )
        writer.write_stat(res.stdout)
        print("Hey finished successfully")
    except Exception as e:
        print_red(f"ERROR: running test produced error: {e}")
        return


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)

        header = params.get("host_header", [""])[0]
        folder = params.get("folder", [""])[0]
        ip_address = params.get("ipaddress", [""])[0]
        endpoint = params.get("endpoint", [""])[0]

        on_request(header, folder, ip_address, endpoint)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK\n")

        # Finish
        print_finish("Host side finished")

    def log_message(self, format, *args):
        pass  # silence default logging


def run_server():
    server = HTTPServer(("0.0.0.0", definitions.HOST_SERVER_PORT), Handler)
    print(f"Listening on http://0.0.0.0:{definitions.HOST_SERVER_PORT}")
    try:
        print("Server running. Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    run_server()
