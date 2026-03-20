"""
This file calculates the orchestration cost for each folder under
./data/scenario{1|2}

It saves figures to folder defined in definitions.FIGURE_DIR

By default it won't save any figures, instead it shows them immediately. Give
command line flag --save to save files. Preview can be disabled with --no-show
"""

import argparse
import itertools
import os

from tables.leaf import math
import definitions
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tools.extra_wc_data import get_extra_orch_cost_means
import tools.read_data_sc1
import tools.read_data_sc2
from tools.statistics_utils import OrchCostMetric

metrics = {}
ai_metrics = {}
wc_extra_metrics = {}
all_files = []

parser = argparse.ArgumentParser(description="My Project CLI")
parser.add_argument(
    "--show", action=argparse.BooleanOptionalAction, help="show images", default=True
)
parser.add_argument(
    "--save", action=argparse.BooleanOptionalAction, help="save images", default=False
)
args = parser.parse_args()


# ***** Calculate the metrics *****
def parse_folders(folder, scenario, metrics_store):
    items = os.listdir(folder)
    for test_case in items:
        metric = metrics_store.get(test_case, OrchCostMetric(test_case=test_case))
        if scenario == 1:
            tools.read_data_sc1.get_orch_cost_values(folder, test_case, metric)
        else:
            tools.read_data_sc2.get_orch_cost_values(folder, test_case, metric)
        metrics_store[test_case] = metric


parse_folders(definitions.SC1_PATH, 1, metrics)
parse_folders(definitions.SC2_PATH, 2, metrics)
parse_folders(definitions.AI_SC1, 1, ai_metrics)
parse_folders(definitions.AI_SC2, 2, ai_metrics)


# Next, get the scenario 2 values from the basic workload and add those to the
# extra metrics.
items = os.listdir(definitions.WC_EXTRA_LOC_MULTI)
for test_case in items:
    metric = wc_extra_metrics.get(test_case, OrchCostMetric(test_case=test_case))
    tools.read_data_sc1.get_orch_cost_values(
        definitions.WC_EXTRA_LOC_MULTI, test_case, metric
    )
    if metric.platform() == "k3s" and metric.language() == "go":
        tools.read_data_sc2.get_orch_cost_values(
            definitions.SC2_PATH, "wc-k3s-multi-go", metric
        )
    if metric.platform() == "k3s" and metric.language() == "rust":
        tools.read_data_sc2.get_orch_cost_values(
            definitions.SC2_PATH, "wc-k3s-multi-rust", metric
        )
    if metric.platform() == "k0s" and metric.language() == "go":
        tools.read_data_sc2.get_orch_cost_values(
            definitions.SC2_PATH, "wc-k0s-multi-go", metric
        )
    if metric.platform() == "k0s" and metric.language() == "rust":
        tools.read_data_sc2.get_orch_cost_values(
            definitions.SC2_PATH, "wc-k0s-multi-rust", metric
        )
    wc_extra_metrics[test_case] = metric

# Add dummy values for spin native kubeedge for both ai and non ai metrics
metrics["spin-kubeedge-multi-native-go"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native-go"
)
metrics["spin-kubeedge-multi-native-rust"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native-rust"
)
ai_metrics["spin-kubeedge-multi-native-go"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native"
)


def create_pd_df():
    return pd.DataFrame(
        {
            "test_case": pd.Series(dtype="string"),
            "value": pd.Series(dtype="float"),
            "platform": pd.Series(dtype="string"),
            "orchestrator": pd.Series(dtype="string"),
            "language": pd.Series(dtype="string"),
        }
    )


single = create_pd_df()
multi = create_pd_df()
multi_no_startup = create_pd_df()
wc_extra = create_pd_df()
ai_multi = create_pd_df()


def transform_to_df(m, df):
    for metric in m.values():
        test_case = metric.test_case_parsed()
        row = {
            "test_case": test_case,
            "value": metric.calculate_metric(),
            "platform": metric.platform(),
            "orchestrator": metric.orchestrator(),
            "language": metric.language(),
        }

        df.loc[len(df)] = row


