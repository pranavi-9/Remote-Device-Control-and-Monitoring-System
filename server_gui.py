import socket
import ssl
import json
import time
import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "0.0.0.0"
PORT = 5000

secure_conn = None
server_socket = None
monitoring = False
server_running = False


# ---------------- GUI ----------------
root = tk.Tk()
root.title("🖥 Secure Server Dashboard")
root.geometry("650x550")
root.config(bg="#1e1e2f")

title = tk.Label(root, text="Secure IoT Server", font=("Arial", 18, "bold"),
                 fg="white", bg="#1e1e2f")
title.pack(pady=10)

log_area = scrolledtext.ScrolledText(root, width=75, height=22,
                                     bg="#2b2b3c", fg="white")
log_area.pack(pady=10)

def log(msg):
    log_area.insert(tk.END, msg + "\n")
    log_area.see(tk.END)


# ---------------- START SERVER ----------------
def start_server():
    global secure_conn, server_socket, server_running

    try:
        server_running = True
        log("🔐 Starting SSL Server...")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        log("📡 Waiting for client connection...")

        conn, addr = server_socket.accept()

        if not server_running:
            return

        secure_conn = context.wrap_socket(conn, server_side=True)
        log(f"✅ Client Connected: {addr}")

        # 🔑 Authentication
        auth_data = secure_conn.recv(1024).decode()
        auth = json.loads(auth_data)

        if auth["device_id"] == "arduino1" and auth["password"] == "1234":
            secure_conn.send("AUTH_SUCCESS".encode())
            log("✅ Authentication Successful!\n")
        else:
            secure_conn.send("AUTH_FAILED".encode())
            log("❌ Authentication Failed!")
            secure_conn.close()

    except Exception as e:
        if server_running:
            log(f"❌ Server Error: {e}")


# ---------------- START MONITORING ----------------
def start_monitoring():
    global monitoring

    if not secure_conn:
        log("⚠ No client connected!")
        return

    monitoring = True
    log("🚀 Monitoring Started (Every 2 Seconds)\n")

    while monitoring:
        try:
            command = {"type": "command", "command": "GET_DATA"}

            start_time = time.time()
            secure_conn.send(json.dumps(command).encode())

            response = secure_conn.recv(1024).decode()
            end_time = time.time()

            latency = (end_time - start_time) * 1000
            data = json.loads(response)

            current_time = datetime.datetime.now().strftime("%I:%M:%S %p")

            log("=" * 55)
            log(f"🌡 Temperature : {data['temperature']} °C")
            log(f"💧 Humidity    : {data['humidity']} %")
            log(f"🕒 Time        : {current_time}")
            log(f"🌐 Latency     : {latency:.2f} ms")
            log("=" * 55 + "\n")

            time.sleep(2)

        except Exception:
            break


# ---------------- EXIT BUTTON (Like Ctrl+C) ----------------
def exit_server():
    global monitoring, server_running

    log("🛑 Stopping Server...")

    monitoring = False
    server_running = False

    try:
        if secure_conn:
            secure_conn.close()
            log("🔌 Client connection closed.")

        if server_socket:
            server_socket.close()
            log("📡 Server socket closed.")

    except:
        pass

    log("✅ Server stopped successfully!\n")


# ---------------- BUTTONS ----------------
btn_frame = tk.Frame(root, bg="#1e1e2f")
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="Start Server",
                      command=lambda: threading.Thread(target=start_server, daemon=True).start(),
                      bg="#4CAF50", fg="white", width=15)
start_btn.grid(row=0, column=0, padx=10)

monitor_btn = tk.Button(btn_frame, text="Start Monitoring",
                        command=lambda: threading.Thread(target=start_monitoring, daemon=True).start(),
                        bg="#2196F3", fg="white", width=15)
monitor_btn.grid(row=0, column=1, padx=10)

exit_btn = tk.Button(btn_frame, text="Stop Server",
                     command=exit_server,
                     bg="#f44336", fg="white", width=15)
exit_btn.grid(row=0, column=2, padx=10)

root.mainloop()