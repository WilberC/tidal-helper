<template>
  <div class="p-6 h-full flex flex-col">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-white">Quick Edit Playlists</h1>
      <router-link
        to="/"
        class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors"
      >
        Back to Dashboard
      </router-link>
    </div>

    <div v-if="loading" class="flex-1 flex justify-center items-center">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"
      ></div>
    </div>

    <div v-else-if="error" class="text-red-400 text-center py-8">
      {{ error }}
    </div>

    <div
      v-else
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 flex-1 overflow-y-auto pb-6"
    >
      <div
        v-for="playlist in playlists"
        :key="playlist.id"
        class="bg-white/5 border border-white/10 rounded-xl flex flex-col h-[500px] overflow-hidden"
        @dragover.prevent
        @drop="onDrop($event, playlist.id)"
      >
        <!-- Header -->
        <div class="p-4 border-b border-white/10 bg-white/5">
          <div class="flex justify-between items-start mb-2">
            <h3
              class="font-bold text-lg truncate flex-1 mr-2"
              :title="playlist.name"
            >
              {{ playlist.name }}
            </h3>
          </div>
          <div class="flex justify-between items-end text-xs text-gray-400">
            <p>
              {{ playlist.songs?.length || 0 }} songs
              <span v-if="playlist.tidal_id" class="ml-1 opacity-60"
                >({{ playlist.tidal_id }})</span
              >
            </p>
            <p>Last push: {{ formatDate(playlist.last_synced_at) }}</p>
          </div>
        </div>

        <!-- Body (Songs List) -->
        <TransitionGroup
          name="list"
          tag="div"
          class="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar relative"
        >
          <div
            v-for="song in playlist.songs"
            :key="`${playlist.id}-${song.id}`"
            class="flex items-center gap-3 p-2 rounded-lg hover:bg-white/10 cursor-grab active:cursor-grabbing group transition-colors w-full"
            draggable="true"
            @dragstart="onDragStart($event, song, playlist.id)"
          >
            <img
              :src="getCoverUrl(song.cover_url) || '/placeholder-cover.jpg'"
              alt="Cover"
              class="w-10 h-10 rounded object-cover bg-black/40"
            />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate text-white">
                {{ song.title }}
              </p>
              <p class="text-xs text-gray-400 truncate">{{ song.artist }}</p>
            </div>
            <button
              v-if="song.id"
              @click.stop="handleRemoveSong(playlist.id, song)"
              class="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-all"
              title="Remove from playlist"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
          <!-- Skeleton Loader -->
          <div
            v-if="addingToPlaylistId === playlist.id"
            class="flex items-center gap-3 p-2 rounded-lg bg-white/5 animate-pulse w-full"
          >
            <div class="w-10 h-10 rounded bg-white/10"></div>
            <div class="flex-1 min-w-0 space-y-2">
              <div class="h-4 bg-white/10 rounded w-3/4"></div>
              <div class="h-3 bg-white/10 rounded w-1/2"></div>
            </div>
          </div>
        </TransitionGroup>

        <div
          v-if="!playlist.songs?.length"
          class="h-full flex flex-col items-center justify-center text-gray-500 text-sm p-4 text-center"
        >
          <p>No songs</p>
          <p class="text-xs mt-1">Drag songs here</p>
        </div>
      </div>
    </div>

    <ConfirmationModal
      :is-open="deleteModalOpen"
      title="Remove Song"
      :message="`Are you sure you want to remove '${songToDelete?.title}' from this playlist?`"
      @confirm="confirmDelete"
      @cancel="deleteModalOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from "vue";
import { usePlaylistStore } from "@/stores/playlists";
import { storeToRefs } from "pinia";
import { useToast } from "vue-toastification";
import { Trash2 } from "lucide-vue-next";
import ConfirmationModal from "@/components/ConfirmationModal.vue";

const playlistStore = usePlaylistStore();
const { playlists, loading, error } = storeToRefs(playlistStore);
const toast = useToast();

const deleteModalOpen = ref(false);
const songToDelete = ref<any>(null);
const playlistToDeleteFrom = ref<number | null>(null);
const addingToPlaylistId = ref<number | null>(null);

onMounted(async () => {
  await playlistStore.fetchPlaylistsDetailed();
});

const onDragStart = (event: DragEvent, song: any, sourcePlaylistId: number) => {
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = "copy";
    event.dataTransfer.setData(
      "application/json",
      JSON.stringify({ song, sourcePlaylistId })
    );
  }
};

const onDrop = async (event: DragEvent, targetPlaylistId: number) => {
  const data = event.dataTransfer?.getData("application/json");
  if (!data) return;

  const { song, sourcePlaylistId } = JSON.parse(data);

  if (sourcePlaylistId === targetPlaylistId) return;

  // Check if song already exists in target playlist
  const targetPlaylist = playlists.value.find((p) => p.id === targetPlaylistId);
  if (targetPlaylist?.songs?.some((s) => s.tidal_id === song.tidal_id)) {
    toast.warning("Song already in playlist");
    return;
  }

  try {
    addingToPlaylistId.value = targetPlaylistId;
    await playlistStore.addSong(targetPlaylistId, song);
    toast.success(`Added "${song.title}" to playlist`);
  } catch (e) {
    // Error handled in store
  } finally {
    addingToPlaylistId.value = null;
  }
};

const handleRemoveSong = (playlistId: number, song: any) => {
  songToDelete.value = song;
  playlistToDeleteFrom.value = playlistId;
  deleteModalOpen.value = true;
};

const confirmDelete = async () => {
  if (playlistToDeleteFrom.value && songToDelete.value) {
    try {
      await playlistStore.removeSong(
        playlistToDeleteFrom.value,
        songToDelete.value.id
      );
      toast.success("Song removed from playlist");
    } catch (e) {
      // Error handled in store
    }
  }
  deleteModalOpen.value = false;
  songToDelete.value = null;
  playlistToDeleteFrom.value = null;
};

const formatDate = (dateString?: string) => {
  if (!dateString) return "Never";
  return new Date(dateString).toLocaleString();
};

const getCoverUrl = (uuid: string | undefined) => {
  if (!uuid) return "";
  uuid = uuid.replace("https://resources.tidal.com/images/", "");
  uuid = uuid.replace("/320x320.jpg", "");
  return `https://resources.tidal.com/images/${uuid.replace(/-/g, "/")}/80x80.jpg`;
};
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

/* List Transitions */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-leave-active {
  position: absolute;
  /* Ensure the element takes up the correct width when absolute */
  left: 0.5rem; /* p-2 */
  right: 0.5rem; /* p-2 */
}
</style>
