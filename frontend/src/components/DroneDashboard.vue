<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'

interface Telemetry {
  drone_id: string
  server_ts: string
  drone_ts: string
  latitude: number
  longitude: number
  altitude: number
  speed: number
  battery: number
  heading: number
}

// SSE에서 수신한 전체 드론 데이터 (drone_id → 최신 텔레메트리)
const drones = ref<Map<string, Telemetry>>(new Map())
// 전체 로그
const logs = ref<string[]>([])
const connected = ref(false)
let eventSource: EventSource | null = null

// 연결된 드론 목록
const droneList = computed(() => {
  return Array.from(drones.value.values())
})

// 드론별 상태 컬러
const statusColor = (battery: number) => {
  if (battery > 60) return 'text-green-400'
  if (battery > 30) return 'text-yellow-400'
  return 'text-red-400'
}

onMounted(() => {
  eventSource = new EventSource('/api/telemetry/stream')
  eventSource.onopen = () => { connected.value = true }

  eventSource.addEventListener('telemetry', (e: MessageEvent) => {
    try {
      const data: Telemetry = JSON.parse(e.data)

      // 드론 데이터 업데이트
      drones.value.set(data.drone_id, data)

      // 로그 (테이블 형식)
      const row = `${data.server_ts} [${data.drone_id}] `
        + `lat=${data.latitude.toFixed(4)} lng=${data.longitude.toFixed(4)} `
        + `alt=${data.altitude.toFixed(1)}m `
        + `spd=${data.speed.toFixed(1)}m/s `
        + `batt=${data.battery.toFixed(0)}% `
        + `hdg=${data.heading}°`
      logs.value.push(row)
      if (logs.value.length > 100) logs.value.shift()

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

    <!-- 드론 상태 요약 -->
    <section class="px-6 py-3 border-b border-gray-700">
      <div class="flex gap-4">
        <div
          v-for="drone in droneList"
          :key="drone.drone_id"
          class="px-4 py-2 rounded-lg bg-gray-800 text-sm"
        >
          <span class="font-semibold">{{ drone.drone_id }}</span>
          <span :class="statusColor(drone.battery)" class="ml-2">
            {{ drone.battery.toFixed(0) }}%
          </span>
          <span class="text-gray-400 ml-2">
            {{ drone.altitude.toFixed(0) }}m / {{ drone.speed.toFixed(1) }}m/s
          </span>
        </div>
        <div v-if="droneList.length === 0" class="text-gray-500 text-sm italic">
          드론 데이터 수신 대기 중...
        </div>
      </div>
    </section>

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
        <p class="text-xs text-gray-500 mt-2">{{ logs.length }}건 수신 (드론 {{ droneList.length }}대)</p>
      </div>
    </main>
  </div>
</template>
