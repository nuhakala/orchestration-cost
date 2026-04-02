import glob
from math import nan
import sys
import pandas as pd
from dataclasses import dataclass

from .print_utils import print_purple


@dataclass
class OrchCostMetric:
    test_case: str = ""
    process_max_cpu_deploy: float = 0
    process_max_cpu_scale: float = 0
    node_max_cpu_deploy: float = 0
    node_max_cpu_scale: float = 0
    process_rss_deploy: float = 0
    process_rss_scale: float = 0
    node_mem_deploy: float = 0
    node_mem_scale: float = 0
    startup: float = 0

    def multi_node(self):
        if "multi" in self.test_case:
            return True
        else:
            return False

    def language(self):
        if "go" in self.test_case:
            return "go"
        else:
            return "rust"

    def platform(self):
        if "k3s" in self.test_case:
            return "K3s"
        if "k0s" in self.test_case:
            return "K0s"
        if "kubeedge" in self.test_case:
            return "KubeEdge"
        return ""

    def orchestrator(self):
        if "-native" in self.test_case:
            return "spin-native"
        if "-container" in self.test_case:
            return "spin-container"
        if "knative" in self.test_case:
            return "knative"
        if "wc" in self.test_case:
            return "wasmCloud"
        if "container" in self.test_case:
            return "container"
        return ""

    def test_case_parsed(self):
        res = self.test_case
        # Remove platform and orchestrator from the test case
        res = res.replace(r"-k3s", "")
        res = res.replace(r"-k0s", "")
        res = res.replace(r"-kubeedge", "")

        res = res.replace(r"-spin", "")
        res = res.replace(r"-knative", "")
        res = res.replace(r"-wc", "")
        res = res.replace(r"-container", "")

        res = res.replace(r"-multi", "")
        res = res.replace(r"-single", "")

        # Fix spin naming
        res = res.replace(r"spin-rust", "spin-cont-rust")
        res = res.replace(r"spin-go", "spin-cont-go")
        if res == "spin":
            res = "spin-cont"
        return res

    def calculate_metric_without_startup(self):
        res = (
            self.process_max_cpu_deploy
            * self.process_max_cpu_scale
            * self.node_max_cpu_deploy
            * self.node_max_cpu_scale
            * self.process_rss_deploy
            * self.process_rss_scale
        )
        root = res ** (1 / 6)
        if root == 0:
            return nan
        return round(root, 2)

    def calculate_metric(self):
        res = (
            self.process_max_cpu_deploy
            * self.process_max_cpu_scale
            * self.node_max_cpu_deploy
            * self.node_max_cpu_scale
            * self.process_rss_deploy
            * self.process_rss_scale
            * self.startup
        )
        root = res ** (1 / 7)
        if root == 0:
            return nan
        return round(root, 2)

    def calculate_metric_paper_version(self):
        res = (
            self.process_max_cpu_deploy
            * self.process_max_cpu_scale
            * self.node_max_cpu_deploy
            * self.node_max_cpu_scale
            * self.process_rss_deploy
            * self.process_rss_scale
            * self.node_mem_deploy
            * self.node_mem_scale
            # * self.startup
        )
        root = res ** (1 / 8)
        if root == 0:
            return nan
        return round(root, 2)


def __get_empty_perf_df():
    return pd.DataFrame(
        {
            "mean_idle_proc": pd.Series(dtype="float"),
            "median_idle_proc": pd.Series(dtype="float"),
            "third_quantile_idle_proc": pd.Series(dtype="float"),
            "max_proc": pd.Series(dtype="float"),
            "mean_idle_glob": pd.Series(dtype="float"),
            "median_idle_glob": pd.Series(dtype="float"),
            "third_quantile_idle_glob": pd.Series(dtype="float"),
            "max_glob": pd.Series(dtype="float"),
            "proc_rss": pd.Series(dtype="float"),
            "mem_total": pd.Series(dtype="float"),
            "mem_used": pd.Series(dtype="float"),
        }
    )


def __get_empty_int_df():
    return pd.DataFrame(
        {
            "sent_mean": pd.Series(dtype="float"),
            "sent_median": pd.Series(dtype="float"),
            "received_mean": pd.Series(dtype="float"),
            "received_median": pd.Series(dtype="float"),
            "total_mean": pd.Series(dtype="float"),
            "total_median": pd.Series(dtype="float"),
        }
    )


