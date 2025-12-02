import time
import json
import random
import paho.mqtt.client as mqtt
import oracledb
from db_utils import insert_telemetry
from db_utils import connect_to_db
from db_utils import get_credentials, connect_to_db

# --- CONFIGURATION ---
BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "watchtower/telemetry"

# Legit devices you want to monitor
DEVICES = [
    {"id": "Camera-01", "ip": "192.168.1.105", "mac": "00:11:22:33:44:55", "type": "camera"},
    {"id": "Printer-X", "ip": "192.168.1.106", "mac": "00:11:22:33:44:66", "type": "printer"},
    {"id": "Thermostat-A", "ip": "192.168.1.107", "mac": "00:11:22:33:44:77", "type": "sensor"}
]

# Suspicious devices (attackers, rogue devices, unknown hosts)
SUSPICIOUS_DEVICES = [
    {"id": "Unknown-Device", "ip": "10.10.50.12", "mac": "AA:BB:CC:DD:EE:99"},
    {"id": "Laptop", "ip": "172.20.33.8", "mac": "AA:11:22:BB:44:88"},
    {"id": "Flock-Camera", "ip": "192.168.1.250", "mac": "DE:AD:BE:EF:FA:CE"}
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

    conn = None

    try:

        username, password, wallet_pw = get_credentials()
        conn = connect_to_db(username, password, wallet_pw)

        while True:

            # 90% chance legit device  
            if random.random() > 0.10:
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
                anomaly_type = random.choice(["load", "ip", "spam"])
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

            payload = {
                "device_id": device["id"],
                "source_ip": source_ip,
                "mac": device.get("mac"),
                "device_type": device.get("type", "unknown"),
                "current_load": current_load,
                "status": status,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }

            insert_telemetry(conn,payload)

            client.publish(TOPIC, json.dumps(payload))
            print(f"Sent: {payload}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    except oracledb.DatabaseError as e:
            error, = e.args
            print("Commit failed")
            print("Code:", error.code)
            print("Message:", error.message)
            raise
    except Exception as e:
        print("\nUSER INSERT ERROR:")
        print("Oracle error:", e)
        raise
    finally:
        if conn:
            try:
                conn.close()
                print("Connection closed.")
            except Exception as ex:
                print("Error closing connection:", ex)



if __name__ == "__main__":
    mqtt_client = connect_mqtt()
    if mqtt_client:
        simulate_traffic(mqtt_client)
