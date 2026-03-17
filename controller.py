import socket
import threading
import json
import time
import ast
from config import HOST, PORT, COMMAND_TIMEOUT
from auth import authenticate
from latency_logger import log_latency

connected_devices = {}

def handle_device(conn, addr):
    try:
        if not authenticate(conn):
            print(f"[AUTH FAIL] {addr}")
            conn.close()
            return

        connected_devices[addr] = conn
        print(f"[AUTH OK] Device registered: {addr}")

        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[STATUS from {addr}] {data.decode()}")

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        connected_devices.pop(addr, None)
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(f"[SERVER] New connection from {addr}")
        thread = threading.Thread(target=handle_device, args=(conn, addr))
        thread.daemon = True
        thread.start()

def send_command(addr, command):
    conn = connected_devices.get(addr)
    if not conn:
        print(f"[ERROR] Device {addr} not connected")
        return None

    payload = json.dumps({"cmd": command}).encode()

    t1 = time.time()
    conn.send(payload)

    conn.settimeout(COMMAND_TIMEOUT)
    try:
        ack_data = conn.recv(1024).decode()
        t2 = time.time()

        latency_ms = round((t2 - t1) * 1000, 2)
        print(f"[ACK from {addr}] {ack_data} | Latency: {latency_ms} ms")
        log_latency(addr, command, latency_ms)
        return latency_ms

    except socket.timeout:
        print(f"[TIMEOUT] No ACK from {addr} for command '{command}'")
        return None

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    time.sleep(1)

    while True:
        print("\n--- Connected devices ---")
        if not connected_devices:
            print("  No devices connected yet")
        else:
            for i, addr in enumerate(connected_devices.keys()):
                print(f"  [{i}] {addr}")

        print("\nOptions:")
        print("  1 - Send command to a device")
        print("  2 - Refresh device list")
        print("  3 - Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            if not connected_devices:
                print("[ERROR] No devices connected")
                continue
            addr_input = input("Enter device address exactly as shown (e.g. ('127.0.0.1', 5001)): ").strip()
            try:
                addr = ast.literal_eval(addr_input)
            except Exception:
                print("[ERROR] Invalid address format")
                continue
            print("Commands: GET_STATUS / REBOOT / SET_LED")
            command = input("Enter command: ").strip()
            send_command(addr, command)

        elif choice == "2":
            continue

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("[ERROR] Invalid choice")