# This would be also good to do using above function, but too cumbersome.
for metric in metrics.values():
    test_case = metric.test_case_parsed()

    row = {
        "test_case": test_case,
        "value": metric.calculate_metric(),
        "platform": metric.platform(),
        "orchestrator": metric.orchestrator(),
        "language": metric.language(),
    }
    row_no_startup = {
        "test_case": test_case,
        "value": metric.calculate_metric_without_startup(),
        "platform": metric.platform(),
        "orchestrator": metric.orchestrator(),
        "language": metric.language(),
    }

    if metric.multi_node():
        multi.loc[len(multi)] = row
        multi_no_startup.loc[len(multi_no_startup)] = row_no_startup
    else:
        single.loc[len(single)] = row

transform_to_df(wc_extra_metrics, wc_extra)
transform_to_df(ai_metrics, ai_multi)
print(ai_multi)


# Replace the orch cost value with the one that were
# calculated from the averages over multiple test sets.
wc_extra_orch_costs = get_extra_orch_cost_means(wc_extra_metrics)
multi.loc[(multi["test_case"] == "wc-go") & (multi["platform"] == "k0s"), "value"] = (
    wc_extra_orch_costs[0]
)
multi.loc[(multi["test_case"] == "wc-rust") & (multi["platform"] == "k0s"), "value"] = (
    wc_extra_orch_costs[1]
)
multi.loc[(multi["test_case"] == "wc-go") & (multi["platform"] == "k3s"), "value"] = (
    wc_extra_orch_costs[2]
)
multi.loc[(multi["test_case"] == "wc-rust") & (multi["platform"] == "k3s"), "value"] = (
    wc_extra_orch_costs[3]
)


# ***** Prepare save files *****
orch_cost_single_sorted = f"{definitions.LATEX_TABLE_LOC}/orch-cost-single-sorted.tex"
orch_cost_multi_sorted = f"{definitions.LATEX_TABLE_LOC}/orch-cost-multi-sorted.tex"
orch_cost_ai_sorted = f"{definitions.LATEX_TABLE_LOC}/orch-cost-ai-sorted.tex"
all_files = all_files + [orch_cost_multi_sorted, orch_cost_single_sorted, orch_cost_ai_sorted]

fig_platform_single = f"{definitions.FIGURE_DIR}/orch_cost_platform_single.png"
fig_platform_multi = f"{definitions.FIGURE_DIR}/orch_cost_platform_multi.png"
fig_platform_multi_no_startup = ( f"{definitions.FIGURE_DIR}/orch_cost_platform_multi_no_startup.png")
fig_platform_multi_wc_extra = ( f"{definitions.FIGURE_DIR}/orch_cost_platform_multi_wc_extra.png")
fig_platform_multi_ai = ( f"{definitions.FIGURE_DIR}/orch_cost_platform_multi_ai.png")
fig_orchestrator_single = f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_single.png"
fig_orchestrator_multi = f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi.png"
fig_orchestrator_multi_ai = f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi_ai.png"
fig_orchestrator_single_curve = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_single_curve.png")
fig_orchestrator_multi_curve = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi_curve.png")
fig_orchestrator_multi_curve_ai = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi_curve_ai.png")
all_files = all_files + [
    fig_platform_single,
    fig_platform_multi,
    fig_platform_multi_no_startup,
    fig_orchestrator_single,
    fig_orchestrator_multi,
    fig_orchestrator_single_curve,
    fig_orchestrator_multi_curve,
    fig_platform_multi_wc_extra,
    fig_platform_multi_ai,
    fig_orchestrator_multi_ai,
    fig_orchestrator_multi_curve_ai,
]

# Remove old files
if args.save:
    print("Removing old files")
    for file in all_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            print("File not found")


