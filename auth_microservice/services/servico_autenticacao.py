from datetime import datetime, timedelta
from auth_microservice.db import obter_conexao_banco
from cache import obter_conexao_redis
from auth_microservice.utils.criptografia_token import gerar_token_simetric, decodificar_token_simetric
import uuid


redis_client = obter_conexao_redis()

def criar_usuario(nome, email, documento, senha):
    conn = obter_conexao_banco()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=%s OR document=%s", (email, documento))
    if cur.fetchone():
        conn.close()
        return {"erro": "Usuário já existe"}, 400
    cur.execute("INSERT INTO users (name, email, document, password) VALUES (%s, %s, %s, %s)", (nome, email, documento, senha))
    conn.commit()
    conn.close()
    token = gerar_token_simetric(email, documento)
    return {"token": token}, 201

def autenticar_usuario(email, senha):
    conn = obter_conexao_banco()
    cur = conn.cursor()
    chave_tentativas = f"login:{email}"
    tentativas = redis_client.get(chave_tentativas)
    if tentativas and int(tentativas) >= 3:
        conn.close()
        return {"erro": "Usuário temporariamente bloqueado (10 minutos)."}, 429
    cur.execute("SELECT document, password FROM users WHERE email=%s", (email,))
    usuario = cur.fetchone()
    conn.close()
    if not usuario or usuario[1] != senha:
        redis_client.incr(chave_tentativas)
        redis_client.expire(chave_tentativas, 600)
        return {"erro": "Credenciais inválidas."}, 401
    redis_client.delete(chave_tentativas)
    token = gerar_token_simetric(email, usuario[0])
    return {"token": token}, 200

def redefinir_senha(email, documento, nova_senha):
    conn = obter_conexao_banco()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=%s AND document=%s", (email, documento))
    usuario = cur.fetchone()
    if not usuario:
        conn.close()
        return {"erro": "Usuário não encontrado"}, 404
    token_temporario = str(uuid.uuid4())
    redis_client.setex(f"reset:{token_temporario}", 600, usuario[0])
    conn.close()
    return {"mensagem": "Token de redefinição criado", "token_reset": token_temporario}, 200

def confirmar_redefinicao(token_reset, nova_senha):
    usuario_id = redis_client.get(f"reset:{token_reset}")
    if not usuario_id:
        return {"erro": "Token inválido ou expirado"}, 400
    conn = obter_conexao_banco()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password=%s WHERE id=%s", (nova_senha, usuario_id))
    conn.commit()
    conn.close()
    redis_client.delete(f"reset:{token_reset}")
    return {"mensagem": "Senha atualizada com sucesso"}, 200

def obter_usuario_autenticado(token):
    email, documento = decodificar_token_simetric(token)
    if not email:
        return {"erro": "Token inválido"}, 400
    conn = obter_conexao_banco()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, document FROM users WHERE email=%s AND document=%s", (email, documento))
    usuario = cur.fetchone()
    conn.close()
    if not usuario:
        return {"erro": "Usuário não encontrado"}, 404
    return {
        "id": usuario[0],
        "nome": usuario[1],
        "email": usuario[2],
        "documento": usuario[3]
    }, 200
