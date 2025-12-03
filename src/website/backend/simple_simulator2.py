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
    {"id": "Laptop", "ip": "192.168.1.108", "mac": "E3:97:23:A1:1B:CE", "type": "camera"},
    {"id": "Printer-X", "ip": "192.168.1.109", "mac": "B8:89:0A:D8:F9:A8", "type": "printer"},
    {"id": "Thermostat-A", "ip": "192.168.1.110", "mac": "E1:BA:18:36:10:EA", "type": "sensor"}
]

# Suspicious devices (attackers, rogue devices, unknown hosts)
SUSPICIOUS_DEVICES = [
    {"id": "Samsung-phone", "ip": "10.10.50.13", "mac": "7E:97:83:CF:B9:BA"},
    {"id": "Laptop", "ip": "172.20.33.10", "mac": "EC:8F:3B:BD:9B:42"},
    {"id": "Phone", "ip": "192.168.1.251", "mac": "A7:2D:63:91:39:E4"}
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
