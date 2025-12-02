import paho.mqtt.client as mqtt
import json
import nmap
import time

BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
MQTT_TOPIC = "watchtower/telemetry"
CLIENT_ID = "WatchTower_Scanner"

nm = nmap.PortScanner()

baseline = {}  # NEW — baseline storage
last_timestamp = {}  # NEW — track message intervals

def scan_device(ip_address):
    nm.scan(hosts=ip_address, arguments='-sn')
    return ip_address in nm.all_hosts()

def learn_baseline(device_id, load, ip, now):
    """Collects baseline for 20 messages."""
    if device_id not in baseline:
        baseline[device_id] = {
            "loads": [],
            "timestamps": [],
            "baseline_ip": ip,
            "learned": False
        }

    baseline[device_id]["loads"].append(load)
    baseline[device_id]["timestamps"].append(now)

    # After 20 samples – lock baseline
    if len(baseline[device_id]["loads"]) == 20 and not baseline[device_id]["learned"]:
        loads = baseline[device_id]["loads"]
        ts = baseline[device_id]["timestamps"]

        baseline[device_id]["min_load"] = min(loads)
        baseline[device_id]["max_load"] = max(loads)

        intervals = [ts[i] - ts[i-1] for i in range(1, len(ts))]
        baseline[device_id]["avg_interval"] = sum(intervals) / len(intervals)

        baseline[device_id]["learned"] = True
        print(f"\n📘 Baseline learned for {device_id}:\n"
              f" - Load range: {baseline[device_id]['min_load']} to {baseline[device_id]['max_load']}\n"
              f" - Avg interval: {baseline[device_id]['avg_interval']:.2f}s\n"
              f" - IP: {baseline[device_id]['baseline_ip']}\n")

def detect_anomaly(device_id, load, ip, now):
    b = baseline[device_id]
    compromised = False

    # Check load anomaly
    if load > b["max_load"] * 1.5:
        print("🚨 HIGH LOAD ANOMALY DETECTED!")
        compromised = True

    # Check IP anomaly
    if ip != b["baseline_ip"]:
        print(f"🚨 NEW IP DETECTED — Possible spoofing! {ip}")
        compromised = True

    # Check frequency anomaly
    if device_id in last_timestamp:
        interval = now - last_timestamp[device_id]
        if interval < b["avg_interval"] * 0.5:
            print("🚨 MESSAGE RATE ANOMALY — Device sending too fast!")
            compromised = True

    last_timestamp[device_id] = now

    if compromised:
        print(f"🔥 DEVICE {device_id} MARKED AS COMPROMISED\n")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected. Listening for messages...")
        client.subscribe(MQTT_TOPIC)
    else:
        print("Failed to connect. Error:", rc)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    device_id = payload["device_id"]
    ip = payload["source_ip"]
    load = payload["current_load"]
    now = time.time()

    print(f"\n📨 Received from {device_id} | load={load} | ip={ip}")

    if device_id not in baseline or not baseline[device_id].get("learned"):
        learn_baseline(device_id, load, ip, now)
        return

    detect_anomaly(device_id, load, ip, now)

    # Nmap validation
    if not scan_device(ip):
        print("👻 Nmap: No real device detected at this IP.")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

print("Starting WatchTower Scanner...\n")

client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
client.loop_forever()