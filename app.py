from flask import Flask, request, jsonify, render_template, Response
from flask_socketio import SocketIO, emit
import sqlite3, time
import os

app = Flask(__name__)
socketio = SocketIO(app)

def get_db_connection():
    conn = sqlite3.connect("the_button.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            presses INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"success": False, "error": "Username required"})

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, presses) VALUES (?, 0)", (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    finally:
        conn.close()

    return jsonify({"success": True}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"success": False, "error": "Username required"})

    conn = get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if row:
        return jsonify({"success": True, "user_id": row["id"]})
    else:
        return jsonify({"success": False, "error": "Username not found"})


@app.route("/get_user_id/<username>", methods=["GET"])
def get_user_id(username):
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row:
        return jsonify({"id": row["id"]})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/num", methods=["GET"])
def get_presses() -> int:
    conn = get_db_connection()
    row = conn.execute("SELECT SUM(presses) AS total_presses FROM users;").fetchone()
    conn.close()
    presses = row[0] if row[0] is not None else 0  # handle NULL
    return jsonify({"total_presses": presses})

@app.route("/press/<int:user_id>", methods=["POST"])
def increment(user_id: int) -> Response:
    conn = get_db_connection()
    conn.execute("UPDATE users SET presses = presses + 1 WHERE id = ?;", (user_id,))
    conn.commit()
    conn.close()

    # Notify all SSE clients
    socketio.emit("update_presses")

    return jsonify({"success": True}), 201

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5100))

    init_db()
    socketio.run(app, 
                 debug=True, 
                 host="0.0.0.0", 
                 port=port, 
                 allow_unsafe_werkzeug=True)  # nötig bei SocketIO + Flask 2.3+
