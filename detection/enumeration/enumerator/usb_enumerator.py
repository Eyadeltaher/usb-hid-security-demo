
from pathlib import Path


SYS_USB = Path("/sys/bus/usb/devices")


def read_file(path):
    """Read a sysfs attribute safely."""
    try:
        return path.read_text().strip()
    except (OSError, PermissionError):
        return None


def get_interfaces(device_path):
    """Collect all interfaces belonging to a USB device."""

    interfaces = []

    for interface_path in device_path.parent.glob(
        device_path.name + ":*"
    ):
        interface = {
            "name": interface_path.name,
            "class": read_file(interface_path / "bInterfaceClass"),
            "subclass": read_file(interface_path / "bInterfaceSubClass"),
            "protocol": read_file(interface_path / "bInterfaceProtocol")
        }

        class_id = interface["class"]

        if class_id == "03":
            interface["type"] = "HID"
        elif class_id == "08":
            interface["type"] = "Mass Storage"
        elif class_id == "02":
            interface["type"] = "Communications"
        elif class_id == "0A":
            interface["type"] = "CDC Data"
        else:
            interface["type"] = "Other"

        interfaces.append(interface)

    return interfaces


def enumerate_usb(device):

    device_path = Path(device.sys_path)

    return {
        "device_path": device.sys_path,
        "vendor_id": read_file(device_path / "idVendor"),
        "product_id": read_file(device_path / "idProduct"),
        "manufacturer": read_file(device_path / "manufacturer"),
        "product": read_file(device_path / "product"),
        "serial_number": read_file(device_path / "serial"),
        "usb_version": read_file(device_path / "version"),
        "device_class": read_file(device_path / "bDeviceClass"),
        "device_subclass": read_file(device_path / "bDeviceSubClass"),
        "device_protocol": read_file(device_path / "bDeviceProtocol"),
        "bus_number": read_file(device_path / "busnum"),
        "device_number": read_file(device_path / "devnum"),
        "interfaces": get_interfaces(device_path)
    }
