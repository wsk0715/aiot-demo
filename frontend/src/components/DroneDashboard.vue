<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

interface Telemetry {
  drone_id: string
  timestamp: string
  latitude: number
  longitude: number
  altitude: number
  speed: number
  battery: number
  heading: number
}

const logs = ref<string[]>([])
const connected = ref(false)
let eventSource: EventSource | null = null

onMounted(() => {
  eventSource = new EventSource('/api/telemetry/stream')
  eventSource.onopen = () => { connected.value = true }
  eventSource.addEventListener('telemetry', (e) => {
    try {
      const data: Telemetry = JSON.parse(e.data)
      const row = `${data.timestamp} [${data.drone_id}] `
        + `lat=${data.latitude.toFixed(4)} lng=${data.longitude.toFixed(4)} `
        + `alt=${data.altitude.toFixed(1)}m `
        + `spd=${data.speed.toFixed(1)}m/s `
        + `batt=${data.battery.toFixed(0)}% `
        + `hdg=${data.heading}°`
      logs.value.push(row)
      nextTick(() => {
        const el = document.getElementById('log-container')
        if (el) el.scrollTop = el.scrollHeight
      })
    } catch {}
  })
})

onUnmounted(() => {
  eventSource?.close()
  connected.value = false
})
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-900 text-gray-100">
    <header class="flex items-center justify-between px-6 py-3 border-b border-gray-700">
      <h1 class="text-lg font-bold tracking-wide">🛸 드론 관제 대시보드</h1>
      <span
        class="text-sm px-3 py-1 rounded-full"
        :class="connected ? 'bg-green-700 text-green-200' : 'bg-red-700 text-red-200'"
      >
        {{ connected ? '● 실시간 연결' : '○ 연결 끊김' }}
      </span>
    </header>

    <main class="flex-1 p-6 overflow-hidden">
      <div class="h-full flex flex-col">
        <h2 class="text-sm font-semibold text-gray-400 mb-2">텔레메트리 로그</h2>
        <div
          id="log-container"
          class="flex-1 overflow-y-auto bg-gray-950 rounded-lg p-4 font-mono text-sm leading-relaxed"
        >
          <div v-if="logs.length === 0" class="text-gray-500 italic">
            텔레메트리 수신 대기 중...
          </div>
          <div v-for="(line, i) in logs" :key="i" class="text-gray-300">
            {{ line }}
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">{{ logs.length }}건 수신</p>
      </div>
    </main>
  </div>
</template>
