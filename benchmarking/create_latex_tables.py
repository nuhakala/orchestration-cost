"""
This file reads the data in each folder under ./data/scenario{1|2} and dumps the
data into latex tables under definitions.LATEX_TABLE_LOC
"""

import os
import definitions
import tools.extra_wc_data
import tools.read_data_sc1
import tools.read_data_sc2

SAVE_DIR = definitions.LATEX_TABLE_LOC
# SAVE_DIR = "./"
all_files = []


def perf_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write(
            "\\textbf{Test case} & \\textbf{CPU orch} & \\textbf{CPU node} & \\textbf{RSS orch (MB)} \\\\\n"
        )
        f.write("\\hline\n")


def int_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write(
            "\\textbf{Test case} & \\textbf{Sent mean} & \\textbf{Sent median} & \\textbf{Received mean} & \\textbf{Received median} \\\\\n"
        )
        f.write("\\hline\n")


def startup_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write(
            "\\textbf{Test case} & \\textbf{Avg startup} & \\textbf{Median startup} \\\\\n"
        )
        f.write("\\hline\n")


def hey_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write(
            "\\textbf{Test case} & \\textbf{Mean} & \\textbf{Median} & \\textbf{Min} & \\textbf{Max} \\\\\n"
        )
        f.write("\\hline\n")


def print_startup_data_line(file, test_case, mean, median):
    with open(file, "a", encoding="utf-8") as f:
        f.write(f"{test_case} & {mean} & {median} \\\\\n")


# ***** Scenario 1 files *****
sc1_single_perf = f"{SAVE_DIR}/sc1_single_perf.tex"
sc1_multi_control_perf = f"{SAVE_DIR}/sc1_multi_control.tex"
sc1_multi_worker_perf = f"{SAVE_DIR}/sc1_multi_worker.tex"
sc1_startup_single = f"{SAVE_DIR}/sc1_single_startup.tex"
sc1_startup_multi = f"{SAVE_DIR}/sc1_multi_startup.tex"
sc1_startup_multi_extra = f"{SAVE_DIR}/sc1_multi_startup_extra.tex"
all_files = all_files + [
    sc1_single_perf,
    sc1_multi_control_perf,
    sc1_multi_worker_perf,
    sc1_startup_single,
    sc1_startup_multi,
    sc1_startup_multi_extra,
]

# ***** Scenario 2 files *****
sc2_single_hey_file = f"{SAVE_DIR}/sc2_single_hey.tex"
sc2_single_perf_file = f"{SAVE_DIR}/sc2_single_perf.tex"
sc2_single_int_file = f"{SAVE_DIR}/sc2_single_int.tex"
sc2_multi_hey_file = f"{SAVE_DIR}/sc2_multi_hey.tex"
sc2_multi_control_perf_file = f"{SAVE_DIR}/sc2_multi_control_perf.tex"
sc2_multi_worker_perf_file = f"{SAVE_DIR}/sc2_multi_worker_perf.tex"
sc2_multi_control_int_file = f"{SAVE_DIR}/sc2_multi_control_int.tex"
sc2_multi_worker_int_file = f"{SAVE_DIR}/sc2_multi_worker_int.tex"
all_files = all_files + [
    sc2_single_hey_file,
    sc2_single_perf_file,
    sc2_single_int_file,
    sc2_multi_hey_file,
    sc2_multi_control_perf_file,
    sc2_multi_worker_perf_file,
    sc2_multi_control_int_file,
    sc2_multi_worker_int_file,
]

# ***** Remove old files *****
print("Removing old files")
for file in all_files:
    try:
        os.remove(file)
    except FileNotFoundError:
        print("File not found")

# Add headers
print(f"Creating files with headers to {SAVE_DIR}")
perf_header(sc1_single_perf)
perf_header(sc1_multi_control_perf)
perf_header(sc1_multi_worker_perf)
startup_header(sc1_startup_single)
startup_header(sc1_startup_multi)
startup_header(sc1_startup_multi_extra)
hey_header(sc2_single_hey_file)
perf_header(sc2_single_perf_file)
int_header(sc2_single_int_file)
hey_header(sc2_multi_hey_file)
perf_header(sc2_multi_control_perf_file)
perf_header(sc2_multi_worker_perf_file)
int_header(sc2_multi_control_int_file)
int_header(sc2_multi_worker_int_file)

