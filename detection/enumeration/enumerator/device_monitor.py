
import pyudev
import json

from datetime import datetime, timezone
from pathlib import Path

from enumerator.usb_enumerator import enumerate_usb
from enumerator.device_classifier import classify_device
from enumerator.device_history import update_history

from enumerator.event_publisher import publish_event


OUTPUT_FILE = Path("output/device_events.json")


def current_time():
    return datetime.now(timezone.utc).isoformat()



class USBMonitor:

    def __init__(self):

        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)

        self.monitor.filter_by(subsystem="usb")

        self.known_devices = {}

    def process_device(self, device, action):

        # Ignore USB interfaces and hubs' internal events.
        if device.device_type != "usb_device":
            return

        device_id = device.sys_path

        if action == "add":

            usb_info = enumerate_usb(device)

            classification = classify_device(usb_info)

            history = update_history(usb_info)

            self.known_devices[device_id] = usb_info

            event = {
                "event": "device_connected",
                "timestamp": current_time(),
                "device": usb_info,
                "classification": classification,
                "history": history
            }

        elif action == "remove":

            usb_info = self.known_devices.pop(device_id, None)

            if usb_info is None:
                usb_info = {
                    "device_path": device_id,
                    "vendor_id": device.properties.get("ID_VENDOR_ID"),
                    "product_id": device.properties.get("ID_MODEL_ID")
                }

            event = {
                "event": "device_disconnected",
                "timestamp": current_time(),
                "device": usb_info
            }

        else:
            return



        ### this is uncommented it if you want messages in the terminal for debug for example
        ## print(json.dumps(event, indent=4))

        publish_event(event)






    def start(self):

        # Subscribe before taking the initial snapshot.
        self.monitor.start()

        print("[+] USB Enumeration Service Started")

        # Enumerate devices that were already connected.
        for device in self.context.list_devices(
            subsystem="usb",
            DEVTYPE="usb_device"
        ):
            self.process_device(device, "add")

        # Continuously monitor new events.
        while True:

            device = self.monitor.poll(timeout=1)

            if device is None:
                continue

            self.process_device(device, device.action)


if __name__ == "__main__":

    monitor = USBMonitor()

    try:
        monitor.start()

    except KeyboardInterrupt:
        print("\n[+] Enumeration Service Stopped")
