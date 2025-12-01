<script setup lang="ts">
import { usePlaylistStore } from "@/stores/playlists";
import { useRoute, useRouter } from "vue-router";
import { onMounted, ref } from "vue";
import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const playlistStore = usePlaylistStore();
const authStore = useAuthStore();

const playlistId = Number(route.params.id);
const searchQuery = ref("");
const searchResults = ref<any[]>([]);
const isSearching = ref(false);
const isSyncing = ref(false);

const syncPlaylist = async () => {
  if (
    !confirm("Sync this playlist with Tidal? This will update the song list.")
  )
    return;
  isSyncing.value = true;
  try {
    await axios.post(
      `${import.meta.env.VITE_API_URL}/api/v1/playlists/${playlistId}/sync`,
      {},
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    await playlistStore.fetchPlaylist(playlistId);
  } catch (error) {
    console.error("Sync failed", error);
    alert("Failed to sync playlist");
  } finally {
    isSyncing.value = false;
  }
};

onMounted(() => {
  playlistStore.fetchPlaylist(playlistId);
});

const handleSearch = async () => {
  if (!searchQuery.value) {
    searchResults.value = [];
    return;
  }
  isSearching.value = true;
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/songs/search`,
      {
        params: { query: searchQuery.value },
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    searchResults.value = response.data;
  } catch (error) {
    console.error("Search failed", error);
  } finally {
    isSearching.value = false;
  }
};

const addSong = async (song: any) => {
  await playlistStore.addSong(playlistId, song);
  searchQuery.value = "";
  searchResults.value = [];
};

const removeSong = async (songId: number) => {
  if (confirm("Remove this song from playlist?")) {
    await playlistStore.removeSong(playlistId, songId);
  }
};

const refreshSong = async (songId: number) => {
  await playlistStore.refreshSong(songId);
};

const goBack = () => {
  router.push("/");
};

const getCoverUrl = (uuid: string | undefined) => {
  if (!uuid) return "";
  return `https://resources.tidal.com/images/${uuid.replace(/-/g, "/")}/80x80.jpg`;
};
</script>

<template>
  <div class="p-6 bg-gray-900 min-h-screen text-white">
    <button
      @click="goBack"
      class="mb-4 text-cyan-400 hover:text-cyan-300 flex items-center gap-2"
    >
      <span>&larr;</span> Back to Dashboard
    </button>

    <div v-if="playlistStore.loading" class="text-center py-10">
      <div
        class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500 mx-auto"
      ></div>
    </div>
    <div v-else-if="playlistStore.currentPlaylist">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-cyan-400 flex items-center gap-4">
          {{ playlistStore.currentPlaylist.name }}
          <button
            @click="syncPlaylist"
            class="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition font-normal"
            :disabled="isSyncing"
          >
            {{ isSyncing ? "Syncing..." : "Sync" }}
          </button>
        </h1>
        <p class="text-gray-400">
          {{ playlistStore.currentPlaylist.description }}
        </p>
      </div>

      <!-- Search -->
      <div class="mb-8 relative max-w-2xl">
        <div class="flex gap-2">
          <input
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            placeholder="Search for songs on Tidal..."
            class="flex-1 bg-gray-800 border border-gray-700 rounded p-3 text-white focus:border-cyan-500 outline-none placeholder-gray-500"
          />
          <button
            @click="handleSearch"
            class="bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-6 py-2 rounded transition"
            :disabled="isSearching"
          >
            {{ isSearching ? "Searching..." : "Search" }}
          </button>
        </div>

        <!-- Search Results -->
        <div
          v-if="searchResults.length > 0"
          class="absolute w-full bg-gray-800 border border-gray-700 rounded mt-2 z-10 max-h-96 overflow-y-auto shadow-xl"
        >
          <div
            v-for="song in searchResults"
            :key="song.tidal_id"
            class="p-3 hover:bg-gray-700 flex justify-between items-center cursor-pointer border-b border-gray-700 last:border-0"
            @click="addSong(song)"
          >
            <div class="flex items-center gap-3">
              <img
                v-if="song.cover_url"
                :src="getCoverUrl(song.cover_url)"
                class="w-12 h-12 rounded object-cover"
              />
              <div
                v-else
                class="w-12 h-12 bg-gray-600 rounded flex items-center justify-center text-xs text-gray-400"
              >
                No Img
              </div>
              <div>
                <div class="font-bold text-white">{{ song.title }}</div>
                <div class="text-sm text-gray-400">
                  {{ song.artist }} • {{ song.album }}
                </div>
              </div>
            </div>
            <button
              class="text-cyan-400 hover:text-white font-bold text-xl px-2"
            >
              +
            </button>
          </div>
        </div>
      </div>

      <!-- Song List -->
      <div
        class="bg-gray-800/50 rounded-xl overflow-hidden border border-white/5"
      >
        <table class="w-full text-left">
          <thead class="bg-gray-800 text-gray-400 uppercase text-xs">
            <tr>
              <th class="p-4 w-12">#</th>
              <th class="p-4">Title</th>
              <th class="p-4">Artist</th>
              <th class="p-4">Album</th>
              <th class="p-4 w-24">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            <tr
              v-for="(song, index) in playlistStore.currentPlaylist.songs"
              :key="song.id"
              class="hover:bg-gray-700/50 transition group"
              :class="{ 'opacity-50 grayscale': song.is_available === false }"
              :title="
                song.is_available === false ? 'Not available on Tidal' : ''
              "
            >
              <td class="p-4 text-gray-500">{{ index + 1 }}</td>
              <td class="p-4 font-medium text-white flex items-center gap-3">
                <img
                  v-if="song.cover_url"
                  :src="getCoverUrl(song.cover_url)"
                  class="w-10 h-10 rounded object-cover"
                />
                <div
                  v-else
                  class="w-10 h-10 bg-gray-600 rounded flex items-center justify-center text-xs text-gray-400"
                >
                  No Img
                </div>
                <div>
                  {{ song.title }}
                  <span
                    v-if="song.is_available === false"
                    class="ml-2 text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded border border-red-500/50"
                    >Unavailable</span
                  >
                </div>
              </td>
              <td class="p-4 text-gray-400">{{ song.artist }}</td>
              <td class="p-4 text-gray-400">{{ song.album }}</td>
              <td class="p-4 flex gap-2">
                <button
                  @click="refreshSong(song.id!)"
                  class="text-blue-400 hover:text-blue-300 opacity-0 group-hover:opacity-100 transition"
                  title="Refresh metadata"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>
                <button
                  @click="removeSong(song.id!)"
                  class="text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition"
                  title="Remove from playlist"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!playlistStore.currentPlaylist.songs?.length">
              <td colspan="5" class="p-12 text-center text-gray-500">
                <p class="text-lg mb-2">This playlist is empty</p>
                <p class="text-sm">
                  Search for songs above to add them to your collection.
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="text-center py-10 text-red-400">
      Playlist not found or error loading.
    </div>
  </div>
</template>
