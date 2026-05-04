import sys
import pandas as pd
import matplotlib.pyplot as plt
import os

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))
from . import statistics_utils
from . import curve_utils
from . import print_utils
import definitions


def __check_folder_basedir(base_dir, stats_dir):
    folder = f"{base_dir}/{stats_dir}"
    print(f"Reading data from {folder}")
    empty = True
    for _ in os.scandir(folder):
        empty = False
        break
    if empty:
        print("No data files found")
        sys.exit(0)
    return folder


# Prints hey stats
def __hey_stats(hey_file):
    # Load CSV file
    df = pd.read_csv(hey_file)

    # Aggregate response-time statistics
    response_stats = {
        "average": df["response-time"].mean(),
        "median": df["response-time"].median(),
        "min": df["response-time"].min(),
        "max": df["response-time"].max(),
    }

    # Count occurrences of each status code
    status_code_counts = df["status-code"].value_counts().sort_index()

    print("Response Time Statistics:")
    for k, v in response_stats.items():
        print(f"  {k}: {v:.6f}")

    print("\nStatus Code Counts:")
    for i, v in status_code_counts.items():
        print(f"Status code {i}: {v}")

    # Empty line
    print()

    # Percentiles to compute
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    # Calculate percentiles
    # Taking a column yields series, taking quantile of series yields series
    pct_values = df["response-time"].quantile([p / 100 for p in percentiles])
    print("Response time Percentiles")
    for i, v in pct_values.items():
        print(f"percentile {i}: {v}s")

    print()


# Forms a latex table row from given hey-file and returns it
def __hey_stats_latex(hey_file, title):
    # Load CSV file
    df = pd.read_csv(hey_file)

    row = title
    row = f"{row} & {round(df["response-time"].mean(), 4)}"
    row = f"{row} & {round(df["response-time"].median(), 4)}"
    row = f"{row} & {round(df["response-time"].min(), 4)}"
    row = f"{row} & {round(df["response-time"].max(), 4)}"

    # Maybe we don't need percentiles
    # percentiles = [1, 25, 50, 75, 99]
    # Calculate percentiles
    # Taking a column yields series, taking quantile of series yields series
    # pct_values = df["response-time"].quantile([p / 100 for p in percentiles])
    # for i, v in pct_values.items():
    #     row = f"{row} & {v}"

    row = f"{row} \\\\\n"
    return row


# forms matplotlib figure of the hey stats and saves it if need
def __hey_plot(hey_file, name, save, plot_title):
    # Load CSV file
    df = pd.read_csv(hey_file)
    # Percentiles to compute
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    # Calculate percentiles
    # Taking a column yields series, taking quantile of series yields series
    heyfig, heyaxes = plt.subplots(1, 1, constrained_layout=True)
    pct_values = df["response-time"].quantile([p / 100 for p in percentiles])
    heyaxes.bar([f"p{int(p * 100)}" for p in pct_values.index], pct_values.to_numpy())
    heyaxes.set_xlabel("Percentile")
    heyaxes.set_ylabel("Response Time (s)")
    heyaxes.set_title("Response Time Percentiles")
    heyfig.suptitle(plot_title)
    if save:
        plt.savefig(f"{definitions.FIGURE_DIR}/{name}.png")
    plt.show()


def __create_curve(name, figtitle, save, file, cpu_curve, show_legend, title=""):
    fig_size = (definitions.PLOT_WIDTH, 2 * definitions.PLOT_HEIGHT)
    fig, ax = plt.subplots(2, 1, layout="constrained", figsize=fig_size, sharey=True)
    curve_utils.create_curve(file, cpu_curve, ax[0], ax[1], "", show_legend, title)

    fig.suptitle(figtitle)
    if save:
        plt.savefig(f"{definitions.FIGURE_DIR}/{name}.png")
    plt.show()


