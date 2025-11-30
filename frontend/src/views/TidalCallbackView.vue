<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gray-900 text-white"
  >
    <div class="text-center">
      <h2 class="text-2xl font-bold mb-4">Connecting to Tidal...</h2>
      <p v-if="error" class="text-red-500">{{ error }}</p>
      <p v-else>Please wait while we complete the authentication.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const error = ref("");

onMounted(async () => {
  const code = route.query.code as string;
  if (!code) {
    error.value = "No authorization code found.";
    return;
  }

  const codeVerifier = sessionStorage.getItem("tidal_code_verifier");
  if (!codeVerifier) {
    error.value = "No code verifier found. Please try connecting again.";
    return;
  }

  try {
    await authStore.handleTidalCallback(code, codeVerifier);
    sessionStorage.removeItem("tidal_code_verifier");
    router.push("/");
  } catch (e: any) {
    error.value = e.message || "Failed to connect to Tidal.";
  }
});
</script>
