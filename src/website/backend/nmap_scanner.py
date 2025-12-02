import json
import time
import nmap
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
MQTT_TOPIC = "watchtower/telemetry"
CLIENT_ID = "WatchTower_Scanner"

# Initialize Nmap
nm = nmap.PortScanner()

# Suspicious / rogue MAC or IP flags
KNOWN_SAFE_MACS = {
    "00:11:22:33:44:55",
    "00:11:22:33:44:66",
    "00:11:22:33:44:77"
}

def scan_device(ip_address):
    """Runs Nmap ping scan to see if device is real."""
    try:
        nm.scan(hosts=ip_address, arguments='-sn')
        return ip_address in nm.all_hosts()
    except:
        return False

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected. Listening for traffic...")
        client.subscribe(MQTT_TOPIC)
    else:
        print("Connection failed:", rc)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    device_id = payload["device_id"]
    ip = payload["source_ip"]
    mac = payload.get("mac")
    load = payload["current_load"]
    status = payload["status"]
    timestamp = payload["timestamp"]

    print("\n========================================")
    print(f"📨 {timestamp} | {device_id}")
    print(f"IP: {ip}   MAC: {mac}   Load: {load}   Status: {status}")

    # 1. Suspicious MAC
    if mac not in KNOWN_SAFE_MACS:
        print("SUSPICIOUS MAC DETECTED!")
    
    # 2. Suspicious IP range
    if ip.startswith("10.") or ip.startswith("172.20") or ip.endswith(".250"):
        print("SUSPICIOUS IP RANGE DETECTED!")

    # 3. Compromised alert
    if status == "COMPROMISED":
        print("COMPROMISED ACTIVITY DETECTED!")

    print("========================================\n")

# MQTT Setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

print("Starting WatchTower Scanner...")
client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
client.loop_forever()
