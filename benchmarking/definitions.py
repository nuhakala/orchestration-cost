import os

WORK_DIR = os.path.expandvars("${HOME}/orch-cost-tools")
ROOT_DIR = os.path.join(WORK_DIR, "benchmarking")
SC1_PATH = os.path.join(ROOT_DIR, 'data/scenario1')
SC2_PATH = os.path.join(ROOT_DIR, 'data/scenario2')

# Hardcoded values for tests
NUM_ITERS = 10 # Number of iterations for scenario 1
TIMEOUT = 30000 # timeout for pinging endpoint in scenario 1
PING_ENDPOINT = "/" # endpoint to ping in scenario 2
HEY_SERVER_IP = "10.164.178.1" # Control plane IP for scenario 2
INTERFACE = "ens3" # interface to search for IP address
HOST_SERVER_PORT = 8000
SCALEDOWN_DELAY = 150 # time to measure scale down effect in scenario 2
WORKER_ADDRESS = "192.168.68.53" # used only in multi node tests
SERVICE_ENDPOINT = "10.164.178.25:31080"
SC2_MINUTES = 5

# For data processing, save location for latex tables
LATEX_TABLE_LOC = "~/thesis/data-tables"
LATEX_TABLE_LOC = os.path.expanduser(LATEX_TABLE_LOC)
FIGURE_DIR = "~/thesis/thesis-images"
FIGURE_DIR = os.path.expanduser(FIGURE_DIR)
latex_text_width = 404.02913
PLOT_WIDTH = latex_text_width / 72
PLOT_HEIGHT = PLOT_WIDTH * 0.6