# ***** Print latex tables *****
def print_orch_cost_table(file, df, write_header):
    if args.save:
        with open(file, "w", encoding="utf-8") as f:
            if write_header:
                f.write(
                    "\\textbf{Test case} & \\textbf{Platform} & \\textbf{Orchestrator} & \\textbf{Orchestration cost} \\\\\n"
                )
            for row in df.sort_values(by="value").itertuples(index=False):
                f.write(
                    f"{row.test_case} & {row.platform} & {row.orchestrator} & {row.value} \\\\\n"
                )
    else:
        print(f"Printing orch cost table for {file}")
        print("Test case & platform & orchestrator & orchestration cost")
        for row in df.sort_values(by="value").itertuples(index=False):
            print(f"{row.test_case} & {row.platform} & {row.orchestrator} & {row.value}")

print_orch_cost_table(orch_cost_single_sorted, single, True)
print_orch_cost_table(orch_cost_multi_sorted, multi, True)
# add wc_extra to same table, hence no header
print_orch_cost_table(orch_cost_multi_sorted, wc_extra, False)
print_orch_cost_table(orch_cost_ai_sorted, ai_multi, True)


# ***** Fuctions for plotting *****
def create_bar_plot(
    x_labels: list[str],
    bar_width: float,
    value_tuples: dict,
    title: str,
    ymin: int,
    ylim: int,
    ncols: int,
    save_location: str,
    bar_font_size=5,
):
    x = np.arange(len(x_labels))  # the label locations
    width = bar_width  # the width of the bars
    multiplier = 0
    fig_size = (definitions.PLOT_WIDTH, definitions.PLOT_HEIGHT)

    _, ax = plt.subplots(layout="constrained", figsize=fig_size)

    # The number of characters defines the density of the pattern
    hatch_cycle = itertools.cycle(
        [
            "////",
            "...",
            "\\\\\\\\",
            "oo",
            "||||",
            "OO",
            "----",
            "xxx",
            "+++",
            "**",
            "//||",
            "\\\\||",
            "--xx",
            "..--",
        ]
    )
    for attribute, measurement in value_tuples.items():
        offset = width * multiplier
        rects = ax.bar(
            x + offset,
            [round(x, 0) for x in measurement],
            width,
            label=attribute,
            hatch=next(hatch_cycle),
            edgecolor="black",
            facecolor="white",
            linewidth=1,
        )
        ax.bar_label(rects, padding=3, fontsize=bar_font_size)
        multiplier += 1

    group_size = len(value_tuples)

    # We need to calculate the centers differently for wasmcloud extra data
    # because there the group sizes are 14 and 8
    # Hack works because no other figure has group size of 14
    #
    # Instead of this we could just define the centers by hand to be
    # [0.455, 1.245]
    if group_size == 14:
        centers = []
        first_center = (math.floor(len(value_tuples) / 2) - 0.5) * width
        centers.append(first_center)
        second_size = sum(
            1 for t in list(value_tuples.values()) if not math.isnan(t[1])
        )
        second_center = (math.floor(second_size / 2) - 0.5) * width
        # First take into account the first group
        # then add the second center
        # then add width because the number is off by one bar for whatever reason
        # then add 0.1 because that is what we set as xmargin below
        centers.append(2 * first_center + second_center + width + 0.02)
        ax.set_xticks(centers, x_labels)
    else:
        if group_size % 2 == 0:
            ax.set_xticks(x + (math.floor(group_size / 2) - 0.5) * width, x_labels)
        else:
            ax.set_xticks(x + (math.floor(group_size / 2) - 0.5) * width + 0.5 * width, x_labels)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    # ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.1), ncols=ncols, handleheight=2)
    ax.set_ylim(ymin, ylim)
    ax.set_xmargin(0.01)

    if args.save:
        plt.savefig(save_location, bbox_inches="tight", pad_inches=0.03)
    if args.show:
        plt.show()
    plt.close()


