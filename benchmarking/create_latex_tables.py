"""
This file reads the data in each folder under ./data/scenario{1|2} and dumps the
data into latex tables under definitions.LATEX_TABLE_LOC
"""

import argparse
import os
import definitions
import tools.extra_wc_data
import tools.read_data_sc1
import tools.read_data_sc2

parser = argparse.ArgumentParser(description="Latex table CLI")
parser.add_argument("target", choices=["thesis", "paper"], help="Choose target")
parser.add_argument(
    "--save", action=argparse.BooleanOptionalAction, help="save images", default=False
)
args = parser.parse_args()

SAVE_DIR = "./"
if args.save:
    SAVE_DIR = definitions.LATEX_TABLE_LOC

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
ai_startup_multi = f"{SAVE_DIR}/ai_multi_startup.tex"
all_files = all_files + [
    sc1_single_perf,
    sc1_multi_control_perf,
    sc1_multi_worker_perf,
    sc1_startup_single,
    sc1_startup_multi,
    sc1_startup_multi_extra,
    ai_startup_multi,
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
sc2_ai_multi_hey_file = f"{SAVE_DIR}/sc2_ai_multi_hey.tex"
# Next four not needed
sc2_ai_multi_control_perf_file = f"/tmp/sc2_ai_multi_control_perf.tex"
sc2_ai_multi_worker_perf_file = f"/tmp/sc2_ai_multi_worker_perf.tex"
sc2_ai_multi_control_int_file = f"/tmp/sc2_ai_multi_control_int.tex"
sc2_ai_multi_worker_int_file = f"/tmp/sc2_ai_multi_worker_int.tex"
all_files = all_files + [
    sc2_single_hey_file,
    sc2_single_perf_file,
    sc2_single_int_file,
    sc2_multi_hey_file,
    sc2_multi_control_perf_file,
    sc2_multi_worker_perf_file,
    sc2_multi_control_int_file,
    sc2_multi_worker_int_file,
    sc2_ai_multi_hey_file,
    sc2_ai_multi_control_perf_file,
    sc2_ai_multi_worker_perf_file,
    sc2_ai_multi_control_int_file,
    sc2_ai_multi_worker_int_file,
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
hey_header(sc2_ai_multi_hey_file)
perf_header(sc2_ai_multi_control_perf_file)
perf_header(sc2_ai_multi_worker_perf_file)
int_header(sc2_ai_multi_control_int_file)
int_header(sc2_ai_multi_worker_int_file)
startup_header(ai_startup_multi)

# ***** Scenario 1 *****
folder_path = definitions.SC1_PATH
items = os.listdir(folder_path)
for test_case in items:
    multi = False
    if "multi" in test_case:
        multi = True

    tools.read_data_sc1.print_latex_table_row(
        folder_path,
        test_case,
        multi,
        sc1_startup_single,
        sc1_startup_multi,
        sc1_single_perf,
        sc1_multi_worker_perf,
        sc1_multi_control_perf,
    )
# Add the extra wc data to the table.
# Needs to be done manually as they are averages of multiple sets
extra_startups_avg = tools.extra_wc_data.get_platform_indicators()
print_startup_data_line(
    sc1_startup_multi,
    "wc-k0s-multi-go-avg",
    extra_startups_avg[0],
    extra_startups_avg[2],
)
print_startup_data_line(
    sc1_startup_multi,
    "wc-k0s-multi-rust-avg",
    extra_startups_avg[0],
    extra_startups_avg[2],
)
print_startup_data_line(
    sc1_startup_multi,
    "wc-k3s-multi-go-avg",
    extra_startups_avg[4],
    extra_startups_avg[6],
)
print_startup_data_line(
    sc1_startup_multi,
    "wc-k3s-multi-rust-avg",
    extra_startups_avg[5],
    extra_startups_avg[7],
)
print_startup_data_line(
    sc1_startup_multi,
    "wc-k0s-multi-go-rc7-avg",
    extra_startups_avg[8],
    extra_startups_avg[10],
)
print_startup_data_line(
    sc1_startup_multi,
    "wc-k0s-multi-rust-rc7-avg",
    extra_startups_avg[9],
    extra_startups_avg[11],
)
# And then write the individual sets into their own table
extra_startups = tools.extra_wc_data.get_set_averages()
for test_case, values in extra_startups.items():
    print_startup_data_line(sc1_startup_multi_extra, test_case, values[0], values[1])
print("Scenario 1 data saved to files")

# ***** AI workload *****
folder_path = definitions.AI_SC1
items = os.listdir(folder_path)
for test_case in items:
    # The folder contains few single-node tests as well, but we want to ignore
    # them
    if "multi" in test_case:
        tools.read_data_sc1.print_latex_startup_table(
            folder_path,
            test_case,
            ai_startup_multi,
        )
print("AI workload data saved to file")

# ***** Scenario 2 *****
for test_case in os.listdir(definitions.SC2_PATH):
    multi = False
    if "multi" in test_case:
        multi = True

    tools.read_data_sc2.print_latex(
        definitions.SC2_PATH,
        test_case,
        multi,
        sc2_single_hey_file,
        sc2_multi_hey_file,
        sc2_single_perf_file,
        sc2_single_int_file,
        sc2_multi_control_perf_file,
        sc2_multi_worker_perf_file,
        sc2_multi_control_int_file,
        sc2_multi_worker_int_file,
    )
for test_case in os.listdir(definitions.AI_SC2):
    tools.read_data_sc2.print_latex(
        definitions.AI_SC2,
        test_case,
        True,
        "",
        sc2_ai_multi_hey_file,
        "",
        "",
        sc2_ai_multi_control_perf_file,
        sc2_ai_multi_worker_perf_file,
        sc2_ai_multi_control_int_file,
        sc2_ai_multi_worker_int_file,
    )
print("Scenario 2 data saved to files")


if args.target == "paper":
    # Remove the extra tables if targetting paper
    paper_files = [sc2_ai_multi_hey_file, ai_startup_multi, sc1_startup_multi]
    print("Targetting paper, removing useless files")
    for file in all_files:
        if file not in paper_files:
            try:
                os.remove(file)
            except FileNotFoundError:
                print("File not found")
    # Update all files, so that cleaning and sorting does not look for
    # non-existent files
    all_files = paper_files

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
