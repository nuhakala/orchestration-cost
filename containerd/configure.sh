#!/usr/bin/env bash

set -xe

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"

standalone() {
	sudo mkdir -p /etc/containerd/certs.d/"${MY_REG}"
	cat <<EOF | sudo tee /etc/containerd/config.toml
version = 3

[plugins."io.containerd.cri.v1.images".registry]
   config_path = "/etc/containerd/certs.d"

disabled_plugins = []
EOF
	sudo cp "${SCRIPT_DIR}/config.toml" /etc/containerd/certs.d/
	sudo sed -i '/config_path/c\config_path = "/etc/containerd/certs.d"' /etc/containerd/certs.d/config.toml
	sudo cp "${SCRIPT_DIR}/hosts.toml" /etc/containerd/certs.d/"${MY_REG}"/hosts.toml
	sudo sed -i "s|server.*|server = \"https://${MY_REG}\"|" /etc/containerd/certs.d/"${MY_REG}"/hosts.toml
	sudo sed -i "s|\[host.*|\[host.\"http://${MY_REG}\"\]|" /etc/containerd/certs.d/"${MY_REG}"/hosts.toml

	MY_REG="192.168.68.51:5000"
	sudo mkdir -p /etc/containerd/certs.d/"${MY_REG}"
	sudo cp "${SCRIPT_DIR}/hosts.toml" /etc/containerd/certs.d/"${MY_REG}"/hosts.toml
	sudo sed -i "s|server.*|server = \"https://${MY_REG}\"|" /etc/containerd/certs.d/"${MY_REG}"/hosts.toml
	sudo sed -i "s|\[host.*|\[host.\"http://${MY_REG}\"\]|" /etc/containerd/certs.d/"${MY_REG}"/hosts.toml

	sudo systemctl daemon-reload
	sudo systemctl restart containerd
}

k3s() {
	sudo mkdir -p /etc/rancher/k3s
	sudo cp "${SCRIPT_DIR}/k3s-registries.yaml" /etc/rancher/k3s/registries.yaml
}

case $1 in
	"k0s") k0s ;;
	"k3s") k3s ;;
	"edge") standalone ;;
	*)
		echo "Wrong arg, supports k0s, k3s, edge"
		;;
esac
