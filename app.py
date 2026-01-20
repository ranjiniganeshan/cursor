from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from pathlib import Path

app = Flask(__name__)

# SQLite database file (stored next to this script)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"


def get_db():
    """
    Open a database connection for the current request (re-used via flask.g).
    """
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row  # lets us access columns by name
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    """
    Close the database at the end of the request (if it was opened).
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    Create the 'tasks' table if it doesn't exist.
    This runs on app startup (simple approach for beginners).
    """
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    db.commit()


@app.before_request
def before_request():
    # Ensure DB/table exists before handling any request
    init_db()


@app.get("/")
def index():
    """
    GET / -> show all tasks
    """
    db = get_db()
    tasks = db.execute(
        "SELECT id, title, description, completed FROM tasks ORDER BY id DESC"
    ).fetchall()
    return render_template("index.html", tasks=tasks)


@app.post("/add")
def add_task():
    """
    POST /add -> add new task
    """
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if title:  # basic validation: require title
        db = get_db()
        db.execute(
            "INSERT INTO tasks (title, description, completed) VALUES (?, ?, 0)",
            (title, description),
        )
        db.commit()

    return redirect(url_for("index"))


@app.post("/complete/<int:task_id>")
def complete_task(task_id):
    """
    POST /complete/<id> -> mark task completed
    """
    db = get_db()
    db.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    # debug=True auto-reloads on save; good for local learning
    app.run(debug=True)