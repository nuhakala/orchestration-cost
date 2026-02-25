#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/../version.sh"

# install cni
if [[ ! -e /opt/cni/bin/bridge ]]; then
	wget -O cni-plugins.tar.gz https://github.com/containernetworking/plugins/releases/download/v1.9.0/cni-plugins-linux-${ARCH}-v1.9.0.tgz
	sudo mkdir -p /opt/cni/bin
	sudo tar Cxzvf /opt/cni/bin cni-plugins.tar.gz
	rm cni-plugins.tar.gz
	sudo mkdir -p /etc/cni/net.d
fi

# install cni cnofig
if [[ ! -e /etc/cni/net.d/10-containerd-netconflist ]]; then
	cat <<EOF | sudo tee /etc/cni/net.d/10-containerd-net.conflist 
{
  "cniVersion": "1.0.0",
  "name": "containerd-net",
  "plugins": [
    {
      "type": "bridge",
      "bridge": "cni0",
      "isGateway": true,
      "ipMasq": true,
      "promiscMode": true,
      "ipam": {
        "type": "host-local",
        "ranges": [
          [{
            "subnet": "10.88.0.0/16"
          }],
          [{
            "subnet": "2001:db8:4860::/64"
          }]
        ],
        "routes": [
          { "dst": "0.0.0.0/0" },
          { "dst": "::/0" }
        ]
      }
    },
    {
      "type": "portmap",
      "capabilities": {"portMappings": true}
    }
  ]
}
EOF
fi
