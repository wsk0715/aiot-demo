"""
게이트웨이 시뮬레이터 — Jetson Orin (NPU/GPU 연산) 역할
실제 하드웨어: 드론 4대로부터 MQTT 수신 → 집계 → 서버로 HTTP REST 전송

Protocol: MQTT 수신 + HTTP REST 송신
Pipeline:
  MQTT subscribe (drone/+/telemetry) ──1초 버퍼──→ HTTP POST (localhost:18080)

실행: python gateway_simulator.py
의존성: mosquitto (localhost:1883), Spring Boot (localhost:18080), paho-mqtt, requests
"""

import json
import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone

import requests
from paho.mqtt import client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

SERVER_URL = "http://localhost:18080/api/gateway/telemetry"

GATEWAY_ID = "ORIN-001"

# 드론 ID별 최신 텔레메트리 버퍼 (OrderedDict으로 마지막 수신 시간 추적)
buffer: OrderedDict = OrderedDict()
buffer_lock = threading.Lock()


def on_mqtt_message(client, userdata, msg):
    """MQTT 메시지 수신 → 버퍼에 저장"""
    global buffer
    try:
        payload = json.loads(msg.payload.decode())
        drone_id = payload.get("drone_id")
        if not drone_id:
            return
        with buffer_lock:
            # 버퍼에 저장 (같은 drone_id면 덮어쓰기)
            buffer[drone_id] = payload
            # 가장 오래된 항목이 너무 많으면 제거 (메모리)
            while len(buffer) > 10:
                buffer.popitem(last=False)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [경고] 메시지 파싱 실패: {e}")


def mqtt_subscriber() -> mqtt.Client:
    """MQTT 구독 클라이언트 생성"""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_mqtt_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except ConnectionRefusedError:
        print(f"  [경고] MQTT broker({MQTT_BROKER}:{MQTT_PORT}) 연결 실패")
        return None

    # 와일드카드로 모든 드론 텔레메트리 구독
    client.subscribe("drone/+/telemetry")
    client.subscribe("drone/+/status")
    client.loop_start()
    return client


def flush_buffer():
    """버퍼를 HTTP POST로 서버 전송"""
    with buffer_lock:
        if not buffer:
            return
        drones = list(buffer.values())
        buffer.clear()

    # 3초 이상 지난 데이터는 제외
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fresh = [d for d in drones
             if (datetime.now(timezone.utc) - datetime.fromisoformat(
                 d.get("timestamp", now_ts).replace("Z", "+00:00")
             )).total_seconds() < 10]

    if not fresh:
        return

    payload = {
        "gateway_id": GATEWAY_ID,
        "gateway_ts": now_ts,
        "drones": fresh,
    }

    try:
        resp = requests.post(SERVER_URL, json=payload, timeout=3)
        if resp.status_code != 200:
            print(f"  [경고] 서버 응답 {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"  [경고] 서버({SERVER_URL}) 연결 실패")
    except Exception as e:
        print(f"  [에러] HTTP 전송 실패: {e}")


def main():
    print(f"\n{'='*50}")
    print(f"  게이트웨이 시뮬레이터")
    print(f"  Gateway ID: {GATEWAY_ID}")
    print(f"  MQTT: tcp://{MQTT_BROKER}:{MQTT_PORT}")
    print(f"  Server: {SERVER_URL}")
    print(f"{'='*50}\n")

    client = mqtt_subscriber()
    if not client:
        return

    print(f"  MQTT 구독 시작 (drone/+/telemetry)")
    print(f"  1초마다 버퍼 → 서버 전송\n")

    try:
        while True:
            time.sleep(1)
            flush_buffer()
    except KeyboardInterrupt:
        print("\n  종료 중...")
    finally:
        client.disconnect()
        print("  ⏹ 게이트웨이 종료")


if __name__ == "__main__":
    main()
