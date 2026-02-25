"""
This file reads the data in each folder under ./data/scenario{1|2} and dumps the
data into latex tables under definitions.LATEX_TABLE_LOC
"""
import os
import definitions
import tools.read_data_sc1
import tools.read_data_sc2

SAVE_DIR = definitions.LATEX_TABLE_LOC
all_files = []

def perf_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write("\\textbf{Test case} & \\textbf{CPU orch} & \\textbf{CPU node} & \\textbf{RSS orch (MB)} \\\\\n")
        f.write("\\hline\n")

def int_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write("\\textbf{Test case} & \\textbf{Avg startup} & \\textbf{Median startup} \\\\\n")
        f.write("\\hline\n")

def startup_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write("\\textbf{Test case} & \\textbf{CPU orch} & \\textbf{CPU node} & \\textbf{RSS orch (MB)} \\\\\n")
        f.write("\\hline\n")

def hey_header(file):
    with open(file, "w", encoding="utf-8") as f:
        f.write("\\textbf{Test case} & \\textbf{Mean} & \\textbf{Median} & \\textbf{Min} & \\textbf{Max} \\\\\n")
        f.write("\\hline\n")

# ***** Scenario 1 files *****
sc1_single_perf = f"{SAVE_DIR}/sc1_single_perf.tex"
sc1_multi_control_perf = f"{SAVE_DIR}/sc1_multi_control.tex"
sc1_multi_worker_perf = f"{SAVE_DIR}/sc1_multi_worker.tex"
sc1_startup_single = f"{SAVE_DIR}/sc1_single_startup.tex"
sc1_startup_multi = f"{SAVE_DIR}/sc1_multi_startup.tex"
all_files = all_files + [
    sc1_single_perf,
    sc1_multi_control_perf,
    sc1_multi_worker_perf,
    sc1_startup_single,
    sc1_startup_multi,
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
perf_header(sc1_single_perf)
perf_header(sc1_multi_control_perf)
perf_header(sc1_multi_worker_perf)
startup_header(sc1_startup_single)
startup_header(sc1_startup_multi)
hey_header(sc2_single_hey_file)
perf_header(sc2_single_perf_file)
int_header(sc2_single_int_file)
hey_header(sc2_multi_hey_file)
perf_header(sc2_multi_control_perf_file)
perf_header(sc2_multi_worker_perf_file)
int_header(sc2_multi_control_int_file)
int_header(sc2_multi_worker_int_file)

# parse data
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

# ***** Scenario 2 *****
sc2_single_hey_file = "./sc2_single_hey.tex"
sc2_single_perf_file = "./sc2_single_perf.tex"
sc2_single_int_file = "./sc2_single_int.tex"
sc2_multi_hey_file = "./sc2_multi_hey.tex"
sc2_multi_control_perf_file = "./sc2_multi_control_perf.tex"
sc2_multi_worker_perf_file = "./sc2_multi_worker_perf.tex"
sc2_multi_control_int_file = "./sc2_multi_control_int.tex"
sc2_multi_worker_int_file = "./sc2_multi_worker_int.tex"
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


# ***** Clean and sort the file contents *****
for file in all_files:
    lines = []
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(file, "w", encoding="utf-8") as f:
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace("-multi", "")
            lines[i] = lines[i].replace("-single", "")
        lines.sort()
        f.writelines(lines)
