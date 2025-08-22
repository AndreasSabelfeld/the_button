from flask import jsonify
from app import supabase, socketio
from app.utils import get_total_presses


def register_user(data):
    username = data.get("username")
    if not username:
        return jsonify({"success": False, "error": "Username required"}), 400

    existing = supabase.table("users").select("*").eq("username", username).execute()
    if existing.data:
        return jsonify({"success": False, "error": "Username already exists"}), 409

    supabase.table("users").insert({"username": username, "presses": 0}).execute()
    return jsonify({"success": True}), 201


def login_user(data):
    username = data.get("username")
    if not username:
        return jsonify({"success": False, "error": "Username required"}), 400

    user = supabase.table("users").select("*").eq("username", username).execute()
    if user.data:
        return jsonify({"success": True, "user_id": user.data[0]["id"]})
    else:
        return jsonify({"success": False, "error": "Username not found"}), 404
    

def get_total_user_presses() -> int:
    """Returns the sum of all presses."""
    try:
        total = get_total_presses()
        return jsonify({"total_presses": total})
    except Exception as e:
        print("Error in /num:", e)
        return jsonify({"error": str(e)}), 500
    

def get_user_id(username: str):
    user = supabase.table("users").select("id").eq("username", username).execute()

    if user.data:
        return jsonify({"id": user.data[0]["id"]})
    else:
        return jsonify({"error": "User not found"}), 404
    

def get_user_presses(user_id: int):
    """Returns the number of presses for a specific user."""
    presses = supabase.table("users").select("presses").eq("id", user_id).execute()

    if presses.data:
        return jsonify({"presses": presses.data[0]["presses"]})
    else:
        return jsonify({"error": "Presses not found"}), 404
    

def delete_user_account(user_id: int):
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        return jsonify({"success": False, "error": "User not found"}), 404

    supabase.table("users").delete().eq("id", user_id).execute()
    return jsonify({"success": True}), 200

def increment_user_presses(user_id: int):
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        return jsonify({"success": False, "error": "User not found"}), 404

    new_count = user.data[0]["presses"] + 1
    supabase.rpc("increment_presses", {"p_user_id": user_id}).execute()

    # Notify all clients
    socketio.emit("update", {"total_presses": get_total_presses()})
    return jsonify({"success": True, "total_presses": new_count}), 201

def get_leaderboard():
    rows = supabase.table("users").select("username, presses").order("presses", desc=True).execute()
    users = [{"username": row["username"], "presses": row["presses"]} for row in rows.data]
    return jsonify({"success": True, "leaderboard": users})
