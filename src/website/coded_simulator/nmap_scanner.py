import paho.mqtt.client as mqtt
import json
import nmap
import time

# --- CONFIGURATION --- FINALLY NMAP PUT TO WORK
BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883
MQTT_TOPIC = "watchtower/telemetry"
CLIENT_ID = "WatchTower_Scanner"

# initialize Nmap
nm = nmap.PortScanner()

def scan_device(ip_address):
    """Uses Nmap to check if a device actually exists at this IP."""
    print(f"🔎 Scanning {ip_address} to verify device presence...")
    try:
        # ping scan (-sn) is fast and enough to check existence
        nm.scan(hosts=ip_address, arguments='-sn')
        
        if ip_address in nm.all_hosts():
            print(f"   ✅ VERIFIED: Device physically found at {ip_address}")
            return True
        else:
            print(f"   👻 GHOST DETECTED: No physical device found at {ip_address}!")
            return False
    except Exception as e:
        print(f"   ❌ Nmap Error: {e}")
        return False

# --- MQTT CALLBACKS ---

# FIX!!!! Added 'properties' argument for Paho MQTT 2.0 compatibility
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker. Watching for traffic...")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Connection failed. Error: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        source_ip = payload.get('source_ip')
        device_id = payload.get('device_id')
        status = payload.get('status')

        print(f"\n📨 PACKET RECEIVED: {device_id} ({source_ip}) | Status: {status}")

        # 1. run Anomaly Check (High Load / Hacked)
        if status == "COMPROMISED":
            print(f"   🚨 ALERT: Payload indicates device is COMPROMISED!")

        # 2. run Nmap Check (Reality Check)
        scan_device(source_ip)

    except Exception as e:
        print(f"Error processing message: {e}")

# --- MAIN EXECUTION ---
# FIX!! use VERSION2 to satisfy the new library requirement
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

print("Starting WatchTower Nmap Scanner...")
print("1. Listening for Data Stream (MQTT)")
print("2. Active Verification Scanning (Nmap)")
print("-" * 40)

try:
    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 WatchTower stopped.")