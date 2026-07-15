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

    public static class DroneTelemetry {
        private String drone_id;
        private String timestamp;
        private double latitude;
        private double longitude;
        private double altitude;
        private double speed;
        private double battery;
        private int heading;

        public String getDrone_id() { return drone_id; }
        public void setDrone_id(String drone_id) { this.drone_id = drone_id; }

        public String getTimestamp() { return timestamp; }
        public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

        public double getLatitude() { return latitude; }
        public void setLatitude(double latitude) { this.latitude = latitude; }

        public double getLongitude() { return longitude; }
        public void setLongitude(double longitude) { this.longitude = longitude; }

        public double getAltitude() { return altitude; }
        public void setAltitude(double altitude) { this.altitude = altitude; }

        public double getSpeed() { return speed; }
        public void setSpeed(double speed) { this.speed = speed; }

        public double getBattery() { return battery; }
        public void setBattery(double battery) { this.battery = battery; }

        public int getHeading() { return heading; }
        public void setHeading(int heading) { this.heading = heading; }
    }
}
