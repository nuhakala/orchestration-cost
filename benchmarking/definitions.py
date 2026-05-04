import os

WORK_DIR = os.path.expandvars("${HOME}/git/omat/orch-cost-tools")
ROOT_DIR = os.path.join(WORK_DIR, "benchmarking")
SC1_PATH = os.path.join(ROOT_DIR, "data/scenario1")
SC2_PATH = os.path.join(ROOT_DIR, "data/scenario2")
AI_SC1 = os.path.join(ROOT_DIR, "data/ai-sc1")
AI_SC2 = os.path.join(ROOT_DIR, "data/ai-sc2")
WC_V2 = os.path.join(ROOT_DIR, "data/wc_v2")
WC_V2_AI = os.path.join(ROOT_DIR, "data/wc_v2_ai")
WC_V2_MULTI = os.path.join(ROOT_DIR, "data/wc_v2_multi")
WC_V2_AI_MULTI = os.path.join(ROOT_DIR, "data/wc_v2_ai_multi")
WC_EXTRA_LOC_MULTI = os.path.join(ROOT_DIR, "data/sc1-extra-wc-data-multi")
WC_EXTRA_LOC_SINGLE = os.path.join(ROOT_DIR, "data/sc1-extra-wc-data-single")

# Hardcoded values for tests
NUM_ITERS = 10  # Number of iterations for scenario 1
TIMEOUT = 30000  # timeout for pinging endpoint in scenario 1
# TIMEOUT = 90000 # 90s for AI workload
PING_ENDPOINT = "/squeezenet"  # endpoint to ping in scenario 2
HEY_SERVER_IP = "192.168.68.54"  # Control plane IP for scenario 2
INTERFACE = "ens3"  # interface to search for IP address
HOST_SERVER_PORT = 8000
HOST_SERVER_ENDPOINT = "/ai"  # / for basic, /ai for AI workload
SCALEDOWN_DELAY = 150  # time to measure scale down effect in scenario 2
WORKER_ADDRESS = "192.168.68.51"  # used only in multi node tests
SERVICE_ENDPOINT = "192.168.68.60:31080"
AI_ENDPOINT = "192.168.68.60:31080/squeezenet"
SC2_MINUTES = 5
SC2_DEPLOY_TIME = 300

# For data processing, save location for latex tables
SAVE_DIR = os.path.expandvars("${HOME}/git/omat/paper-orch-cost")
LATEX_TABLE_LOC = os.path.join(SAVE_DIR, "data-tables")
FIGURE_DIR = os.path.join(SAVE_DIR, "images")
latex_text_width = 404.02913
# For thesis
# PLOT_WIDTH = latex_text_width / 72
# PLOT_HEIGHT = PLOT_WIDTH * 0.6
# For paper
PLOT_WIDTH = 3.6
PLOT_HEIGHT = PLOT_WIDTH * 0.7

folders_k0s_go = [
    "wc-k0s-multi-go-2",
    "wc-k0s-multi-go-3",
    "wc-k0s-multi-go-4",
    "wc-k0s-multi-go-5",
]
folders_k0s_rust = [
    "wc-k0s-multi-rust-2",
    "wc-k0s-multi-rust-3",
    "wc-k0s-multi-rust-4",
    "wc-k0s-multi-rust-5",
]
folders_k0s_go_rc7 = [
    "wcrc7-k0s-multi-go-1",
    "wcrc7-k0s-multi-go-2",
    "wcrc7-k0s-multi-go-3",
]
folders_k0s_rust_rc7 = [
    "wcrc7-k0s-multi-rust-1",
    "wcrc7-k0s-multi-rust-2",
    "wcrc7-k0s-multi-rust-3",
]
folders_k3s_go = [
    "wc-k3s-multi-go-2",
    "wc-k3s-multi-go-3",
    "wc-k3s-multi-go-4",
    "wc-k3s-multi-go-5",
]
folders_k3s_rust = [
    "wc-k3s-multi-rust-2",
    "wc-k3s-multi-rust-3",
    "wc-k3s-multi-rust-4",
    "wc-k3s-multi-rust-5",
]
folders_k0s_single_go = [
    "wc-k0s-single-go-2",
    "wc-k0s-single-go-3",
    "wc-k0s-single-go-4",
    "wc-k0s-single-go-5",
    "wc-k0s-single-go-6",
]
folders_k0s_single_rust = [
    "wc-k0s-single-rust-2",
    "wc-k0s-single-rust-3",
    "wc-k0s-single-rust-4",
    "wc-k0s-single-rust-5",
    "wc-k0s-single-rust-6",
]
