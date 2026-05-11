FROM golang:1.21-alpine AS builder
WORKDIR /app
ENV GOPROXY=https://goproxy.cn,direct
ENV GONOSUMCHECK=*
ENV GONOSUMDB=*
COPY go.mod go.sum main.go ./
RUN go mod download
RUN CGO_ENABLED=0 go build -o server main.go

FROM alpine:3.18
RUN apk add --no-cache ca-certificates curl
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 3003
CMD ["./server"]
