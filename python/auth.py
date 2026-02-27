import sqlite3, os, bcrypt, jwt
from dotenv import load_dotenv
load_dotenv()
DB_PATH = os.environ.get("USERS_DB_PATH", "./db/users.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")

def check_creds(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT password FROM Admin WHERE username = ?", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return False

    stored_password = row[0]
    return bcrypt.checkpw(password.encode('utf-8'), stored_password)

def generate_token(username, secret_key=SECRET_KEY):
    payload = {"sub": username}
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def verify_token(token, secret_key=SECRET_KEY):
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload["sub"]
    except:
        return None