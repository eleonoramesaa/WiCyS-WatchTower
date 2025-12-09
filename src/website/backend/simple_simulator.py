# simple_simulator.py
import time
import json
import random
import paho.mqtt.client as mqtt
import oracledb
from db_utils import insert_telemetry, connect_to_db, get_credentials

# --- CONFIGURATION ---
BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "watchtower/telemetry"


# Legit devices 
DEVICES = [
    {
        "id": "Camera-01",
        "ip": "192.168.1.105",
        "mac": "00:11:22:33:44:55",
        "type": "camera",
        "os": "Embedded Linux"
    },
    {
        "id": "Printer-X",
        "ip": "192.168.1.106",
        "mac": "00:11:22:33:44:66",
        "type": "printer",
        "os": "Linux"
    },
    {
        "id": "Thermostat-A",
        "ip": "192.168.1.107",
        "mac": "00:11:22:33:44:77",
        "type": "sensor",
        "os": "RTOS"
    }
]

# Suspicious devices
SUSPICIOUS_DEVICES = [
    {
        "id": "Unknown-Device",
        "ip": "10.10.50.12",
        "mac": "AA:BB:CC:DD:EE:99",
        "os": "Unknown"
    },
    {
        "id": "Laptop",
        "ip": "172.20.33.8",
        "mac": "AA:11:22:BB:44:88",
        "os": "Windows"
    },
    {
        "id": "Flock-Camera",
        "ip": "192.168.1.250",
        "mac": "DE:AD:BE:EF:FA:CE",
        "os": "Embedded Linux"
    }
]


# --------------------------
# MQTT CONNECTION
# --------------------------
def connect_mqtt():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="Python_Simulator_Sender"
    )

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        print("Connected to MQTT broker.")
        return client
    except Exception as e:
        print("MQTT connection failed:", e)
        return None


# --------------------------
# THREAT SCORING FUNCTION
# --------------------------
def calculate_threat(device, status, payload_size):
    """
    Returns an integer threat score (0-9).
    Heuristics used:
      - suspicious device: +3
      - compromised status: +3
      - payload_size spikes add 0..3
      - small random jitter (0..1)
    """
    threat = 0

    # Suspicious device baseline
    if device["id"] in {d["id"] for d in SUSPICIOUS_DEVICES}:
        threat += 3

    # Status-based
    if status == "COMPROMISED":
        threat += 3

    # Payload-size contribution (bytes)
    # tune thresholds to your environment
    if payload_size is not None:
        if payload_size > 10000:
            threat += 3
        elif payload_size > 5000:
            threat += 2
        elif payload_size > 2000:
            threat += 1

    # small random jitter for variety
    threat += random.randint(0, 1)

    # cap to 0..9
    if threat < 0:
        threat = 0
    threat = min(threat, 9)
    return threat


# --------------------------
# SIMULATION LOOP
# --------------------------
def simulate_traffic(client):
    print("Simulator running... Press Ctrl+C to stop.\n")

    conn = None

    try:
        username, password, wallet_pw = get_credentials()
        conn = connect_to_db(username, password, wallet_pw)
        print("Connected to DB successfully")

        while True:
            status = "ACTIVE"
            sus_flag = 0

            # 90% legit, 10% suspicious
            if random.random() > 0.10:
                device = random.choice(DEVICES)
            else:
                device = random.choice(SUSPICIOUS_DEVICES)
                print(f"\nROGUE PACKET from {device['id']}! (Suspicious device)\n")
                status = "SUSPICIOUS"
                sus_flag = 1

            # ----------------------------
            # PAYLOAD SIZE = our load metric
            # ----------------------------
            payload_size = random.randint(150, 1500)   # bytes

            source_ip = device["ip"]

            # --------------------------------------------
            # RANDOM LEGIT ANOMALIES (compromise simulation)
            # --------------------------------------------
            if random.random() < 0.10:
                anomaly_type = random.choice(["load", "ip", "spam"])
                print(f"\nANOMALY on {device['id']} — {anomaly_type}\n")

                if anomaly_type == "load":
                    payload_size = random.randint(5000, 20000)  # malicious spike
                    status = "COMPROMISED"

                elif anomaly_type == "ip":
                    source_ip = "10.0.0." + str(random.randint(200, 250))
                    status = "COMPROMISED"

                elif anomaly_type == "spam":
                    status = "COMPROMISED"
                    # mini-delay to simulate burst
                    time.sleep(0.05)

            # ----------------------------
            # CALCULATE THREAT
            # ----------------------------
            threat = calculate_threat(device, status, payload_size)

            # ----------------------------
            # BUILD TELEMETRY PAYLOAD
            # ----------------------------
            payload = {
                "device_id": device["id"],
                "source_ip": source_ip,
                "mac": device.get("mac"),
                "device_type": device.get("type", "unknown"),
                "os": device.get("os", "unknown"),
                "payload_size": payload_size,
                "threat": threat,
                "status": status,
                "suspicious_device": sus_flag,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # Store in Oracle
            # ----------------------------
            # CHECK USER PERMISSIONS
            # ----------------------------
            user_lower = username.lower()
            if user_lower in ("dev1", "admin"):
                print(f"WARNING: User '{username}' is not allowed to insert telemetry. Skipping DB insert.")
            else:
                insert_telemetry(conn, payload)
                print(f"Inserted telemetry for {device['id']} into DB.")

            # Publish over MQTT
            client.publish(TOPIC, json.dumps(payload))
            print(f"Sent: {payload}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")

    except oracledb.DatabaseError as e:
        error, = e.args
        print("Oracle insert failed")
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
        mqtt_client.disconnect()
