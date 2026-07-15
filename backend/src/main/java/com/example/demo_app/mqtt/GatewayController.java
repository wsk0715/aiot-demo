package com.example.demo_app.mqtt;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 게이트웨이(Jetson Orin)로부터 HTTP REST로 수신
 *
 * POST /api/gateway/telemetry
 *   Body: GatewayTelemetryRequest (gateway_id, gateway_ts, drones[])
 *   → server_ts 추가
 *   → 각 드론 데이터를 SSE로 broadcast
 */
@RestController
@RequestMapping("/api/gateway")
public class GatewayController {

    private static final Logger log = LoggerFactory.getLogger(GatewayController.class);
    private final SseService sseService;

    public GatewayController(SseService sseService) {
        this.sseService = sseService;
    }

    @PostMapping("/telemetry")
    public Map<String, Object> receiveTelemetry(
            @RequestBody GatewayTelemetryRequest request) {

        String serverTs = Instant.now().toString();

        if (request.getDrones() == null || request.getDrones().isEmpty()) {
            log.warn("게이트웨이 {}: 드론 데이터 없음", request.getGateway_id());
            Map<String, Object> res = new HashMap<>();
            res.put("status", "ok");
            res.put("count", 0);
            return res;
        }

        for (GatewayTelemetryRequest.DroneTelemetry drone : request.getDrones()) {
            // Frontend SSE 스키마로 변환: server_ts + drong_ts 추가
            Map<String, Object> ssePayload = new HashMap<>();
            ssePayload.put("drone_id", drone.getDrone_id());
            ssePayload.put("server_ts", serverTs);
            ssePayload.put("drone_ts", drone.getTimestamp());
            ssePayload.put("latitude", drone.getLatitude());
            ssePayload.put("longitude", drone.getLongitude());
            ssePayload.put("altitude", drone.getAltitude());
            ssePayload.put("speed", drone.getSpeed());
            ssePayload.put("battery", drone.getBattery());
            ssePayload.put("heading", drone.getHeading());

            sseService.broadcast(ssePayload);
        }

        log.info("게이트웨이 {}: {}건 수신 → SSE 브로드캐스트",
                request.getGateway_id(), request.getDrones().size());

        Map<String, Object> result = new HashMap<>();
        result.put("status", "ok");
        result.put("count", request.getDrones().size());
        return result;
    }
}
