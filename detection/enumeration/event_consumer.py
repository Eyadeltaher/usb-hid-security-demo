import socket
import json
from pathlib import Path


SOCKET_PATH = "/run/usb-security/enumerator.sock"


def start_consumer():

    Path(SOCKET_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    server = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM
    )

    server.bind(SOCKET_PATH)
    server.listen(10)

    print("[+] Detection Engine listening")

    while True:

        connection, _ = server.accept()

        with connection:
            buffer = b""

            while True:
                data = connection.recv(4096)

                if not data:
                    break

                buffer += data

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)

                    if not line:
                        continue

                    event = json.loads(line.decode("utf-8"))

                    process_event(event)


def process_event(event):

    print("[+] Received event:")
    print(json.dumps(event, indent=4))


if __name__ == "__main__":
    start_consumer()