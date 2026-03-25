import socket
import serial
import json
import time

# 🔑 CHANGE IF USING 2 SYSTEMS
SERVER_IP = "10.30.201.110"
PORT = 5000

# 🔑 CHANGE THIS (CHECK DEVICE MANAGER)
SERIAL_PORT = "COM4"
BAUD_RATE = 9600

DEVICE_ID = "arduino1"
PASSWORD = "1234"

# Connect to Arduino
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
time.sleep(2)

# Connect to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

# Authentication
auth = {
    "device_id": DEVICE_ID,
    "password": PASSWORD
}

client.send(json.dumps(auth).encode())
print(client.recv(1024).decode())

while True:
    try:
        data = client.recv(1024).decode()
        if not data:
            break

        msg = json.loads(data)

        if msg["type"] == "command":
            if msg["command"] == "GET_DATA":

                # 🔥 Clear old data
                arduino.reset_input_buffer()

                # Send command
                arduino.write(b'READ\n')

                # Wait for sensor
                time.sleep(2)

                start = time.time()
                response = arduino.readline().decode().strip()
                end = time.time()

                print("RAW FROM ARDUINO:", response)

                if response and "," in response:
                    try:
                        temp, hum = response.split(",")

                        reply = {
                            "type": "data",
                            "temperature": float(temp),
                            "humidity": float(hum),
                            "latency": (end - start) * 1000
                        }
                    except:
                        reply = {
                            "type": "error",
                            "message": f"Parse error: {response}"
                        }
                else:
                    reply = {
                        "type": "error",
                        "message": f"Invalid data: {response}"
                    }

                client.send(json.dumps(reply).encode())

    except Exception as e:
        print("Error:", e)
        break

client.close()
