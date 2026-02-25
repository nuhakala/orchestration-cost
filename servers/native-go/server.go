package main

import (
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

var sleep = time.Second * 3
// In case we would want to limit the concurrency.
// No really need to limit concurrency as it is limited by hey
// to a fixed RPS value.
// var concurrent = 10
// var sem = make(chan struct{}, concurrent)

func getWait(w http.ResponseWriter, r *http.Request) {
	// sem <- struct{}{}
	// defer func() { <-sem }()

	time.Sleep(sleep)
	response := fmt.Sprintf("Slept for %v in native Go!\n", sleep)
	io.WriteString(w, response)
}

func getRoot(w http.ResponseWriter, r *http.Request) {
	// sem <- struct{}{}
	// defer func() { <-sem }()

	io.WriteString(w, "Hello from native go!\n")
}

func main() {
	http.HandleFunc("/", getRoot)
	http.HandleFunc("/wait", getWait)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	fmt.Printf("Starting server on port %s\n", port)
	err := http.ListenAndServe(fmt.Sprintf(":%s", port), nil)
	if errors.Is(err, http.ErrServerClosed) {
		fmt.Printf("server closed\n")
	} else if err != nil {
		fmt.Printf("error starting server: %s\n", err)
		os.Exit(1)
	}
}
