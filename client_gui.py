import socket
import ssl
import serial
import json
import time
import threading
import tkinter as tk
from tkinter import scrolledtext

SERVER_IP = "192.168.56.1"
PORT = 5000

SERIAL_PORT = "COM4"
BAUD_RATE = 9600

DEVICE_ID = "arduino1"
PASSWORD = "1234"

# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("🔌 Arduino Client Dashboard")
root.geometry("600x500")
root.config(bg="#1e1e2f")

title = tk.Label(root, text="Arduino Client", font=("Arial", 18, "bold"), fg="white", bg="#1e1e2f")
title.pack(pady=10)

log_area = scrolledtext.ScrolledText(root, width=70, height=20, bg="#2b2b3c", fg="white")
log_area.pack(pady=10)

def log(message):
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END)

# ---------------- CLIENT LOGIC ----------------
def start_client():
    try:
        log("🔌 Connecting to Arduino...")
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        log("✅ Arduino Connected!")

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_client = context.wrap_socket(client_socket, server_hostname=SERVER_IP)

        log("🌐 Connecting to Server...")
        secure_client.connect((SERVER_IP, PORT))
        log("🔐 Secure Connection Established!")

        auth = {"device_id": DEVICE_ID, "password": PASSWORD}
        secure_client.send(json.dumps(auth).encode())

        response = secure_client.recv(1024).decode()

        if response == "AUTH_SUCCESS":
            log("✅ Authentication Successful!\n")
        else:
            log("❌ Authentication Failed!")
            return

        while True:
            data = secure_client.recv(1024).decode()
            if not data:
                break

            message = json.loads(data)

            if message["type"] == "command" and message["command"] == "GET_DATA":
                log("🔄 Reading data from Sensor...")

                arduino.reset_input_buffer()
                arduino.write(b'READ\n')
                time.sleep(2)

                sensor_data = arduino.readline().decode(errors="ignore").strip()
                log(f"📥 Raw Data: {sensor_data}")

                if sensor_data and "," in sensor_data:
                    temp, hum = sensor_data.split(",")

                    reply = {
                        "type": "data",
                        "temperature": float(temp),
                        "humidity": float(hum)
                    }

                    secure_client.send(json.dumps(reply).encode())
                    log("✅ Data Sent to server successfully!\n")

    except Exception as e:
        log(f"❌ Error: {e}")

threading.Thread(target=start_client, daemon=True).start()

root.mainloop()