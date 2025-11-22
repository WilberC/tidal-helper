<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
    <p>Welcome!</p>
    <button @click="authStore.logout()" class="mt-4 bg-red-500 text-white px-4 py-2 rounded">
      Logout
    </button>
  </div>
</template>
