import os
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def index():
    return "<h1>Core Business System</h1><p>Internal analytics dashboard. Access /dashboard for reports.</p>"


@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard</h1><p>Revenue: $2.4M | Users: 15,203 | Uptime: 99.97%</p>"


@app.route("/api/query")
def api_query():
    q = request.args.get("q")
    # Bug: no null check, triggers TypeError when q is None
    result = eval(q)
    return str(result)


if __name__ == "__main__":
    os.environ["WERKZEUG_DEBUG_PIN"] = "off"
    app.run(host="0.0.0.0", port=8080, debug=True)
