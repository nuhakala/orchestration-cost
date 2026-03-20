import glob
import re
import sys
import matplotlib.pyplot as plt
import os

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools"))
sys.path.insert(0, os.path.abspath("."))
import definitions
from tools import curve_utils
from tools import statistics_utils


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



def __startup_times(folder):
    median, average = statistics_utils.startup_time_indicators(folder)
    print(f"Average startup value: {average}, median {median}")


def startup_times_latex(folder, row_title):
    median, average = statistics_utils.startup_time_indicators(folder)
    row = f"{row_title} & {average} & {median} \\\\\n"
    return row


def __create_curve(name, figtitle, save, files, cpu_curve, show_legend, title=""):
    fig_size=(definitions.PLOT_WIDTH, 2 * definitions.PLOT_HEIGHT)
    fig, ax = plt.subplots(2, 1, layout="constrained", figsize=fig_size, sharey=True)
    for file in files:
        label = re.findall(r"\d+", file)[-1]
        curve_utils.create_curve(file, cpu_curve, ax[0], ax[1], label, show_legend, title)

    fig.suptitle(figtitle)
    if save:
        plt.savefig(f"{definitions.FIGURE_DIR}/{name}.png")
    plt.show()


def create_curves(base_dir, stats_dir, multi):
    """
    Creates curves from the statistics dir using matplotlib. Note that this
    method can also save the figures into files, but it requires changing the
    variable in the script.

        stats_dir - the data directory
        multi - whether it is multi-node test or not, affects the # of curves
    """
    SAVE_FIGURES = False
    folder = __check_folder_basedir(base_dir, stats_dir)

    perf_files = glob.glob(f"{folder}/[0-9]-perf.csv")
    if multi:
        worker_perf_files = glob.glob(f"{folder}/[0-9]-worker-perf.csv")
        __create_curve(f"sc1-control-perf", stats_dir, SAVE_FIGURES, perf_files, True, True, f"control")
        __create_curve(f"sc1-control-memory", stats_dir, SAVE_FIGURES, perf_files, False, True, "control")
        __create_curve(f"sc1-worker-perf", stats_dir, SAVE_FIGURES, worker_perf_files, True, True, "worker")
        __create_curve(f"sc1-worker-memory", stats_dir, SAVE_FIGURES, worker_perf_files, False, True, "worker")
    else:
        __create_curve("sc1-control-perf.png", stats_dir, SAVE_FIGURES, perf_files, True, True, "control")
        __create_curve("sc1-control-memory.png", stats_dir, SAVE_FIGURES, perf_files, False, True, "control")


def parse_stats(base_dir, stats_dir, multi):
    """
    Parses statistics from the statistics dir and prints them.

        stats_dir - the data directory
        multi - whether to print worker stats or not
    """
    folder = __check_folder_basedir(base_dir, stats_dir)

    __startup_times(folder)

    perf_files = glob.glob(f"{folder}/[0-9]-perf.csv")
    worker_perf_files = glob.glob(f"{folder}/[0-9]-worker-perf.csv")
    if multi:
        statistics_utils.calculate_and_print_perf(perf_files, multi, "control")
    statistics_utils.calculate_and_print_perf(worker_perf_files, multi, "worker")


def print_latex_startup_table(
    base_dir,
    stats_dir,
    filename,
    ):
    folder = __check_folder_basedir(base_dir, stats_dir)

    with open(filename, "a", encoding="utf-8") as f:
        f.write(startup_times_latex(folder, stats_dir))


def print_latex_table_row(
    base_dir,
    stats_dir,
    multi,
    single_startup,
    multi_startup,
    single_perf,
    multi_control,
    multi_worker
):
    """
    Parses statistics from the statistics dir and format them as latex table and
    save to the given files. Single- and multi-node files need to be given
    separately, as we want to have separate files for multi-node data and
    single-node data.

        base_dir - the dir where stats_dir is located
        stats_dir - the data directory
        multi - whether to print worker stats or not
        single_startup - save file for single-node startup data
        multi_startup - save file for multi-node startup data
        single_perf - save file for single-node perf data
        multi_control - save file for control plane perf data with multiple nodes
        multi_worker - save file for worker node perf data with multiple nodes
    """
    folder = __check_folder_basedir(base_dir, stats_dir)

    perf_files = glob.glob(f"{folder}/[0-9]-perf.csv")
    worker_perf_files = glob.glob(f"{folder}/[0-9]-worker-perf.csv")
    if multi:
        with open(multi_control, "a", encoding="utf-8") as f:
            f.write(statistics_utils.get_latex_row_perf(perf_files, f"{stats_dir}"))
        with open(multi_worker, "a", encoding="utf-8") as f:
            f.write(statistics_utils.get_latex_row_perf(worker_perf_files, f"{stats_dir}"))
        with open(multi_startup, "a", encoding="utf-8") as f:
            f.write(startup_times_latex(folder, stats_dir))
    else:
        with open(single_perf, "a", encoding="utf-8") as f:
            f.write(statistics_utils.get_latex_row_perf(perf_files, f"{stats_dir}"))
        with open(single_startup, "a", encoding="utf-8") as f:
            f.write(startup_times_latex(folder, stats_dir))


def get_orch_cost_values(base_dir, stats_dir, metric: statistics_utils.OrchCostMetric):
    """
    Parses scenario 1 statistics and saves them to the metric-object.

        base_dir - the dir where stats_dir is located
        stats_dir - directory to read stats from
        metric - statistics_utils.OrchCostMetric object
    """
    folder = __check_folder_basedir(base_dir, stats_dir)
    startup_median, _ = statistics_utils.startup_time_indicators(folder)
    metric.startup = startup_median
    if metric.multi_node():
        perf_files = glob.glob(f"{folder}/[0-9]-perf.csv")
        c_max_proc, c_max_glob, c_proc_rss = statistics_utils.get_orch_cost_metrics(perf_files)
        worker_perf_files = glob.glob(f"{folder}/[0-9]-worker-perf.csv")
        w_max_proc, w_max_glob, w_proc_rss = statistics_utils.get_orch_cost_metrics(worker_perf_files)
        max_proc = (c_max_proc + w_max_proc) / 2
        max_glob = (c_max_glob + w_max_glob) / 2
        proc_rss = (c_proc_rss + w_proc_rss) / 2
    else:
        perf_files = glob.glob(f"{folder}/[0-9]-perf.csv")
        max_proc, max_glob, proc_rss = statistics_utils.get_orch_cost_metrics(perf_files)

    metric.process_max_cpu_deploy = max_proc
    metric.node_max_cpu_deploy = max_glob
    metric.process_rss_deploy = proc_rss


if __name__ == "__main__":
    folder = sys.argv[1]
    multi = sys.argv[2] == "true"
    create_curves(definitions.SC1_PATH, folder, multi)
    parse_stats(definitions.SC1_PATH, folder, multi)
