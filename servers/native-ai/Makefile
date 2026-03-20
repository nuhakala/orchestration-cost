MANIFEST=rust-server-ai-manifest
IMAGE_NAME=rust-server-ai
REGISTRY=10.164.178.1:5000

all:
	podman manifest create --amend --tls-verify=false $(IMAGE_NAME)
	podman build -f ./Dockerfile -t $(REGISTRY)/$(IMAGE_NAME) --platform linux/arm64 --manifest $(MANIFEST) ..
	podman build -f ./Dockerfile -t $(REGISTRY)/$(IMAGE_NAME) --platform linux/amd64 --manifest $(MANIFEST) ..
	podman manifest push $(MANIFEST) --tls-verify=false $(REGISTRY)/$(IMAGE_NAME)

push:
	podman manifest push $(MANIFEST) --tls-verify=false $(REGISTRY)/$(IMAGE_NAME)
