#!/usr/bin/env bash

set -ex

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

install_k3s() {
	. "${SCRIPT_DIR}/../version.sh"
	"${SCRIPT_DIR}/../prepare.sh"
	# Install containerd separately and configure it as standalone
	# When using external containerd, we need to install also cni
	# "${SCRIPT_DIR}/../install-docker.sh"
	# "${SCRIPT_DIR}/../containerd/configure.sh" edge
	# "${SCRIPT_DIR}/../containerd/install-cni.sh"
	# Use the builtin containerd
	"${SCRIPT_DIR}/../containerd/configure.sh" k3s

	# Create the .kube directory if it doesn't already exist
	mkdir -p ~/.kube

	# ***** Install k3s binary *****
	export INSTALL_K3S_SKIP_ENABLE=true # do not enable k3s automatically
	export INSTALL_K3S_VERSION="${K3S_VERSION}" # use this version
	# Get k3s binary
	if ! k3s > /dev/null; then
		curl -sfL https://get.k3s.io | sh -s
	fi
}

case $1 in
	control)
		# export INSTALL_K3S_EXEC="server --write-kubeconfig "${HOME}/.kube/config" --write-kubeconfig-mode 644 --container-runtime-endpoint unix:///var/run/containerd/containerd.sock"
		export INSTALL_K3S_EXEC="server --write-kubeconfig "${HOME}/.kube/config" --write-kubeconfig-mode 644"
		install_k3s
		sudo systemctl enable k3s
		sudo systemctl start k3s
		;;
	agent)
		if [[ $# -lt 3 ]]; then
			echo "Give control plane ip and token as args"
			exit 0
		fi
		# export INSTALL_K3S_EXEC="agent --container-runtime-endpoint unix:///var/run/containerd/containerd.sock"
		export INSTALL_K3S_EXEC="agent"
		export K3S_URL="https://$2:6443"
		export K3S_TOKEN="$3"
		install_k3s
		sudo systemctl enable k3s-agent
		sudo systemctl start k3s-agent
		;;
	uninstallcontrol) k3s-uninstall.sh ;;
	uninstallagent) k3s-agent-uninstall.sh ;;
	token) sudo cat /var/lib/rancher/k3s/server/node-token ;;

	# If don't want to install systemd service
	install) install_k3s ;;
	server) 
		sudo k3s server \
			--write-kubeconfig "${HOME}/.kube/config" \
			--write-kubeconfig-mode 644 \
			--container-runtime-endpoint unix:///var/run/containerd/containerd.sock
		;;
	worker)
		sudo k3s agent \
			--server https://192.168.68.51:6443 \
			--token "$2"
			# --container-runtime-endpoint unix:///var/run/containerd/containerd.sock
		;;
	*) cat <<EOF ;;
Usage:

	control            > start control plane
	agent <ip> <token> > start agent node and join cluster
	uninstallcontrol   > uninstall conrol plane node
	uninstallagent     > uninstall agent node
	install            > install K3s without creating systemd service and starting it
	server             > start k3s server
	worker             > start k3s agent
	token              > print join token
EOF
esac
