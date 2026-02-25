#!/usr/bin/env bash

set -ex

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"

TAR_BALL=containerd-shim-spin.tar.gz
BINARY=containerd-shim-spin-v2

if [[ ! -e /usr/local/bin/${BINARY} ]]; then
	if [[ "${ARCH}" == "amd64" ]]; then
		wget -O "${TAR_BALL}" https://github.com/spinframework/containerd-shim-spin/releases/download/${SPIN_SHIM_VERSION}/containerd-shim-spin-v2-linux-x86_64.tar.gz
	else
		wget -O "${TAR_BALL}" https://github.com/spinframework/containerd-shim-spin/releases/download/${SPIN_SHIM_VERSION}/containerd-shim-spin-v2-linux-aarch64.tar.gz
	fi

	tar xf "${TAR_BALL}"
	sudo mv "${BINARY}" /usr/local/bin
	rm "${TAR_BALL}"

fi
cat <<EOF | sudo tee -a /etc/containerd/config.toml
[plugins."io.containerd.cri.v1.runtime".containerd.runtimes."spin"]
	runtime_type = "/usr/local/bin/containerd-shim-spin-v2"
[plugins."io.containerd.cri.v1.runtime".containerd.runtimes.spin.options]
	SystemdCgroup = true
EOF
sudo systemctl daemon-reload
sudo systemctl restart containerd
