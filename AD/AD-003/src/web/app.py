import os
import subprocess
import requests
from flask import Flask, render_template, request, abort
from urllib.parse import urlparse

app = Flask(__name__)


@app.route("/")
def index():
    if request.remote_addr == "127.0.0.1":
        return """<html><head><title>Castle Corp - Internal Portal</title></head><body>
<h1>Internal Service Status</h1>
<ul>
<li><a href="/preview">/preview</a> - Link Preview (public)</li>
<li><a href="/internal/exec">/internal/exec</a> - Maintenance Console (localhost only)</li>
<li><a href="/health">/health</a> - Health Check</li>
</ul>
<p>DB connection: mssql+pyodbc://sa:sa123456@db:1433/master</p>
</body></html>""", 200
    return render_template("index.html")


@app.route("/preview")
def preview():
    url = request.args.get("url", "")
    if not url:
        return render_template("index.html", error="Please provide a URL")
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "http://" + url
        resp = requests.get(url, timeout=5, allow_redirects=False)
        content = resp.text[:2000]
        return render_template("index.html", url=url, content=content,
                               status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return render_template("index.html", url=url,
                               error=f"Could not connect to {url}")
    except Exception as e:
        return render_template("index.html", url=url, error=str(e))


@app.route("/internal/exec")
def internal_exec():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    cmd = request.args.get("cmd", "")
    if not cmd:
        return "Usage: ?cmd=<command>\n", 200
    output = subprocess.getoutput(cmd)
    return output, 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