def __create_int_curve(name, figtitle, save, file, show_legend, title=""):
    fig_size = (definitions.PLOT_WIDTH, 2 * definitions.PLOT_HEIGHT)
    fig, ax = plt.subplots(1, 1, layout="constrained", figsize=fig_size, sharey=True)
    curve_utils.create_int_curve(file, ax, show_legend, title)

    fig.suptitle(figtitle)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.1), ncols=3, handleheight=2)

    if save:
        plt.savefig(f"{definitions.FIGURE_DIR}/{name}.png")
    plt.show()


def create_curves(base_dir, stats_dir, multi):
    """
    Creates multiple curves visualizing the scenario 2 data in given stats dir.
    Note, that this can be made to also save the figures into files, but it
    requires changing the variable in the script.

        base_dir - the dir where stats_dir is located
        stats_dir - statistics dir
        multi - whether it is multi or single-node test
    """
    SAVE_FIGURES = False
    folder = __check_folder_basedir(base_dir, stats_dir)

    hey_file = f"{folder}/hey.csv"
    int_file = f"{folder}/interface.csv"
    perf_file = f"{folder}/perf.csv"

    __hey_plot(hey_file, "sc2-hey", True, stats_dir)

    if multi:
        worker_perf_file = f"{folder}/worker-perf.csv"
        worker_int_file = f"{folder}/worker-int.csv"
        __create_curve(
            f"sc2-control-perf",
            stats_dir,
            SAVE_FIGURES,
            perf_file,
            True,
            False,
            f"control",
        )
        __create_curve(
            f"sc2-control-mem",
            stats_dir,
            SAVE_FIGURES,
            perf_file,
            False,
            False,
            f"control",
        )
        __create_curve(
            f"sc2-worker-perf",
            stats_dir,
            SAVE_FIGURES,
            worker_perf_file,
            True,
            False,
            f"worker",
        )
        __create_curve(
            f"sc2-worker-mem",
            stats_dir,
            SAVE_FIGURES,
            worker_perf_file,
            False,
            False,
            f"worker",
        )

        __create_int_curve(
            f"sc2-control-int", stats_dir, SAVE_FIGURES, int_file, True, "control"
        )
        __create_int_curve(
            f"sc2-worker-int", stats_dir, SAVE_FIGURES, worker_int_file, True, "worker"
        )
    else:
        __create_curve(
            f"sc2-control-perf",
            stats_dir,
            SAVE_FIGURES,
            perf_file,
            True,
            False,
            f"control",
        )
        __create_curve(
            f"sc2-control-mem",
            stats_dir,
            SAVE_FIGURES,
            perf_file,
            False,
            False,
            f"worker",
        )


def parse_stats(base_dir, stats_dir, multi):
    """
    Parses statistics from the statistics dir and prints them.

        base_dir - the dir where stats_dir is located
        stats_dir - the data directory
        multi - whether to print worker stats or not
    """
    folder = __check_folder_basedir(base_dir, stats_dir)

    hey_file = f"{folder}/hey.csv"
    int_file = f"{folder}/interface.csv"
    perf_file = f"{folder}/perf.csv"
    worker_perf_file = f"{folder}/worker-perf.csv"
    worker_int_file = f"{folder}/worker-int.csv"

    __hey_stats(hey_file)

    print_utils.print_purple(f"Performance data {stats_dir}:")
    statistics_utils.calculate_and_print_perf([perf_file], multi, "control")
    print_utils.print_purple(f"Interface data {stats_dir}:")
    statistics_utils.calculate_and_print_int([int_file], "control")

    if multi:
        print_utils.print_purple(f"Performance data {stats_dir}:")
        statistics_utils.calculate_and_print_perf([worker_perf_file], multi, "worker")
        print_utils.print_purple(f"Interface data {stats_dir}:")
        statistics_utils.calculate_and_print_int([worker_int_file], "worker")


