import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-please")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as schema:
                db.executescript(schema.read())
            db.commit()


@app.teardown_appcontext

def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    results = cur.fetchall()
    cur.close()
    return (results[0] if results else None) if one else results


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


def current_user():
    user_id = session.get("user_id")
    if user_id:
        return query_db("SELECT id, username FROM users WHERE id = ?", (user_id,), one=True)
    return None


def login_required():
    if not current_user():
        flash("Please log in to continue.", "warning")
        return False
    return True




@app.route("/")
def index():
    return render_template("index.html", user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("register"))

        if query_db("SELECT id FROM users WHERE username = ?", (username,), one=True):
            flash("That username is already taken.", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        execute_db("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = query_db("SELECT id, username, password_hash FROM users WHERE username = ?", (username,), one=True)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        flash("Welcome back, {}!".format(user["username"]), "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    tasks = query_db(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY completed, due_date IS NULL, due_date",
        (user["id"],),
    )
    return render_template("dashboard.html", user=user, tasks=tasks)


@app.route("/task/new", methods=["GET", "POST"])
def create_task():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "")

        if not title:
            flash("Task title cannot be empty.", "error")
            return redirect(url_for("create_task"))

        user = current_user()
        execute_db(
            "INSERT INTO tasks (user_id, title, description, due_date) VALUES (?, ?, ?, ?)",
            (user["id"], title, description, due_date or None),
        )
        flash("Task added successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("task_form.html", user=current_user(), task=None)


@app.route("/task/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    task = query_db("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user["id"]), one=True)
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "")
        completed = 1 if request.form.get("completed") == "on" else 0

        if not title:
            flash("Task title cannot be empty.", "error")
            return redirect(url_for("edit_task", task_id=task_id))

        execute_db(
            "UPDATE tasks SET title = ?, description = ?, due_date = ?, completed = ? WHERE id = ? AND user_id = ?",
            (title, description, due_date or None, completed, task_id, user["id"]),
        )
        flash("Task updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("task_form.html", user=user, task=task)


@app.route("/task/delete/<int:task_id>")
def delete_task(task_id):
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    execute_db("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user["id"]))
    flash("Task deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/task/toggle/<int:task_id>")
def toggle_task(task_id):
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    task = query_db("SELECT completed FROM tasks WHERE id = ? AND user_id = ?", (task_id, user["id"]), one=True)
    if task:
        execute_db(
            "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
            (0 if task["completed"] else 1, task_id, user["id"]),
        )
        flash("Task status updated.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
