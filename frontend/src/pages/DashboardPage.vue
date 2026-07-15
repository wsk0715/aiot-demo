<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useKakaoMap } from '../composables/useKakaoMap'

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

const drones = ref<Map<string, Telemetry>>(new Map())
const connected = ref(false)
const mapReady = ref(false)
const mapError = ref('')
let eventSource: EventSource | null = null

const droneList = ref<Telemetry[]>([])
const mapContainer = ref<HTMLElement | null>(null)

let kakaoMap: kakao.maps.Map | null = null
const markers = new Map<string, kakao.maps.Marker>()

onMounted(async () => {
  // Kakao Map init
  if (mapContainer.value) {
    try {
      const { createMap } = useKakaoMap()
      kakaoMap = await createMap(mapContainer.value, { lat: 37.5665, lng: 126.978 }, 7)
      kakaoMap.setMapTypeId(2) // 2 = SKYVIEW (위성사진)
      mapReady.value = true

      // 초기 마커는 드론 데이터 수신 후 생성
    } catch (e: any) {
      mapError.value = e.message ?? 'Kakao Map 초기화 실패'
    }
  }

  // SSE
  eventSource = new EventSource('/api/telemetry/stream')
  eventSource.onopen = () => { connected.value = true }

  eventSource.addEventListener('telemetry', (e: MessageEvent) => {
    try {
      const data: Telemetry = JSON.parse(e.data)
      drones.value.set(data.drone_id, data)
      droneList.value = Array.from(drones.value.values())
    } catch { /* ignore parse errors */ }
  })
})

// 드론 데이터 변경 시 마커 업데이트
watch(droneList, (list) => {
  if (!kakaoMap || !mapReady.value) return
  const { makeMarker, moveMarker } = useKakaoMap()

  const seen = new Set<string>()
  for (const d of list) {
    seen.add(d.drone_id)
    if (markers.has(d.drone_id)) {
      moveMarker(markers.get(d.drone_id)!, d.latitude, d.longitude)
    } else {
      const m = makeMarker(kakaoMap, { lat: d.latitude, lng: d.longitude }, d.drone_id)
      markers.set(d.drone_id, m)
    }
  }
  // 사라진 드론 마커 제거
  for (const [id, m] of markers) {
    if (!seen.has(id)) {
      m.setMap(null)
      markers.delete(id)
    }
  }
}, { deep: true })

onUnmounted(() => {
  eventSource?.close()
  connected.value = false
  for (const m of markers.values()) m.setMap(null)
  markers.clear()
})
</script>

<template>
  <div class="flex-1 flex flex-col min-h-0">
    <!-- Header -->
    <header class="h-16 flex items-center justify-between px-6 border-b border-gray-700 shrink-0">
      <h1 class="text-lg font-bold tracking-wide text-gray-100">Dashboard</h1>
      <span
        class="text-sm px-3 py-1 rounded-full"
        :class="connected ? 'bg-green-700 text-green-200' : 'bg-red-700 text-red-200'"
      >
        {{ connected ? '● Connected' : '○ Disconnected' }}
      </span>
    </header>

    <!-- Stats Cards -->
    <section class="h-20 flex items-center gap-4 px-6 border-b border-gray-700 shrink-0">
      <div class="flex-1 h-12 bg-gray-800 rounded-lg flex items-center px-4">
        <div class="flex items-center gap-3 w-full">
          <span class="text-lg">🚁</span>
          <div>
            <div class="text-xs text-gray-400">Active Drones</div>
            <div class="text-lg font-bold text-gray-100">{{ droneList.length }}</div>
          </div>
        </div>
      </div>
      <div class="flex-1 h-12 bg-gray-800 rounded-lg flex items-center px-4">
        <div class="flex items-center gap-3 w-full">
          <span class="text-lg">📡</span>
          <div>
            <div class="text-xs text-gray-400">Gateways</div>
            <div class="text-lg font-bold text-gray-100">1</div>
          </div>
        </div>
      </div>
      <div class="flex-1 h-12 bg-gray-800 rounded-lg flex items-center px-4">
        <div class="flex items-center gap-3 w-full">
          <span class="text-lg">📹</span>
          <div>
            <div class="text-xs text-gray-400">Streaming</div>
            <div class="text-lg font-bold text-gray-100">{{ connected ? droneList.length : 0 }}</div>
          </div>
        </div>
      </div>
      <div class="flex-1 h-12 bg-gray-800 rounded-lg flex items-center px-4">
        <div class="flex items-center gap-3 w-full">
          <span class="text-lg">⚠️</span>
          <div>
            <div class="text-xs text-gray-400">Alerts</div>
            <div class="text-lg font-bold text-yellow-400">0</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Content Grid (50/50) -->
    <section class="flex-1 flex gap-4 p-4 min-h-0">
      <!-- Left: Kakao Map -->
      <div ref="mapContainer" class="flex-1 bg-gray-800 rounded-lg border border-gray-700 relative overflow-hidden">
        <div v-if="mapError" class="absolute inset-0 flex items-center justify-center text-red-400 text-sm z-10 bg-gray-800/80">
          ⚠️ {{ mapError }}
          <br>
          <span class="text-gray-500 text-xs mt-1">VITE_KAKAO_MAP_KEY 환경변수를 설정하세요</span>
        </div>
        <div v-if="!mapReady && !mapError" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm z-10">
          🗺️ 지도 로딩 중...
        </div>
      </div>

      <!-- Right: Monitoring -->
      <div class="flex-1 flex flex-col gap-4 min-h-0">
        <!-- Camera Grid (4x4) -->
        <div class="flex-1 bg-gray-800 rounded-lg border border-gray-700 p-2 flex flex-col">
          <div class="text-xs text-gray-400 mb-2 px-1">Camera Feed</div>
          <div class="flex-1 grid grid-cols-4 grid-rows-4 gap-1.5">
            <div
              v-for="i in 16"
              :key="i"
              class="bg-gray-900 rounded border border-gray-700 flex items-center justify-center text-xs text-gray-600 relative overflow-hidden"
              :class="{ 'ring-1 ring-cyan-500/50': i === 1 }"
            >
              <!-- X-cross wireframe -->
              <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 75">
                <line x1="0" y1="0" x2="100" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/>
                <line x1="100" y1="0" x2="0" y2="75" stroke="currentColor" stroke-width="0.3" class="text-gray-700"/>
              </svg>
              <span class="relative z-10">Cam {{ i }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
