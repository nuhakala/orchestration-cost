
This folder contains python scripts and tools for benchmarking different
orchestrators. The `tools` folder contains reusable scripts and `tests` contain
individual test setups. `data` contains the collected data.

# Usage

Scripts under `tests` are supposed to be invoked directly with `python3
<test-case> <test-scenario> <parse data: true|false> <multi-node< true|false>`.
Scripts under `tools` are meant to be called from other scripts. Scripts in the
root are meant to be invoked directly.

- `test.py` is an entrypoint for running individual tests.
- `hey_server.py` starts an HTTP server which will start hey load generator on
  request.
- `worker_server.py` start HTTP server which will start/stop measuring system
  and process data on request.
- `create_latex_tables.py` parses the collected data and exports everything into
  latex tables in their own files.
- `calculate_orch_cost_metric.py` calculates the orchestration cost for each
  test case and creates figures out of them.
- `print_startups.py` is a small tool to print wasmCloud extra measurement
  startup times.

For more detailed usage instructions, consult the individual files.

## Data

All the collected data is under `./data`

- `./data/ai-sc1/` Scenario 1 multi-node data for AI workload
- `./data/ai-sc1-single/` Scenario 1 single-node data for AI workload. No
  figures made out of this.
- `./data/ai-sc2/` Scenario 2 multi-node data for AI workload
- `./data/sc1-extra-wc-data-single/` Extra wasmCloud single-node data. No
  figures made out of this. Only parsed in `./print_startups.py`
- `./data/sc1-extra-wc-data-multi/` Extra wasmCloud multi-node data. This is
  used in figures and tables.
- `./data/scenario1/` Artificial workload scenario 1 data. Both single- and
  multi-node.
- `./data/scenario2/` Artificial workload scenario 2 data. Both single- and
  multi-node.

In hindsight, would have been better to create different folders for single- and
multi-node results for artificial workload as well.
