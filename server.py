import socket
import threading
import time

HOST = '0.0.0.0'
PORT = 5000

AUTH_KEY = "SECRET123"

clients = {}
lock = threading.Lock()

def log(message):
    print(message)
    with open("log.txt", "a") as f:
        f.write(message + "\n")

def handle_client(client_socket, addr):

    try:
        # Authentication
        client_socket.send(f"AUTH {AUTH_KEY}".encode())
        response = client_socket.recv(1024).decode()

        if response != "AUTH_SUCCESS":
            log(f"{addr} failed authentication")
            client_socket.close()
            return

        log(f"{addr} authenticated successfully")

        with lock:
            clients[str(addr)] = client_socket

        while True:
            data = client_socket.recv(1024).decode()

            if not data:
                break

            log(f"{addr} → {data}")

    except:
        pass

    finally:
        with lock:
            if str(addr) in clients:
                del clients[str(addr)]

        client_socket.close()
        log(f"{addr} disconnected")


def command_interface():

    while True:

        print("\nConnected devices:")
        for device in clients:
            print(device)

        device = input("\nEnter device address (or 'all'): ")

        command = input("Enter command (TURN_ON_LED / TURN_OFF_LED / GET_TEMP / STATUS): ")

        start = time.time()

        if device == "all":
            for client in clients.values():
                client.send(command.encode())
        else:
            if device in clients:
                clients[device].send(command.encode())
            else:
                print("Device not found")
                continue

        end = time.time()
        latency = end - start

        log(f"Command sent: {command}")
        log(f"Latency: {latency:.4f} seconds")


def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    log("Server started. Waiting for Raspberry Pi devices...")

    threading.Thread(target=command_interface, daemon=True).start()

    while True:
        client_socket, addr = server.accept()

        log(f"Device connected: {addr}")

        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr)
        )

        client_thread.start()


if __name__ == "__main__":
    start_server()