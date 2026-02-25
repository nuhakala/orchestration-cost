import subprocess

import print_utils


def get_ip_starting(ip_start) -> str:
    """Gets IP address that starts with given parameter"""
    try:
        res = subprocess.run(
            ["hostname", "--all-ip-addresses"],
            text=True,
            check=True,
            capture_output=True,
        )
        addresses = res.stdout.split()
        for addr in addresses:
            if addr.startswith(ip_start):
                return addr
    except Exception as e:
        print_utils.print_red(f"ERROR: running start command produced error: {e}")

    return ""
