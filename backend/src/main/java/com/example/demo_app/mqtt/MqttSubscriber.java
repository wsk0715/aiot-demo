package com.example.demo_app.mqtt;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;

@Service
public class MqttSubscriber {

    private static final Logger log = LoggerFactory.getLogger(MqttSubscriber.class);

    @Value("${mqtt.broker}")
    private String broker;

    @Value("${mqtt.client-id}")
    private String clientId;

    @Value("${mqtt.topic}")
    private String topic;

    @PostConstruct
    public void subscribe() {
        try {
            MqttClient client = new MqttClient(broker, clientId);
            MqttConnectOptions options = new MqttConnectOptions();
            options.setAutomaticReconnect(true);
            client.connect(options);

            client.subscribe(topic, (t, message) ->
                log.info("MQTT 수신 >> {}", new String(message.getPayload()))
            );

            log.info("MQTT 구독 시작: {} -> {}", broker, topic);
        } catch (Exception e) {
            log.error("MQTT 연결 실패: {}", e.getMessage());
        }
    }
}
