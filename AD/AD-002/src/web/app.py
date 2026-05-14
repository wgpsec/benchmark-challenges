import os
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)
DB_PATH = "/tmp/employees.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT, department TEXT, email TEXT,
        ad_account TEXT, ad_password TEXT
    )""")
    c.execute("SELECT COUNT(*) FROM employees")
    if c.fetchone()[0] == 0:
        employees = [
            (1, "Alice Chen", "Engineering", "alice@north.local", "alice.chen", "Alice#Eng2024"),
            (2, "Bob Wang", "Marketing", "bob@north.local", "bob.wang", "Marketing123"),
            (3, "Portal Service", "IT", "portal@north.local", "portal_svc", "Portal@Svc2024!"),
            (4, "Charlie Li", "Finance", "charlie@north.local", "charlie.li", "Finance@789"),
        ]
        c.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?)", employees)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    q = request.args.get("q", "")
    if not q:
        return render_template("index.html", results=[], query="")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Vulnerable to SQL injection
    query = f"SELECT id, name, department, email FROM employees WHERE name LIKE '%{q}%' OR department LIKE '%{q}%'"
    try:
        c.execute(query)
        results = c.fetchall()
    except Exception:
        results = []
    conn.close()
    return render_template("index.html", results=results, query=q)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
