"""
This file is specialized to provide data for printing the extra wc data.
Not really meant to be used for anything else.
"""
import pandas as pd

import definitions
from definitions import (
    folders_k0s_go,
    folders_k0s_rust,
    folders_k3s_go,
    folders_k3s_rust,
    folders_k0s_go_rc7,
    folders_k0s_rust_rc7,
)
from . import statistics_utils

STATS_DIR = definitions.WC_EXTRA_LOC_MULTI


def get_indicators(stats_dir, folders_go, folders_rust):
    go_values = []
    rust_values = []
    for folder in folders_go:
        go_values = go_values + statistics_utils.startup_time_values(
            f"{stats_dir}/{folder}"
        )
    for folder in folders_rust:
        rust_values = rust_values + statistics_utils.startup_time_values(
            f"{stats_dir}/{folder}"
        )
    go = pd.Series(go_values)
    rust = pd.Series(rust_values)
    go_average: float = float(round(go.mean(), 2))
    rust_average: float = float(round(rust.mean(), 2))
    go_median: float = float(round(go.median(), 2))
    rust_median: float = float(round(rust.median(), 2))
    return [go_average, rust_average, go_median, rust_median]


def get_platform_indicators():
    k0s_indicators = get_indicators(STATS_DIR, folders_k0s_go, folders_k0s_rust)
    k0s_rc7_indicators = get_indicators(STATS_DIR, folders_k0s_go_rc7, folders_k0s_rust_rc7)
    k3s_indicators = get_indicators(STATS_DIR, folders_k3s_go, folders_k3s_rust)

    return k0s_indicators + k3s_indicators + k0s_rc7_indicators


def get_set_averages():
    all_folders = (
        folders_k0s_go
        + folders_k0s_rust
        + folders_k0s_go_rc7
        + folders_k0s_rust_rc7
        + folders_k3s_go
        + folders_k3s_rust
    )
    res = {}
    for folder in all_folders:
        path = f"{STATS_DIR}/{folder}"
        res[folder] = statistics_utils.startup_time_indicators(path)
    return res


def get_extra_orch_cost_means(metrics: dict[str, statistics_utils.OrchCostMetric]):
    def calc_mean(folders):
        sum = 0
        for key in folders:
            sum += metrics[key].calculate_metric()
        return sum / len(folders)

    k0s_go = calc_mean(folders_k0s_go)
    k0s_rust = calc_mean(folders_k0s_rust)
    k3s_go = calc_mean(folders_k3s_go)
    k3s_rust = calc_mean(folders_k3s_rust)
    return [k0s_go, k0s_rust, k3s_go, k3s_rust]
