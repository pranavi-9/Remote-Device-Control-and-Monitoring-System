import json
from config import SECRET_TOKEN

def authenticate(conn):
    try:
        conn.settimeout(5)  # wait max 5 sec for token
        data = conn.recv(1024).decode()
        msg = json.loads(data)

        if msg.get("token") == SECRET_TOKEN:
            conn.send(json.dumps({"status": "AUTH_OK"}).encode())
            return True
        else:
            conn.send(json.dumps({"status": "AUTH_FAIL"}).encode())
            return False
    except Exception:
        return False