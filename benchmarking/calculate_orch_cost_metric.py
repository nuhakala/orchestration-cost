"""
This file calculates the orchestration cost using data under ./data

It saves figures to folder defined in definitions.FIGURE_DIR

By default it won't save any figures, instead it shows them immediately. Give
command line flag --save to save files. Preview can be disabled with --no-show

There are two targets thesis and paper. They produce different figures.
"""

import argparse
import os

from tables.leaf import math
from tools.orch_cost_utils import (
    ORCHESTRATORS,
    PLATFORMS_MULTI,
    PLATFORMS_SINGLE,
    bar_chart_by_platform_multi,
    create_bar_plot,
    create_line_plot,
    orchestrator_multi_values,
    orchestrator_single_values,
    parse_folders,
    create_pd_df,
    platform_single_values,
    platform_single_values_wc_extra,
    print_orch_cost_table,
    transform_to_df,
)
import definitions
import matplotlib.pyplot as plt

from tools.extra_wc_data import get_extra_orch_cost_means
import tools.read_data_sc1
import tools.read_data_sc2
from tools.statistics_utils import OrchCostMetric

metrics_single = {}
metrics_multi = {}
ai_metrics = {}
wc_extra_metrics = {}
all_files = []

parser = argparse.ArgumentParser(description="My Project CLI")
parser.add_argument("target", choices=["thesis", "paper"], help="Choose target")
parser.add_argument(
    "--show", action=argparse.BooleanOptionalAction, help="show images", default=True
)
parser.add_argument(
    "--save", action=argparse.BooleanOptionalAction, help="save images", default=False
)
args = parser.parse_args()


# ***** Calculate the metrics *****
parse_folders(definitions.SC1_PATH, 1, metrics_multi, True, False, False)
parse_folders(definitions.SC1_PATH, 1, metrics_single, False, True, False)
parse_folders(definitions.SC2_PATH, 2, metrics_multi, True, False, False)
parse_folders(definitions.SC2_PATH, 2, metrics_single, False, True, False)
parse_folders(definitions.AI_SC1, 1, ai_metrics, False, False, True)
parse_folders(definitions.AI_SC2, 2, ai_metrics, False, False, True)


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
metrics_multi["spin-kubeedge-multi-native-go"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native-go"
)
metrics_multi["spin-kubeedge-multi-native-rust"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native-rust"
)
ai_metrics["spin-kubeedge-multi-native-go"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native"
)
ai_metrics["spin-kubeedge-multi-native-go"] = OrchCostMetric(
    test_case="spin-kubeedge-multi-native"
)


single = create_pd_df()
multi = create_pd_df()
multi_no_startup = create_pd_df()
wc_extra = create_pd_df()
ai_multi = create_pd_df()
ai_multi_paper = create_pd_df()
multi_paper = create_pd_df()


transform_to_df(metrics_single, single, lambda metric: metric.calculate_metric())
transform_to_df(metrics_multi, multi, lambda metric: metric.calculate_metric())
transform_to_df(
    metrics_multi,
    multi_no_startup,
    lambda metric: metric.calculate_metric_without_startup(),
)
transform_to_df(wc_extra_metrics, wc_extra, lambda metric: metric.calculate_metric())
transform_to_df(ai_metrics, ai_multi, lambda metric: metric.calculate_metric())
transform_to_df(ai_metrics, ai_multi_paper, lambda metric: metric.calculate_metric_paper_version())
transform_to_df(metrics_multi, multi_paper, lambda metric: metric.calculate_metric_paper_version())


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
all_files = all_files + [
    orch_cost_multi_sorted,
    orch_cost_single_sorted,
    orch_cost_ai_sorted,
]

