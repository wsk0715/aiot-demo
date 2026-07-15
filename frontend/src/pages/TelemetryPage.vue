<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown } from '@lucide/vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

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

// ---------- state ----------
const MAX_HISTORY = 1800 // 30분치 (1초 간격)
const history = ref<Map<string, Telemetry[]>>(new Map())
const droneIds = ref<string[]>([])
const selectedDrone = ref('')
const timeRange = ref<'realtime' | '1h' | '6h' | '24h'>('realtime')
const connected = ref(false)
let eventSource: EventSource | null = null

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 300 },
  scales: {
    x: {
      display: true,
      ticks: { color: '#6b7280', maxTicksLimit: 8, font: { size: 10 } },
      grid: { color: '#374151' },
    },
    y: {
      display: true,
      ticks: { color: '#6b7280', font: { size: 10 } },
      grid: { color: '#374151' },
      beginAtZero: true,
    },
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1f2937',
      titleColor: '#e5e7eb',
      bodyColor: '#9ca3af',
      borderColor: '#374151',
      borderWidth: 1,
    },
  },
}

function makeChartData(values: number[], color: string, fillColor: string) {
  return {
    labels: values.map(() => ''),
    datasets: [
      {
        data: values,
        borderColor: color,
        backgroundColor: fillColor,
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.3,
      },
    ],
  }
}

// 접속자 수 기준으로 표시할 텔레메트리 수 계산
const maxPoints = computed(() => {
  switch (timeRange.value) {
    case 'realtime': return 60
    case '1h': return 3600
    case '6h': return 720
    case '24h': return 1440
    default: return 60
  }
})

const droneHistory = computed(() => {
  if (!selectedDrone.value) return [] as Telemetry[]
  const h = history.value.get(selectedDrone.value)
  if (!h) return []
  const n = maxPoints.value
  return h.slice(-n)
})

const altitudeData = computed(() => makeChartData(
  droneHistory.value.map((t) => t.altitude), '#22d3ee', 'rgba(34,211,238,0.08)',
))
const speedData = computed(() => makeChartData(
  droneHistory.value.map((t) => t.speed), '#34d399', 'rgba(52,211,153,0.08)',
))
const batteryData = computed(() => makeChartData(
  droneHistory.value.map((t) => t.battery), '#fbbf24', 'rgba(251,191,36,0.08)',
))
const headingData = computed(() => makeChartData(
  droneHistory.value.map((t) => t.heading), '#f472b6', 'rgba(244,114,182,0.08)',
))

const timeRanges = [
  { key: 'realtime' as const, label: 'Real-time' },
  { key: '1h' as const, label: '1h' },
  { key: '6h' as const, label: '6h' },
  { key: '24h' as const, label: '24h' },
]

const telemetryColumns = ['Time', 'Alt', 'Speed', 'Batt', 'Heading', 'Lat', 'Lng']
const telemetryRows = computed(() => droneHistory.value.slice(-20).reverse())

// ---------- SSE ----------
onMounted(() => {
  eventSource = new EventSource('/api/telemetry/stream')
  eventSource.onopen = () => { connected.value = true }

  eventSource.addEventListener('telemetry', (e: MessageEvent) => {
    try {
      const data: Telemetry = JSON.parse(e.data)
      const h = history.value.get(data.drone_id) ?? []
      h.push(data)
      if (h.length > MAX_HISTORY) h.splice(0, h.length - MAX_HISTORY)
      history.value.set(data.drone_id, h)
      // 첫 수신 시 드론 목록 갱신 + 첫 드론 자동 선택
      if (!droneIds.value.includes(data.drone_id)) {
        droneIds.value.push(data.drone_id)
        if (!selectedDrone.value) selectedDrone.value = data.drone_id
      }
    } catch { /* ignore */ }
  })
})

