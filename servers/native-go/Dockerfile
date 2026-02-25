FROM golang:1.25-alpine3.22 as builder

WORKDIR /usr/src/app

# pre-copy/cache go.mod for pre-downloading dependencies and only redownloading them in subsequent builds if they change
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -v -o /usr/local/bin/app ./...

# Create smaller image for app
FROM alpine:3.22
COPY --from=builder /usr/local/bin/app /usr/local/bin/app

CMD ["app"]
