CONTAINER_TAG=192.168.68.54:5000/go-server-final-arm

all:
	podman build -t $(CONTAINER_TAG) .
	podman push --tls-verify=false $(CONTAINER_TAG)

serve: 
	podman run -it --rm -p 3333:3333 --name my-go-server $(CONTAINER_TAG)

push:
	podman push --tls-verify=false $(CONTAINER_TAG)

run:
	go run .
