import socket
import ssl
import json
import time
import datetime

HOST = "0.0.0.0"
PORT = 5000

print("🔐 Starting Secure SSL Server...\n")

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("📡 Waiting for client...")
conn, addr = server_socket.accept()
secure_conn = context.wrap_socket(conn, server_side=True)

print(f"✅ Client Connected: {addr}")

# 🔑 Receive Authentication Data
auth_data = secure_conn.recv(1024).decode()
auth = json.loads(auth_data)

expected_device = input("🔐 Enter Device ID for Authentication: ")

if auth["device_id"] == expected_device and auth["password"] == "1234":
    secure_conn.send("AUTH_SUCCESS".encode())
    print("✅ Authentication Successful!\n")
else:
    secure_conn.send("AUTH_FAILED".encode())
    print("❌ Authentication Failed!")
    secure_conn.close()
    exit()

# 🔥 ASK FOR COMMAND AFTER AUTH
command_input = input("📌 Enter Command (GET_DATA): ").upper()

if command_input != "GET_DATA":
    print("❌ Invalid Command!")
    secure_conn.close()
    exit()

print("🚀 Continuous Data Fetching Started...\n")

# 🔁 CONTINUOUS LOOP
while True:
    try:
        command = {"type": "command", "command": "GET_DATA"}

        start_time = time.time()
        secure_conn.send(json.dumps(command).encode())

        response = secure_conn.recv(1024).decode()
        end_time = time.time()

        latency = (end_time - start_time) * 1000
        data = json.loads(response)

        if data["type"] == "data":
            current_time = datetime.datetime.now().strftime("%I:%M:%S %p")

            print("\n" + "="*60)
            print(f"🌡 Temperature : {data['temperature']} °C")
            print(f"💧 Humidity    : {data['humidity']} %")
            print(f"🕒 Time        : {current_time}")
            print(f"🌐 Latency     : {latency:.2f} ms")
            print("="*60)

        time.sleep(2)

    except Exception as e:
        print("❌ Error:", e)
        break

secure_conn.close()
server_socket.close()