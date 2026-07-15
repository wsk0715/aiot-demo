<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Plane, Satellite, Search, Plus, X, Wifi, WifiOff, Gauge, Cpu } from '@lucide/vue'

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

interface DroneDevice {
  id: string
  name: string
  model: string
  gateway: string
  battery: number
  status: 'FLYING' | 'LANDING' | 'IDLE' | 'CHARGING' | 'OFFLINE'
  lat: number
  lng: number
  updatedAt: string
}

interface GatewayDevice {
  id: string
  name: string
  gpu: number
  cpu: number
  memory: number
  connectedDrones: string[]
  network: 'ONLINE' | 'OFFLINE' | 'DEGRADED'
  lat: number
  lng: number
  location: string
}

type Tab = 'drones' | 'gateways'

const activeTab = ref<Tab>('drones')
const searchQuery = ref('')
const selectedDevice = ref<DroneDevice | GatewayDevice | null>(null)
const connected = ref(false)
let eventSource: EventSource | null = null

const telemetryMap = ref<Map<string, Telemetry>>(new Map())

const gateways: GatewayDevice[] = [
  {
    id: 'ORIN-001',
    name: 'Jetson Orin NX',
    gpu: 67, cpu: 34, memory: 58,
    connectedDrones: ['DRONE-001', 'DRONE-002', 'DRONE-003', 'DRONE-004'],
    network: 'ONLINE', lat: 37.57, lng: 126.98,
    location: '서울특별시 중구',
  },
]

const drones = computed<DroneDevice[]>(() => {
  return Array.from(telemetryMap.value.values()).map((t) => ({
    id: t.drone_id,
    name: t.drone_id,
    model: 'PX4 SITL gz_x500',
    gateway: 'ORIN-001',
    battery: t.battery,
    status: t.battery <= 0 ? 'LANDING' : 'FLYING' as const,
    lat: t.latitude,
    lng: t.longitude,
    updatedAt: t.drone_ts,
  }))
})

const filteredItems = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (activeTab.value === 'drones') {
    return drones.value.filter((d) => d.id.toLowerCase().includes(q))
  }
  return gateways.filter((g) => g.id.toLowerCase().includes(q) || g.name.toLowerCase().includes(q))
})

function statusLabel(status: string) {
  const map: Record<string, string> = {
    FLYING: '비행중', LANDING: '착륙', IDLE: '대기',
    CHARGING: '충전중', OFFLINE: '오프라인',
  }
  return map[status] ?? status
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    FLYING: 'text-green-400', LANDING: 'text-yellow-400',
    IDLE: 'text-gray-400', CHARGING: 'text-cyan-400',
    OFFLINE: 'text-red-400',
  }
  return map[status] ?? 'text-gray-400'
}

function networkIcon(network: string) {
  if (network === 'ONLINE') return Wifi
  if (network === 'DEGRADED') return Wifi
  return WifiOff
}

function networkColor(network: string) {
  return network === 'ONLINE' ? 'text-green-400'
    : network === 'DEGRADED' ? 'text-yellow-400'
    : 'text-red-400'
}

function batteryColor(battery: number) {
  return battery > 60 ? 'text-green-400' : battery > 30 ? 'text-yellow-400' : 'text-red-400'
}

function selectDevice(d: DroneDevice | GatewayDevice) {
  selectedDevice.value = selectedDevice.value?.id === d.id ? null : d
}

