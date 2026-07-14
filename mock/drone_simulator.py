import json
import random
import time
from datetime import datetime, timezone

import math

BASE_LAT, BASE_LNG = 37.5665, 126.9780
battery = 100.0
lat, lng = BASE_LAT, BASE_LNG
heading = random.randint(0, 359)  # 초기 방향
STEP = 0.002  # 1초 이동 거리 (약 200m)


def generate_telemetry():
    global battery, lat, lng, heading
    battery = max(0, battery - 1)
    # 방향을 기준으로 이동 (약간의 흔들림 추가)
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
    print("🛸 드론 시뮬레이터 시작")
    try:
        while True:
            print(json.dumps(generate_telemetry()))
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹  종료")


if __name__ == "__main__":
    main()
