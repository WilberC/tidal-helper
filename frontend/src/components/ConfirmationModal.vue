<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/80 backdrop-blur-sm"
          @click="$emit('cancel')"
        ></div>

        <!-- Modal Content -->
        <div
          class="relative bg-[#111111] border border-white/10 rounded-xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all"
        >
          <div class="p-6">
            <h3 class="text-xl font-bold text-white mb-2">{{ title }}</h3>
            <p class="text-gray-400">{{ message }}</p>
          </div>

          <div class="px-6 py-4 bg-white/5 flex justify-end gap-3">
            <button
              @click="$emit('cancel')"
              class="px-4 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="$emit('confirm')"
              class="px-4 py-2 rounded-lg text-sm font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  isOpen: boolean;
  title: string;
  message: string;
}>();

defineEmits(["confirm", "cancel"]);
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .transform,
.modal-leave-active .transform {
  transition: all 0.2s ease;
}

.modal-enter-from .transform,
.modal-leave-to .transform {
  opacity: 0;
  transform: scale(0.95);
}
</style>
