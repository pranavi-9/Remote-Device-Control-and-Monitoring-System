import csv, os
from datetime import datetime

LOG_FILE = "latency_log.csv"

def log_latency(addr, command, latency_ms):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "device", "command", "latency_ms"])
        writer.writerow([datetime.now().isoformat(), str(addr), command, latency_ms])