#!/usr/bin/env bash

set -xe

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"
"${SCRIPT_DIR}/../install-docker.sh"

# Install keadm
if ! keadm version > /dev/null; then
	wget https://github.com/kubeedge/kubeedge/releases/download/${KEADM_VERSION}/keadm-${KEADM_VERSION}-linux-${ARCH}.tar.gz
	tar -zxvf keadm-${KEADM_VERSION}-linux-${ARCH}.tar.gz
	sudo cp keadm-${KEADM_VERSION}-linux-${ARCH}/keadm/keadm /usr/local/bin/keadm
	sudo rm -r ./keadm*
fi

# In case the kubeedge components are in different registry
# KUBEEDGE_REGISTRY="${MY_REG}"
KUBEEDGE_REGISTRY=192.168.68.51:5000

cloud () {
	# Install cluster
	"${SCRIPT_DIR}/../native-infra/init-node.sh"

	# Fucking important this line
	sudo iptables -P FORWARD ACCEPT

	sudo keadm init \
		--advertise-address="${IP_ADDRESS}" \
		--kubeedge-version=v1.22.0 \
		--kube-config="${HOME}/.kube/config" \
		--set cloudCore.modules.dynamicController.enable=true \
		--image-repository "${KUBEEDGE_REGISTRY}"
	sleep 5
}

joinedge() {
	sudo keadm gettoken --kube-config="${HOME}/.kube/config"
	echo "Ip: ${IP_ADDRESS}"
}

edge () {
	if [[ $1 == "" ]]; then
		echo "Need the token"
		exit 1
	fi
	if [[ $2 == "" ]]; then
		echo "Need IP address of cloud"
		exit 1
	fi
	TOKEN=$1
	IP_ADDRESS=$2

	# install cni and configure containerd
	"${SCRIPT_DIR}/../containerd/install-cni.sh"
	"${SCRIPT_DIR}/../containerd/configure.sh" edge

	sudo keadm join \
		--cloudcore-ipport="${IP_ADDRESS}":10000 \
		--token "${TOKEN}" \
		--kubeedge-version=v1.22.0 \
		--image-repository "${KUBEEDGE_REGISTRY}/kubeedge" \
		--edgenode-name edge
	
	# THIS WAS NEEDED TO ALLOW SPINKUBE CONTAINER TO FETCH WASM IMAGE
	sudo iptables -P FORWARD ACCEPT
}

case $1 in
    "cloud")
		cloud
		joinedge
		;;
    "edge")
		edge "$2" "$3"
		;;
	"token") joinedge ;;
    *)
		cat <<EOF
Usage:
	cloud
	edge <token> <ip>
	token
EOF
        ;;
esac

