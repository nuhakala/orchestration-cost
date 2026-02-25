COMPONENT=spin-go-server
TAG=latest
REGISTRY_ADDRESS ?= 10.164.178.1:5000
MANIFEST=spin-go-server.yaml

build:
	spin build

push:
	spin registry push --insecure --build $(REGISTRY_ADDRESS)/$(COMPONENT):$(TAG)

manifest:
	spin kube scaffold --from $(REGISTRY_ADDRESS)/$(COMPONENT):$(TAG) \
		--out $(MANIFEST)

deploy:
	kubectl apply -f $(MANIFEST)
