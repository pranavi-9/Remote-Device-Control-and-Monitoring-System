import socket
import time

HOST = '0.0.0.0'   # Accept connections from any system
PORT = 5000
PASSWORD = "admin123"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("Server started. Waiting for client...")

conn, addr = server_socket.accept()
print(f"Connected to {addr}")

authenticated = False

while True:
    command = input("Enter command: ")
    start_time = time.time()

    conn.send(command.encode())

    if command.startswith("AUTH"):
        response = conn.recv(1024).decode()
        print("Client:", response)
        if "SUCCESS" in response:
            authenticated = True

    elif authenticated:
        response = conn.recv(1024).decode()
        end_time = time.time()
        print("Client:", response)
        print(f"Latency: {end_time - start_time:.4f} seconds")

        if command == "EXIT":
            break
    else:
        print("Authenticate first!")

conn.close()
server_socket.close()
