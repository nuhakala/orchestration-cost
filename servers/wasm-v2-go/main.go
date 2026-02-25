//go:generate go tool wit-bindgen-go generate --world wasmcloud:http-server/http-server --out gen ./wit

package main

import (
	"net/http"
	"time"
	"fmt"

	"github.com/julienschmidt/httprouter"
	"go.wasmcloud.dev/component/net/wasihttp"
)

var sleep = time.Second * 3

func init() {
	router := httprouter.New()
	router.HandlerFunc(http.MethodGet, "/", indexHandler)
	router.HandlerFunc(http.MethodGet, "/wait", waitHandler)
	wasihttp.Handle(router)
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	_, _ = w.Write([]byte("Hello from wasm go!"))
}

func waitHandler(w http.ResponseWriter, r *http.Request) {
	time.Sleep(sleep)
	response := fmt.Sprintf("Slept for %v in wasm Go!\n", sleep)
	_, _ = w.Write([]byte(response))
}

func main() {}
