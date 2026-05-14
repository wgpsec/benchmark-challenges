import os
from flask import Flask, render_template, send_from_directory, request, abort

app = Flask(__name__)

LDAP_USER = "web_admin"
LDAP_PASS = "WebAdmin@2024!"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username == LDAP_USER and password == LDAP_PASS:
        flag = open("/flag.txt").read().strip()
        return render_template("dashboard.html", flag=flag)
    return render_template("index.html", error="Invalid credentials")


@app.route("/about")
def about():
    return "<h1>About</h1><p>Corp Portal v2.3.1 - Internal Authentication Gateway</p>"


@app.route("/backup/<path:filename>")
def backup_files(filename):
    if ".." in filename:
        abort(403)
    return send_from_directory("/app/backup", filename)


@app.route("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /backup/\n", 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
