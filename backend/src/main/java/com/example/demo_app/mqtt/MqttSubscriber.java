package com.example.demo_app.mqtt;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;

@Service
@ConditionalOnProperty(name = "mqtt.subscriber.enabled", havingValue = "true", matchIfMissing = false)
public class MqttSubscriber {

    private static final Logger log = LoggerFactory.getLogger(MqttSubscriber.class);

    @Value("${mqtt.broker}")
    private String broker;

    @Value("${mqtt.client-id}")
    private String clientId;

    @Value("${mqtt.topic}")
    private String topic;

    private final SseService sseService;

    public MqttSubscriber(SseService sseService) {
        this.sseService = sseService;
    }

    @PostConstruct
    public void subscribe() {
        try {
            MqttClient client = new MqttClient(broker, clientId);
            MqttConnectOptions options = new MqttConnectOptions();
            options.setAutomaticReconnect(true);
            client.connect(options);

            client.subscribe(topic, (t, message) -> {
                String payload = new String(message.getPayload());
                log.info("MQTT 수신 >> {}", payload);
                sseService.broadcast(payload);
            });

            log.info("MQTT 구독 시작: {} -> {}", broker, topic);
        } catch (Exception e) {
            log.error("MQTT 연결 실패: {}", e.getMessage());
        }
    }
}
