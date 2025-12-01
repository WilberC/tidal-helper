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
          <h3 class="font-bold text-lg truncate" :title="playlist.name">
            {{ playlist.name }}
          </h3>
          <p class="text-xs text-gray-400">
            {{ playlist.songs?.length || 0 }} songs
          </p>
        </div>

        <!-- Body (Songs List) -->
        <div class="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar">
          <div
            v-for="song in playlist.songs"
            :key="`${playlist.id}-${song.id}`"
            class="flex items-center gap-3 p-2 rounded-lg hover:bg-white/10 cursor-grab active:cursor-grabbing group transition-colors"
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
          </div>

          <div
            v-if="!playlist.songs?.length"
            class="h-full flex flex-col items-center justify-center text-gray-500 text-sm p-4 text-center"
          >
            <p>No songs</p>
            <p class="text-xs mt-1">Drag songs here</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from "vue";
import { usePlaylistStore } from "@/stores/playlists";
import { storeToRefs } from "pinia";
import { useToast } from "vue-toastification";

const playlistStore = usePlaylistStore();
const { playlists, loading, error } = storeToRefs(playlistStore);
const toast = useToast();

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
    await playlistStore.addSong(targetPlaylistId, song);
    toast.success(`Added "${song.title}" to playlist`);
    // Refresh detailed playlists to update UI
    // await playlistStore.fetchPlaylistsDetailed();
    // Optimization: Manually update the local state instead of full refetch if possible,
    // but addSong in store calls fetchPlaylist(id) which updates currentPlaylist, not the list in 'playlists'.
    // So we should probably refetch or manually update.
    // Let's manually push to the list for immediate feedback if we can, or just refetch.
    // Refetching detailed playlists might be heavy.
    // Ideally, addSong should return the added song or we construct it.
    // For now, let's just refetch detailed playlists to be safe and consistent.
    await playlistStore.fetchPlaylistsDetailed();
  } catch (e) {
    // Error handled in store
  }
};

const getCoverUrl = (uuid: string | undefined) => {
  if (!uuid) return "";
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
</style>
