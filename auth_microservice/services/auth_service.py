from datetime import datetime, timedelta
from db import get_connection
from utils.token_utils import generate_token, decode_token


def signup(name, email, document, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=%s OR document=%s", (email, document))
    if cur.fetchone():
        conn.close()
        return {"error": "Usuário já existe"}, 400

    cur.execute(
        "INSERT INTO users (name, email, document, password) VALUES (%s, %s, %s, %s) RETURNING id",
        (name, email, document, password)
    )
    conn.commit()

    token = generate_token(email, document)
    conn.close()
    return {"token": token}, 201

def login(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT attempts, last_attempt FROM login_attempts WHERE email=%s", (email,))
    attempt_data = cur.fetchone()

    if attempt_data:
        attempts, last_attempt = attempt_data
        now = datetime.now()
        elapsed = now - last_attempt

        if attempts >= 3 and elapsed < timedelta(minutes=10):
            conn.close()
            return {"error": "Usuário bloqueado por 10 minutos devido a múltiplas tentativas."}, 429

        elif elapsed >= timedelta(minutes=10):
            cur.execute("UPDATE login_attempts SET attempts=0 WHERE email=%s", (email,))
            conn.commit()

    # --- Valida credenciais ---
    cur.execute("SELECT document, password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user or user[1] != password:
        if attempt_data:
            cur.execute(
                "UPDATE login_attempts SET attempts = attempts + 1, last_attempt = NOW() WHERE email=%s",
                (email,)
            )
        else:
            cur.execute(
                "INSERT INTO login_attempts (email, attempts, last_attempt) VALUES (%s, 1, NOW())",
                (email,)
            )
        conn.commit()
        conn.close()
        return {"error": "Credenciais inválidas."}, 401

    cur.execute("DELETE FROM login_attempts WHERE email=%s", (email,))
    conn.commit()

    token = generate_token(email, user[0])
    conn.close()
    return {"token": token}, 200


def recover_password(email, document, new_password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=%s AND document=%s", (email, document))
    user = cur.fetchone()

    if not user:
        conn.close()
        return {"error": "Usuário não encontrado"}, 404

    cur.execute("UPDATE users SET password=%s WHERE id=%s", (new_password, user[0]))
    conn.commit()
    conn.close()

    token = generate_token(email, document)
    return {"token": token}, 200


def get_me(token):
    email, document = decode_token(token)
    if not email:
        return {"error": "Token inválido"}, 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, document FROM users WHERE email=%s AND document=%s", (email, document))
    user = cur.fetchone()
    conn.close()

    if not user:
        return {"error": "Usuário não encontrado"}, 404

    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "document": user[3]
    }, 200
