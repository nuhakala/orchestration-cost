#!/bin/bash

set -xe

# Installation copied from https://docs.docker.com/engine/install/ubuntu/

if ! sudo docker version > /dev/null; then
	SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
	. "${SCRIPT_DIR}/version.sh"
	. /etc/os-release

	# Add Docker's official GPG key:
	sudo apt-get update
	sudo apt-get install -y ca-certificates curl
	sudo install -m 0755 -d /etc/apt/keyrings
	sudo curl -fsSL "https://download.docker.com/linux/${ID}/gpg" -o /etc/apt/keyrings/docker.asc
	sudo chmod a+r /etc/apt/keyrings/docker.asc

	# Add the repository to Apt sources:
	sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/${ID}
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

	# Check available version https://download.docker.com/linux/ubuntu/dists/noble/pool/stable/amd64/
	sudo apt update
	sudo apt install -y \
		docker-ce=$DOCKER_VERSION_STRING \
		docker-ce-cli=$DOCKER_VERSION_STRING \
		containerd.io=$CONTAINERD_VERSION_STRING \
		docker-buildx-plugin docker-compose-plugin
	sudo usermod -aG docker "${USER}"

	# Install cri-dockerd
	# wget https://github.com/Mirantis/cri-dockerd/releases/download/v0.3.21/cri-dockerd_0.3.21.3-0.debian-bookworm_amd64.deb
	# sudo apt install -y ./cri-dockerd_0.3.21.3-0.debian-bookworm_amd64.deb
	# rm ./cri-dockerd_0.3.21.3-0.debian-bookworm_amd64.deb

	# Enable insecure registry
	sudo mkdir -p /etc/docker/
	sudo cp "${SCRIPT_DIR}/daemon.json" /etc/docker/
	sudo systemctl restart docker
fi
