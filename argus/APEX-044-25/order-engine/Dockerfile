FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod go.sum* ./
COPY main.go .
RUN go mod tidy && go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -o order-engine .

FROM alpine:3.19

RUN apk add --no-cache curl

WORKDIR /app
COPY --from=builder /app/order-engine .

EXPOSE 8081

CMD ["./order-engine"]
