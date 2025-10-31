from flask import Blueprint, request
from auth_microservice.services.servico_autenticacao import (
    criar_usuario,
    autenticar_usuario,
    redefinir_senha,
    confirmar_redefinicao,
    obter_usuario_autenticado
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/signup", methods=["POST"])
def rota_signup():
    dados = request.get_json()
    return criar_usuario(
        dados["nome"],
        dados["email"],
        dados["documento"],
        dados["senha"]
    )

@auth_bp.route("/login", methods=["POST"])
def rota_login():
    dados = request.get_json()
    return autenticar_usuario(dados["email"], dados["senha"])

@auth_bp.route("/recover", methods=["POST"])
def rota_recuperar():
    dados = request.get_json()
    return redefinir_senha(dados["email"], dados["documento"], dados["nova_senha"])

@auth_bp.route("/me", methods=["GET"])
def rota_me():
    token = request.headers.get("Authorization")
    return obter_usuario_autenticado(token)
