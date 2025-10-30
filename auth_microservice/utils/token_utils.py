import base64

def generate_token(email, document):
    token_str = f"{email}:{document}"
    token_bytes = token_str.encode("utf-8")
    return base64.b64encode(token_bytes).decode("utf-8")

def decode_token(token):
    try:
        decoded = base64.b64decode(token).decode("utf-8")
        email, document = decoded.split(":")
        return email, document
    except Exception:
        return None, None
