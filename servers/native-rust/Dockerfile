FROM rust:1.92-alpine3.22 as builder

WORKDIR /usr/src/app

COPY . .
RUN cargo install --path .

# Create smaller image for app, build deps are 1.8gb
FROM alpine:3.22
COPY --from=builder /usr/local/cargo/bin/app /usr/local/bin/app
ENV ROCKET_ADDRESS="0.0.0.0"
ENV ROCKET_PORT=8080
ENV ROCKET_WORKERS=10

CMD ["app"]
