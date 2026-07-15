<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/devices', label: 'Devices', icon: '🚁' },
  { path: '/telemetry', label: 'Telemetry', icon: '📈' },
  { path: '/settings', label: 'Settings', icon: '⚙️' },
]

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path)
}
</script>

<template>
  <aside class="w-60 h-screen bg-gray-800 border-r border-gray-700 flex flex-col shrink-0">
    <!-- Logo -->
    <div class="h-16 flex items-center px-5 border-b border-gray-700">
      <span class="text-lg font-bold tracking-wide text-gray-100">
        <span class="text-cyan-400">AIoT</span> Drone
      </span>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-3 py-4 space-y-1">
      <button
        v-for="item in navItems"
        :key="item.path"
        @click="router.push(item.path)"
        class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
        :class="isActive(item.path)
          ? 'bg-cyan-600/20 text-cyan-300'
          : 'text-gray-400 hover:bg-gray-700/50 hover:text-gray-200'"
      >
        <span class="text-base">{{ item.icon }}</span>
        {{ item.label }}
      </button>
    </nav>

    <!-- Footer -->
    <div class="px-5 py-3 border-t border-gray-700 text-xs text-gray-500">
      v0.1.0 · AIoT Platform
    </div>
  </aside>
</template>
