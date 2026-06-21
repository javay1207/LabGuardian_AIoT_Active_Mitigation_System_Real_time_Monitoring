# LabGuardian AIoT Active Mitigation System: Real-time Monitoring

## Introduction
The LabGuardian project is designed to address the safety monitoring needs of school laboratories. Using the Raspberry Pi 5 as a high-performance central gateway, the system tracks ambient temperature and humidity levels in real-time to prevent equipment overheating or fire hazards. 

While traditional systems rely on audible alarms or simple notifications that may be ignored when a laboratory is unattended, this design utilizes the high computational power of Raspberry Pi 5 to bridge edge computing with high-torque mechatronics. The primary contribution is the development of an automated, soft-hard integrated mechanism capable of physically 'yanking' the power plug from the socket during a critical overheat event. 

## Target Users & Usage Scenario
* **Campus Lab Managers:** Who need to oversee multiple lab rooms.
* **Engineering Students:** Who leave experimental setups running for long periods.

**Usage Scenario:** A student is running a stress test on a server rack inside the Smart Campus lab. 
1. The room's air conditioning fails during the weekend.
2. The server rack temperature begins to rise rapidly, reaching a dangerous threshold.
3. The Raspberry Pi 5 detects the temperature spike through its sensors.
4. It immediately publishes an alert message via MQTT. The Node-RED dashboard turns red and triggers an on-screen notification, allowing the duty manager to intervene before the hardware is damaged.

## Key Features
* **Real-time Sensing:** A Python script on the Raspberry Pi 5 reads sensor data every few seconds to monitor the environment.
* **Active Physical Mitigation:** If the temperature exceeds 40°C, the system automatically triggers a "Warning" logic node. It activates a high-torque servo motor to physically yank the power plug from the socket and turns on an LED indicator to prevent hardware damage.
* **Data Visualization:** Node-RED subscribes to the MQTT data, processing the values to display them on an intuitive web-based Gauges and Charts dashboard.
* **Historical Data Analysis:** The system utilizes an SQLite database to record data and calculate the moving average of temperature and humidity (based on the last 20 records) to smooth out sensor fluctuations and track long-term patterns.

## System Architecture & Requirements

### Hardware Composition
* **Primary Platform:** Raspberry Pi 5
* **Sensors:** DHT11/DHT22 Temperature & Humidity Sensor (GPIO 23)
* **Indicators:** LED for local visual alerts (GPIO 16)
* **Actuator:** High-Torque Servo Motor (GPIO 18)

### Software Workflow
* **Operating System:** Raspberry Pi OS
* **Programming Language:** Python 3 (`gpiozero`, `adafruit_dht`, `paho-mqtt`, `sqlite3`)
* **Communication Protocol:** MQTT (Mosquitto Broker hosted on the Pi)
* **Database:** SQLite3 (Fields: id, timestamp, temperature, humidity, status)
* **UI & Logic:** Node-RED

## Quick Start

**1. System Update & Preparation**
Ensure your Raspberry Pi is up to date and install the necessary MQTT services:
```bash
sudo apt-get update
sudo apt-get install -y mosquitto mosquitto-clients
```
**2. Install Python Dependencies**
Navigate to the project directory and install the required libraries:

```bash
pip install -r requirements.txt
```
**3. Configure Node-RED Dashboard**
Before starting the sensor script, you need to set up the visualization interface:

* Start Node-RED on your Raspberry Pi.
* Open a browser and go to `http://<Your_Raspberry_Pi_IP_Address>:1880`.
* Click the menu icon `(≡)` in the top right corner and select Import.
* Upload the `flows.json` file included in this repository.
* Click the red `Deploy` button in the top right corner to activate the MQTT listener and dashboard logic.

**4. Run the Monitoring Script**
Execute the Python script. The system will automatically create the `lab.db` database and start publishing data to the MQTT Broker every 5 seconds:

```bash
python3 system.py
```
**5. Access the Dashboard**
Open a web browser on any device within the same local network and navigate to the UI page to view real-time data:`http://<Your_Raspberry_Pi_IP_Address>:1880/ui`
