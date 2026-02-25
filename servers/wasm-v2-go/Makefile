REGISTRY_ADDRESS?=10.164.178.1:5000
WASM_BINARY=./wasm-v2-go.wasm
IMAGE_NAME=wash-go-server:0.1.0

# Disable go.work from repository toplevel as this example is not part of the monorepo
GOWORK = off
export GOWORK

all: build

# .PHONY: build
build:
	tinygo build -target wasip2 -wit-package ./wit -wit-world http-server -o $(WASM_BINARY) ./

.PHONY: bindgen
bindgen:
	go generate ./...

push:
	washv2 oci push $(REGISTRY_ADDRESS)/$(IMAGE_NAME) $(WASM_BINARY) --insecure
