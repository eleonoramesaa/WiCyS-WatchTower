import time
import json
import random
import paho.mqtt.client as mqtt

# --- CONFIGURATION ---
BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "watchtower/telemetry"

DEVICES = [
    {"id": "Camera-01", "ip": "192.168.1.105", "type": "camera"},
    {"id": "Printer-X", "ip": "192.168.1.106", "type": "printer"},
    {"id": "Thermostat-A", "ip": "192.168.1.107", "type": "sensor"}
]


def connect_mqtt():
    # FIX: Use VERSION2 to satisfy the new library requirement
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Python_Simulator_Sender")
    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        print(f"✅ Connected to MQTT Broker at {BROKER_ADDRESS}")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Broker: {e}")
        return None


def simulate_traffic(client):
    print(f"🚀 Simulator running. Sending data to '{TOPIC}'...")
    print("Press Ctrl+C to stop.\n")

    try:
        message_count = 0
        while True:
            device = random.choice(DEVICES)
            message_count += 1

            # Simulating Anomalies
            if message_count % 10 == 0:
                print(f"⚠️  SIMULATING ATTACK on {device['id']}!")
                current_load = 99
                status = "COMPROMISED"
            else:
                current_load = random.randint(5, 30)
                status = "active"

            payload = {
                "device_id": device["id"],
                "source_ip": device["ip"],
                "device_type": device["type"],
                "current_load": current_load,
                "status": status,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }

            json_payload = json.dumps(payload)
            client.publish(TOPIC, json_payload)
            print(f"📤 Sent: {json_payload}")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")


if __name__ == "__main__":
    mqtt_client = connect_mqtt()
    if mqtt_client:
        simulate_traffic(mqtt_client)