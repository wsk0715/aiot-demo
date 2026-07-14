import json
import math
import random
import time
from datetime import datetime, timezone

from paho.mqtt import client as mqtt

BASE_LAT, BASE_LNG = 37.5665, 126.9780
battery = 100.0
lat, lng = BASE_LAT, BASE_LNG
heading = random.randint(0, 359)
STEP = 0.002

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "drone/telemetry"


def generate_telemetry():
    global battery, lat, lng, heading
    battery = max(0, battery - 1)
    heading += random.uniform(-2, 2)
    rad = math.radians(heading)
    lat += math.cos(rad) * STEP
    lng += math.sin(rad) * STEP
    altitude = max(10, min(120, lat - BASE_LAT + random.uniform(40, 80)))
    speed = round(random.uniform(8, 12), 1)
    return {
        "drone_id": "DRONE-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": round(lat, 6),
        "longitude": round(lng, 6),
        "altitude": round(altitude, 1),
        "speed": speed,
        "battery": battery,
        "heading": round(heading) % 360,
    }


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    print(f"🛸 드론 시뮬레이터 시작 → mqtt://{MQTT_BROKER}:{MQTT_PORT}/{MQTT_TOPIC}")
    try:
        while True:
            data = generate_telemetry()
            payload = json.dumps(data)
            client.publish(MQTT_TOPIC, payload)
            print(payload)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹  종료")


if __name__ == "__main__":
    main()