fig_platform_single = f"{definitions.FIGURE_DIR}/orch_cost_platform_single.pdf"
fig_platform_multi = f"{definitions.FIGURE_DIR}/orch_cost_platform_multi.pdf"
fig_platform_multi_no_startup = ( f"{definitions.FIGURE_DIR}/orch_cost_platform_multi_no_startup.pdf")
fig_platform_multi_wc_extra = ( f"{definitions.FIGURE_DIR}/orch_cost_platform_multi_wc_extra.pdf")
fig_platform_multi_ai = f"{definitions.FIGURE_DIR}/orch_cost_platform_multi_ai.pdf"
fig_orchestrator_single = f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_single.pdf"
fig_orchestrator_multi = f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi.pdf"
fig_orchestrator_multi_ai = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi_ai.pdf")
fig_orchestrator_single_curve = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_single_curve.pdf")
fig_orchestrator_multi_curve = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi_curve.pdf")
fig_orchestrator_multi_curve_ai = ( f"{definitions.FIGURE_DIR}/orch_cost_orchestrator_multi_curve_ai.pdf")
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


if args.target == "thesis":
    print_orch_cost_table(orch_cost_single_sorted, single, True, args.save)
    print_orch_cost_table(orch_cost_multi_sorted, multi, True, args.save)
    # add wc_extra to same table, hence no header
    print_orch_cost_table(orch_cost_multi_sorted, wc_extra, False, args.save)
    print_orch_cost_table(orch_cost_ai_sorted, ai_multi, True, args.save)

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
    single_values_platform = platform_single_values(single_sorted)
    multi_values_platform = bar_chart_by_platform_multi(multi_sorted)
    multi_values_platform_no_startup = bar_chart_by_platform_multi(
        multi_no_startup_sorted
    )
    multi_values_wc_extra = platform_single_values_wc_extra(wc_extra_sorted)
    ai_multi_values_platform = bar_chart_by_platform_multi(ai_multi_sorted)

    create_bar_plot(
        PLATFORMS_SINGLE,
        0.09,
        single_values_platform,
        "Orchestration cost by platform for single-node tests",
        50,
        115,
        3,
        fig_platform_single,
        args.save,
        args.show,
        bar_font_size=7,
    )
    create_bar_plot(
        PLATFORMS_MULTI,
        0.09,
        multi_values_platform,
        "Orchestration cost by platform for multi-node tests",
        70,
        210,
        3,
        fig_platform_multi,
        args.save,
        args.show,
    )
    create_bar_plot(
        PLATFORMS_MULTI,
        0.09,
        multi_values_platform_no_startup,
        "Orchestration cost by platform for multi-node tests without startup times",
        50,
        130,
        3,
        fig_platform_multi_no_startup,
        args.save,
        args.show,
    )
    create_bar_plot(
        PLATFORMS_SINGLE,
        0.07,
        multi_values_wc_extra,
        "Orchestration cost by platform for additional measurements with wasmCloud",
        50,
        145,
        3,
        fig_platform_multi_wc_extra,
        args.save,
        args.show,
    )
    create_bar_plot(
        PLATFORMS_MULTI,
        0.15,
        ai_multi_values_platform,
        "Orchestration cost by platform for multi-node tests with real-world workload",
        100,
        240,
        3,
        fig_platform_multi_ai,
        args.save,
        args.show,
        bar_font_size=7,
    )

    # ***** Bar charts by orchestrator *****
    single_values_orchestrator = orchestrator_single_values(single_sorted)
    multi_values_orchestrator = orchestrator_multi_values(multi_sorted)
    ai_multi_values_orchestrator = orchestrator_multi_values(ai_multi_sorted)
    create_bar_plot(
        ORCHESTRATORS,
        0.2,
        single_values_orchestrator,
        "Orchestration cost by orchestrators for single-node tests",
        60,
        115,
        4,
        fig_orchestrator_single,
        args.save,
        args.show,
        bar_font_size=7,
    )
    create_bar_plot(
        ORCHESTRATORS,
        0.15,
        multi_values_orchestrator,
        "Orchestration cost by orchestrators for multi-node tests",
        70,
        210,
        3,
        fig_orchestrator_multi,
        args.save,
        args.show,
    )
    create_bar_plot(
        ORCHESTRATORS,
        0.3,
        ai_multi_values_orchestrator,
        "Orchestration cost by orchestrators for multi-node tests with real-world workload",
        100,
        240,
        3,
        fig_orchestrator_multi_ai,
        args.save,
        args.show,
        bar_font_size=7,
    )

    # ***** Curve plots *****
    create_line_plot(
        ORCHESTRATORS,
        single_values_orchestrator,
        "Orchestration cost by orchestrators for single-node tests",
        60,
        125,
        3,
        fig_orchestrator_single_curve,
        args.save,
        args.show,
    )

    create_line_plot(
        ORCHESTRATORS,
        multi_values_orchestrator,
        "Orchestration cost by orchestrators for multi-node tests",
        40,
        220,
        3,
        fig_orchestrator_multi_curve,
        args.save,
        args.show,
    )

    create_line_plot(
        ORCHESTRATORS,
        ai_multi_values_orchestrator,
        "Orchestration cost by orchestrators for multi-node tests with real-world workload",
        100,
        240,
        3,
        fig_orchestrator_multi_curve_ai,
        args.save,
        args.show,
    )


