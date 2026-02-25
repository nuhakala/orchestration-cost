package main

import (
	"fmt"
	"io"
	"net/http"
	"time"

	spinhttp "github.com/spinframework/spin-go-sdk/v2/http"
)

func init() {
	spinhttp.Handle(handleRequest)
}

func getWait(w http.ResponseWriter, _ *http.Request) {
	sleep := time.Second * 3
	time.Sleep(sleep)
	response := fmt.Sprintf("Slept for %v in spin Go!\n", sleep)
	io.WriteString(w, response)
}

func getRoot(w http.ResponseWriter, _ *http.Request) {
	io.WriteString(w, "Hello from spin go!\n")
}

//nolint:revive
func handleRequest(w http.ResponseWriter, r *http.Request) {
	switch r.URL.Path {
	case "/":
		getRoot(w, r)
	case "/wait":
		getWait(w, r)
	}
}