onUnmounted(() => {
  eventSource?.close()
  connected.value = false
})
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <!-- Header -->
    <div class="h-16 flex items-center justify-between px-6 border-b border-gray-700 shrink-0">
      <h1 class="text-lg font-bold tracking-wide text-gray-100">Telemetry</h1>
      <span
        class="text-xs px-2 py-0.5 rounded-full"
        :class="connected ? 'bg-green-700 text-green-200' : 'bg-red-700 text-red-200'"
      >
        {{ connected ? '● Live' : '○ Offline' }}
      </span>
    </div>

    <!-- Controls: drone selector + time range -->
    <div class="flex items-center gap-4 px-6 py-3 border-b border-gray-700 shrink-0">
      <!-- Drone dropdown -->
      <div class="relative">
        <select
          v-model="selectedDrone"
          class="appearance-none h-9 pl-3 pr-8 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 outline-none focus:border-cyan-600 transition-colors cursor-pointer"
        >
          <option v-for="id in droneIds" :key="id" :value="id">{{ id }}</option>
        </select>
        <ChevronDown class="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
      </div>

      <!-- Time range -->
      <div class="flex gap-1 bg-gray-800 rounded-lg p-1">
        <button
          v-for="r in timeRanges"
          :key="r.key"
          @click="timeRange = r.key"
          class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
          :class="timeRange === r.key ? 'bg-cyan-600/20 text-cyan-300' : 'text-gray-400 hover:text-gray-200'"
        >
          {{ r.label }}
        </button>
      </div>

      <div class="text-xs text-gray-600 ml-auto">
        {{ droneHistory.length }} samples
      </div>
    </div>

    <!-- Chart grid (2x2) -->
    <div class="flex-1 grid grid-cols-2 grid-rows-2 gap-4 p-4 min-h-0">
      <div v-for="(item, idx) in [
        { title: 'Altitude (m)', data: altitudeData, icon: '🔺' },
        { title: 'Speed (m/s)', data: speedData, icon: '💨' },
        { title: 'Battery (%)', data: batteryData, icon: '🔋' },
        { title: 'Heading (°)', data: headingData, icon: '🧭' },
      ]" :key="idx" class="bg-gray-800 rounded-lg border border-gray-700 p-3 flex flex-col">
        <div class="text-xs text-gray-400 mb-1.5">{{ item.icon }} {{ item.title }}</div>
        <div class="flex-1 min-h-0">
          <Line v-if="(item.data as any).datasets[0].data.length > 1" :data="item.data as any" :options="chartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-600 text-xs">Waiting for data...</div>
        </div>
      </div>
    </div>

    <!-- Telemetry table -->
    <div class="max-h-72 border-t border-gray-700 overflow-y-auto shrink-0">
      <table class="w-full text-xs">
        <thead class="sticky top-0 bg-gray-800">
          <tr class="text-gray-400 border-b border-gray-700">
            <th v-for="col in telemetryColumns" :key="col" class="text-left px-4 py-2 font-medium">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in telemetryRows" :key="i" class="border-b border-gray-800/50" :class="i % 2 === 0 ? 'bg-gray-850/30' : 'bg-gray-900/30'">
            <td class="px-4 py-1.5 text-gray-400 font-mono">{{ row.drone_ts.slice(11, 19) }}</td>
            <td class="px-4 py-1.5 text-gray-200 font-mono">{{ row.altitude.toFixed(1) }}</td>
            <td class="px-4 py-1.5 text-gray-200 font-mono">{{ row.speed.toFixed(1) }}</td>
            <td class="px-4 py-1.5 font-mono" :class="row.battery > 60 ? 'text-green-400' : row.battery > 30 ? 'text-yellow-400' : 'text-red-400'">{{ row.battery.toFixed(0) }}</td>
            <td class="px-4 py-1.5 text-gray-200 font-mono">{{ row.heading }}°</td>
            <td class="px-4 py-1.5 text-gray-400 font-mono">{{ row.latitude.toFixed(4) }}</td>
            <td class="px-4 py-1.5 text-gray-400 font-mono">{{ row.longitude.toFixed(4) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
/* Tailwind v4 gray-850 fallback */
.bg-gray-850\/30 { background-color: rgba(30, 41, 59, 0.3); }
</style>
