
import time
import json
import random
import paho.mqtt.client as mqtt

# --- CONFIGURATION ---
BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "watchtower/telemetry"

# --- STATEFUL DEVICES ---
# Each device keeps track of its current state so values "drift" realistically
devices_state = [
    {"id": "Camera-01", "ip": "192.168.1.105", "type": "camera", "temp": 45.0, "load": 10, "status": "active"},
    {"id": "Printer-X", "ip": "192.168.1.106", "type": "printer", "temp": 30.0, "load": 5, "status": "active"},
    {"id": "Thermostat-A", "ip": "192.168.1.107", "type": "sensor", "temp": 22.0, "load": 2, "status": "active"}
]

def get_rogue_ip():
    """Generates a random IP address to simulate spoofing/external attacks"""
    return f"{random.randint(1, 200)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def update_device_state(device):
    """Evolves the device state naturally or triggers specific anomalies."""
    
    # 1. Natural Drift (Responsive Behavior)
    # Temp changes slowly (+/- 0.5 degrees)
    device["temp"] += random.uniform(-0.5, 0.5)
    # Load fluctuates slightly (+/- 2%)
    device["load"] += random.randint(-2, 2)
    
    # Clamp values to realistic ranges
    device["temp"] = max(10.0, min(90.0, device["temp"]))
    device["load"] = max(0, min(100, device["load"]))
    
    # 2. Random Anomaly Trigger (1 in 20 chance per cycle)
    if random.randint(1, 20) == 20:
        anomaly_type = random.choice(["overheat", "ddos", "spoof"])
        
        if anomaly_type == "overheat":
            print(f"\n⚠️  Anomaly: {device['id']} is OVERHEATING!")
            device["temp"] += 20.0 # Sudden spike
            device["status"] = "WARNING_HEAT"
            
        elif anomaly_type == "ddos":
            print(f"\n⚠️  Anomaly: {device['id']} under HIGH LOAD (DDoS)!")
            device["load"] = 99
            device["status"] = "COMPROMISED"
            
        elif anomaly_type == "spoof":
            print(f"\n⚠️  Anomaly: {device['id']} IP SPOOFED!")
            # Return a payload with a FAKE IP, but keep the device's real state safe
            return {
                "device_id": device["id"],
                "source_ip": get_rogue_ip(), # <--- The anomaly for Nmap to catch
                "device_type": device["type"],
                "current_temp": round(device["temp"], 1),
                "current_load": device["load"],
                "status": "active", 
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
    else:
        # Reset status if not currently anomalous
        device["status"] = "active"

    # Return normal state payload
    return {
        "device_id": device["id"],
        "source_ip": device["ip"],
        "device_type": device["type"],
        "current_temp": round(device["temp"], 1),
        "current_load": device["load"],
        "status": device["status"],
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

def connect_mqtt():
    # Using CallbackAPIVersion.VERSION2 for Paho MQTT 2.x compatibility
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Python_Smart_Simulator")
    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        print(f"✅ Connected to MQTT Broker at {BROKER_ADDRESS}")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Broker: {e}")
        return None

def simulate_traffic(client):
    print(f"🚀 Smart Simulator running. Sending data to '{TOPIC}'...")
    print("Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Update and send data for ALL devices in each cycle
            for device in devices_state:
                payload = update_device_state(device)
                
                json_payload = json.dumps(payload)
                client.publish(TOPIC, json_payload)
                
                # Visual indicator for the terminal
                status_icon = "🔴" if payload['status'] != "active" or payload['source_ip'] != device['ip'] else "🟢"
                print(f"{status_icon} {payload['device_id']} | IP: {payload['source_ip']} | Temp: {payload['current_temp']}°C | Load: {payload['current_load']}%")
                
                time.sleep(0.5) # Small delay between devices to make it readable
            
            print("-" * 30)
            time.sleep(2.0) # Wait before next update cycle
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")

if __name__ == "__main__":
    # Ensure Mosquitto is running: 'sudo service mosquitto start'
    mqtt_client = connect_mqtt()
    if mqtt_client:
        simulate_traffic(mqtt_client)