def create_line_plot(
    x_labels: list[str],
    value_tuples: dict,
    title: str,
    ymin: int,
    ymax: int,
    ncols: int,
    save_location: str,
):
    x = np.arange(len(x_labels))  # the label locations
    fig_size = (definitions.PLOT_WIDTH, definitions.PLOT_HEIGHT)

    _, ax = plt.subplots(layout="constrained", figsize=fig_size)

    styles = itertools.cycle(
        [
            "solid",
            "dotted",
            "dashed",
            "dashdot",
            (0, (1, 5)),
            (5, (10, 3)),
            (0, (5, 10)),
            (0, (5, 5)),
            (0, (3, 5, 1, 5)),
            (0, (3, 5, 1, 5, 1, 5)),
            "*",
        ]
    )
    for attribute, measurement in value_tuples.items():
        ax.plot(
            x,
            measurement,
            marker="o",
            label=attribute,
            linestyle=next(styles),
            color="black",
        )

    # ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x, x_labels)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.1), ncols=ncols, handlelength=5)
    ax.set_ylim(ymin, ymax)

    if args.save:
        plt.savefig(save_location, bbox_inches="tight", pad_inches=0.03)
    if args.show:
        plt.show()
    plt.close()


# ***** Helpers *****
def platform_single_values(single_sorted):
    orchestrator_values_single = {}
    for i in range(0, len(single_sorted), 2):
        row = single_sorted.iloc[i]
        row2 = single_sorted.iloc[i + 1]
        orchestrator_values_single[row.test_case] = (
            float(row["value"]),
            float(row2["value"]),
        )
    return orchestrator_values_single


def platform_single_values_wc_extra(single_sorted):
    orchestrator_values_single = {}
    for i in range(0, 16, 2):
        row = single_sorted.iloc[i]
        row2 = single_sorted.iloc[i + 1]
        orchestrator_values_single[row.test_case] = (
            float(row["value"]),
            float(row2["value"]),
        )
    for i in range(0, 6):
        row = single_sorted.iloc[i + 16]
        orchestrator_values_single[row.test_case] = (
            float(row["value"]),
            math.nan,
        )
    return orchestrator_values_single


def bar_chart_by_platform_multi(sorted):
    orchestrator_values = {}
    for i in range(0, len(sorted), 3):
        row = sorted.iloc[i]
        row2 = sorted.iloc[i + 1]
        row3 = sorted.iloc[i + 2]
        orchestrator_values[row.test_case] = (
            float(row["value"]),
            float(row2["value"]),
            float(row3["value"]),
        )
    return orchestrator_values


def orchestrator_single_values(sorted):
    platform_values = {}
    for i in range(0, int(len(sorted) / 5)):
        row = sorted.iloc[i]
        row2 = sorted.iloc[i + 4]
        row3 = sorted.iloc[i + 8]
        row4 = sorted.iloc[i + 12]
        row5 = sorted.iloc[i + 16]
        platform_values[f"{row.platform}-{row.language}"] = (
            float(row["value"]),
            float(row2["value"]),
            float(row3["value"]),
            float(row4["value"]),
            float(row5["value"]),
        )
    return platform_values


def orchestrator_multi_values(sorted):
    platform_values = {}
    period = int(len(sorted) / 5)
    for i in range(0, period):
        row = sorted.iloc[i]
        row2 = sorted.iloc[i + period]
        row3 = sorted.iloc[i + 2 * period]
        row4 = sorted.iloc[i + 3 * period]
        row5 = sorted.iloc[i + 4 * period]
        platform_values[f"{row.platform}-{row.language}"] = (
            float(row["value"]),
            float(row2["value"]),
            float(row3["value"]),
            float(row4["value"]),
            float(row5["value"]),
        )
    return platform_values


# ***** Set matplotlib font size *****
font_size = 9
plt.rcParams.update(
    {
        "font.size": font_size,
        "axes.titlesize": font_size,
        "axes.labelsize": font_size,
        "xtick.labelsize": font_size,
        "ytick.labelsize": font_size,
        "legend.fontsize": font_size,
    }
)

# ***** Create figures *****
single_sorted = single.sort_values(["test_case", "platform"])
multi_sorted = multi.sort_values(["test_case", "platform"])
ai_multi_sorted = ai_multi.sort_values(["test_case", "platform"])
wc_extra_sorted = wc_extra.sort_values(["test_case", "platform"])
multi_no_startup_sorted = multi_no_startup.sort_values(["test_case", "platform"])
print(single_sorted)
print(multi_sorted)

