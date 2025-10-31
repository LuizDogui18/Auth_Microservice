import redis
import os
from dotenv import load_dotenv

load_dotenv()

def obter_conexao_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )
