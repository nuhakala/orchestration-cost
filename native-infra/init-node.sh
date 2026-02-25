#!/bin/bash

set -ex

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"
"${SCRIPT_DIR}/../install-kubeadm.sh"
"${SCRIPT_DIR}/../install-docker.sh"
"${SCRIPT_DIR}/../containerd/configure.sh" edge
"${SCRIPT_DIR}/../containerd/install-cni.sh"

# If swap is on, we need to prevent kubelet from failing.
if swapon; then
	sudo sed -i "s/KUBELET_EXTRA_ARGS.*/KUBELET_EXTRA_ARGS=--fail-swap-on=false/" /etc/default/kubelet
fi

# init k8s
sudo kubeadm init \
	--pod-network-cidr=10.244.0.0/16 \
	--kubernetes-version "$K8S_VERSION_MINOR" \
	--cri-socket=unix:///var/run/containerd/containerd.sock

mkdir -p "$HOME/.kube"
sudo cp -i /etc/kubernetes/admin.conf "$HOME/.kube/config"
sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"

kubectl taint node "$(hostname)" node-role.kubernetes.io/control-plane:NoSchedule-

sudo modprobe br_netfilter
sudo sysctl net.bridge.bridge-nf-call-iptables=1
# kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
