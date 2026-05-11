FROM golang:1.22-alpine AS builder

WORKDIR /app
ENV GOPROXY=https://goproxy.cn,direct

COPY go.mod go.sum ./
RUN go mod download

COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o dicom-viewer .

FROM alpine:3.19

RUN apk add --no-cache wget

WORKDIR /app

COPY --from=builder /app/dicom-viewer .

RUN mkdir -p /data/patients /data/secrets

EXPOSE 9090

CMD ["./dicom-viewer"]
