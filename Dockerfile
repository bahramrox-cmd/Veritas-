# syntax=docker/dockerfile:1
FROM alpine:3.20

WORKDIR /app
COPY README.md .

 ["echo", "veritas docker-build-cloud-demo"]