else:
    multi_paper_no_go = multi_paper.loc[multi_paper["language"] == "rust"]

    print_orch_cost_table(orch_cost_ai_sorted, ai_multi_paper, True, args.save)
    print_orch_cost_table(orch_cost_multi_sorted, multi_paper_no_go, True, args.save)

    font_size = 8
    plt.rcParams.update(
        {
            "font.size": font_size,
            "font.family": "serif",
            "font.serif": "Times New Roman",
            "axes.titlesize": font_size,
            "axes.labelsize": font_size,
            "xtick.labelsize": font_size,
            "ytick.labelsize": font_size,
            "legend.fontsize": font_size,
        }
    )
    ai_multi_sorted = ai_multi_paper.sort_values(["test_case", "platform"])
    multi_sorted = multi_paper_no_go.sort_values(["test_case", "platform"])
    ai_multi_values_orchestrator = orchestrator_multi_values(ai_multi_sorted, False)
    ai_multi_values_platform = bar_chart_by_platform_multi(ai_multi_sorted, False)
    multi_values_orchestrator = orchestrator_multi_values(multi_sorted, False)

    if not args.save:
        print("AI Multi sorted")
        print(ai_multi_sorted)
        print()
        print("Multi sorted no Golang data")
        print(multi_sorted)
        print()
        print("Multi sorted all")
        print(multi_paper.sort_values(["test_case", "platform"]))
        print()

    max = 280
    min = 160
    legend_anchor = (-0.02, -0.11)
    legend_height = 1.5

    create_bar_plot(
        ORCHESTRATORS,
        0.3,
        ai_multi_values_orchestrator,
        "Orchestration Cost by orchestrators for real-world workload",
        min,
        max,
        3,
        fig_orchestrator_multi_ai,
        args.save,
        args.show,
        bar_font_size=8,
        legend_anchor=legend_anchor,
        legend_height=legend_height,
    )

    create_bar_plot(
        PLATFORMS_MULTI,
        0.15,
        ai_multi_values_platform,
        "Orchestration Cost by platforms for real-world workload",
        min,
        max,
        3,
        fig_platform_multi_ai,
        args.save,
        args.show,
        bar_font_size=8,
        legend_anchor=legend_anchor,
        legend_height=legend_height,
    )

    create_line_plot(
        ORCHESTRATORS,
        ai_multi_values_orchestrator,
        "Orchestration Cost by orchestrators for real-world workload",
        min,
        max - 10,
        3,
        fig_orchestrator_multi_curve_ai,
        args.save,
        args.show,
        legend_anchor=legend_anchor,
        legend_height=legend_height,
        legend_width=4.5,
    )

    create_bar_plot(
        ORCHESTRATORS,
        0.3,
        multi_values_orchestrator,
        "Orchestration Cost by orchestrators for artificial workload",
        min - 30,
        max,
        3,
        fig_orchestrator_multi,
        args.save,
        args.show,
        legend_anchor=legend_anchor,
        legend_height=legend_height,
        bar_font_size=8,
    )
