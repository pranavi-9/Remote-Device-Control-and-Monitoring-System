import socket
import ssl
import serial
import json
import time

SERVER_IP = "192.168.56.1"
PORT = 5000

SERIAL_PORT = "COM4"
BAUD_RATE = 9600

DEVICE_ID = "arduino1"
PASSWORD = "1234"

# 🔌 Connect to Arduino
print("🔌 Connecting to Arduino...")
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
time.sleep(2)
print("✅ Arduino Connected!\n")

# 🔐 SSL Setup
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_client = context.wrap_socket(client_socket, server_hostname=SERVER_IP)

print("🌐 Connecting to Secure Server...")
secure_client.connect((SERVER_IP, PORT))
print("🔐 Secure Connection Established!\n")

# 🔑 Send Authentication Data
auth = {
    "device_id": DEVICE_ID,
    "password": PASSWORD
}

secure_client.send(json.dumps(auth).encode())

response = secure_client.recv(1024).decode()

if response == "AUTH_SUCCESS":
    print("✅ Authentication Successful!\n")
else:
    print("❌ Authentication Failed!")
    secure_client.close()
    exit()

print("🚀 Waiting for commands...\n")

# 🔁 Continuous Listening
while True:
    try:
        data = secure_client.recv(1024).decode()
        if not data:
            break

        message = json.loads(data)

        if message["type"] == "command" and message["command"] == "GET_DATA":

            print("🔄 Reading data from Sensor...")
            arduino.reset_input_buffer()
            arduino.write(b'READ\n')
            time.sleep(2)

            sensor_data = arduino.readline().decode(errors="ignore").strip()

            print("📥 Raw data :", sensor_data)

            if sensor_data and "," in sensor_data:
                temp, hum = sensor_data.split(",")

                reply = {
                    "type": "data",
                    "temperature": float(temp),
                    "humidity": float(hum)
                }

                secure_client.send(json.dumps(reply).encode())
                print("✅ Data Sent to server successfully!\n")

    except Exception as e:
        print("❌ Error:", e)
        break

secure_client.close()