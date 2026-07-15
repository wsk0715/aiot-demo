package com.example.demo_app.mqtt;

import java.util.List;

/**
 * 게이트웨이 → 서버 HTTP POST 요청 DTO
 */
public class GatewayTelemetryRequest {

    private String gateway_id;
    private String gateway_ts;
    private List<DroneTelemetry> drones;

    public String getGateway_id() { return gateway_id; }
    public void setGateway_id(String gateway_id) { this.gateway_id = gateway_id; }

    public String getGateway_ts() { return gateway_ts; }
    public void setGateway_ts(String gateway_ts) { this.gateway_ts = gateway_ts; }

    public List<DroneTelemetry> getDrones() { return drones; }
    public void setDrones(List<DroneTelemetry> drones) { this.drones = drones; }
}
