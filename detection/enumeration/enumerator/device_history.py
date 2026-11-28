
import json
from pathlib import Path
from datetime import datetime, timezone


HISTORY_FILE = Path("data/device_history.json")


def load_history():

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not HISTORY_FILE.exists():
        return {}

    try:
        return json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def update_history(device):

    history = load_history()

    key = (
        f"{device.get('vendor_id', 'unknown')}:"
        f"{device.get('product_id', 'unknown')}:"
        f"{device.get('serial_number') or device.get('device_path')}"
    )

    now = datetime.now(timezone.utc).isoformat()

    if key not in history:

        history[key] = {
            "first_seen": now,
            "last_seen": now,
            "connection_count": 1
        }

        previously_seen = False

    else:

        history[key]["last_seen"] = now
        history[key]["connection_count"] += 1

        previously_seen = True

    HISTORY_FILE.write_text(
        json.dumps(history, indent=4)
    )

    return {
        "previously_seen": previously_seen,
        "connection_count": history[key]["connection_count"],
        "first_seen": history[key]["first_seen"]
    }
