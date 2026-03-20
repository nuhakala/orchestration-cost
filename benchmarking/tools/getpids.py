import subprocess
import sys

from . import print_utils

"""
***** Common *****
Basically we want to include the core control plane components:
- kube-apiserver
- etcd (kine for k0s)
- kube-scheduler
- kube-controller-manager

In addition, we want to include the framework specific orchestrator components.

***** Wasmcloud *****
- runtime-operator
- NATS server

***** Knative *****
- activator
- autoscaler
- autoscaler-hpa
- controller
- webhook
- kourier

These are listed as /ko-app/<name> in ps aux output

***** Spin *****
- Spin operator

***** Native containers *****
No extra in top of K8s control plane components
"""


# Helper to actualle get the pids
def __get_pids(names):
    pids = []
    for name in names:
        cmd = ""
        try:
            cmd = subprocess.run(
                ["pgrep", "-f", name], text=True, check=True, capture_output=True
            )
            pids = pids + cmd.stdout.strip().splitlines()
        except Exception as e:
            print_utils.print_red(f"ERROR: program '{name}' not found, error: {e}")

    pids = list(set(pids))
    pids.sort()
    return pids


# Gets IP address that starts with given parameter
def get_pids(targets) -> list[str]:
    """
    Gets the pids associated with the target. Each target has different set of
    processes associated.
    """
    names = []
    for target in targets:
        match target:
            case "knative":
                # 6 pids
                names.append("ko-app")  # knative components
            case "k0ssingle":
                # 5 pids
                names = names + [
                    "kine",  # replaced etcd in single node setup
                    "kube-apiserver",
                    "kube-scheduler",
                    "kube-controller-manager",
                    "/usr/local/bin/k0s",
                ]
            case "k0smulti":
                # 6 pids
                # in addition to below names, there is k0s api
                names = names + [
                    "etcd",
                    "kube-apiserver",
                    "kube-scheduler",
                    "kube-controller-manager",
                    "/usr/local/bin/k0s",
                ]
            case "k0sworker":
                # 1 pid
                names = names + [
                    "/usr/local/bin/k0s",
                ]
            case "k3s":
                # 1 pids
                names.append("k3s server")
            case "k3sagent":
                # 3 pids
                names.append("k3s agent")
            case "kubeedge":
                names = names + [
                    "etcd",
                    "kube-apiserver",
                    "kube-scheduler",
                    "kube-controller-manager",
                    "cloudcore",
                    "iptables-manager",
                ]
            case "kubeedge-agent":
                names = names + ["mosquitto", "edgecore"]
            case "spin":
                # gets the operator inside a pod
                # 1 pid
                names.append("health-probe-bind-address=:8082")
            case "wasmcloud":
                # gets the operator inside a pod
                # 2 pid
                names.append("runtime-operator")
                names.append("nats-server")
            case _:
                print_utils.print_red(f"Target {target} not recognized")

    pids = __get_pids(names)
    return pids


if __name__ == "__main__":
    print(get_pids([sys.argv[1]]))
