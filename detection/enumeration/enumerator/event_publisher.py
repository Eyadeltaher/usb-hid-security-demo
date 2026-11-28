import json
import socket
from pathlib import Path



SOCKET_PATH = "/run/usb-security/enumerator.sock"

OUTPUT_FILE = (
    Path(__file__).resolve().parent.parent
    / "output"
    / "device_events.jsonl"
)


def publish_event(event):

    # 1. Persist the event
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")
        file.flush()
    
    print(f"[+] Event saved: {OUTPUT_FILE}")

    # 2. Send event to Detection Engine
    try:
        with socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM
        ) as client:

            client.connect(SOCKET_PATH)

            message = json.dumps(event) + "\n"

            client.sendall(message.encode("utf-8"))

    except (ConnectionRefusedError, FileNotFoundError):
        print("[!] Detection Engine is unavailable")