def __append_file_stats(file: str, data: pd.DataFrame):
    df = pd.read_csv(file)

    # Identify process CPU and RSS columns
    cpu_cols = [c for c in df.columns if c.endswith("/cpu")]
    rss_cols = [c for c in df.columns if c.endswith("/rss")]

    # Aggregate process columns
    df["proc_cpu"] = df[cpu_cols].sum(axis=1)
    df["proc_rss"] = df[rss_cols].sum(axis=1)

    # Compute differences between consecutive rows
    diff_df = df.diff()

    # Keep original time column for x-axis
    diff_df["time"] = df["time"]

    # Drop first row (diff is NaN)
    # Drop first two seconds as well, they often contain error
    # Drop last two seconds too
    diff_df = diff_df.iloc[3:-2]

    diff_df["glob_perc"] = (diff_df["total"] - diff_df["idle"]) / diff_df["total"] * 100
    diff_df["proc_cpu_perc"] = diff_df["proc_cpu"] / diff_df["total"] * 100

    # Get idle period to calculate avg usage
    idle_df = diff_df.iloc[150:250]

    # Transform values into megabytes
    df["mem_total"] = df["mem_total"] / 1024
    df["mem_free"] = df["mem_free"] / 1024
    df["proc_rss"] = df["proc_rss"] / 1024

    row = {
        "mean_idle_proc": round(idle_df["proc_cpu_perc"].mean(), 2),
        "median_idle_proc": round(idle_df["proc_cpu_perc"].median(), 2),
        "third_quantile_idle_proc": round(idle_df["proc_cpu_perc"].quantile(0.75), 2),
        "max_proc": round(diff_df["proc_cpu_perc"].max(), 2),
        "mean_idle_glob": round(idle_df["glob_perc"].mean(), 2),
        "median_idle_glob": round(idle_df["glob_perc"].median(), 2),
        "third_quantile_idle_glob": round(idle_df["glob_perc"].quantile(0.75), 2),
        "max_glob": round(diff_df["glob_perc"].max(), 2),
        "proc_rss": round(df["proc_rss"].mean(), 2),
        "mem_total": round(df["mem_total"].mean(), 2),
        "mem_used": round((df["mem_total"] - df["mem_free"]).mean(), 2),
    }

    data.loc[len(data)] = row


def __append_int_stats(file: str, data: pd.DataFrame):
    df = pd.read_csv(file)
    # Total column is actually included in the data. But it is recorded there
    # wrong, so I recalculate it here.
    df["total"] = df["sent"] + df["received"]

    # Compute differences between consecutive rows
    diff_df = df.diff()

    # Keep original time column for x-axis
    diff_df["time"] = df["time"]

    # Drop first row (diff is NaN)
    diff_df = diff_df.iloc[1:]

    row = {
        "sent_mean": round(df["sent"].mean(), 2),
        "sent_median": round(df["sent"].median(), 2),
        "received_mean": round(df["received"].mean(), 2),
        "received_median": round(df["received"].median(), 2),
        "total_mean": round(df["total"].mean(), 2),
        "total_median": round(df["total"].median(), 2),
    }
    data.loc[len(data)] = row


def __print_stats(df: pd.DataFrame, title, multi):
    print_purple("CPU usage data:")
    if multi:
        print(f"{title} Mean idle process CPU: {round(df["mean_idle_proc"].mean(), 2)}")
        print(
            f"{title} Median idle process CPU: {round(df["median_idle_proc"].mean(), 2)}"
        )
        print(
            f"{title} 0.75 quantile idle process CPU: {round(df["third_quantile_idle_proc"].mean(), 2)}"
        )
        print()
        print(f"{title} Mean idle global CPU: {round(df["mean_idle_glob"].mean(), 2)}")
        print(
            f"{title} Median quantile idle global CPU: {round(df["median_idle_glob"].mean(), 2)}"
        )
        print(
            f"{title} 0.75 quantile idle global CPU: {round(df["third_quantile_idle_glob"].mean(), 2)}"
        )
        print()

    print(f"{title} CPU peak whole time proc: {round(df["max_proc"].mean(), 2)}")
    print(f"{title} CPU peak whole time glob: {round(df["max_glob"].mean(), 2)}")
    print()

    print_purple("Memory usage data:")
    print(f"{title} AVG proc memory: {round(df["proc_rss"].mean(), 2)}")
    print(f"{title} AVG glob memory: {round(df["mem_total"].mean(), 2)}")
    print()


