import os
import pickle
import base64
from flask import Flask, request

app = Flask(__name__)
FLAG = os.environ.get("FLAG", open("/flag.txt").read().strip())


@app.route("/")
def index():
    return "<h1>OA System</h1><p>Internal Office Automation</p><ul><li><a href='/import'>Data Import</a></li></ul>"


@app.route("/import", methods=["GET", "POST"])
def import_data():
    if request.method == "GET":
        return '''<h1>Data Import</h1>
<form method="POST">
<label>Paste serialized data (base64):</label><br>
<textarea name="data" rows="5" cols="60"></textarea><br>
<button type="submit">Import</button>
</form>'''

    data = request.form.get("data", "")
    if not data:
        return "No data provided", 400

    try:
        obj = pickle.loads(base64.b64decode(data))
        return f"<h1>Import Success</h1><p>Imported {type(obj).__name__} object</p>"
    except Exception as e:
        return f"<h1>Import Failed</h1><p>Error: {e}</p>", 400


@app.route("/status")
def status():
    return f"<h1>OA Status</h1><p>Running. Flag: {FLAG}</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