# ***** Scenario 1 *****
folder_path = definitions.SC1_PATH
items = os.listdir(folder_path)
for test_case in items:
    if "multi" in test_case:
        tools.read_data_sc1.print_latex_table_row(
            test_case,
            True,
            sc1_startup_single,
            sc1_startup_multi,
            sc1_single_perf,
            sc1_multi_worker_perf,
            sc1_multi_control_perf,
        )
    else:
        tools.read_data_sc1.print_latex_table_row(
            test_case,
            False,
            sc1_startup_single,
            sc1_startup_multi,
            sc1_single_perf,
            sc1_multi_worker_perf,
            sc1_multi_control_perf,
        )
# Add the extra wc data to the table.
# Needs to be done manually as they are averages of multiple sets
extra_startups_avg = tools.extra_wc_data.get_platform_indicators()
print_startup_data_line(sc1_startup_multi, "wc-k0s-multi-go-avg", extra_startups_avg[0], extra_startups_avg[2])
print_startup_data_line(sc1_startup_multi, "wc-k0s-multi-rust-avg", extra_startups_avg[0], extra_startups_avg[2])
print_startup_data_line(sc1_startup_multi, "wc-k3s-multi-go-avg", extra_startups_avg[4], extra_startups_avg[6])
print_startup_data_line(sc1_startup_multi, "wc-k3s-multi-rust-avg", extra_startups_avg[5], extra_startups_avg[7])
print_startup_data_line(sc1_startup_multi, "wc-k0s-multi-go-rc7-avg", extra_startups_avg[8], extra_startups_avg[10])
print_startup_data_line(sc1_startup_multi, "wc-k0s-multi-rust-rc7-avg", extra_startups_avg[9], extra_startups_avg[11])
# And then write the individual sets into their own table
extra_startups = tools.extra_wc_data.get_set_averages()
for test_case, values in extra_startups.items():
    print_startup_data_line(sc1_startup_multi_extra, test_case, values[0], values[1])
print("Scenario 1 data saved to files")

# ***** Scenario 2 *****
sc2_single_hey_file = f"{SAVE_DIR}/sc2_single_hey.tex"
sc2_single_perf_file = f"{SAVE_DIR}/sc2_single_perf.tex"
sc2_single_int_file = f"{SAVE_DIR}/sc2_single_int.tex"
sc2_multi_hey_file = f"{SAVE_DIR}/sc2_multi_hey.tex"
sc2_multi_control_perf_file = f"{SAVE_DIR}/sc2_multi_control_perf.tex"
sc2_multi_worker_perf_file = f"{SAVE_DIR}/sc2_multi_worker_perf.tex"
sc2_multi_control_int_file = f"{SAVE_DIR}/sc2_multi_control_int.tex"
sc2_multi_worker_int_file = f"{SAVE_DIR}/sc2_multi_worker_int.tex"
all_files = all_files + [
    sc2_single_hey_file,
    sc2_single_perf_file,
    sc2_single_int_file,
    sc2_multi_hey_file,
    sc2_multi_control_perf_file,
    sc2_multi_worker_perf_file,
    sc2_multi_control_int_file,
    sc2_multi_worker_int_file,
]

folder_path = definitions.SC2_PATH
items = os.listdir(folder_path)
for test_case in items:
    if "multi" in test_case:
        tools.read_data_sc2.print_latex(
            test_case,
            True,
            sc2_single_hey_file,
            sc2_multi_hey_file,
            sc2_single_perf_file,
            sc2_single_int_file,
            sc2_multi_control_perf_file,
            sc2_multi_worker_perf_file,
            sc2_multi_control_int_file,
            sc2_multi_worker_int_file,
        )
    else:
        tools.read_data_sc2.print_latex(
            test_case,
            False,
            sc2_single_hey_file,
            sc2_multi_hey_file,
            sc2_single_perf_file,
            sc2_single_int_file,
            sc2_multi_control_perf_file,
            sc2_multi_worker_perf_file,
            sc2_multi_control_int_file,
            sc2_multi_worker_int_file,
        )
print("Scenario 2 data saved to files")


# ***** Clean and sort the file contents *****
for file in all_files:
    lines = []
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(file, "w", encoding="utf-8") as f:
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace("-multi", "")
            lines[i] = lines[i].replace("-single", "")
        lines = lines[:2] + sorted(lines[2:])
        f.writelines(lines)
print("Files cleaned and sorted")
