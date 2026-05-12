import os
import socket
import urllib.parse
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/preview", methods=["POST"])
def preview():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template("index.html", error="Please enter a URL")

    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (80 if parsed.scheme == "http" else 6379)
        path = parsed.path or "/"

        if parsed.scheme in ("http", "https"):
            import requests as req
            resp = req.get(url, timeout=5)
            content = resp.text[:2000]
        elif parsed.scheme in ("redis", "dict", "gopher", ""):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            if parsed.scheme == "dict":
                cmd = path.lstrip("/").replace(":", " ")
                sock.sendall(f"{cmd}\r\nQUIT\r\n".encode())
            elif parsed.scheme in ("redis", ""):
                raw = path.lstrip("/").replace("/", "\r\n")
                if raw:
                    sock.sendall(f"{raw}\r\nQUIT\r\n".encode())
                else:
                    sock.sendall(b"INFO\r\nQUIT\r\n")
            else:
                payload = urllib.parse.unquote(path.lstrip("/"))
                sock.sendall(payload.encode() + b"\r\n")
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            sock.close()
            content = data.decode("utf-8", errors="replace")[:2000]
        else:
            content = f"Unsupported scheme: {parsed.scheme}"
    except Exception as e:
        content = f"Error fetching URL: {e}"

    return render_template("index.html", result=content, url=url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
