IMAGE_NAME=rust-server-final-arm
REGISTRY=192.168.68.54:5000

all:
	podman build -t $(REGISTRY)/$(IMAGE_NAME) .
	podman push --tls-verify=false $(REGISTRY)/$(IMAGE_NAME)

push:
	podman push --tls-verify=false $(REGISTRY)/$(IMAGE_NAME)
