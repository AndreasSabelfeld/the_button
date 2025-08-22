from flask import Blueprint, request, render_template
from app.services import register_user, login_user, get_user_presses, get_user_id, get_total_user_presses, delete_user_account, increment_user_presses, get_leaderboard

routes = Blueprint("routes", __name__)


@routes.route("/")
def index():
    return render_template("index.html")


@routes.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")


@routes.route("/api/leaderboard", methods=["GET"])
def build_leaderboard():
    return get_leaderboard()

@routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    return register_user(data)


@routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    return login_user(data)
    

@routes.route("/num", methods=["GET"])
def get_presses():
    return get_total_user_presses()


@routes.route("/get_user_id/<username>", methods=["GET"])
def get_id(username: str):
    return get_user_id(username)
    
    
@routes.route("/get_user_presses/<user_id>", methods=["GET"])
def get_personal_presses(user_id: int):
    return get_user_presses(user_id)
    
    
@routes.route("/delete_account/<int:user_id>", methods=["DELETE"])
def delete_account(user_id: int):
    return delete_user_account(user_id)


@routes.route("/press/<int:user_id>", methods=["POST"])
def press(user_id: int):
    return increment_user_presses(user_id)