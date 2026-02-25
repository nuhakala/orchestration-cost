import time
import sys

import writestats


def __get_stats(interface):
    with open("/proc/net/dev", "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith(interface):
            values = line.strip().split()
            # These values are in kilobytes
            sent = round(int(values[9]) / 1024, 2)
            received = round(int(values[1]) / 1024, 2)
            total = round(
                int(sent + received) / 1024, 2
            )  # oops, should not divide by 1024 :D
            return [sent, received, total]
    return ["", "", ""]


def watch_interface(interface, stop, file, start_time):
    """
    Watches the given interfaces and writes the interface stats into given file

        interface - interface to watch
        stop - function which should return true when we want to stop watchin
        file - save file
        start_time - unix time stamp when started (in ns)
    """
    writer = writestats.StatWriter(file, "sent,received,total", start_time)

    while True:
        v = __get_stats(interface)
        writer.write_stats(f"{v[0]},{v[1]},{v[2]}")
        # print( f"sent: {v[0]}, received: {v[1]}, total: {v[2]}")

        if stop():
            break

        time.sleep(1)


def main():
    interface = sys.argv[1]
    watch_interface(interface, lambda: False, "interface.csv", time.time())


if __name__ == "__main__":
    main()
