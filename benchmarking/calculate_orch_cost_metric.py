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

import tools.read_data_sc1
import tools.read_data_sc2
from tools.statistics_utils import OrchCostMetric

metrics = {}
all_files = []

parser = argparse.ArgumentParser(description="My Project CLI")
parser.add_argument("--show", action=argparse.BooleanOptionalAction, help="show images", default=True)
parser.add_argument("--save", action=argparse.BooleanOptionalAction, help="save images", default=False)
args = parser.parse_args()

# ***** Calculate the metrics *****
items = os.listdir(definitions.SC1_PATH)
for test_case in items:
    metric = metrics.get(test_case, OrchCostMetric(test_case=test_case))
    tools.read_data_sc1.get_orch_cost_values(test_case, metric)
    metrics[test_case] = metric

items = os.listdir(definitions.SC2_PATH)
for test_case in items:
    metric = metrics.get(test_case, OrchCostMetric(test_case=test_case))
    tools.read_data_sc2.get_orch_cost_values(test_case, metric)
    metrics[test_case] = metric

# Add dummy values for spin native kubeedge
metrics["spin-kubeedge-multi-native-go"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native-go"
)
metrics["spin-kubeedge-multi-native-rust"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native-rust"
)


single = pd.DataFrame(
    {
        "test_case": pd.Series(dtype="string"),
        "value": pd.Series(dtype="float"),
        "platform": pd.Series(dtype="string"),
        "orchestrator": pd.Series(dtype="string"),
        "language": pd.Series(dtype="string"),
    }
)
multi = pd.DataFrame(
    {
        "test_case": pd.Series(dtype="string"),
        "value": pd.Series(dtype="float"),
        "platform": pd.Series(dtype="string"),
        "orchestrator": pd.Series(dtype="string"),
        "language": pd.Series(dtype="string"),
    }
)
multi_no_startup = pd.DataFrame(
    {
        "test_case": pd.Series(dtype="string"),
        "value": pd.Series(dtype="float"),
        "platform": pd.Series(dtype="string"),
        "orchestrator": pd.Series(dtype="string"),
        "language": pd.Series(dtype="string"),
    }
)
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


# ***** Prepare save files *****
orch_cost_single_sorted = f"{definitions.LATEX_TABLE_LOC}/orch-cost-single-sorted.tex"
orch_cost_multi_sorted = f"{definitions.LATEX_TABLE_LOC}/orch-cost-multi-sorted.tex"
all_files = all_files + [orch_cost_multi_sorted, orch_cost_single_sorted]

fig_platform_single = f"{definitions.FIGURE_DIR}/orch_cost_platform_single.png"
fig_platform_multi = f"{definitions.FIGURE_DIR}/orch_cost_platform_multi.png"
fig_platform_multi_no_startup = f"{definitions.FIGURE_DIR}/orch_cost_platform_multi_no_startup.png"
fig_orchestrator_single = f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_single.png"
fig_orchestrator_multi = f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi.png"
fig_orchestrator_single_curve = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_single_curve.png")
fig_orchestrator_multi_curve = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi_curve.png")
all_files = all_files + [
    fig_platform_single,
    fig_platform_multi,
    fig_platform_multi_no_startup,
    fig_orchestrator_single,
    fig_orchestrator_multi,
    fig_orchestrator_single_curve,
    fig_orchestrator_multi_curve,
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
with open(orch_cost_single_sorted, "w", encoding="utf-8") as f:
    f.write(
        "\\textbf{Test case} & \\textbf{Platform} & \\textbf{Orchestrator} & \\textbf{Orchestration cost} \\\\\n"
    )
    for row in single.sort_values(by="value").itertuples(index=False):
        f.write(
            f"{row.test_case} & {row.platform} & {row.orchestrator} & {row.value} \\\\\n"
        )

with open(orch_cost_multi_sorted, "w", encoding="utf-8") as f:
    f.write(
        "\\textbf{Test case} & \\textbf{Platform} & \\textbf{Orchestrator} & \\textbf{Orchestration cost} \\\\\n"
    )
    for row in multi.sort_values(by="value").itertuples(index=False):
        f.write(
            f"{row.test_case} & {row.platform} & {row.orchestrator} & {row.value} \\\\\n"
        )


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
    hatch_cycle = itertools.cycle([
        "////",
        "...",
        "\\\\\\\\",
        "oo",
        "||||",
        "OO",
        "----",
        "xxx",
        "+++",
        "**"
    ])
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

    # Add some text for labels, title and custom x-axis tick labels, etc.
    group_size = len(value_tuples)
    # ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x + (math.floor(group_size / 2) - 0.5) * width, x_labels)
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
    for i in range(0, int(len(sorted) / 5)):
        row = sorted.iloc[i]
        row2 = sorted.iloc[i + 6]
        row3 = sorted.iloc[i + 12]
        row4 = sorted.iloc[i + 18]
        row5 = sorted.iloc[i + 24]
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
plt.rcParams.update({
    "font.size": font_size,
    "axes.titlesize": font_size,
    "axes.labelsize": font_size,
    "xtick.labelsize": font_size,
    "ytick.labelsize": font_size,
    "legend.fontsize": font_size,
})

# ***** Create figures *****
single_sorted = single.sort_values(["test_case", "platform"])
multi_sorted = multi.sort_values(["test_case", "platform"])
multi_no_startup_sorted = multi_no_startup.sort_values(["test_case", "platform"])
print(single_sorted)
print(multi_sorted)

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
