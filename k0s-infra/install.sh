#!/usr/bin/env bash

set -xe

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"
"${SCRIPT_DIR}/../prepare.sh"
# Install containerd separately and configure it as standalone
"${SCRIPT_DIR}/../install-docker.sh"
"${SCRIPT_DIR}/../containerd/configure.sh" edge
# Use the builtin containerd
# "${SCRIPT_DIR}/../containerd/configure.sh" k0s

# ***** Install k0s binary *****
if ! k0s help > /dev/null; then
	K0S_VERSION=${K0S_VERSION:-v1.34.3}
	K0S_ARCH="${ARCH:-amd64}"
	DOWNLOAD="https://github.com/k0sproject/k0s/releases/download/$K0S_VERSION/k0s-$K0S_VERSION-$K0S_ARCH"
	curl -sSLf "${DOWNLOAD}" > ./k0s-binary
	sudo mv ./k0s-binary /usr/local/bin/k0s
	sudo chmod 755 -- /usr/local/bin/k0s
fi

case $1 in
	single)
		# Force flag -> forces reinstallation to update it
		sudo k0s install controller \
			--single \
			--force \
			--cri-socket=remote:unix:///var/run/containerd/containerd.sock
		sudo k0s start
		sleep 10
		mkdir -p "${HOME}/.kube"
		sudo k0s kubeconfig admin | sudo tee "${HOME}/.kube/config" > /dev/null
		;;
	multi)
		sudo k0s install controller \
			--force \
			--cri-socket=remote:unix:///var/run/containerd/containerd.sock
		sudo k0s start
		sleep 10
		mkdir -p "${HOME}/.kube"
		sudo k0s kubeconfig admin | sudo tee "${HOME}/.kube/config" > /dev/null
		sudo k0s token create --role=worker > ~/k0s-worker-token
		;;
	worker)
		if [[ $# -lt 2 ]]; then
			echo "Provide tokenfile as second argument"
			exit 0
		fi
		sudo k0s install worker \
			--token-file $2 \
			--cri-socket=remote:unix:///var/run/containerd/containerd.sock
		sudo k0s start
		;;
	*)
		echo "Wrong arg"
		exit 0
		;;
esac
