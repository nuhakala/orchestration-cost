"""
This file provides utility functions for handling orchestration cost data and
plotting the data with matplotlib.
"""

import itertools
import math
import os
import pandas as pd
from pandas.io.formats.style import plt
from tables import np
import definitions
import tools.read_data_sc1
import tools.read_data_sc2
from tools.statistics_utils import OrchCostMetric


ORCHESTRATORS = [
    "container",
    "Knative",
    "Spin cont",
    "Spin native",
    "wasmCloud",
]
PLATFORMS_MULTI = ["K0s", "K3s", "KubeEdge"]
PLATFORMS_SINGLE = ["K0s", "K3s"]


def parse_folders(folder, scenario, metrics_store, multi, single, all):
    items = os.listdir(folder)
    for test_case in items:
        metric = metrics_store.get(test_case, OrchCostMetric(test_case=test_case))
        if scenario == 1:
            tools.read_data_sc1.get_orch_cost_values(folder, test_case, metric)
        else:
            tools.read_data_sc2.get_orch_cost_values(folder, test_case, metric)

        if multi and metric.multi_node():
            metrics_store[test_case] = metric
        elif single and not metric.multi_node():
            metrics_store[test_case] = metric
        elif all:
            metrics_store[test_case] = metric


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


def transform_to_df(m, df, metric_fn):
    for metric in m.values():
        test_case = metric.test_case_parsed()
        row = {
            "test_case": test_case,
            "value": metric_fn(metric),
            "platform": metric.platform(),
            "orchestrator": metric.orchestrator(),
            "language": metric.language(),
        }

        df.loc[len(df)] = row


def print_orch_cost_table(file, df, write_header, save):
    if save:
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
            print(
                f"{row.test_case} & {row.platform} & {row.orchestrator} & {row.value}"
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
    save: bool,
    show: bool,
    bar_font_size=5,
    ylabel="",
    legend_anchor=(0, -0.1),
    legend_height=2.0,
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
            ax.set_xticks(
                x + (math.floor(group_size / 2) - 0.5) * width + 0.5 * width, x_labels
            )

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if ylabel != "":
        ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=legend_anchor,
        ncols=ncols,
        handleheight=legend_height,
    )
    ax.set_ylim(ymin, ylim)
    ax.set_xmargin(0.01)

    if save:
        plt.savefig(save_location, bbox_inches="tight", pad_inches=0.03, format="pdf")
    if show:
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
    save: bool,
    show: bool,
    ylabel="",
    legend_anchor=(0, -0.1),
    legend_height=2.0,
    legend_width=2.0,
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

    if ylabel != "":
        ax.set_ylabel("Orchestration cost")
    ax.set_title(title)
    ax.set_xticks(x, x_labels)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=legend_anchor,
        ncols=ncols,
        handleheight=legend_height,
        handlelength=legend_width,
    )
    ax.set_ylim(ymin, ymax)

    if save:
        plt.savefig(save_location, bbox_inches="tight", pad_inches=0.03, format="pdf")
    if show:
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


def bar_chart_by_platform_multi(sorted, lang_in_name=True):
    orchestrator_values = {}
    for i in range(0, len(sorted), 3):
        row = sorted.iloc[i]
        row2 = sorted.iloc[i + 1]
        row3 = sorted.iloc[i + 2]
        key = f"{row.orchestrator}-{row.language}"
        if not lang_in_name:
            key = f"{row.orchestrator}"
        orchestrator_values[key] = (
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


def orchestrator_multi_values(sorted, lang_in_name=True):
    platform_values = {}
    period = int(len(sorted) / 5)
    for i in range(0, period):
        row = sorted.iloc[i]
        row2 = sorted.iloc[i + period]
        row3 = sorted.iloc[i + 2 * period]
        row4 = sorted.iloc[i + 3 * period]
        row5 = sorted.iloc[i + 4 * period]
        key = f"{row.platform}-{row.language}"
        if not lang_in_name:
            key = f"{row.platform}"
        platform_values[key] = (
            float(row["value"]),
            float(row2["value"]),
            float(row3["value"]),
            float(row4["value"]),
            float(row5["value"]),
        )
    return platform_values
