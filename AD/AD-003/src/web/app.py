import os
import requests
from flask import Flask, render_template, request
from urllib.parse import urlparse

app = Flask(__name__)


@app.route("/")
def index():
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
