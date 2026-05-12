import os
import subprocess
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/diagnostic", methods=["POST"])
def diagnostic():
    host = request.form.get("host", "")
    if not host:
        return render_template("index.html", error="Please enter a host")
    result = subprocess.getoutput(f"ping -c 2 {host}")
    return render_template("index.html", result=result, host=host)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
