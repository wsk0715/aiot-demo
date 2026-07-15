<script setup lang="ts">
import { RouterView } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
</script>

<template>
  <div class="h-screen flex bg-gray-900 text-gray-100 overflow-hidden">
    <Sidebar />
    <RouterView />
  </div>
</template>