def print_latex(
    base_dir,
    stats_dir,
    multi,
    single_hey,
    multi_hey,
    single_perf,
    single_int,
    multi_control_perf,
    multi_worker_perf,
    multi_control_int,
    multi_worker_int,
):
    """
    Parses statistics from the statistics dir and format them as latex table and
    save to the given files. Single- and multi-node files need to be given
    separately, as we want to have separate files for multi-node data and
    single-node data.

        base_dir - the dir where stats_dir is located
        stats_dir - the data directory
        multi - whether to print worker stats or not
        single_hey - save file for single-node hey data
        multi_hey - save file for multi-node hey data
        single_perf - save file for single-node perf data
        single_int - save file for single-node interface data
        multi_control_perf - save file for control plane perf data with multiple nodes
        multi_worker_perf - save file for worker node perf data with multiple nodes
        multi_control_int - save file for control plane interface data with multiple nodes
        multi_worker_int - save file for worker node interface data with multiple nodes
    """
    folder = __check_folder_basedir(base_dir, stats_dir)

    hey_file = f"{folder}/hey.csv"
    int_file = f"{folder}/interface.csv"
    perf_file = f"{folder}/perf.csv"
    worker_perf_file = f"{folder}/worker-perf.csv"
    worker_int_file = f"{folder}/worker-int.csv"

    if multi:
        with open(multi_hey, "a", encoding="utf-8") as f:
            f.write(__hey_stats_latex(hey_file, stats_dir))

        with open(multi_control_perf, "a", encoding="utf-8") as f:
            f.write(statistics_utils.get_latex_row_perf([perf_file], f"{stats_dir}"))
        with open(multi_worker_perf, "a", encoding="utf-8") as f:
            f.write(
                statistics_utils.get_latex_row_perf([worker_perf_file], f"{stats_dir}")
            )

        with open(multi_control_int, "a", encoding="utf-8") as f:
            f.write(statistics_utils.get_latex_row_int([int_file], f"{stats_dir}"))
        with open(multi_worker_int, "a", encoding="utf-8") as f:
            f.write(
                statistics_utils.get_latex_row_int([worker_int_file], f"{stats_dir}")
            )
    else:
        with open(single_hey, "a", encoding="utf-8") as f:
            f.write(__hey_stats_latex(hey_file, stats_dir))
        with open(single_perf, "a", encoding="utf-8") as f:
            f.write(statistics_utils.get_latex_row_perf([perf_file], f"{stats_dir}"))
        with open(single_int, "a", encoding="utf-8") as f:
            f.write(statistics_utils.get_latex_row_int([int_file], f"{stats_dir}"))


def get_orch_cost_values(base_dir, stats_dir, metric: statistics_utils.OrchCostMetric):
    """
    Parses scenario 2 statistics and saves them to the metric-object.

        base_dir - the dir where stats_dir is located
        stats_dir - directory to read stats from
        metric - statistics_utils.OrchCostMetric object
    """
    folder = __check_folder_basedir(base_dir, stats_dir)

    perf_file = f"{folder}/perf.csv"
    worker_perf_file = f"{folder}/worker-perf.csv"

    if metric.multi_node():
        c_max_proc, c_max_glob, c_proc_rss, c_node_mem, _ = (
            statistics_utils.get_orch_cost_metrics([perf_file])
        )
        w_max_proc, w_max_glob, w_proc_rss, w_node_mem, node_max_mem = (
            statistics_utils.get_orch_cost_metrics([worker_perf_file])
        )
        max_proc = (c_max_proc + w_max_proc) / 2
        max_glob = (c_max_glob + w_max_glob) / 2
        proc_rss = (c_proc_rss + w_proc_rss) / 2
        node_mem = (c_node_mem + w_node_mem) / 2
    else:
        max_proc, max_glob, proc_rss, node_mem, node_max_mem = statistics_utils.get_orch_cost_metrics(
            [perf_file]
        )

    metric.process_max_cpu_scale = max_proc
    metric.node_max_cpu_scale = max_glob
    metric.process_rss_scale = proc_rss
    metric.node_mem_scale = node_mem
    metric.node_max_mem = node_max_mem


if __name__ == "__main__":
    folder = sys.argv[1]
    multi = sys.argv[2] == "true"
    create_curves(definitions.SC2_PATH, folder, multi)
    parse_stats(definitions.SC2_PATH, folder, multi)
