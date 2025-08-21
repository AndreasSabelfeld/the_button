from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import os
from supabase import create_client, Client

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Supabase Client
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_total_presses() -> int:
    """Returns the sum of all presses."""
    result = supabase.table("users").select("presses").execute()
    total = sum([r["presses"] for r in result.data])
    return total

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"success": False, "error": "Username required"}), 400

    existing = supabase.table("users").select("*").eq("username", username).execute()
    if existing.data:
        return jsonify({"success": False, "error": "Username already exists"}), 409

    supabase.table("users").insert({"username": username, "presses": 0}).execute()
    return jsonify({"success": True}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"success": False, "error": "Username required"}), 400

    user = supabase.table("users").select("*").eq("username", username).execute()
    if user.data:
        return jsonify({"success": True, "user_id": user.data[0]["id"]})
    else:
        return jsonify({"success": False, "error": "Username not found"}), 404

@app.route("/num", methods=["GET"])
def get_presses():
    try:
        total = get_total_presses()
        return jsonify({"total_presses": total})
    except Exception as e:
        print("Error in /num:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/get_user_id/<username>", methods=["GET"])
def get_user_id(username: str):
    user = supabase.table("users").select("id").eq("username", username).execute()

    if user.data:
        return jsonify({"id": user.data[0]["id"]})
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route("/get_user_presses/<user_id>", methods=["GET"])
def get_user_presses(user_id: int):
    presses = supabase.table("users").select("presses").eq("id", user_id).execute()

    if presses.data:
        return jsonify({"presses": presses.data[0]["presses"]})
    else:
        return jsonify({"error": "Presses not found"}), 404

@app.route("/press/<int:user_id>", methods=["POST"])
def press(user_id: int):
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        return jsonify({"success": False, "error": "User not found"}), 404

    new_count = user.data[0]["presses"] + 1
    supabase.table("users").update({"presses": new_count}).eq("id", user_id).execute()

    # Notify all clients
    socketio.emit("update", {"total_presses": get_total_presses()})
    return jsonify({"success": True, "total_presses": new_count}), 201

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5100))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
