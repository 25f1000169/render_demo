from datetime import datetime
import sqlite3
from flask import Flask, g, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE = "notes.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """
        )
        db.commit()


# Home / Canvas Editor Route (New or Edit mode)
@app.route("/")
def index():
    note_id = request.args.get("id")
    current_note = None
    if note_id:
        db = get_db()
        cursor = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        current_note = cursor.fetchone()
    return render_template("index.html", current_note=current_note)


# API Route to Save a Note (JSON Canvas State)
@app.route("/save", methods=["POST"])
def save_note():
    data = request.get_json()
    title = data.get("title", "Untitled Sketch")
    canvas_json = data.get("data")
    note_id = data.get("id")

    db = get_db()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if note_id:
        # Update existing note
        db.execute(
            "UPDATE notes SET title = ?, data = ? WHERE id = ?",
            (title, canvas_json, note_id),
        )
        db.commit()
        return jsonify({"success": True, "id": note_id})
    else:
        # Insert new note
        cursor = db.execute(
            "INSERT INTO notes (title, data, created_at) VALUES (?, ?, ?)",
            (title, canvas_json, timestamp),
        )
        db.commit()
        return jsonify({"success": True, "id": cursor.lastrowid})


# API Route to List All Saved Notes
@app.route("/notes", methods=["GET"])
def list_notes():
    db = get_db()
    cursor = db.execute("SELECT id, title, created_at FROM notes ORDER BY id DESC")
    notes = [dict(row) for row in cursor.fetchall()]
    return jsonify(notes)


# API Route to Delete a Note
@app.route("/delete/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    db = get_db()
    db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return jsonify({"success": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
