#!/usr/bin/env bash

set -xe

# Instructions:
# https://www.spinkube.dev/docs/install/installing-with-helm/

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"
"${SCRIPT_DIR}/../install-helm.sh" # ensure helm
"${SCRIPT_DIR}/../install-kubeadm.sh" # ensure kubectl
"${SCRIPT_DIR}/../containerd/install-spin-shim.sh" # install spin shim

install_cert() {
	kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml
	kubectl wait -n cert-manager \
		--for=condition=Available \
		deployment/cert-manager \
		deployment/cert-manager-webhook \
		deployment/cert-manager-cainjector \
		--timeout=300s
}

install_spin() {
	kubectl apply -f https://github.com/spinframework/spin-operator/releases/download/v0.6.1/spin-operator.crds.yaml
	kubectl apply -f https://github.com/spinframework/spin-operator/releases/download/v0.6.1/spin-operator.runtime-class.yaml
	kubectl apply -f https://github.com/spinframework/spin-operator/releases/download/v0.6.1/spin-operator.shim-executor.yaml

	# Install Spin Operator with Helm
	helm upgrade spin-operator \
		--install \
		--namespace spin-operator \
		--create-namespace \
		--version 0.6.1 \
		--wait \
		oci://ghcr.io/spinframework/charts/spin-operator
}

install_spin_cli() {
	if [[ ! $(spin --version) ]]; then
		mkdir -p ./spin-cli
		pushd ./spin-cli
		curl -fsSL https://spinframework.dev/downloads/install.sh | bash -s -- -v "${SPIN_VERSION}"
		popd
		sudo cp ./spin-cli/spin /usr/local/bin
		rm -r ./spin-cli
	fi

	spin plugins update
	spin plugins install -y kube
}

uninstall_spin() {
	kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml
	helm uninstall -n spin-operator spin-operator
}

case $1 in
	install)
		install_cert
		install_spin
		# install_spin_cli
		;;
	uninstall) uninstall_spin ;;
	*)
		echo "Wrong arg, install or uninstall"
		exit 0
		;;
esac
