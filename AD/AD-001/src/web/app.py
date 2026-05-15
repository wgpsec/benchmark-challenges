import os
import subprocess

from flask import Flask, render_template, send_from_directory, request, abort, session, redirect

app = Flask(__name__)
app.secret_key = os.urandom(16).hex()

LDAP_USER = "web_admin"
LDAP_PASS = "WebAdmin@2024!"


@app.route("/")
def index():
    if session.get("logged_in"):
        return redirect("/dashboard")
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username == LDAP_USER and password == LDAP_PASS:
        session["logged_in"] = True
        return redirect("/dashboard")
    return render_template("index.html", error="Invalid credentials")


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")
    flag = open("/flag.txt").read().strip()
    return render_template("dashboard.html", flag=flag)


@app.route("/diagnostic", methods=["POST"])
def diagnostic():
    if not session.get("logged_in"):
        return redirect("/")
    host = request.form.get("host", "")
    action = request.form.get("action", "ping")
    if not host:
        return render_template("dashboard.html",
                               flag=open("/flag.txt").read().strip(),
                               diag_error="Please enter a hostname")
    if action == "nslookup":
        result = subprocess.getoutput(f"nslookup {host}")
    else:
        result = subprocess.getoutput(f"ping -c 2 {host}")
    return render_template("dashboard.html",
                           flag=open("/flag.txt").read().strip(),
                           diag_result=result, diag_host=host)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


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
