<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { usePlaylistStore } from "@/stores/playlists";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const playlistStore = usePlaylistStore();
const router = useRouter();

onMounted(() => {
  playlistStore.fetchPlaylists();
});

// Form State
const showForm = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);
const formName = ref("");
const formDesc = ref("");

// Delete Confirmation State
const showDeleteConfirm = ref(false);
const deleteId = ref<number | null>(null);

// Sync State
const isSyncing = ref(false);
const syncMessage = ref("");

const handleSync = async () => {
  isSyncing.value = true;
  try {
    const result = await playlistStore.syncData();
    syncMessage.value = result.message;
    setTimeout(() => {
      syncMessage.value = "";
    }, 3000);
  } catch (e) {
    // Error is handled in store
  } finally {
    isSyncing.value = false;
  }
};

const openCreate = () => {
  isEditing.value = false;
  editingId.value = null;
  formName.value = "";
  formDesc.value = "";
  showForm.value = true;
};

const openEdit = (playlist: any) => {
  isEditing.value = true;
  editingId.value = playlist.id;
  formName.value = playlist.name;
  formDesc.value = playlist.description || "";
  showForm.value = true;
};

const handleSubmit = async () => {
  if (!formName.value) return;

  if (isEditing.value && editingId.value) {
    await playlistStore.updatePlaylist(
      editingId.value,
      formName.value,
      formDesc.value
    );
  } else {
    await playlistStore.createPlaylist(formName.value, formDesc.value);
  }

  showForm.value = false;
  formName.value = "";
  formDesc.value = "";
};

const openDeleteConfirm = (id: number) => {
  deleteId.value = id;
  showDeleteConfirm.value = true;
};

const confirmDelete = async () => {
  if (deleteId.value) {
    await playlistStore.deletePlaylist(deleteId.value);
    showDeleteConfirm.value = false;
    deleteId.value = null;
  }
};

const openPlaylist = (id: number) => {
  router.push({ name: "playlist-detail", params: { id } });
};
</script>

<template>
  <div class="p-6 bg-gray-900 min-h-screen text-white">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-cyan-400">My Playlists</h1>
      <div class="flex gap-4">
        <button
          @click="handleSync"
          :disabled="isSyncing"
          class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg
            v-if="isSyncing"
            class="animate-spin h-5 w-5 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span v-else>Sync Data</span>
        </button>
        <button
          @click="openCreate"
          class="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-2 px-4 rounded transition"
        >
          New Playlist
        </button>
        <button
          @click="authStore.logout()"
          class="bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded transition"
        >
          Logout
        </button>
      </div>
    </div>

    <!-- Toast Notification -->
    <div
      v-if="syncMessage"
      class="fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg z-50 transition-all duration-300"
    >
      {{ syncMessage }}
    </div>

    <!-- Create/Edit Form -->
    <div
      v-if="showForm"
      class="fixed inset-0 bg-black/50 flex items-center justify-center backdrop-blur-sm z-50"
    >
      <div
        class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700 shadow-xl"
      >
        <h2 class="text-xl font-bold mb-4 text-white">
          {{ isEditing ? "Edit Playlist" : "Create Playlist" }}
        </h2>
        <form @submit.prevent="handleSubmit">
          <input
            v-model="formName"
            placeholder="Playlist Name"
            class="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-4 text-white focus:border-cyan-500 outline-none placeholder-gray-500"
            required
          />
          <textarea
            v-model="formDesc"
            placeholder="Description"
            class="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-4 text-white focus:border-cyan-500 outline-none placeholder-gray-500"
          ></textarea>
          <div class="flex justify-end gap-2">
            <button
              type="button"
              @click="showForm = false"
              class="text-gray-400 hover:text-white px-4 py-2"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-4 py-2 rounded transition"
            >
              {{ isEditing ? "Update" : "Create" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black/50 flex items-center justify-center backdrop-blur-sm z-50"
    >
      <div
        class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700 shadow-xl"
      >
        <h2 class="text-xl font-bold mb-4 text-white">Delete Playlist</h2>
        <p class="text-gray-300 mb-6">
          Are you sure you want to delete this playlist? This action cannot be
          undone.
        </p>
        <div class="flex justify-end gap-2">
          <button
            @click="showDeleteConfirm = false"
            class="text-gray-400 hover:text-white px-4 py-2"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            class="bg-red-500 hover:bg-red-400 text-white font-bold px-4 py-2 rounded transition"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="playlistStore.loading" class="text-center py-10">
      <div
        class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500 mx-auto"
      ></div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="playlistStore.error"
      class="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded mb-4"
    >
      {{ playlistStore.error }}
    </div>

    <!-- Empty State -->
    <div
      v-else-if="playlistStore.playlists.length === 0"
      class="text-center py-20 text-gray-400"
    >
      <p class="text-xl mb-4">No playlists yet</p>
      <p>Create your first playlist to start organizing your music!</p>
    </div>

    <!-- Playlist Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="playlist in playlistStore.playlists"
        :key="playlist.id"
        @click="openPlaylist(playlist.id)"
        class="bg-gray-800/50 border border-white/10 rounded-xl p-6 hover:bg-gray-800 transition group relative shadow-lg hover:shadow-cyan-500/10 cursor-pointer"
      >
        <div class="flex justify-between items-start mb-2">
          <h3
            class="text-xl font-bold text-white group-hover:text-cyan-400 transition"
          >
            {{ playlist.name }}
          </h3>
          <button
            @click.stop="openEdit(playlist)"
            class="text-gray-500 hover:text-white opacity-0 group-hover:opacity-100 transition"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
              />
            </svg>
          </button>
        </div>
        <p class="text-gray-400 text-sm mb-4 line-clamp-2">
          {{ playlist.description || "No description" }}
        </p>
        <div
          class="flex justify-between items-center text-xs text-gray-500 mt-auto"
        >
          <span>{{ new Date(playlist.created_at).toLocaleDateString() }}</span>
          <button
            @click.stop="openDeleteConfirm(playlist.id)"
            class="text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
