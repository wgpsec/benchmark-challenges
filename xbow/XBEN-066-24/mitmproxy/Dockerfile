FROM mitmproxy/mitmproxy:6.0.2

WORKDIR /app

ENTRYPOINT mitmdump --mode reverse:http://${SERVER_HOSTNAME}:${SERVER_PORT} -p 80 --set block_global=false --no-http2