
def classify_device(device):

    interfaces = device.get("interfaces", [])

    interface_types = {
        interface.get("type")
        for interface in interfaces
    }

    device_types = []

    if "HID" in interface_types:
        device_types.append("HID")

    if "Mass Storage" in interface_types:
        device_types.append("Mass Storage")

    if "Communications" in interface_types:
        device_types.append("Communications")

    if "CDC Data" in interface_types:
        device_types.append("Serial/Data")

    if not device_types:
        device_types.append("Unknown")

    return {
        "device_types": device_types,
        "is_hid": "HID" in interface_types,
        "is_storage": "Mass Storage" in interface_types,
        "is_composite": len(interfaces) > 1
    }
