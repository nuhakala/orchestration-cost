"""
This script prints all the extra wasmCloud measurements and the median & mean of
related measurement. Furthermore, it aggregates the results and prints the mean
& median of K0s, K3s, and K0s rc7 measurements.

The purpose of this script is to print all the raw data so it can be copy-pasted
to github issue.
"""

import argparse
import glob
import os

from pandas.io.orc import pd

import tools.extra_wc_data
import definitions
from definitions import (
    WC_EXTRA_LOC_MULTI,
    WC_EXTRA_LOC_SINGLE,
    WC_V2,
    WC_V2_AI,
    WC_V2_AI_MULTI,
    WC_V2_MULTI,
)


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


def print_values_and_indicators(base_dir, go_fold, rust_fold, title, set_title = ""):
    if set_title != "":
        print(set_title)

    for folder in go_fold:
        startup_time_values(f"{base_dir}/{folder}", folder)
    for folder in rust_fold:
        startup_time_values(f"{base_dir}/{folder}", folder)

    indicators = tools.extra_wc_data.get_indicators(base_dir, go_fold, rust_fold)
    print(
        f"{title}: go avg: {indicators[0]}, rust avg: {indicators[1]}, go median: {indicators[2]}, rust median: {indicators[3]}"
    )
    print()


def print_wc_startups_rc6_rc7():
    print_values_and_indicators(
        WC_EXTRA_LOC_MULTI,
        definitions.folders_k0s_go,
        definitions.folders_k0s_rust,
        "k0s",
    )
    print_values_and_indicators(
        WC_EXTRA_LOC_MULTI,
        definitions.folders_k3s_go,
        definitions.folders_k3s_rust,
        "k3s",
    )

    print_values_and_indicators(
        WC_EXTRA_LOC_MULTI,
        definitions.folders_k0s_go_rc7,
        definitions.folders_k0s_rust_rc7,
        "k0s rc7",
    )

    print_values_and_indicators(
        WC_EXTRA_LOC_MULTI,
        definitions.folders_k0s_single_go,
        definitions.folders_k0s_single_rust,
        "k0s single",
    )


def print_wc_startups_v2():
    single_go = [os.path.basename(p) for p in glob.glob(f"{WC_V2}/*-go")]
    single_rust = [os.path.basename(p) for p in glob.glob(f"{WC_V2}/*-rust")]
    multi_go = [os.path.basename(p) for p in glob.glob(f"{WC_V2_MULTI}/*-go")]
    multi_rust = [os.path.basename(p) for p in glob.glob(f"{WC_V2_MULTI}/*-rust")]
    ai = [os.path.basename(p) for p in glob.glob(f"{WC_V2_AI}/*")]
    ai_multi = [os.path.basename(p) for p in glob.glob(f"{WC_V2_AI_MULTI}/*")]

    print_values_and_indicators(WC_V2, single_go, single_rust, "single", "Regular workload single node")
    print_values_and_indicators(WC_V2_MULTI, multi_go, multi_rust, "multi", "Regular workload two nodes")
    print_values_and_indicators(WC_V2_AI, [], ai, "ai", "Image recognition workload single node")
    print_values_and_indicators(WC_V2_AI_MULTI, [], ai_multi, "ai multi", "Image recognition workload two nodes")


parser = argparse.ArgumentParser(description="Startup time aggregator")
parser.add_argument("target", choices=["rc6", "v2"], help="Choose target")
args = parser.parse_args()

match args.target:
    case "rc6":
        print_wc_startups_rc6_rc7()
    case "v2":
        print_wc_startups_v2()
    case "_":
        print("Unknown target")
