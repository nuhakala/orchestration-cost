#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/version.sh"

if ! wash -V > /dev/null; then
	wget -O wash https://github.com/wasmCloud/wash/releases/download/wash-${WC_VERSION}/wash-${ARCH_86}-unknown-linux-musl
	sudo chmod +x wash
	sudo mv wash /usr/local/bin
fi

if ! wasm-tools -V > /dev/null; then
	wget -O tools.tar.gz https://github.com/bytecodealliance/wasm-tools/releases/download/v${WASM_TOOLS_VER}/wasm-tools-${WASM_TOOLS_VER}-${ARCH_86}-linux.tar.gz
	tar xf tools.tar.gz
	sudo mv wasm-tools-${WASM_TOOLS_VER}-${ARCH_86}-linux/wasm-tools /usr/local/bin
	rm tools.tar.gz
	rm -rf wasm-tools-${WASM_TOOLS_VER}-${ARCH_86}-linux
fi
