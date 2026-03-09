"""
This script prints all the extra wasmCloud measurements and the median & mean of
related measurement. Furthermore, it aggregates the results and prints the mean
& median of K0s, K3s, and K0s rc7 measurements.
"""
import glob

from pandas.io.orc import pd

import definitions
import tools.extra_wc_data


def startup_time_values(folder, title):
    startup_files = glob.glob(f"{folder}/*-startup.txt")

    values = []
    for filepath in startup_files:
        with open(filepath, "r") as f:
            value = float(f.read().strip())
            values.append(value)

    if values:
        s = pd.Series(values)
        median: float = float(round(s.median(), 2))
        average: float = float(round(s.mean(), 2))
        print(f"{title}\tavg: {average}\tmedian: {median}  \tvalues: {values}")
    return values


STATS_DIR = f"{definitions.ROOT_DIR}/data/sc1-extra-wc-data/"

for folder in definitions.folders_k0s_go:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)
for folder in definitions.folders_k0s_rust:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)

k0s_indicators = tools.extra_wc_data.get_indicators(
    STATS_DIR, definitions.folders_k0s_go, definitions.folders_k0s_rust
)
print(
    f"k0s: go avg: {k0s_indicators[0]}, rust avg: {k0s_indicators[1]}, go median: {k0s_indicators[2]}, rust median: {k0s_indicators[3]}"
)
print()

for folder in definitions.folders_k3s_go:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)
for folder in definitions.folders_k3s_rust:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)

k3s_indicators = tools.extra_wc_data.get_indicators(
    STATS_DIR, definitions.folders_k3s_go, definitions.folders_k3s_rust
)
print(
    f"k3s: go avg: {k3s_indicators[0]}, rust avg: {k3s_indicators[1]}, go median: {k3s_indicators[2]}, rust median: {k3s_indicators[3]}"
)
print()

for folder in definitions.folders_k0s_go_rc7:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)
for folder in definitions.folders_k0s_rust_rc7:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)

k0s_indicators_rc7 = tools.extra_wc_data.get_indicators(
    STATS_DIR, definitions.folders_k0s_go_rc7, definitions.folders_k0s_rust_rc7
)
print(
    f"k0s rc7: go avg: {k0s_indicators_rc7[0]}, rust avg: {k0s_indicators_rc7[1]}, go median: {k0s_indicators_rc7[2]}, rust median: {k0s_indicators_rc7[3]}"
)
print()

for folder in definitions.folders_k0s_single_go:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)
for folder in definitions.folders_k0s_single_rust:
    startup_time_values(f"{STATS_DIR}/{folder}", folder)

k0s_indicators = tools.extra_wc_data.get_indicators(
    STATS_DIR, definitions.folders_k0s_single_go, definitions.folders_k0s_single_rust
)
print(
    f"k0s single: go avg: {k0s_indicators[0]}, rust avg: {k0s_indicators[1]}, go median: {k0s_indicators[2]}, rust median: {k0s_indicators[3]}"
)
