import pandas as pd


def create_curve(
    perf_file: str,
    cpu_curve: bool,
    proc_plt,
    glob_plt,
    curve_label: str,
    show_legend: bool,
    title="",
):
    """Creates a curve to plot

    Arguments:
        perf_file -- string, csv file to read
        cpu_curve -- boolean, true -> plot cpu; false -> plot memory
        proc_plt -- matplotlib Axes, plot for process stats
        glob_plt -- matplotlib Axes, plot for global stats
        curve_label -- string, label for curve
        show_legend -- boolean, show legend for the plot
        calculate_stats -- calculate numeric stats for the curves
        title -- optional identifier for figures

    Matplotlib axes docs:
    https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes
    """
    df = pd.read_csv(perf_file)

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

    if cpu_curve:
        diff_df["glob_perc"] = (
            (diff_df["total"] - diff_df["idle"]) / diff_df["total"] * 100
        )
        diff_df["proc_cpu_perc"] = diff_df["proc_cpu"] / diff_df["total"] * 100

        # Plot (time is in ms)
        proc_plt.plot(diff_df["time"], diff_df["proc_cpu_perc"], label=f"{curve_label}")
        glob_plt.plot(diff_df["time"], diff_df["glob_perc"], label=f"{curve_label}")

        proc_plt.set_title(f"Process CPU {title}")
        glob_plt.set_title(f"Global CPU {title}")
        proc_plt.set_xlabel("Time (ms)")
        glob_plt.set_xlabel("Time (ms)")
        proc_plt.set_ylabel("CPU %")
        glob_plt.set_ylabel("CPU %")
    else:
        # Transform values into megabytes
        df["mem_total"] = df["mem_total"] / 1024
        df["mem_free"] = df["mem_free"] / 1024
        df["proc_rss"] = df["proc_rss"] / 1024

        proc_plt.plot(df["time"], df["proc_rss"], label=f"{curve_label}")
        glob_plt.plot(df["time"], df["mem_total"] - df["mem_free"], label=f"{curve_label}")

        proc_plt.set_title(f"Process Memory {title}")
        glob_plt.set_title(f"Global Memory (total {df["mem_total"][0]}) {title}")
        proc_plt.set_xlabel("Time (ms)")
        glob_plt.set_xlabel("Time (ms)")
        proc_plt.set_ylabel("Memory (MB)")
        glob_plt.set_ylabel("Memory (MB)")

    if show_legend:
        proc_plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        glob_plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))


def create_int_curve(int_file: str, plt, show_legend: bool, title=""):
    """Creates curve for interface statistics.

    Arguments:
        int_file -- string, csv file to read
        plt -- matplotlib Axes, plot for global stats
        show_legend -- boolean, show legend for the plot
        title -- optional identifier for figures
    """
    df = pd.read_csv(int_file)
    # Total column is actually included in the data. But it is recorded there
    # wrong, so I recalculate it here.
    df["total"] = df["sent"] + df["received"]

    # Compute differences between consecutive rows
    diff_df = df.diff()

    # Keep original time column for x-axis
    diff_df["time"] = df["time"]

    # Drop first row (diff is NaN)
    diff_df = diff_df.iloc[1:]

    # Plot (time is in ms)
    plt.plot(diff_df["time"], diff_df["sent"], label="sent")
    plt.plot(diff_df["time"], diff_df["received"], label="received")
    plt.plot(diff_df["time"], diff_df["total"], label="total")

    plt.set_title(f"Interface stats {title}")
    plt.set_xlabel("Time (ms)")
    plt.set_ylabel("KB")

    if show_legend:
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
