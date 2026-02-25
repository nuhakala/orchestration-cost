#!/usr/bin/env bash

set -ex

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"
"${SCRIPT_DIR}/../install-kubeadm.sh" # ensure kubectl is installed
"${SCRIPT_DIR}/../prepare.sh" # ensure ip address is there

# IP address to assign for the kourier service
# This IP exposes the services
# IP_ADDRESS="192.168.0.1"

kourier() {
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-${KN_VERSION}/serving-crds.yaml
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-${KN_VERSION}/serving-core.yaml
	# sed -i "s/externalIPs: .*/externalIPs: [\"${IP_ADDRESS}\"]/" "${SCRIPT_DIR}/kourier.yaml"
	kubectl apply -f "${SCRIPT_DIR}/kourier.yaml"
	kubectl patch configmap/config-network \
		--namespace knative-serving \
		--type merge \
		--patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'
	kubectl patch configmap/config-domain \
		--namespace knative-serving \
		--type merge \
		--patch '{"data":{"nuhakala.com":""}}'
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-${KN_VERSION}/serving-hpa.yaml
	watch kubectl get pods -n knative-serving
}

delete_kourier() {
	set +e
	kubectl delete -f https://github.com/knative/serving/releases/download/knative-${KN_VERSION}/serving-hpa.yaml
	kubectl delete -f ${SCRIPT_DIR}/kourier.yaml
	kubectl delete -f https://github.com/knative/serving/releases/download/knative-${KN_VERSION}/serving-core.yaml
	kubectl delete -f https://github.com/knative/serving/releases/download/knative-${KN_VERSION}/serving-crds.yaml
}

case $1 in
	install) kourier ;;
	delete) delete_kourier ;;
	*)
		echo "Wrong arg, either install or delete"
		;;
esac