if not args.save:
    print("Single sorted")
    print(single_sorted)
    print()
    print("Multi sorted")
    print(multi_sorted)
    print()
    print("AI Multi sorted")
    print(ai_multi_sorted)
    print()
    print("WC extra sorted")
    print(wc_extra_sorted)
    print()

# ***** Bar charts by platform *****
extra_labels = [
    ("container", 0, "container"),
    ("Knative", 2, "knative"),
    ("Spin cont", 4, "spin-cont"),
    ("Spin nat", 6, "spin-native"),
    ("wasmCloud", 8, "wc"),
]
single_values_platform = platform_single_values(single_sorted)
multi_values_platform = bar_chart_by_platform_multi(multi_sorted)
multi_values_platform_no_startup = bar_chart_by_platform_multi(multi_no_startup_sorted)
multi_values_wc_extra = platform_single_values_wc_extra(wc_extra_sorted)
ai_multi_values_platform = bar_chart_by_platform_multi(ai_multi_sorted)
platforms_single = ["K0s", "K3s"]
platforms_multi = ["K0s", "K3s", "KubeEdge"]

create_bar_plot(
    platforms_single,
    0.09,
    single_values_platform,
    "Orchestration cost by platform for single-node tests",
    50,
    115,
    3,
    fig_platform_single,
    bar_font_size=7,
)
create_bar_plot(
    platforms_multi,
    0.09,
    multi_values_platform,
    "Orchestration cost by platform for multi-node tests",
    70,
    210,
    3,
    fig_platform_multi,
)
create_bar_plot(
    platforms_multi,
    0.09,
    multi_values_platform_no_startup,
    "Orchestration cost by platform for multi-node tests without startup times",
    50,
    130,
    3,
    fig_platform_multi_no_startup,
)
create_bar_plot(
    platforms_single,
    0.07,
    multi_values_wc_extra,
    "Orchestration cost by platform for additional measurements with wasmCloud",
    50,
    145,
    3,
    fig_platform_multi_wc_extra,
)
create_bar_plot(
    platforms_multi,
    0.15,
    ai_multi_values_platform,
    "Orchestration cost by platform for multi-node tests with real-world workload",
    100,
    240,
    3,
    fig_platform_multi_ai,
    bar_font_size=7,
)


# ***** Bar charts by orchestrator *****
orchestrators = [
    "native container",
    "Knative",
    "Spin container",
    "Spin native",
    "wasmCloud",
]
orchestrators_mask = [
    "native container",
    "Knative",
    "Spin container",
    None,
    "wasmCloud",
]
single_values_orchestrator = orchestrator_single_values(single_sorted)
multi_values_orchestrator = orchestrator_multi_values(multi_sorted)
ai_multi_values_orchestrator = orchestrator_multi_values(ai_multi_sorted)
create_bar_plot(
    orchestrators,
    0.2,
    single_values_orchestrator,
    "Orchestration cost by orchestrators for single-node tests",
    60,
    115,
    4,
    fig_orchestrator_single,
    bar_font_size=7,
)
create_bar_plot(
    orchestrators,
    0.15,
    multi_values_orchestrator,
    "Orchestration cost by orchestrators for multi-node tests",
    70,
    210,
    3,
    fig_orchestrator_multi,
)
create_bar_plot(
    orchestrators,
    0.3,
    ai_multi_values_orchestrator,
    "Orchestration cost by orchestrators for multi-node tests with real-world workload",
    100,
    240,
    3,
    fig_orchestrator_multi_ai,
    bar_font_size=7,
)

# ***** Curve plots *****
create_line_plot(
    orchestrators,
    single_values_orchestrator,
    "Orchestration cost by orchestrators for single-node tests",
    60,
    125,
    3,
    fig_orchestrator_single_curve,
)

create_line_plot(
    orchestrators,
    multi_values_orchestrator,
    "Orchestration cost by orchestrators for multi-node tests",
    40,
    220,
    3,
    fig_orchestrator_multi_curve,
)

create_line_plot(
    orchestrators,
    ai_multi_values_orchestrator,
    "Orchestration cost by orchestrators for multi-node tests with real-world workload",
    100,
    240,
    3,
    fig_orchestrator_multi_curve_ai,
)
