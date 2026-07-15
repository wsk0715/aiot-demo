<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useKakaoMap } from '../composables/useKakaoMap'
import { Plane, Satellite, Camera, TriangleAlert, Plus, Minus, Map as MapIcon, Crosshair } from '@lucide/vue'

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
const mapType = ref(2) // 2=SKYVIEW | 1=ROADMAP
const currentLevel = ref(8)
let eventSource: EventSource | null = null

const droneList = ref<Telemetry[]>([])
const mapContainer = ref<HTMLElement | null>(null)

let kakaoMap: kakao.maps.Map | null = null
const markers = new Map<string, kakao.maps.Marker>()

onMounted(async () => {
  if (mapContainer.value) {
    try {
      const { createMap } = useKakaoMap()
      kakaoMap = await createMap(mapContainer.value, { lat: 37.5665, lng: 126.978 }, currentLevel.value)
      kakaoMap.setMapTypeId(2)
      currentLevel.value = kakaoMap.getLevel()
      mapReady.value = true
    } catch (e: any) {
      mapError.value = e.message ?? 'Kakao Map 초기화 실패'
    }
  }

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
  for (const [id, m] of markers) {
    if (!seen.has(id)) {
      m.setMap(null)
      markers.delete(id)
    }
  }
}, { deep: true })

function zoomIn() {
  if (!kakaoMap) return
  const level = kakaoMap.getLevel()
  if (level > 1) {
    kakaoMap.setLevel(level - 1)
    currentLevel.value = level - 1
  }
}

function zoomOut() {
  if (!kakaoMap) return
  const level = kakaoMap.getLevel()
  if (level < 13) {
    kakaoMap.setLevel(level + 1)
    currentLevel.value = level + 1
  }
}

function toggleMapType() {
  if (!kakaoMap) return
  const next = mapType.value === 1 ? 2 : 1
  kakaoMap.setMapTypeId(next)
  mapType.value = next
}

function goToCurrentLocation() {
  if (!navigator.geolocation) return
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      if (!kakaoMap) return
      const latlng = new window.kakao.maps.LatLng(pos.coords.latitude, pos.coords.longitude)
      kakaoMap.setCenter(latlng)
      kakaoMap.setLevel(5)
      currentLevel.value = 5
    },
    () => {
      alert('현재 위치를 가져올 수 없습니다. 위치 권한을 확인하세요.')
    },
    { enableHighAccuracy: true, timeout: 5000 },
  )
}

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
          <Plane class="w-5 h-5 text-cyan-400 shrink-0" />
          <div>
            <div class="text-xs text-gray-400">Active Drones</div>
            <div class="text-lg font-bold text-gray-100">{{ droneList.length }}</div>
          </div>
        </div>
      </div>
      <div class="flex-1 h-12 bg-gray-800 rounded-lg flex items-center px-4">
        <div class="flex items-center gap-3 w-full">
          <Satellite class="w-5 h-5 text-gray-400 shrink-0" />
          <div>
            <div class="text-xs text-gray-400">Gateways</div>
            <div class="text-lg font-bold text-gray-100">1</div>
          </div>
        </div>
      </div>
      <div class="flex-1 h-12 bg-gray-800 rounded-lg flex items-center px-4">
        <div class="flex items-center gap-3 w-full">
          <Camera class="w-5 h-5 text-gray-400 shrink-0" />
          <div>
            <div class="text-xs text-gray-400">Streaming</div>
            <div class="text-lg font-bold text-gray-100">{{ connected ? droneList.length : 0 }}</div>
          </div>
        </div>
      </div>
      <div class="flex-1 h-12 bg-gray-800 rounded-lg flex items-center px-4">
        <div class="flex items-center gap-3 w-full">
          <TriangleAlert class="w-5 h-5 text-yellow-500 shrink-0" />
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
        <!-- Loading / Error overlay -->
        <div v-if="mapError" class="absolute inset-0 flex items-center justify-center text-red-400 text-sm z-20 bg-gray-800/80">
          ⚠️ {{ mapError }}
          <br>
          <span class="text-gray-500 text-xs mt-1">VITE_KAKAO_MAP_KEY 환경변수를 설정하세요</span>
        </div>
        <div v-if="!mapReady && !mapError" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm z-20">
          🗺️ 지도 로딩 중...
        </div>

        <!-- Map controls (top-right) -->
        <div v-if="mapReady" class="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
          <!-- Map type toggle -->
          <button
            @click="toggleMapType"
            title="지도 형식 전환"
            class="w-9 h-9 bg-gray-900/80 hover:bg-gray-900 rounded-lg border border-gray-600 flex items-center justify-center text-xs text-gray-300 transition-colors"
          >
            <MapIcon v-if="mapType === 1" class="w-4 h-4" />
            <Satellite v-else class="w-4 h-4" />
          </button>
          <!-- Current location -->
          <button
            @click="goToCurrentLocation"
            title="내 위치"
            class="w-9 h-9 bg-gray-900/80 hover:bg-gray-900 rounded-lg border border-gray-600 flex items-center justify-center text-xs text-gray-300 transition-colors"
          >
            <Crosshair class="w-4 h-4" />
          </button>
        </div>

        <!-- Zoom controls (bottom-right) -->
        <div v-if="mapReady" class="absolute bottom-3 right-3 z-10 flex flex-col gap-px rounded-lg overflow-hidden shadow-lg">
          <button
            @click="zoomIn"
            title="확대"
            class="w-9 h-9 bg-gray-900/90 hover:bg-gray-700 flex items-center justify-center text-sm text-gray-200 transition-colors border-b border-gray-700"
          >
            <Plus class="w-4 h-4" />
          </button>
          <button
            @click="zoomOut"
            title="축소"
            class="w-9 h-9 bg-gray-900/90 hover:bg-gray-700 flex items-center justify-center text-sm text-gray-200 transition-colors"
          >
            <Minus class="w-4 h-4" />
          </button>
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
