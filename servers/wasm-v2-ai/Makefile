REGISTRY_ADDRESS?=10.164.178.1:5000
WASM_BINARY=./target/wasm32-wasip2/release/hello_world.wasm
IMAGE=wash-ai:0.1.0

.PHONY: build
all:
	washv2 build
	washv2 push --insecure $(REGISTRY_ADDRESS)/$(IMAGE) $(WASM_BINARY)

build:
	washv2 build

wasmtime:
	wasmtime serve -S cli=y $(WASM_BINARY)

push:
	washv2 oci push $(REGISTRY_ADDRESS)/$(IMAGE) $(WASM_BINARY) --insecure
