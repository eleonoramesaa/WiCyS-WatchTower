# WiCyS-WatchTower  

A lightweight cybersecurity tool that simulates IoT devices, detects anomalies, stores telemetry in a database, and displays alerts in a dashboard.  
WatchTower learns what “normal” behavior looks like and identifies suspicious or compromised activity — all without needing real IoT devices.

---

## Project Overview

WatchTower emulates a real IoT security monitoring environment:

- simulated IoT devices generate live telemetry  
- WatchTower Scanner detects anomalies in real time  
- Oracle Autonomous Database (optional) stores device data  
- a React dashboard displays alerts and device activity  
- a one-command launcher starts the whole system automatically  

This makes WatchTower perfect for demos, classroom projects, and cybersecurity research.

Components
-------------

### IoT Device Simulator (Python)

**File:** `src/website/backend/simple_simulator.py`

Simulates realistic IoT devices, including:

-   device ID, IP, MAC, and type (camera, printer, thermostat)

-   random "normal" load and status

-   occasional anomalies like:

    -   high CPU/load spikes

    -   traffic from unexpected IP ranges

    -   spam-like bursts

For each telemetry event, it:

-   publishes a JSON message to MQTT topic `watchtower/telemetry`

-   inserts the event into an Oracle database via `db_utils.insert_telemetry(...)`

* * * * *

### WatchTower Scanner (Python)

**File:** `src/website/backend/nmap_scanner.py`

Listens to the same MQTT topic and performs lightweight anomaly checks:

-   **Suspicious MAC detection**

    -   compares each MAC against a known safe list

-   **Suspicious IP ranges**

    -   flags private or unusual ranges such as `10.x`, `172.20.x`, or `.250` endings

-   **Compromised status**

    -   if the simulator marks the device as `"COMPROMISED"`, it raises an alert

For each received packet, it prints a readable summary like:

`========================================
📨 2025-11-24 19:40:28 | Camera-01
IP: 192.168.1.105   MAC: 00:11:22:33:44:55   Load: 12   Status: active
========================================`

If it detects something suspicious, it prints additional messages:

-   `SUSPICIOUS MAC DETECTED!`

-   `SUSPICIOUS IP RANGE DETECTED!`

-   `COMPROMISED ACTIVITY DETECTED!`

* * * * *

### Oracle Autonomous Database (Optional)

Used for storing:

-   telemetry events

-   device behavior history

-   alerts and compromised events

**Wallet directory path (expected):**

`src/website/backend/Wallet_WatchTowerDev/`

`db_utils.py` handles:

-   secure connection using the wallet + `oracledb`

-   helper functions for inserting telemetry from the simulator

> If the wallet is not present or misconfigured, the simulator will print an Oracle error and exit, but the rest of the architecture (MQTT + Scanner + Frontend) can still be demonstrated.

* * * * *

### React Frontend Dashboard

**Location:** `src/website/frontend/`

This is a Vite + React implementation of a cybersecurity dashboard UI based on a Figma design.\
The current version focuses on:

-   overall layout and visual representation of a cyber monitoring dashboard

-   space for device lists, alerts, and telemetry visualizations

You start it using `npm run dev` and access it at:

`http://localhost:3000/`

* * * * *

### One-Command Launcher

**File:** `orchestration/run_watchtower.py`

This script is designed to:

-   ensure Mosquitto (MQTT broker) is running

-   open **three new terminal windows** (macOS) or processes (Windows) for:

    -   IoT Simulator (`simple_simulator.py`)

    -   WatchTower Scanner (`nmap_scanner.py`)

    -   Frontend Dashboard (`npm run dev`)

It centralizes startup so you can demo the full system using a single command.

* * * * *

Prerequisites
----------------

### 1. Mosquitto MQTT Broker

#### macOS

`brew install mosquitto
brew services start mosquitto`

Verify it is running:

`mosquitto_sub -h localhost -t "#" -v`

If it just waits and does **not** error, your broker is up.

#### Windows

1.  Download Mosquitto from:\
    <https://mosquitto.org/download/>

2.  Install with default settings.

