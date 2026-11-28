
import socket
import json
import os
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

    # Check whether another Detection Engine is running.
    if os.path.exists(SOCKET_PATH):
        test_socket = socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM
        )

        try:
            test_socket.connect(SOCKET_PATH)
            raise RuntimeError(
                "Another Detection Engine is already running"
            )

        except ConnectionRefusedError:
            # Stale socket: no process is listening.
            os.remove(SOCKET_PATH)

        finally:
            test_socket.close()

    try:
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

    finally:
        server.close()

        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)


def process_event(event):


    #### here the part that prints data in terminal 

    print("[+] Received event:")
    print(json.dumps(event, indent=4, ensure_ascii=False))


    ### Send the event to the Detection Engine's processing logic or behavioral or however wants data event
    
    #detection_engine.process_event(event)


if __name__ == "__main__":
    try:
        start_consumer()

    except KeyboardInterrupt:
        print("\n[+] Detection Engine stopped")
