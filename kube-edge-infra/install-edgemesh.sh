#!/usr/bin/env bash

kubectl taint nodes --all node-role.kubernetes.io/master-
kubectl label services kubernetes service.edgemesh.kubeedge.io/service-proxy-name=""
set -ex

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"

PSK_CIPHER=$(openssl rand -base64 32)

if [[ ! -d ${SCRIPT_DIR}/edgemesh ]]; then
	git clone -b release-1.17 https://github.com/kubeedge/edgemesh.git
fi

edgemesh() {
	# Before install, set relayNodes and PSK cipher into the configmap.
	# Copy the template in place and then edit the values there.
	AGENT_DIR=${SCRIPT_DIR}/edgemesh/build/agent/resources
	cp ${SCRIPT_DIR}/edgemesh-agent-04-configmap.yaml ${AGENT_DIR}/04-configmap.yaml
	sed -i "s/nodeName: .*/nodeName: $(hostname)/" ${AGENT_DIR}/04-configmap.yaml
	sed -i "s/advertiseAddress: .*/advertiseAddress: [\"${IP_ADDRESS}\"]/" ${AGENT_DIR}/04-configmap.yaml
	sed -i "s#psk: .*#psk: ${PSK_CIPHER}#" ${AGENT_DIR}/04-configmap.yaml

	kubectl apply -f edgemesh/build/crds/istio
	kubectl apply -f edgemesh/build/agent/resources/
}

gateway() {
	GATEWAY_DIR=${SCRIPT_DIR}/edgemesh/build/gateway/resources
	cp ${SCRIPT_DIR}/gateway-agent-04-configmap.yaml "${GATEWAY_DIR}/04-configmap.yaml"
	sed -i "s/nodeName: .*/nodeName: $(hostname)/" ${GATEWAY_DIR}/04-configmap.yaml
	sed -i "s/advertiseAddress: .*/advertiseAddress: [\"${IP_ADDRESS}\"]/" ${GATEWAY_DIR}/04-configmap.yaml
	sed -i "s#psk: .*#psk: ${PSK_CIPHER}#" ${GATEWAY_DIR}/04-configmap.yaml
	sed -i "s/nodeName: .*/nodeName: $(hostname)/" ${GATEWAY_DIR}/05-deployment.yaml

	kubectl apply -f edgemesh/build/gateway/resources
}

case $1 in
	both)
		edgemesh
		gateway
		;;
	mesh) edgemesh ;;
	gate) gateway ;;
	*)
		echo "Usage: both or mesh or gate"
		;;
esac
