# WiCyS-WatchTower
Cybersecurity tool that keeps an eye on smart devices in your home or office, like printers, cameras, speakers, thermostats, and smart plugs. The tool learns what “normal” behavior looks like for each device and flags anything unusual.

---

## What Is WatchTower?
WatchTower monitors Internet-of-Things (IoT) devices by observing their normal behavior patterns and detecting anything out of the ordinary.  
This helps identify potential cyberattacks, unsafe network traffic, or unusual device activity inside a home or small office.

The goal of WatchTower is to make it easy to understand when something suspicious is happening on your network without needing deep cybersecurity knowledge.

---

## Tools Used

### IoT Data Simulator
Used to generate realistic fake IoT devices that behave like real ones.  
This lets the team test WatchTower without needing physical hardware.

### Mosquitto (MQTT Broker)
Serves as a central “message hub” where simulated devices send their data.  
WatchTower listens to these messages to understand what devices are doing.

### Nmap
A network scanning tool that checks which devices and ports are visible on the network.  
It helps WatchTower identify devices that appear online, including the simulated ones.

### WatchTower Backend (Python)
Receives device messages, builds a baseline of normal behavior, and detects anything unusual or suspicious.

### WatchTower Dashboard
Displays device information, activity logs, alerts, and any suspicious behavior in a clean user interface.

### Docker / Docker-Compose
Allows all components (simulator, MQTT broker, backend, dashboard) to run together in containers.  
This makes the system easy to start, stop, and share among team members.

---

## How to Run WatchTower

### 1. Start the IoT Simulator
Navigate into the simulator folder and run:

```bash
docker-compose up
```

This launches:

- the IoT data simulator  
- its user interface  
- MongoDB  
- Minio  
- RabbitMQ  

Open the simulator UI at:

```
http://localhost:8090
```

---

### 2. Create Your Fake Devices
Inside the simulator UI:

- Create a session  
- Add devices (camera, thermostat, plug, etc.)  
- Choose how often they send data  
- Set the target system to **MQTT**  
- Use topics such as:
  - `devices/cam-1`
  - `devices/thermo-1`
  - `devices/plug-1`

The simulator will now begin generating normal and suspicious IoT traffic.

---

### 3. Start Mosquitto (MQTT Broker)
If you are using Docker Compose, Mosquitto starts automatically.

You can verify it's working by subscribing to device topics:

```bash
mosquitto_sub -h localhost -t "devices/#" -v
```

If messages appear, MQTT is functioning correctly.

---

### 4. Run the WatchTower Backend
The backend subscribes to MQTT, stores device data, analyzes behavior, and detects anomalies.

Run it with:

```bash
python app.py
```

---

### 5. Run the WatchTower Dashboard
Start your dashboard UI (React or Flask):

```bash
npm start
```

or:

```bash
python dashboard.py
```

The dashboard will show:

- connected devices  
- real-time activity  
- alerts  
- suspicious events  
- device history  

---

## Special Features

### Suspicious IoT Behavior Detection
WatchTower identifies unusual events such as:

- sudden temperature spikes  
- motion detected at unexpected times  
- devices connecting to new IP addresses  
- rapidly repeated messages  
- behavior that does not match normal patterns  

### Simulated Devices Behave Like Real Devices
Using Mosquitto and Nmap, simulated devices appear on the network with real traffic and open ports.

This makes it possible to:

- discover them with Nmap  
- analyze them like physical IoT devices  

### Built-In Attack Scenarios
We intentionally create strange or malicious behavior to test detection abilities, including:

- cameras turning on unexpectedly  
- thermostats jumping to unsafe levels  
- fake power-usage spikes  
- extremely frequent data bursts  

These realistic scenarios help WatchTower detect real-world attacks.

### Fully Containerized Project
All tools run in Docker, which makes the project:

- portable  
- easy to set up  
- consistent across team members  

### Easy to Extend
You can add:

- new IoT devices  
- new suspicious behavior patterns  
- more dashboard views  
- custom detection rules  

with minimal configuration.

---

## Project Summary
WiCyS-WatchTower learns what normal IoT device behavior looks like and alerts you when something unusual, unsafe, or suspicious occurs. It uses an IoT simulator, MQTT, Nmap, and a custom detection dashboard to create a realistic, beginner-friendly cybersecurity monitoring system.
