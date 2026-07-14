package com.example.demo_app.mqtt;

import java.io.IOException;
import java.util.concurrent.CopyOnWriteArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Service
public class SseService {

    private static final Logger log = LoggerFactory.getLogger(SseService.class);
    private final CopyOnWriteArrayList<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    public SseEmitter subscribe() {
        SseEmitter emitter = new SseEmitter(1800_000L); // 30분 타임아웃
        emitter.onCompletion(() -> remove(emitter));
        emitter.onTimeout(() -> remove(emitter));
        emitter.onError(e -> remove(emitter));
        emitters.add(emitter);
        log.info("SSE 클라이언트 연결 (총 {}개)", emitters.size());
        return emitter;
    }

    public void broadcast(String payload) {
        for (var it = emitters.iterator(); it.hasNext();) {
            SseEmitter emitter = it.next();
            try {
                emitter.send(SseEmitter.event().name("telemetry").data(payload));
            } catch (IOException e) {
                it.remove();
                log.info("SSE 클라이언트 연결 종료 (총 {}개)", emitters.size());
            }
        }
    }

    private void remove(SseEmitter emitter) {
        emitters.remove(emitter);
        log.info("SSE 클라이언트 제거 (총 {}개)", emitters.size());
    }
}
