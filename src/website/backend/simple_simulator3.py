import time
import json
import random
import paho.mqtt.client as mqtt
from db_utils import insert_telemetry
from db_utils import connect_to_db

#Another instance of simulator w/diff configs
# --- CONFIGURATION ---
BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "watchtower/telemetry"

# Legit devices you want to monitor
DEVICES = [
    {"id": "Camera-01", "ip": "192.168.1.105", "mac": "00:11:22:33:44:55", "type": "camera"},
    {"id": "Printer", "ip": "192.168.1.106", "mac": "00:11:22:33:44:66", "type": "printer"},
    {"id": "Thermostat-A", "ip": "192.168.1.107", "mac": "00:11:22:33:44:77", "type": "sensor"},
    {"id": "Door-Lock-01", "ip": "192.168.1.108", "mac": "00:11:22:33:44:88", "type": "door-lock"},
    {"id": "Smart-TV-LivingRoom", "ip": "192.168.1.109", "mac": "00:11:22:33:44:99", "type": "tv"},
    {"id": "Laptop-Office", "ip": "192.168.1.110", "mac": "00:11:22:33:AA:11", "type": "laptop"},
    {"id": "AccessPoint-01", "ip": "192.168.1.111", "mac": "00:11:22:33:AA:22", "type": "network"},
    {"id": "NAS-Storage", "ip": "192.168.1.112", "mac": "00:11:22:33:AA:33", "type": "storage"},
]

# Suspicious devices (attackers, rogue devices, unknown hosts)
SUSPICIOUS_DEVICES = [
    {"id": "Unknown-Device", "ip": "10.10.50.12", "mac": "AA:BB:CC:DD:EE:99"},
    {"id": "Printer", "ip": "172.20.33.8", "mac": "AA:11:22:BB:44:88"},
    {"id": "Speaker", "ip": "192.168.1.250", "mac": "DE:AD:BE:EF:FA:CE"},
    {"id": "Rogue-AP", "ip": "192.168.1.240", "mac": "66:55:44:33:22:11"},
    {"id": "Unknown-Laptop", "ip": "192.168.1.222", "mac": "12:34:56:78:9A:BC"},
    {"id": "Malicious-Bot-01", "ip": "203.0.113.45", "mac": "BA:DB:EE:F0:0D:01"},
    {"id": "Spoofed-MAC-Device", "ip": "192.168.1.199", "mac": "00:11:22:33:44:55"},  # Spoof of your legit Camera-01
    {"id": "External-Scanner", "ip": "198.51.100.77", "mac": "FA:CE:F0:0D:BA:BE"},
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

            # 70% chance legit device, 30% suspicious
            if random.random() > 0.30:
                device = random.choice(DEVICES)
            else:
                # 10% of packets come from attacker devices
                device = random.choice(SUSPICIOUS_DEVICES)
                print(f"\nROGUE PACKET from {device['id']}! (Suspicious device)\n")

            current_load = random.randint(5, 30)
            source_ip = device["ip"]
            status = "active"

            # --- RANDOM ANOMALIES FOR LEGIT DEVICES ONLY ---
            if device in DEVICES and random.random() < 0.30:
                anomaly_type = random.choice([
                    "load",
                    "ip",
                    "spam",
                    "mac_spoof",
                    "port_scan",
                    "failed_logins",
                    "data_exfiltration",
                    "arp_poison",
                    "dns_tunnel",
                    "malformed_packets",
                    "beaconing"])
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

                elif anomaly_type == "mac_spoof":
                    device["mac"] = "AA:BB:" + ":".join(f"{random.randint(0, 255):02X}" for _ in range(4))
                    status = "COMPROMISED"

                elif anomaly_type == "port_scan":
                    current_load = random.randint(60, 95)
                    print(f"   → Rapid port activity detected from {device['id']}")

                elif anomaly_type == "failed_logins":
                    current_load = random.randint(55, 80)
                    print(f"   → Multiple failed authentications detected")

                elif anomaly_type == "data_exfiltration":
                    current_load = random.randint(80, 100)
                    source_ip = f"192.168.1.{random.randint(180, 254)}"
                    print("   → Large outbound data transfer anomaly")

                elif anomaly_type == "arp_poison":
                    print(f"   → Device attempting ARP spoofing on the network")
                    status = "COMPROMISED"

                elif anomaly_type == "dns_tunnel":
                    current_load = random.randint(65, 90)
                    print("   → Suspicious DNS query bursts detected")

                elif anomaly_type == "malformed_packets":
                    print("   → High number of malformed or corrupted packets")
                    current_load = random.randint(40, 60)

                elif anomaly_type == "beaconing":
                    print("   → Regular outbound beaconing (possible C2 behavior)")
                    status = "COMPROMISED"
                    current_load = random.randint(50, 70)


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
