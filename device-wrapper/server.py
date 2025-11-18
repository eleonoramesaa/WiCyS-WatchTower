# device-wrapper/server.py

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import paho.mqtt.client as mqtt

# Settings
MQTT_BROKER = "mosquitto"      # Use "mosquitto" when running in the same Docker network
MQTT_PORT = 1883
MQTT_TOPIC = "test/devices"

BASE_PORT = 5001               # First port to use
MAX_DEVICES = 7                # Maximum number of devices to expose

# Global in-memory mapping: device_id -> port
device_ports = {}              # e.g. {"thermo_01": 5001, "cam_01": 5002}


class DeviceHandler(BaseHTTPRequestHandler):
    """
    Simple HTTP handler that represents a fake IoT device.
    Each HTTP server instance gets a .device_id attribute from the wrapper.
    """

    def do_GET(self):
        # Always respond with JSON showing which device this is
        response = {
            "device_id": self.server.device_id,
            "status": "online",
            "info": "Simulated IoT device exposed by WatchTower wrapper"
        }
        body = json.dumps(response).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Silence default HTTP logging to keep logs cleaner
        return


def start_device_server(device_id: str, port: int):
    """
    Start an HTTP server in a background thread for a single device.
    """
    server = HTTPServer(("", port), DeviceHandler)
    server.device_id = device_id  # attach device id to the server

    def serve():
        print(f"[HTTP] Device {device_id} listening on port {port}")
        server.serve_forever()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()


def assign_port_for_device(device_id: str) -> int | None:
    """
    Decide which port to use for this device.
    If we've already seen it, return the existing port.
    If it's new and we still have capacity, assign the next port.
    If we are at capacity, return None.
    """
    if device_id in device_ports:
        return device_ports[device_id]

    if len(device_ports) >= MAX_DEVICES:
        print(f"[WRAPPER] Max devices ({MAX_DEVICES}) reached, ignoring new device: {device_id}")
        return None

    # Assign next available port
    port = BASE_PORT + len(device_ports)
    device_ports[device_id] = port
    print(f"[WRAPPER] Assigned port {port} to device {device_id}")
    return port


# MQTT callbacks

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("[MQTT] Connected with result code:", reason_code)
    client.subscribe(MQTT_TOPIC)
    print(f"[MQTT] Subscribed to topic: {MQTT_TOPIC}")


def on_message(client, userdata, msg):
    print(f"[MQTT] Message on {msg.topic}: {msg.payload}")

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print("[WRAPPER] Could not parse JSON payload, skipping")
        return

    device_id = payload.get("device_id")
    if not device_id:
        print("[WRAPPER] No 'device_id' field in message, skipping")
        return

    # Get or assign a port for this device
    port = assign_port_for_device(device_id)
    if port is None:
        # Capacity reached or some other issue
        return

    # If this is a new device, we must start an HTTP server for it
    if payload.get("device_id") not in [srv_id for srv_id in device_ports.keys()]:
        # (Note: the check above is redundant because assign_port_for_device
        # has already inserted into device_ports, but we keep the logic simple.)
        pass

    # Start HTTP server only once per device
    # If the device just got assigned, start the server
    # We can check based on length: if the current length equals (port - BASE_PORT + 1),
    # it means we just added it.
    # For clarity, we add a separate "servers_started" set.
    global servers_started
    if 'servers_started' not in globals():
        servers_started = set()

    if device_id not in servers_started:
        start_device_server(device_id, port)
        servers_started.add(device_id)


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[WRAPPER] Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    print("[WRAPPER] Device wrapper is running. Waiting for MQTT messages...")
    client.loop_forever()


if __name__ == "__main__":
    main()
