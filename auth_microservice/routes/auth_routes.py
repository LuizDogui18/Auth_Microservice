from flask import Blueprint, request
from services.auth_service import signup, login, recover_password, get_me

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/signup", methods=["POST"])
def route_signup():
    data = request.get_json()
    return signup(data["name"], data["email"], data["document"], data["password"])

@auth_bp.route("/login", methods=["POST"])
def route_login():
    data = request.get_json()
    return login(data["login"], data["password"])

@auth_bp.route("/recuperar-senha", methods=["POST"])
def route_recover():
    data = request.get_json()
    return recover_password(data["email"], data["document"], data["new_password"])

@auth_bp.route("/me", methods=["GET"])
def route_me():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"error": "Token ausente"}, 400

    token = auth_header.replace("SDWork ", "")
    return get_me(token)
