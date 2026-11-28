### Brief to run enumeration. ( gives data about the devices that connects or dis connect)

```bash
sudo dnf install python3 python3-pip python3-pyudev

### the consumer is the part that accept data from the publisher it will print in terminal so you ### can edit to direct data to your code it depends on socket.

sudo cd enumeration
sudo python3 enumeration/event_consumer.py


### then run the publisher this the part that produce data 
sudo python3 main.py 

# or you can
# (&) makes it run in background so you can use terminal but becareful here
sudo python3 main.py &
##  here if you want to terminate main.py
sudo pkill -f "python3 main.py"



### here is the shape of data 

## 5. Event Format

The Enumerator generates structured JSON events.

Example:

```json
{
    "event": "device_connected",
    "timestamp": "2026-11-28T12:00:18.372803+00:00",
    "device": {
        "vendor_id": "2341",
        "product_id": "8037",
        "manufacturer": "Arduino",
        "product": "Arduino Leonardo",
        "interfaces": [
            {
                "class": "03",
                "subclass": "01",
                "protocol": "01",
                "type": "HID"
            }
        ]
    },
    "classification": {
        "device_types": ["HID"],
        "is_hid": true,
        "is_composite": false
    }
}
```




# USB Enumeration Service

## 1. Overview

The USB Enumeration Service is a component of a USB security monitoring system. Its primary responsibility is to detect USB device connections and disconnections, collect device information, classify device capabilities, and publish events to other security components.

The Enumerator does not independently determine whether a device is malicious. It collects and provides information to the Detection Engine for further analysis and correlation.

## 2. Responsibilities

The Enumeration Service performs the following tasks:

- Detect USB device connections and disconnections.
- Collect USB device metadata.
- Identify USB interfaces and their classes.
- Identify device capabilities, such as HID and Mass Storage.
- Detect composite USB devices.
- Maintain device connection history.
- Generate structured JSON events.
- Persist events for auditing and recovery.
- Communicate with the Detection Engine through Unix Domain Sockets.

## 3. Architecture

```text
Enumeration/
│
├── main.py
│
├── enumerator/
│   ├── __init__.py
│   ├── device_detector.py
│   ├── usb_enumerator.py
│   ├── device_classifier.py
│   ├── device_monitor.py
│   ├── device_history.py
│   └── event_publisher.py
│
├── data/
│   └── device_history.json
│
├── output/
│   └── device_events.jsonl
│
└── requirements.txt
```

### Module descriptions

| Module | Responsibility |
|---|---|
| `main.py` | Application entry point |
| `device_detector.py` | Device detection functionality, if used separately |
| `usb_enumerator.py` | Collects USB device metadata |
| `device_classifier.py` | Identifies device types and capabilities |
| `device_monitor.py` | Monitors USB connection and disconnection events |
| `device_history.py` | Maintains device connection history |
| `event_publisher.py` | Saves and publishes generated events |

## 4. Collected Information

The Enumerator collects information such as:

- Vendor ID (VID)
- Product ID (PID)
- Manufacturer
- Product name
- Serial number
- USB version
- Device class, subclass, and protocol
- Bus number and device number
- Interface classes, subclasses, and protocols

### Supported interface classifications

| USB Class | Description |
|---|---|
| `03` | HID |
| `08` | Mass Storage |
| `02` | Communications |
| `0A` | CDC Data |
| Other | Other USB interfaces |

Device classification describes capabilities and does not determine maliciousness.

## 5. Event Format

The Enumerator generates structured JSON events.

Example:

```json
{
    "event": "device_connected",
    "timestamp": "2026-11-28T12:00:18.372803+00:00",
    "device": {
        "vendor_id": "2341",
        "product_id": "8037",
        "manufacturer": "Arduino",
        "product": "Arduino Leonardo",
        "interfaces": [
            {
                "class": "03",
                "subclass": "01",
                "protocol": "01",
                "type": "HID"
            }
        ]
    },
    "classification": {
        "device_types": ["HID"],
        "is_hid": true,
        "is_composite": false
    }
}
```

Events are stored in JSONL format, with one complete JSON event per line.

## 6. Inter-Service Communication

The Enumeration Service communicates with the Detection Engine using Unix Domain Sockets.

Socket path:

```text
/run/usb-security/enumerator.sock
```

The communication architecture separates event generation from event analysis.

The Enumerator:

1. Generates an event.
2. Saves the event locally.
3. Publishes the event to the Detection Engine.
4. Retains undelivered events for recovery.

The Detection Engine consumes events and uses them alongside behavioral observations to make security decisions.

A persistent delivery queue and acknowledgment mechanism are required to guarantee recovery of events when the Detection Engine is unavailable.

## 7. Dependencies

The project uses Python 3 and the following external dependency:

```text
pyudev>=0.24.0
```

Other modules, including `json`, `socket`, `pathlib`, and `datetime`, are part of Python's standard library.

## 8. Installation

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-pip python3-pyudev
```

### RHEL / Rocky Linux / AlmaLinux

```bash
sudo dnf install python3 python3-pip python3-pyudev
```

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## 9. Execution

Run the Enumeration Service from its project directory:

```bash
sudo python3 main.py
```

The service should run in the background using systemd in a production environment.

## 10. Operating System Compatibility

The Enumeration Service targets Linux distributions using the Linux USB sysfs interface and udev.

Supported distribution families include:

- Debian
- Ubuntu
- RHEL
- Rocky Linux