onMounted(() => {
  eventSource = new EventSource('/api/telemetry/stream')
  eventSource.onopen = () => { connected.value = true }
  eventSource.addEventListener('telemetry', (e: MessageEvent) => {
    try {
      const data: Telemetry = JSON.parse(e.data)
      telemetryMap.value.set(data.drone_id, data)
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
      <h1 class="text-lg font-bold tracking-wide text-gray-100">Devices</h1>
      <div class="flex items-center gap-3">
        <span
          class="text-xs px-2 py-0.5 rounded-full"
          :class="connected ? 'bg-green-700 text-green-200' : 'bg-red-700 text-red-200'"
        >
          {{ connected ? '● Live' : '○ Offline' }}
        </span>
        <button class="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 rounded-lg text-xs text-white font-medium transition-colors">
          <Plus class="w-3.5 h-3.5" />
          Add Device
        </button>
      </div>
    </div>

    <!-- Search + Tab -->
    <div class="flex items-center gap-4 px-6 py-3 border-b border-gray-700 shrink-0">
      <!-- Search -->
      <div class="relative flex-1 max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search devices..."
          class="w-full h-9 pl-9 pr-3 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 placeholder-gray-500 outline-none focus:border-cyan-600 transition-colors"
        />
      </div>
      <!-- Tabs -->
      <div class="flex gap-1 bg-gray-800 rounded-lg p-1">
        <button
          @click="activeTab = 'drones'"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
          :class="activeTab === 'drones' ? 'bg-cyan-600/20 text-cyan-300' : 'text-gray-400 hover:text-gray-200'"
        >
          <Plane class="w-3.5 h-3.5" />
          Drones ({{ drones.length }})
        </button>
        <button
          @click="activeTab = 'gateways'"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
          :class="activeTab === 'gateways' ? 'bg-cyan-600/20 text-cyan-300' : 'text-gray-400 hover:text-gray-200'"
        >
          <Satellite class="w-3.5 h-3.5" />
          Gateways ({{ gateways.length }})
        </button>
      </div>
    </div>

    <!-- Content + Detail panel -->
    <div class="flex-1 flex min-h-0">
      <!-- Device list -->
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="filteredItems.length === 0" class="flex items-center justify-center h-full text-gray-500 text-sm">
          No devices found.
        </div>
        <!-- Drone cards -->
        <div v-if="activeTab === 'drones'" class="space-y-2">
          <div
            v-for="d in (filteredItems as DroneDevice[])"
            :key="d.id"
            @click="selectDevice(d)"
            class="flex items-center gap-4 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600"
            :class="{ 'border-cyan-600/50': selectedDevice?.id === d.id }"
          >
            <Plane class="w-5 h-5 text-gray-400 shrink-0" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-gray-100">{{ d.id }}</span>
                <span class="text-xs text-gray-500">{{ d.model }}</span>
              </div>
              <div class="flex items-center gap-3 mt-1 text-xs text-gray-400">
                <span>🔗 {{ d.gateway }}</span>
                <span>{{ d.lat.toFixed(4) }}, {{ d.lng.toFixed(4) }}</span>
              </div>
            </div>
            <div class="text-right shrink-0">
              <div class="text-sm font-bold" :class="batteryColor(d.battery)">{{ d.battery.toFixed(0) }}%</div>
              <div class="text-xs" :class="statusColor(d.status)">{{ statusLabel(d.status) }}</div>
            </div>
          </div>
        </div>
        <!-- Gateway cards -->
        <div v-else class="space-y-2">
          <div
            v-for="g in (filteredItems as GatewayDevice[])"
            :key="g.id"
            @click="selectDevice(g)"
            class="flex items-center gap-4 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer transition-colors hover:border-gray-600"
            :class="{ 'border-cyan-600/50': selectedDevice?.id === g.id }"
          >
            <Satellite class="w-5 h-5 text-gray-400 shrink-0" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-gray-100">{{ g.id }}</span>
                <span class="text-xs text-gray-500">{{ g.name }}</span>
              </div>
              <div class="flex items-center gap-3 mt-1 text-xs text-gray-400">
                <span>📌 {{ g.location }}</span>
                <span>🚁 {{ g.connectedDrones.length }} connected</span>
              </div>
            </div>
            <div class="text-right shrink-0 space-y-0.5">
              <div class="flex items-center gap-1 justify-end text-xs">
                <Cpu class="w-3 h-3" />
                <span>{{ g.cpu }}%</span>
                <Gauge class="w-3 h-3 ml-1" />
                <span>{{ g.gpu }}%</span>
              </div>
              <div class="flex items-center gap-1 justify-end text-xs" :class="networkColor(g.network)">
                <component :is="networkIcon(g.network)" class="w-3 h-3" />
                {{ g.network }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detail panel (right drawer) -->
      <Transition name="slide">
        <div
          v-if="selectedDevice"
          class="w-80 border-l border-gray-700 bg-gray-850 overflow-y-auto shrink-0"
        >
          <div class="h-full flex flex-col">
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700">
              <h3 class="text-sm font-semibold text-gray-100">{{ selectedDevice.id }}</h3>
              <button @click="selectedDevice = null" class="text-gray-500 hover:text-gray-300 transition-colors">
                <X class="w-4 h-4" />
              </button>
            </div>
            <div class="flex-1 px-5 py-4 text-xs space-y-4">
              <!-- Drone detail -->
              <template v-if="'status' in selectedDevice">
                <div class="space-y-3">
                  <div class="flex justify-between"><span class="text-gray-500">Model</span><span class="text-gray-200">{{ (selectedDevice as DroneDevice).model }}</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Gateway</span><span class="text-gray-200">{{ (selectedDevice as DroneDevice).gateway }}</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Battery</span><span class="text-gray-200" :class="batteryColor((selectedDevice as DroneDevice).battery)">{{ (selectedDevice as DroneDevice).battery.toFixed(0) }}%</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Status</span><span class="text-gray-200" :class="statusColor((selectedDevice as DroneDevice).status)">{{ statusLabel((selectedDevice as DroneDevice).status) }}</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Latitude</span><span class="text-gray-200">{{ (selectedDevice as DroneDevice).lat.toFixed(6) }}</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Longitude</span><span class="text-gray-200">{{ (selectedDevice as DroneDevice).lng.toFixed(6) }}</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Updated</span><span class="text-gray-200">{{ (selectedDevice as DroneDevice).updatedAt }}</span></div>
                </div>
              </template>
              <!-- Gateway detail -->
              <template v-else>
                <div class="space-y-3">
                  <div class="flex justify-between"><span class="text-gray-500">Name</span><span class="text-gray-200">{{ (selectedDevice as GatewayDevice).name }}</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">GPU Usage</span><span class="text-gray-200">{{ (selectedDevice as GatewayDevice).gpu }}%</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">CPU Usage</span><span class="text-gray-200">{{ (selectedDevice as GatewayDevice).cpu }}%</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Memory</span><span class="text-gray-200">{{ (selectedDevice as GatewayDevice).memory }}%</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Network</span><span class="text-gray-200" :class="networkColor((selectedDevice as GatewayDevice).network)">{{ (selectedDevice as GatewayDevice).network }}</span></div>
                  <div class="flex justify-between"><span class="text-gray-500">Location</span><span class="text-gray-200">{{ (selectedDevice as GatewayDevice).location }}</span></div>
                  <div>
                    <span class="text-gray-500 block mb-1">Connected Drones</span>
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="droneId in (selectedDevice as GatewayDevice).connectedDrones"
                        :key="droneId"
                        class="px-2 py-0.5 bg-gray-800 rounded text-gray-300 text-xs"
                      >{{ droneId }}</span>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: width 0.2s ease, opacity 0.2s ease;
}
.slide-enter-from, .slide-leave-to {
  width: 0 !important;
  opacity: 0;
  overflow: hidden;
}
</style>
