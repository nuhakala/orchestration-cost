#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"
"${SCRIPT_DIR}/../install-helm.sh"
"${SCRIPT_DIR}/../install-kubeadm.sh" # for kubectl
# "${SCRIPT_DIR}/../prepare.sh" # ensure ip address is there

case $1 in
	single)
		VALUES_FILE="values.single.yaml"
		;;
	multi)
		VALUES_FILE="values.multi.yaml"
		;;
	test)
		VALUES_FILE="values.test.yaml"
		;;
	kube1)
		VALUES_FILE="values.kubeedge-sc1.yaml"
		;;
	kube2)
		VALUES_FILE="values.kubeedge-sc2.yaml"
		;;
	*)
		echo "Wrong arg"
		exit 0
		;;
esac

helm upgrade wasmcloud \
	--install \
	-f "${SCRIPT_DIR}/${VALUES_FILE}" \
	"${SCRIPT_DIR}/runtime-operator_rc6/"