def __print_int_stats(df: pd.DataFrame, title):
    print(f"{title} sent mean: {round(df["sent_mean"].mean(), 2)}")
    print(f"{title} sent median: {round(df["sent_median"].mean(), 2)}")
    print(f"{title} received mean: {round(df["received_mean"].mean(), 2)}")
    print(f"{title} received median: {round(df["received_median"].mean(), 2)}")
    print(f"{title} total mean: {round(df["total_mean"].mean(), 2)}")
    print(f"{title} total median: {round(df["total_median"].mean(), 2)}")


def __latex_int_row(df: pd.DataFrame, title):
    row = title
    row = f"{row} & {round(df["sent_mean"].mean(), 2)}"
    row = f"{row} & {round(df["sent_median"].mean(), 2)}"
    row = f"{row} & {round(df["received_mean"].mean(), 2)}"
    row = f"{row} & {round(df["received_median"].mean(), 2)}"
    # Total is just sent + received
    row = f"{row} \\\\\n"
    return row


def __latex_perf_row(df: pd.DataFrame, title):
    row = title

    row = f"{row} & {round(df["max_proc"].mean(), 2)}"
    row = f"{row} & {round(df["max_glob"].mean(), 2)}"
    row = f"{row} & {round(df["proc_rss"].mean(), 2)}"

    row = f"{row} \\\\\n"

    return row


def get_latex_row_perf(list_files: list[str], title=""):
    """
    Gets latex table row by aggregting data in list_files

        list_files - list of files to parse data
        title - optional title for the row (to be used in first column)
    """
    df = __get_empty_perf_df()
    for file in list_files:
        __append_file_stats(file, df)
    return __latex_perf_row(df, title)


def get_latex_row_int(list_files: list[str], title=""):
    """
    Gets latex table row by aggregting data in list_files

        list_files - list of files to parse data
        title - optional title for the row (to be used in first column)
    """
    df = __get_empty_int_df()
    for file in list_files:
        __append_int_stats(file, df)
    return __latex_int_row(df, title)


def calculate_and_print_perf(list_files: list[str], multi: bool, title=""):
    """
    Calculates the perf stats and prints them.

        list_files - list of files to parse data
        multi - multi-node test or not
        title - optional title for the row (to be used in first column)
    """
    df = __get_empty_perf_df()
    for file in list_files:
        __append_file_stats(file, df)
    __print_stats(df, title, multi)


def calculate_and_print_int(list_files: list[str], title=""):
    """
    Calculates the interface stats and prints them.

        list_files - list of files to parse data
        multi - multi-node test or not
        title - optional title for the row (to be used in first column)
    """
    df = __get_empty_int_df()
    for file in list_files:
        __append_int_stats(file, df)
    __print_int_stats(df, title)


def get_orch_cost_metrics(list_files: list[str]):
    """
    Calculates the orchestration cost metrics for given list of files.

        list_files - list of files to calculate the orch-cost metrics
    """
    df = __get_empty_perf_df()
    for file in list_files:
        __append_file_stats(file, df)
    return (
        float(df["max_proc"].mean()),
        float(df["max_glob"].mean()),
        float(df["proc_rss"].mean()),
        float(df["mem_used"].mean()),
    )


def startup_time_values(folder):
    """
    Aggregates all startup times into an array from given folder.

        folder - full system path for startup file folder
    """
    startup_files = glob.glob(f"{folder}/*-startup.txt")

    values = []
    for filepath in startup_files:
        with open(filepath, "r") as f:
            value = float(f.read().strip())
            values.append(value)
    return values


def startup_time_indicators(folder):
    """
    Aggregates all startup times from given folder and calculates median and
    mean for the values.

    Returns a tuple: (median, mean)

        folder - full system path for startup file folder
    """
    values = startup_time_values(folder)

    if values:
        s = pd.Series(values)
        median: float = float(round(s.median(), 2))
        average: float = float(round(s.mean(), 2))
        return median, average
    else:
        print(f"No startup files found from {folder}")
        sys.exit(0)
