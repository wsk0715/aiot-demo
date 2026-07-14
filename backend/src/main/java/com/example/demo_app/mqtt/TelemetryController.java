package com.example.demo_app.mqtt;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/telemetry")
public class TelemetryController {

    private final SseService sseService;

    public TelemetryController(SseService sseService) {
        this.sseService = sseService;
    }

    @GetMapping("/stream")
    public SseEmitter stream() {
        return sseService.subscribe();
    }
}
