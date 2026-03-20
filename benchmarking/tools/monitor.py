import subprocess
import time
import sys

from . import writestats
from . import print_utils

# Note! according to manual pages "man 5 proc_stat" and "man 5 proc_pid_stat"
# and my understanding of time management (clock ticks = unit of USER_HZ), the
# value read from /proc/stat and /proc/pid/stat are in the same units and hence
# we can safely compare them.


res = subprocess.run(
    [
        "getconf",
        "PAGESIZE",
    ],
    capture_output=True,
    text=True,
)
PAGESIZE = int(res.stdout)


# Extract the amount of memory from given line and check if it is in kilobytes
# line format: <identifier>: <amount> <unit>
def __extract_mem_line(line):
    values = line.strip().split()
    if values[2] != "kB":
        print_utils.print_red(f"{line[0]} is in unit {values[2]}, not in kB")
    return int(values[1])


# Reads global (machine) performance statistics
def __read_glob_stat():
    # see https://www.man7.org/linux/man-pages/man5/proc_stat.5.html
    with open("/proc/stat", "r") as f:
        line = f.readline()

    parts = line.strip().split()
    values = list(map(int, parts[1:9]))  # skip 'cpu' prefix
    total = 0
    for v in values:
        total += v
    idle = values[3] + values[4]  # idle & iowait

    # see https://www.man7.org/linux/man-pages/man5/proc_meminfo.5.html
    # Lines contain the unit, probably kB
    with open("/proc/meminfo", "r") as f:
        mem_total = __extract_mem_line(f.readline())
        mem_free = __extract_mem_line(f.readline())
        f.readline()  # skip MemAvailable
        mem_buffers = __extract_mem_line(f.readline())
        mem_cached = __extract_mem_line(f.readline())

    return [total, idle, mem_total, mem_free, mem_buffers, mem_cached]


# Reads per-process stats of the given pid
def __read_proc_stat(pid):
    # see https://www.man7.org/linux/man-pages//man5/proc_pid_stat.5.html
    with open(f"/proc/{pid}/stat", "r") as f:
        line = f.readline()
    stat_parts = line.strip().split()
    rss = 0
    with open(f"/proc/{pid}/status", "r") as f:
        for line in f:
            line.strip()
            if line.startswith("VmRSS"):
                rss = __extract_mem_line(line)
    res = [
        pid,
        int(stat_parts[13]) + int(stat_parts[14]),  # user mode + system mode CPU time
        rss,
    ]
    return res


# Prints the statistics to stdout
def __print_stats(glob_prev, glob_curr, procs_prev, procs_curr):
    delta_total = glob_curr[0] - glob_prev[0]
    delta_idle = glob_curr[1] - glob_prev[1]
    print(f"Global CPU: {(delta_total - delta_idle) / delta_total * 100}%")

    mem_total = glob_curr[2] / 1024 / 1024  # get gigs
    mem_free = (glob_curr[3] + glob_curr[4] + glob_curr[5]) / 1024 / 1024
    print(f"Global mem: {mem_total - mem_free}/{mem_total}GB")

    for proc in range(len(procs_curr)):
        print(f"Process with pid {procs_curr[proc][0]}")
        delta_proc_active = procs_curr[proc][1] - procs_prev[proc][1]
        print(f"Process CPU: {delta_proc_active / delta_total * 100}%")

        proc_rss = procs_curr[proc][2] / 1024
        print(f"Process VmRSS: {proc_rss * PAGESIZE / 1024}MB")
    print("\n\n")


def record_stats(pids, stop, file: str, start_time, print_instead_writing=False):
    """Record stats, can either print stats into csv file or into stdout

    Arguments:
        pids -- list of pids (list of numbers)
        stop -- function that returns 'True' when monitoring should be stopped
        file -- string, file name to write stats
        start_time -- int, start time stamp in nano seconds
        print_instead_writing -- boolean
    """
    # The previous values only needed for printing
    glob_prev = __read_glob_stat()
    procs_prev = []

    proc_header = ""
    for pid in pids:
        proc_header = proc_header + f",{pid}/cpu,{pid}/rss"
        procs_prev.append(__read_proc_stat(pid))

    writer = writestats.StatWriter(
        file, f"total,idle,mem_total,mem_free{proc_header}", start_time
    )

    while True:
        time.sleep(1)
        glob_curr = __read_glob_stat()
        procs_curr = []
        for pid in pids:
            procs_curr.append(__read_proc_stat(pid))

        if print_instead_writing:
            __print_stats(glob_prev, glob_curr, procs_prev, procs_curr)
            glob_prev = glob_curr
            procs_prev = procs_curr
        else:
            proc_values = ""
            for proc in procs_curr:
                proc_values = proc_values + f",{proc[1]},{proc[2]}"
            writer.write_stats(
                f"{glob_curr[0]},{glob_curr[1]},{glob_curr[2]},{glob_curr[3]}{proc_values}"
            )

        if stop():
            break


def main():
    if len(sys.argv) == 1:
        print("No pid given, will watch only system resources.")

    pids = sys.argv[1:]
    record_stats(
        pids, lambda: False, "./stats.csv", time.time_ns(), print_instead_writing=False
    )


if __name__ == "__main__":
    main()
