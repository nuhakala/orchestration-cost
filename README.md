# Orchestration cost

This repository contains tools, scripts, and data for benchmarking wasm and
container orchestrators.

- `./benchmarking/` contains python scripts to do measurements
- `./*-infra` contains setup scripts for setting up environments for testing
- `./servers/` contain the apps used in testing

The deployments utilize K8s autoscaling using Nginx ingress controller to create
RPS metric.

## Servers

The Spin and wasmCloud servers are mostly copied from the quickstart guides and
only edited slightly.
