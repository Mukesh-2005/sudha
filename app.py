import sqlite3
from functools import wraps

from flask import Flask, g, redirect, render_template, request, session, url_for

DB_PATH = "voting.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deploying"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    student_id = request.form.get("student_id", "").strip()
    password = request.form.get("password", "").strip()

    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE STUDENT_ID = ?", (student_id,)
    ).fetchone()

    if student is None or student["PASSWORD"] != password:
        return render_template("login.html", error="Invalid Student ID or password.")

    session["student_id"] = student["STUDENT_ID"]
    return redirect(url_for("vote"))


@app.route("/vote", methods=["GET", "POST"])
@login_required
def vote():
    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE STUDENT_ID = ?", (session["student_id"],)
    ).fetchone()

    if student["VOTE_STATUS"] == 1:
        return redirect(url_for("confirmation"))

    if request.method == "POST":
        candidate_id = request.form.get("candidate_id")
        candidate = db.execute(
            "SELECT * FROM candidates WHERE CANDIDATE_ID = ?", (candidate_id,)
        ).fetchone()

        if candidate is None:
            candidates = db.execute("SELECT * FROM candidates").fetchall()
            return render_template(
                "vote.html", student=student, candidates=candidates,
                error="Please select a valid candidate."
            )

        # Re-check vote status right before writing, to guard against a
        # double submit racing two requests for the same student.
        student = db.execute(
            "SELECT * FROM students WHERE STUDENT_ID = ?", (session["student_id"],)
        ).fetchone()
        if student["VOTE_STATUS"] == 1:
            return redirect(url_for("confirmation"))

        db.execute(
            "UPDATE candidates SET VOTE_COUNT = VOTE_COUNT + 1 WHERE CANDIDATE_ID = ?",
            (candidate_id,),
        )
        db.execute(
            "UPDATE students SET VOTE_STATUS = 1, VOTED_FOR = ? WHERE STUDENT_ID = ?",
            (candidate_id, session["student_id"]),
        )
        db.commit()
        return redirect(url_for("confirmation"))

    candidates = db.execute("SELECT * FROM candidates").fetchall()
    return render_template("vote.html", student=student, candidates=candidates)


@app.route("/confirmation")
@login_required
def confirmation():
    db = get_db()
    student = db.execute(
        """SELECT students.*, candidates.CANDIDATE_NAME, candidates.PARTY
           FROM students LEFT JOIN candidates
           ON students.VOTED_FOR = candidates.CANDIDATE_ID
           WHERE STUDENT_ID = ?""",
        (session["student_id"],),
    ).fetchone()
    return render_template("confirmation.html", student=student)


@app.route("/logout")
def logout():
    session.pop("student_id", None)
    return redirect(url_for("login"))


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("results"))
        return render_template("admin_login.html", error="Invalid admin credentials.")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/results")
@admin_required
def results():
    db = get_db()
    candidates = db.execute(
        "SELECT * FROM candidates ORDER BY VOTE_COUNT DESC"
    ).fetchall()
    total_students = db.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
    total_votes = db.execute(
        "SELECT COUNT(*) AS c FROM students WHERE VOTE_STATUS = 1"
    ).fetchone()["c"]
    return render_template(
        "results.html", candidates=candidates,
        total_students=total_students, total_votes=total_votes
    )


if __name__ == "__main__":
    app.run(debug=True)
