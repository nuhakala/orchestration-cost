
This folder contains python scripts and tools for benchmarking different
orchestrators. The `tools` folder contains reusable scripts and `tests` contain
individual test setups. `data` contains the collected data.

# Usage

Scripts under `tests` are supposed to be invoked directly with `python3
<test-case> <test-scenario> <parse data: true|false> <multi-node< true|false>`.
Scripts under `tools` are meant to be called from other scripts. Scripts in the
root are meant to be invoked directly.

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
