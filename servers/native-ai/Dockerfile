# IMPORTANT
# Fixture is copied to container, but I want to keep it one folder up, because
# it is shared between WASM components and this container. Hence, the build
# context needs to be also one dir up, and that affects the copy paths.

FROM rust:1.92-alpine3.22 as builder

WORKDIR /usr/src/app

COPY ./native-ai .
RUN cargo install --path .

# Create smaller image for app, build deps are 1.8gb
FROM alpine:3.22
COPY --from=builder /usr/local/cargo/bin/app /usr/local/bin/app
COPY ./fixture /fixture
ENV ROCKET_ADDRESS="0.0.0.0"
ENV ROCKET_PORT=8080
ENV ROCKET_WORKERS=10

CMD ["app"]
