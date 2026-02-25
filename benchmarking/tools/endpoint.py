import requests
import sys

import print_utils


def ping_endpoint(address, host_header, timeout=0):
    """Pings the given address and returns True if available, False otherwise."""
    headers = {}
    if len(host_header) != 0:
        headers = {"Host": host_header}
    try:
        r = requests.get(address, timeout=timeout, headers=headers)
        r.raise_for_status()  # check statuscode
        return True
    except:
        return False


def main():
    if len(sys.argv) <= 3:
        print_utils.print_red("ERROR: need address and host header as parameter.")

    address = sys.argv[1]
    header = sys.argv[2]
    ping_endpoint(address, header, timeout=10)


if __name__ == "__main__":
    main()
