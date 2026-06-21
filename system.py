import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt
from gpiozero import AngularServo, LED
import sqlite3
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

led = LED(16)
led.off()
servo = AngularServo(18, min_angle=-90, max_angle=90, min_pulse_width=0.0005, max_pulse_width=0.0025)
dhtDevice = adafruit_dht.DHT11(board.D23)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("localhost", 1883, 60)

conn = sqlite3.connect('lab.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        temperature REAL,
        humidity REAL,
        status TEXT
    )
''')
conn.commit()

TEMP_THRESHOLD = 40.0
is_plug_pulled = False
servo.angle = 0

while True:
    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        
        current_status = "已斷電" if is_plug_pulled else "正常"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("INSERT INTO sensor_log (timestamp, temperature, humidity, status) VALUES (?, ?, ?, ?)", 
                       (current_time, temperature_c, humidity, current_status))
        conn.commit()
        
        cursor.execute("SELECT AVG(temperature), AVG(humidity) FROM (SELECT temperature, humidity FROM sensor_log ORDER BY id DESC LIMIT 10)")
        avg_data = cursor.fetchone()
        
        avg_temp = avg_data[0] if avg_data[0] is not None else temperature_c
        avg_hum = avg_data[1] if avg_data[1] is not None else humidity
        
        print(f"[{current_time}] 溫度: {temperature_c:.1f}°C (平均: {avg_temp:.1f}) 濕度: {humidity:.1f}% (平均: {avg_hum:.1f}) 狀態: {current_status}")

        client.publish("lab/sensor", f"{temperature_c:.1f},{humidity:.1f},{avg_temp:.1f},{avg_hum:.1f}")
        client.publish("lab/status", current_status)
        
        if temperature_c >= TEMP_THRESHOLD and not is_plug_pulled:
            print("觸發")
            servo.angle = 90
            led.on()
            is_plug_pulled = True
        elif temperature_c < TEMP_THRESHOLD and is_plug_pulled:
            print("恢復正常")
            servo.angle = 0
            led.off()
            is_plug_pulled = False
            
    except RuntimeError as error:
        print("感測器重試:", error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        led.off()
        servo.detach()
        conn.close()
        raise error
        
    time.sleep(5.0)
