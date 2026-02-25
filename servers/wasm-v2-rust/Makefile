REGISTRY_ADDRESS?=10.164.178.1:5000
WASM_BINARY=./target/wasm32-wasip2/release/hello_world.wasm
IMAGE_NAME=wash-rust-server:0.1.0

all: build

build:
	washv2 build

push:
	washv2 oci push $(REGISTRY_ADDRESS)/$(IMAGE_NAME) $(WASM_BINARY) --insecure
