import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    print("DB_USER:", os.getenv("DB_USER"))
    print("DB_NAME:", os.getenv("DB_NAME"))
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    conn.set_client_encoding('UTF8')
    return conn