3.  Start the broker from a terminal:

`mosquitto`

Leave this window open while using WatchTower.

* * * * *

### 2. Python Dependencies

From the **project root** (`WiCyS-WatchTower/`), install:

`pip install paho-mqtt python-nmap oracledb`

If you are using a virtual environment, activate it first.

* * * * *

### 3. Frontend Dependencies

From the frontend folder:

`cd src/website/frontend
npm install
npm install -D @vitejs/plugin-react-swc`

This installs React, Vite, and the necessary SWC plugin.

* * * * *

### 4. Oracle Wallet

You will need to create your own Oracle wallet: https://docs.oracle.com/middleware/1213/wls/JDBCA/oraclewallet.htm#JDBCA596

Place your **Oracle wallet folder** here:

`src/website/backend/Wallet_WatchTowerDev/`

`db_utils.py` is configured to look in that relative path.\
If it is missing, database insertion in `simple_simulator.py` will fail with `DPY-4026` (missing `tnsnames.ora`).

* * * * *

Run WatchTower With ONE Command
----------------------------------

From the **project root** (`WiCyS-WatchTower/`):

### macOS

`python3 orchestration/run_watchtower.py`

### Windows

`python orchestration/run_watchtower.py`

This will:

-   check and/or start Mosquitto

-   launch the **IoT Simulator** (backend)

-   launch the **WatchTower Scanner**

-   launch the **Frontend Dashboard**

You should then see the dashboard at:

`http://localhost:3000/`

> If some windows show errors (e.g., missing `nmap` or Oracle wallet), those services might fail, but the others can still run. You can use the error messages as part of a troubleshooting or "real-world complexity" explanation.

* * * * *

Manual Run Instructions (Optional)
-------------------------------------

If you want to run each component separately instead of using the orchestration script:

* * * * *

### 1\. Start MQTT Broker

#### macOS

`brew services start mosquitto`

#### Windows

`mosquitto`

* * * * *

### 2\. Run WatchTower Scanner

From the **project root** or from `src/website/backend`:

`cd src/website/backend
python nmap_scanner.py`

You should see output like:

`Starting WatchTower Scanner...
Connected. Listening for traffic...`

* * * * *

### 3\. Run IoT Device Simulator

In another terminal:

`cd src/website/backend
python simple_simulator.py`

You should see:

-   "Connected to MQTT broker."

-   "Simulator running... Press Ctrl+C to stop."

-   `Sent: { ... }` lines for each generated packet

If Oracle DB is configured correctly, telemetry is also inserted into the database.

* * * * *

### 4\. Start the Frontend Dashboard

In another terminal:

`cd src/website/frontend
npm run dev`

You should see something like:

`VITE v6.x.x  ready in XXX ms
➜  Local:   http://localhost:3000/`

Open that URL in your browser to view the dashboard.

* * * * *

How WatchTower Detects Anomalies
-----------------------------------

WatchTower uses **simple, rule-based detection**, not machine learning.\
This keeps the system:

-   easy to understand

-   predictable

-   demo-friendly

### Baseline Behavior

"Normal" behavior in this version is defined by:

-   expected IP ranges for legitimate IoT devices

-   known MAC addresses for allowed devices

-   typical load range (e.g., 5--30) from the simulator

The simulator **mostly** emits normal behavior, but:

-   occasionally emits packets from **rogue devices**

-   occasionally marks legitimate devices as **COMPROMISED**

-   sometimes sends traffic from **unexpected IP ranges**

-   sometimes simulates **high load** or **spammy timing**

### Detection Rules

The scanner flags anomalies like:

| Behavior | What It Means |
| --- | --- |
| Load spike (70--99) | Possible malware or heavy misuse |
| IP in `10.x` or `172.20.x` | Suspicious internal or lateral movement |
| IP ending in `.250` | Potential infrastructure or rogue node |
| Unknown MAC address | Unauthorized / shadow device |
| Status == `COMPROMISED` | Device marked as suspicious by logic |

Because this is rule-based, you can explain every alert clearly in your report or presentation.

* * * * *
