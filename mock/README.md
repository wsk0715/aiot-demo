# Mock — 드론 시뮬레이터

## 개요

드론 텔레메트리를 1초 간격으로 생성하는 모킹 스크립트.

## 실행

```bash
pip install -r requirements.txt  # 필요 시
python drone_simulator.py
```

출력은 표준 출력(stdout)으로 JSON이 한 줄씩 나옵니다.  
Ctrl+C 로 종료합니다.

---

## 데이터 명세

| 필드 | 타입 | 설명 | 범위 / 비고 |
|------|------|------|------------|
| `drone_id` | string | 드론 식별자 | `DRONE-001` (고정) |
| `timestamp` | string | UTC ISO-8601 시각 | `2026-07-14T07:35:00+00:00` |
| `latitude` | number | 위도 | 37.56 부근, 이동 시 변화 |
| `longitude` | number | 경도 | 126.97 부근, 이동 시 변화 |
| `altitude` | number | 고도 (m) | 10 ~ 120 |
| `speed` | number | 속도 (m/s) | 8 ~ 12 |
| `battery` | number | 잔량 (%) | 100 → 1초마다 1 감소 |
| `heading` | integer | 방위각 (°) | 0 ~ 359 |

## 예시 출력

```json
{"drone_id":"DRONE-001","timestamp":"2026-07-14T16:20:00+00:00","latitude":37.570123,"longitude":126.981234,"altitude":75.3,"speed":10.2,"battery":87,"heading":45}
```
