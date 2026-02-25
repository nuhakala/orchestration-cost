#!/usr/bin/env bash

nettools() {
	kubectl run -it --rm --image=jrecord/nettools nettools --restart=Never --namespace=default
	# kubectl run -it --rm --image=jrecord/nettools nettools --restart=Never \
	#   --overrides='{ "apiVersion": "v1", "spec": { "nodeSelector": { "node-role.kubernetes.io/control-plane": ""}}}'
}

get_ip() {
	IP_ADDRESS=$(ip -4 addr show ens3 | grep 10.164 | awk '{print $2}' | cut -d/ -f1)
	echo "$IP_ADDRESS"
}

multipass_deploy() {
	TARGET=$2
	if [[ "${TARGET}" == "" ]]; then
		echo "Empty target, aborting..."
		exit 1
	fi
	if multipass list | grep -qF -- "${TARGET}"; then
		echo "Will delete ${TARGET}, continue? Y/n"
		read -r answer

		case "$answer" in
			[Yy]|"" )
				# User answered yes (or just pressed Enter)
				echo "Continuing..."
				;;
			[Nn] )
				echo "Aborted."
				exit 1
				;;
			*)
				echo "Invalid response. Aborted."
				exit 1
				;;
		esac
		multipass delete --purge "${TARGET}"
		echo "${TARGET} Deleted"
	fi
	echo "Launching new instance"
	multipass launch noble --name "${TARGET}" --cpus 6 --memory 16G --disk 30G
	echo "Mounting orch-cost-tools"
	multipass mount --type=classic ${HOME}/orch-cost-tools "${TARGET}":/home/ubuntu/orch-cost-tools
}

curl_knative() {
	curl -H "Host: knative-go.default.nuhakala.com" "$(get_ip)"
}

curl_faas() {
	# ip_address=$(get_ip)
	ip_address=192.168.0.1
	curl "${ip_address}:8080/function/faas-go-server"
}

case $1 in
	nettools) nettools ;;
	ip) get_ip ;;
	mp) multipass_deploy "$@" ;;
	kc) curl_knative ;;
	fc) curl_faas ;;
	*)
		cat <<EOF
Usage:
	nettools       | start nettools
	ip             | get ip
	mp <node name> | multipass reset
	kc             | curl knative with the IP of this node
	fc             | curl faas deployment with thi IP of this node
EOF
		;;
esac
