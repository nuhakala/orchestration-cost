#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"
"${SCRIPT_DIR}/../install-helm.sh"
"${SCRIPT_DIR}/../install-kubeadm.sh" # ensure kubectl is installed

install_nginx() {
	kubectl create -f "${SCRIPT_DIR}/prom-operator.yaml"
	sleep 5
	kubectl apply -f "${SCRIPT_DIR}/prom.yaml"
	sleep 5

	# Install the ingress framework
	helm upgrade nginx-ingress \
		--install \
		"${SCRIPT_DIR}/nginx-ingress/"

	# Create adapter
	kubectl create -f "${SCRIPT_DIR}/prometheus-adapter/manifests/"
	# Register the custom API
	kubectl create -f "${SCRIPT_DIR}/register-api.yaml"
}

uninstall_nginx() {
	kubectl delete -f "${SCRIPT_DIR}/register-api.yaml"
	kubectl delete -f "${SCRIPT_DIR}/prometheus-adapter/manifests/"
	helm uninstall nginx-ingress
	kubectl delete -f "${SCRIPT_DIR}/prom-operator.yaml"
	kubectl delete -f "${SCRIPT_DIR}/prom.yaml"
}

case $1 in
	deploy) install_nginx ;;
	undeploy) uninstall_nginx ;;
	*)
		echo "Wrong arg, deploy or undeploy"
		exit 0
		;;
esac
