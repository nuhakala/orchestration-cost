#!/usr/bin/env bash

set -x

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/version.sh"

sudo rm -rf /usr/local/go
wget "https://go.dev/dl/go${GO_VER}.linux-${ARCH}.tar.gz"
sudo tar -C /usr/local -xzf "go${GO_VER}.linux-${ARCH}.tar.gz"
rm "./go${GO_VER}.linux-${ARCH}.tar.gz"
echo 'export PATH=$PATH:/usr/local/go/bin:${HOME}/go/bin' >> ${HOME}/.bashrc

wget -O tinygo.deb https://github.com/tinygo-org/tinygo/releases/download/v${TINYGO_VER}/tinygo_${TINYGO_VER}_${ARCH}.deb
sudo dpkg -i tinygo.deb
rm tinygo.deb
