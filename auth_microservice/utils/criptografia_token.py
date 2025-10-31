from cryptography.fernet import Fernet
import os

chave = os.getenv("TOKEN_SECRET_KEY")

def gerar_token_simetric(dados):
    f = Fernet(chave)
    return f.encrypt(dados.encode()).decode()

def decodificar_token_simetric(token):
    try:
        f = Fernet(chave)
        return f.decrypt(token.encode()).decode()
    except Exception:
        return None
