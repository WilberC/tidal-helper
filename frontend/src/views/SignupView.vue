<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const error = ref("");

const handleSignup = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match";
    return;
  }
  try {
    await authStore.signup({ email: email.value, password: password.value });
  } catch (e) {
    error.value = "Registration failed. User might already exist.";
  }
};
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 relative overflow-hidden"
  >
    <!-- Background Elements -->
    <div
      class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-tidal-cyan/10 rounded-full blur-[120px] pointer-events-none"
    ></div>

    <div class="max-w-md w-full space-y-8 relative z-10">
      <div class="text-center">
        <h2 class="text-4xl font-bold tracking-tight text-white mb-2">
          Create Account
        </h2>
        <p class="text-gray-400">Join the community today</p>
      </div>

      <div
        class="bg-tidal-surface backdrop-blur-xl rounded-2xl p-8 border border-white/10 shadow-2xl"
      >
        <form class="space-y-6" @submit.prevent="handleSignup">
          <div class="space-y-4">
            <div>
              <label
                for="email-address"
                class="block text-sm font-medium text-gray-300 mb-1"
                >Email address</label
              >
              <input
                id="email-address"
                name="email"
                type="email"
                autocomplete="email"
                required
                v-model="email"
                class="appearance-none block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-tidal-cyan/50 focus:border-transparent transition-all duration-200"
                placeholder="Enter your email"
              />
            </div>
            <div>
              <label
                for="password"
                class="block text-sm font-medium text-gray-300 mb-1"
                >Password</label
              >
              <input
                id="password"
                name="password"
                type="password"
                autocomplete="new-password"
                required
                v-model="password"
                class="appearance-none block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-tidal-cyan/50 focus:border-transparent transition-all duration-200"
                placeholder="Create a password"
              />
            </div>
            <div>
              <label
                for="confirm-password"
                class="block text-sm font-medium text-gray-300 mb-1"
                >Confirm Password</label
              >
              <input
                id="confirm-password"
                name="confirm-password"
                type="password"
                autocomplete="new-password"
                required
                v-model="confirmPassword"
                class="appearance-none block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-tidal-cyan/50 focus:border-transparent transition-all duration-200"
                placeholder="Confirm your password"
              />
            </div>
          </div>

          <div
            v-if="error"
            class="text-red-400 text-sm text-center bg-red-500/10 py-2 rounded-lg border border-red-500/20"
          >
            {{ error }}
          </div>

          <div>
            <button
              type="submit"
              class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-black bg-tidal-cyan hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-tidal-cyan transition-all duration-200 shadow-[0_0_20px_rgba(0,255,255,0.3)] hover:shadow-[0_0_30px_rgba(0,255,255,0.5)]"
            >
              Sign up
            </button>
          </div>

          <div class="text-center mt-6">
            <router-link
              to="/login"
              class="text-sm font-medium text-gray-400 hover:text-tidal-cyan transition-colors duration-200"
            >
              Already have an account?
              <span class="text-tidal-cyan">Sign in</span>
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
