import time
import json
import random
import paho.mqtt.client as mqtt
from db_utils import insert_telemetry
from db_utils import connect_to_db

# --- CONFIGURATION ---
BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "watchtower/telemetry"

# Legit devices you want to monitor
DEVICES = [
    {"id": "Camera-Lobby", "ip": "192.168.50.10", "mac": "00:21:5A:3F:11:01", "type": "camera"},
    {"id": "Badge-Reader-01", "ip": "192.168.50.11", "mac": "00:1C:42:9F:2D:12", "type": "access-control"},
    {"id": "Smart-Light-07", "ip": "192.168.50.12", "mac": "00:16:3E:44:72:BB", "type": "lighting"},
    {"id": "HVAC-Unit-3", "ip": "192.168.50.13", "mac": "00:25:96:FF:2A:33", "type": "hvac"},
    {"id": "Conference-TV", "ip": "192.168.50.14", "mac": "00:50:C2:88:55:90", "type": "tv"},
    {"id": "Office-Laptop-03", "ip": "192.168.50.15", "mac": "02:42:AC:11:00:02", "type": "laptop"},
    {"id": "Server-Backup", "ip": "192.168.50.16", "mac": "00:1B:44:11:3A:B7", "type": "server"},
    {"id": "IoT-Fridge", "ip": "192.168.50.17", "mac": "00:1A:79:23:44:F0", "type": "appliance"},
]

# Suspicious devices (attackers, rogue devices, unknown hosts)
SUSPICIOUS_DEVICES = [
    {"id": "Rogue-Tablet", "ip": "172.30.5.44", "mac": "DE:AD:00:22:FA:11"},
    {"id": "Unknown-IoT-Box", "ip": "10.55.22.78", "mac": "AA:7C:33:11:BC:77"},
    {"id": "Fake-AP-02", "ip": "192.168.50.200", "mac": "66:44:22:11:FA:64"},
    {"id": "Compromised-Node", "ip": "203.0.113.88", "mac": "BA:AD:F0:0D:33:92"},
    {"id": "ShadowDevice", "ip": "198.51.100.29", "mac": "AB:BC:CD:DE:EF:01"},
    {"id": "Botnet-Agent-09", "ip": "204.12.77.190", "mac": "FE:ED:FA:CE:55:09"},
]

def connect_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="Python_Simulator_Sender")
    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        print("Connected to MQTT broker.")
        return client
    except Exception as e:
        print("MQTT connection failed:", e)
        return None

def simulate_traffic(client):
    print("Simulator running... Press Ctrl+C to stop.\n")

    try:
        while True:

            # 50% chance legit device, 50% suspicious
            if random.random() > 0.50:
                device = random.choice(DEVICES)
            else:
                # 10% of packets come from attacker devices
                device = random.choice(SUSPICIOUS_DEVICES)
                print(f"\nROGUE PACKET from {device['id']}! (Suspicious device)\n")

            current_load = random.randint(5, 30)
            source_ip = device["ip"]
            status = "active"

            # --- RANDOM ANOMALIES FOR LEGIT DEVICES ONLY ---
            if device in DEVICES and random.random() < 0.10:
                anomaly_type = random.choice([
                "load",
                "ip",
                "spam",
                "ntp_flood",
                "http_bruteforce",
                "unauthorized_firmware_update",
                "unexpected_encryption",
                "suspicious_time_shift",
                "bluetooth_jamming",])
                print(f"\nANOMALY on {device['id']} — {anomaly_type}\n")

                if anomaly_type == "load":
                    current_load = random.randint(70, 99)
                    status = "COMPROMISED"

                elif anomaly_type == "ip":
                    source_ip = "10.0.0." + str(random.randint(200, 250))
                    status = "COMPROMISED"

                elif anomaly_type == "spam":
                    status = "COMPROMISED"
                    time.sleep(0.05)

                elif anomaly_type == "ntp_flood":
                    print("   → High-rate NTP request flood detected")
                    current_load = random.randint(70, 95)
                    status = "COMPROMISED"

                elif anomaly_type == "http_bruteforce":
                    print("   → Multiple HTTP authentication attempts detected (bruteforce)")
                    current_load = random.randint(60, 90)
                    status = "COMPROMISED"

                elif anomaly_type == "unauthorized_firmware_update":
                    print("   → Device attempting unauthorized firmware update")
                    current_load = random.randint(50, 80)
                    status = "COMPROMISED"

                elif anomaly_type == "unexpected_encryption":
                    print("   → Device switched to unexpected encrypted traffic patterns")
                    current_load = random.randint(55, 85)
                    status = "COMPROMISED"

                elif anomaly_type == "suspicious_time_shift":
                    print("   → System clock time shift detected (possible tampering)")
                    current_load = random.randint(40, 65)
                    status = "COMPROMISED"

                elif anomaly_type == "bluetooth_jamming":
                    print("   → Device emitting strong Bluetooth interference signals")
                    current_load = random.randint(60, 90)
                    status = "COMPROMISED"

                elif anomaly_type == "shadow_process":
                    print("   → Unknown background process started (shadow process behavior)")
                    current_load = random.randint(50, 75)
                    status = "COMPROMISED"

            payload = {
                "device_id": device["id"],
                "source_ip": source_ip,
                "mac": device.get("mac"),
                "device_type": device.get("type", "unknown"),
                "current_load": current_load,
                "status": status,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }

            client.publish(TOPIC, json.dumps(payload))
            print(f"Sent: {payload}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == "__main__":
    mqtt_client = connect_mqtt()
    if mqtt_client:
        simulate_traffic(mqtt_client)
