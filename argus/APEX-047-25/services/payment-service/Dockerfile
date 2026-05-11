FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download || go mod tidy
COPY . .
RUN go mod tidy && CGO_ENABLED=0 go build -o payment main.go

FROM alpine:3.18
RUN apk --no-cache add curl wget
WORKDIR /app
COPY --from=builder /app/payment .
EXPOSE 3003
CMD ["./payment"]
