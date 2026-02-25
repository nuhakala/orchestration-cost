export K8S_VERSION=v1.32
export K8S_VERSION_MINOR=v1.32.11
export KN_VERSION=v1.20.0
export K3S_VERSION="v1.32.11+k3s1"
export K0S_VERSION=v1.32.11+k0s.0
export SPIN_VERSION=v3.5.1
export GO_VER=1.24.12
export SPIN_SHIM_VERSION=v0.22.0
export KEADM_VERSION=v1.22.1
export ISTIO_VERSION=1.27.1
export FAAS_HELM_VERSION=14.2.132
export WC_VERSION=v2.0.0-rc.6
export TINYGO_VER=0.39.0
export WASM_TOOLS_VER=1.244.0
export KEDA_VERSION=2.18.3

# Computer architecture
ARCH="arm64"
ARCH_86="arm64"
if [[ $(uname -m) == "x86_64" ]]; then
	ARCH="amd64"
	ARCH_86="x86_64"
fi
export ARCH
export ARCH_86

# Docker stuff
export DOCKER_VERSION_STRING=5:29.1.3-1~ubuntu.24.04~noble
export CONTAINERD_VERSION_STRING=2.2.0-2~ubuntu.24.04~noble
export MY_REG=10.164.178.1:5000

# available IP address
INTERFACE="ens3"
IP_ADDR_PREFIX="10.164"

# For raspberry pi
if [[ "${ARCH}" == "arm64" ]]; then
	INTERFACE="wlan0"
	IP_ADDR_PREFIX="192.168.68"
	export DOCKER_VERSION_STRING=5:29.1.3-1~debian.13~trixie
	export CONTAINERD_VERSION_STRING=2.1.5-1~debian.13~trixie
	export MY_REG=192.168.68.54:5000
fi

IP_ADDRESS=$(ip -4 addr show ${INTERFACE} | grep "${IP_ADDR_PREFIX}" | awk '{print $2}' | cut -d/ -f1)
export IP_ADDRESS
