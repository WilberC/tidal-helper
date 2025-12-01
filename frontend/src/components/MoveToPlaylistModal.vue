<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/75" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div
          class="flex min-h-full items-center justify-center p-4 text-center"
        >
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              class="w-full max-w-md transform overflow-hidden rounded-2xl bg-gray-900 border border-white/10 p-6 text-left align-middle shadow-xl transition-all"
            >
              <DialogTitle
                as="h3"
                class="text-lg font-medium leading-6 text-white mb-4"
              >
                Move to Playlist
              </DialogTitle>

              <div class="mt-2">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search playlists..."
                  class="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 transition-colors mb-4"
                  autofocus
                />

                <div
                  class="max-h-60 overflow-y-auto custom-scrollbar space-y-1"
                >
                  <div
                    v-for="playlist in filteredPlaylists"
                    :key="playlist.id"
                    @click="selectPlaylist(playlist)"
                    class="px-3 py-2 rounded-lg cursor-pointer transition-colors flex justify-between items-center"
                    :class="
                      selectedPlaylist?.id === playlist.id
                        ? 'bg-cyan-500/20 text-cyan-400'
                        : 'hover:bg-white/5 text-gray-300'
                    "
                  >
                    <span class="truncate">{{ playlist.name }}</span>
                    <span
                      class="text-xs opacity-50 ml-2"
                      v-if="playlist.tidal_id"
                    >
                      {{ playlist.tidal_id }}
                    </span>
                  </div>
                  <div
                    v-if="filteredPlaylists.length === 0"
                    class="text-center text-gray-500 py-4"
                  >
                    No playlists found
                  </div>
                </div>
              </div>

              <div class="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  class="inline-flex justify-center rounded-lg px-4 py-2 text-sm font-medium text-gray-300 hover:bg-white/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75 transition-colors"
                  @click="closeModal"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  class="inline-flex justify-center rounded-lg border border-transparent bg-cyan-500/20 px-4 py-2 text-sm font-medium text-cyan-400 hover:bg-cyan-500/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!selectedPlaylist"
                  @click="confirmMove"
                >
                  Move
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from "@headlessui/vue";

interface Playlist {
  id: number;
  name: string;
  tidal_id?: string;
}

const props = defineProps<{
  isOpen: boolean;
  playlists: Playlist[];
  currentPlaylistId?: number;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "move", targetPlaylistId: number): void;
}>();

const searchQuery = ref("");
const selectedPlaylist = ref<Playlist | null>(null);

const filteredPlaylists = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return props.playlists
    .filter((p) => p.id !== props.currentPlaylistId) // Exclude current playlist
    .filter(
      (p) =>
        p.name.toLowerCase().includes(query) ||
        (p.tidal_id && p.tidal_id.toLowerCase().includes(query))
    );
});

const selectPlaylist = (playlist: Playlist) => {
  selectedPlaylist.value = playlist;
};

const closeModal = () => {
  emit("close");
  searchQuery.value = "";
  selectedPlaylist.value = null;
};

const confirmMove = () => {
  if (selectedPlaylist.value) {
    emit("move", selectedPlaylist.value.id);
    closeModal();
  }
};

// Reset selection when modal opens
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      searchQuery.value = "";
      selectedPlaylist.value = null;
    }
  }
);
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
