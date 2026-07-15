"""
드론 시뮬레이터 — 4대 MQTT 발행
실제 드론을 흉내내어 게이트웨이(Jetson Orin)로 텔레메트리 전송

Protocol: MQTT
Topic:
  - drone/{id}/telemetry   (1Hz, 위치/고도/속도/배터리)
  - drone/{id}/status      (이벤트 기반: TAKEOFF/FLYING/LANDING/EMERGENCY)

실행: python drone_simulator.py
의존성: mosquitto (localhost:1883), paho-mqtt
"""

import json
import math
import os
import random
import threading
import time
from datetime import datetime, timezone

from paho.mqtt import client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# 각 드론의 초기 위치 (서울 일대, 서로 다른 지점)
DRONE_INIT = [
    {"id": "DRONE-001", "lat": 37.5665, "lng": 126.9780, "heading": 0},
    {"id": "DRONE-002", "lat": 37.5512, "lng": 126.9885, "heading": 90},
    {"id": "DRONE-003", "lat": 37.5789, "lng": 126.9700, "heading": 180},
    {"id": "DRONE-004", "lat": 37.5600, "lng": 126.9950, "heading": 270},
]

STEP = 0.0015  # 1초당 이동 거리 (약 150m)


def mqtt_client() -> mqtt.Client:
    """MQTT 클라이언트 생성 (한 드론당 하나씩)"""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except ConnectionRefusedError:
        print(f"  [경고] MQTT broker({MQTT_BROKER}:{MQTT_PORT}) 연결 실패")
        return None
    client.loop_start()
    return client


class Drone:
    """드론 1대 — 자체 좌표/배터리를 가지고 MQTT 발행"""

    def __init__(self, drone_id: str, lat: float, lng: float, heading: int):
        self.id = drone_id
        self.lat = lat
        self.lng = lng
        self.heading = heading
        self.altitude = random.uniform(40, 120)
        self.speed = random.uniform(6, 14)
        self.battery = random.uniform(70, 100)
        self.status = "FLYING"
        self._client = None

    def connect_mqtt(self) -> bool:
        self._client = mqtt_client()
        return self._client is not None

    def _update(self):
        """1틱 — 좌표/배터리/고도 업데이트"""
        self.battery -= random.uniform(0.3, 1.0)
        self.battery = max(0, self.battery)

        # heading ±5° 랜덤 변동
        self.heading += random.uniform(-5, 5)
        rad = math.radians(self.heading)
        self.lat += math.cos(rad) * STEP
        self.lng += math.sin(rad) * STEP

        self.altitude += random.uniform(-2, 2)
        self.altitude = max(10, min(150, self.altitude))

        self.speed += random.uniform(-0.5, 0.5)
        self.speed = max(2, min(20, self.speed))

        # 배터리 0% → 착륙
        if self.battery <= 0 and self.status != "LANDING":
            self.status = "LANDING"
        # 5% 확률로 EMERGENCY → 10초 후 복귀
        if random.random() < 0.005 and self.status == "FLYING":
            self.status = "EMERGENCY"
            threading.Timer(10.0, self._recover).start()

    def _recover(self):
        self.status = "FLYING"

    def _telemetry_payload(self) -> dict:
        return {
            "drone_id": self.id,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "latitude": round(self.lat, 6),
            "longitude": round(self.lng, 6),
            "altitude": round(self.altitude, 1),
            "speed": round(self.speed, 1),
            "battery": round(self.battery, 1),
            "heading": round(self.heading) % 360,
        }

    def _status_payload(self) -> dict:
        return {
            "drone_id": self.id,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": self.status,
        }

    def tick(self):
        """1초마다 호출 — 텔레메트리 + status 발행"""
        self._update()
        if not self._client:
            return

        # telemetry
        tel = self._telemetry_payload()
        self._client.publish(f"drone/{self.id}/telemetry", json.dumps(tel))

        # status (상태 변경 시에만)
        self._client.publish(f"drone/{self.id}/status", json.dumps(self._status_payload()))

    def stop(self):
        if self._client:
            self._client.disconnect()


def run_drone(drone: Drone):
    """드론 1대의 메인 루프 (1 thread)"""
    if not drone.connect_mqtt():
        print(f"  ✗ {drone.id} MQTT 연결 실패")
        return
    print(f"  ✓ {drone.id} 시작")
    try:
        while True:
            drone.tick()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        drone.stop()
        print(f"  ⏹ {drone.id} 종료")


def main():
    print(f"\n{'='*50}")
    print(f"  드론 시뮬레이터")
    print(f"  broker: tcp://{MQTT_BROKER}:{MQTT_PORT}")
    print(f"  드론: {len(DRONE_INIT)}대")
    print(f"{'='*50}\n")

    drones = [Drone(**init) for init in DRONE_INIT]
    threads = []

    for d in drones:
        t = threading.Thread(target=run_drone, args=(d,), daemon=True)
        t.start()
        threads.append(t)

    print(f"\n  모든 드론 실행 중 (Ctrl+C로 종료)\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  종료 중...")

    for d in drones:
        d.stop()


if __name__ == "__main__":
    main()
