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
          <div class="flex justify-between items-start mb-2 group/header">
            <div v-if="editingPlaylistId === playlist.id" class="flex-1 mr-2">
              <input
                ref="playlistNameInput"
                v-model="editingName"
                @blur="savePlaylistName(playlist)"
                @keyup.enter="savePlaylistName(playlist)"
                @keyup.esc="cancelEdit"
                class="w-full bg-white/10 border border-white/20 rounded px-2 py-1 text-sm font-bold text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
            <h3
              v-else
              class="font-bold text-lg truncate flex-1 mr-2 cursor-pointer hover:text-cyan-400 transition-colors"
              :title="playlist.name"
              @click="startEditing(playlist)"
            >
              {{ playlist.name }}
              <Pencil
                class="w-3 h-3 inline-block ml-1 opacity-0 group-hover/header:opacity-50"
              />
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
            v-for="(song, index) in playlist.songs"
            :key="`${playlist.id}-${song.id}`"
            class="flex items-center gap-3 p-2 rounded-lg cursor-grab active:cursor-grabbing group transition-colors w-full select-none"
            :class="{
              'animate-pulse bg-white/5 pointer-events-none':
                song.id &&
                deletingItems.has(getSelectionKey(playlist.id, song.id)),
              'bg-cyan-500/20 border border-cyan-500/30': isSelected(
                playlist.id,
                song.id
              ),
              'hover:bg-white/10': !isSelected(playlist.id, song.id),
              'bg-white/5':
                !isSelected(playlist.id, song.id) &&
                (!song.id ||
                  !deletingItems.has(getSelectionKey(playlist.id, song.id))),
            }"
            draggable="true"
            @dragstart="onDragStart($event, song, playlist.id)"
            @click="handleSelection($event, song, playlist.id, index)"
            @contextmenu.prevent="handleContextMenu($event, song, playlist.id)"
          >
            <template
              v-if="
                song.id &&
                deletingItems.has(getSelectionKey(playlist.id, song.id))
              "
            >
              <div class="w-10 h-10 rounded bg-white/10"></div>
              <div class="flex-1 min-w-0 space-y-2">
                <div class="h-4 bg-white/10 rounded w-3/4"></div>
                <div class="h-3 bg-white/10 rounded w-1/2"></div>
              </div>
            </template>
            <template v-else>
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
            </template>
          </div>
          <!-- Skeleton Loader -->
          <template v-if="addingState?.playlistId === playlist.id">
            <div
              v-for="n in addingState.count"
              :key="`skeleton-${n}`"
              class="flex items-center gap-3 p-2 rounded-lg bg-white/5 animate-pulse w-full"
            >
              <div class="w-10 h-10 rounded bg-white/10"></div>
              <div class="flex-1 min-w-0 space-y-2">
                <div class="h-4 bg-white/10 rounded w-3/4"></div>
                <div class="h-3 bg-white/10 rounded w-1/2"></div>
              </div>
            </div>
          </template>
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
      title="Remove Songs"
      :message="deleteMessage"
      @confirm="confirmDelete"
      @cancel="deleteModalOpen = false"
    />

    <MoveToPlaylistModal
      :is-open="moveModalOpen"
      :playlists="playlists"
      :current-playlist-id="playlistToMoveFrom || undefined"
      @close="moveModalOpen = false"
      @move="confirmMove"
    />

    <!-- Context Menu -->
    <div
      v-if="contextMenu.visible"
      class="fixed z-50 bg-gray-800 border border-white/10 rounded-lg shadow-xl py-1 min-w-[160px]"
      :style="{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }"
    >
      <button
        @click="openMoveModal"
        class="w-full text-left px-4 py-2 text-sm text-gray-200 hover:bg-white/10 flex items-center gap-2"
      >
        <Move class="w-4 h-4" />
        Move to...
      </button>
      <button
        @click="handleContextRemove"
        class="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-white/10 flex items-center gap-2"
      >
        <Trash2 class="w-4 h-4" />
        Remove
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, onUnmounted } from "vue";
import { usePlaylistStore } from "@/stores/playlists";
import { storeToRefs } from "pinia";
import { useToast } from "vue-toastification";
import { Trash2, Move, Pencil } from "lucide-vue-next";
import ConfirmationModal from "@/components/ConfirmationModal.vue";
import MoveToPlaylistModal from "@/components/MoveToPlaylistModal.vue";

const playlistStore = usePlaylistStore();
const { playlists, loading, error } = storeToRefs(playlistStore);
const toast = useToast();

const deleteModalOpen = ref(false);
const moveModalOpen = ref(false);
const songsToDelete = ref<any[]>([]);
const playlistToDeleteFrom = ref<number | null>(null);
const playlistToMoveFrom = ref<number | null>(null);
const songsToMove = ref<any[]>([]);

const editingPlaylistId = ref<number | null>(null);
const editingName = ref("");
const playlistNameInput = ref<HTMLInputElement[] | null>(null);

const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  playlistId: null as number | null,
  song: null as any,
});
const addingState = ref<{ playlistId: number; count: number } | null>(null);
const deletingItems = ref<Set<string>>(new Set());

const deleteMessage = computed(() => {
  if (songsToDelete.value.length === 1) {
    return `Are you sure you want to remove '${songsToDelete.value[0].title}' from this playlist?`;
  }
  return `Are you sure you want to remove ${songsToDelete.value.length} songs from this playlist?`;
});

onMounted(async () => {
  await playlistStore.fetchPlaylistsDetailed();
});

const selectedSongs = ref<Set<string>>(new Set());
const lastSelected = ref<{ playlistId: number; index: number } | null>(null);

const getSelectionKey = (playlistId: number, songId: number) =>
  `${playlistId}-${songId}`;

const isSelected = (playlistId: number, songId: number | undefined) =>
  songId ? selectedSongs.value.has(getSelectionKey(playlistId, songId)) : false;

const handleSelection = (
  event: MouseEvent,
  song: any,
  playlistId: number,
  index: number
) => {
  if (!song.id) return;
  const key = getSelectionKey(playlistId, song.id);

  // Enforce single-playlist selection
  if (selectedSongs.value.size > 0) {
    const firstKey = selectedSongs.value.values().next().value;
    if (firstKey) {
      const [firstPlaylistId] = firstKey.split("-");
      if (parseInt(firstPlaylistId) !== playlistId) {
        selectedSongs.value.clear();
      }
    }
  }

  if (
    event.shiftKey &&
    lastSelected.value &&
    lastSelected.value.playlistId === playlistId
  ) {
    const start = Math.min(lastSelected.value.index, index);
    const end = Math.max(lastSelected.value.index, index);
    const playlist = playlists.value.find((p) => p.id === playlistId);

    if (playlist && playlist.songs) {
      if (!event.ctrlKey && !event.metaKey) {
        selectedSongs.value.clear();
      }
      for (let i = start; i <= end; i++) {
        const s = playlist.songs[i];
        if (s.id) {
          selectedSongs.value.add(getSelectionKey(playlistId, s.id));
        }
      }
    }
  } else if (event.ctrlKey || event.metaKey) {
    if (selectedSongs.value.has(key)) {
      selectedSongs.value.delete(key);
    } else {
      selectedSongs.value.add(key);
    }
    lastSelected.value = { playlistId, index };
  } else {
    selectedSongs.value.clear();
    selectedSongs.value.add(key);
    lastSelected.value = { playlistId, index };
  }
};

const onDragStart = (event: DragEvent, song: any, sourcePlaylistId: number) => {
  if (!song.id) return;
  if (event.dataTransfer) {
    // If dragging an unselected item, select it first (and clear others)
    if (!isSelected(sourcePlaylistId, song.id)) {
      selectedSongs.value.clear();
      selectedSongs.value.add(getSelectionKey(sourcePlaylistId, song.id));
      const playlist = playlists.value.find((p) => p.id === sourcePlaylistId);
      const index =
        playlist?.songs?.findIndex((s: any) => s.id === song.id) ?? 0;
      lastSelected.value = { playlistId: sourcePlaylistId, index };
    }

    // Collect all selected songs
    const songsToDrag: any[] = [];
    const playlist = playlists.value.find((p) => p.id === sourcePlaylistId);
    if (playlist && playlist.songs) {
      playlist.songs.forEach((s: any) => {
        if (
          s.id &&
          selectedSongs.value.has(getSelectionKey(sourcePlaylistId, s.id))
        ) {
          songsToDrag.push(s);
        }
      });
    }

    event.dataTransfer.effectAllowed = "copy";
    event.dataTransfer.setData(
      "application/json",
      JSON.stringify({ songs: songsToDrag, sourcePlaylistId })
    );
  }
};

const onDrop = async (event: DragEvent, targetPlaylistId: number) => {
  const data = event.dataTransfer?.getData("application/json");
  if (!data) return;

  const { songs, sourcePlaylistId } = JSON.parse(data);

  if (sourcePlaylistId === targetPlaylistId) return;

  const targetPlaylist = playlists.value.find((p) => p.id === targetPlaylistId);
  if (!targetPlaylist) return;

  addingState.value = { playlistId: targetPlaylistId, count: songs.length };
  let addedCount = 0;
  let skippedCount = 0;

  try {
    for (const song of songs) {
      const exists = targetPlaylist.songs?.some(
        (s) => s.tidal_id === song.tidal_id
      );

      if (exists) {
        skippedCount++;
      } else {
        await playlistStore.addSong(targetPlaylistId, song);
        addedCount++;
      }

      if (addingState.value) {
        addingState.value.count--;
      }
    }

    if (addedCount > 0) {
      toast.success(
        `Added ${addedCount} song${addedCount > 1 ? "s" : ""} to playlist`
      );
    }
    if (skippedCount > 0) {
      toast.warning(
        `${skippedCount} song${skippedCount > 1 ? "s" : ""} already in playlist`
      );
    }
  } catch (e) {
    // Error handled in store
  } finally {
    addingState.value = null;
    selectedSongs.value.clear();
  }
};

const handleRemoveSong = (playlistId: number, song: any) => {
  playlistToDeleteFrom.value = playlistId;

  if (isSelected(playlistId, song.id) && selectedSongs.value.size > 1) {
    // Multi-delete
    const playlist = playlists.value.find((p) => p.id === playlistId);
    if (playlist && playlist.songs) {
      songsToDelete.value = playlist.songs.filter(
        (s) =>
          s.id && selectedSongs.value.has(getSelectionKey(playlistId, s.id))
      );
    }
  } else {
    // Single delete
    songsToDelete.value = [song];
  }
  deleteModalOpen.value = true;
};

const confirmDelete = async () => {
  if (!playlistToDeleteFrom.value || songsToDelete.value.length === 0) return;

  const playlistId = playlistToDeleteFrom.value;
  const songs = [...songsToDelete.value];

  // Close modal and clear selection immediately
  deleteModalOpen.value = false;
  songsToDelete.value = [];
  playlistToDeleteFrom.value = null;

  // Set deleting state
  songs.forEach((s) => {
    if (s.id) deletingItems.value.add(getSelectionKey(playlistId, s.id));
  });

  try {
    await Promise.all(
      songs.map((s) =>
        s.id ? playlistStore.removeSong(playlistId, s.id) : Promise.resolve()
      )
    );
    toast.success(
      `Removed ${songs.length} song${songs.length > 1 ? "s" : ""} from playlist`
    );
  } catch (e) {
    // Error handled in store
  } finally {
    songs.forEach((s) => {
      if (s.id) deletingItems.value.delete(getSelectionKey(playlistId, s.id));
    });
    selectedSongs.value.clear();
  }
};

const handleContextMenu = (
  event: MouseEvent,
  song: any,
  playlistId: number
) => {
  if (!song.id) return;

  // If right-clicked song is not selected, select it (and clear others)
  if (!isSelected(playlistId, song.id)) {
    selectedSongs.value.clear();
    selectedSongs.value.add(getSelectionKey(playlistId, song.id));
    lastSelected.value = {
      playlistId,
      index:
        playlists.value
          .find((p) => p.id === playlistId)
          ?.songs?.findIndex((s) => s.id === song.id) ?? 0,
    };
  }

  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    playlistId,
    song,
  };
};

const closeContextMenu = () => {
  contextMenu.value.visible = false;
};

const openMoveModal = () => {
  if (!contextMenu.value.playlistId) return;

  playlistToMoveFrom.value = contextMenu.value.playlistId;

  // Collect selected songs
  const playlist = playlists.value.find(
    (p) => p.id === contextMenu.value.playlistId
  );
  if (playlist && playlist.songs) {
    songsToMove.value = playlist.songs.filter(
      (s) =>
        s.id &&
        selectedSongs.value.has(
          getSelectionKey(contextMenu.value.playlistId!, s.id)
        )
    );
  }

  moveModalOpen.value = true;
  closeContextMenu();
};

const handleContextRemove = () => {
  if (!contextMenu.value.playlistId || !contextMenu.value.song) return;
  handleRemoveSong(contextMenu.value.playlistId, contextMenu.value.song);
  closeContextMenu();
};

const confirmMove = async (targetPlaylistId: number) => {
  if (!playlistToMoveFrom.value || songsToMove.value.length === 0) return;

  const sourcePlaylistId = playlistToMoveFrom.value;
  const songs = [...songsToMove.value];

  // Close modal
  moveModalOpen.value = false;

  // Optimistic UI update could be complex here, so we'll rely on store updates
  // But we can show loading state if we want. For now, just toast.

  let movedCount = 0;
  let skippedCount = 0;

  try {
    const targetPlaylist = playlists.value.find(
      (p) => p.id === targetPlaylistId
    );

    for (const song of songs) {
      if (!song.id) continue;

      // Check if already in target
      const exists = targetPlaylist?.songs?.some(
        (s) => s.tidal_id === song.tidal_id
      );

      if (!exists) {
        // Add to new playlist
        await playlistStore.addSong(targetPlaylistId, song);
        // Remove from old playlist
        await playlistStore.removeSong(sourcePlaylistId, song.id);
        movedCount++;
      } else {
        // If it exists in target, we might still want to remove it from source?
        // "Move" usually implies it ends up in target and not in source.
        // If it's already in target, we should just remove from source.
        await playlistStore.removeSong(sourcePlaylistId, song.id);
        skippedCount++; // It was "skipped" for adding, but "moved" effectively.
      }
    }

    if (movedCount > 0) {
      toast.success(
        `Moved ${movedCount} song${movedCount > 1 ? "s" : ""} to playlist`
      );
    }
    if (skippedCount > 0) {
      toast.info(
        `${skippedCount} song${skippedCount > 1 ? "s" : ""} were already in target playlist (removed from source)`
      );
    }
  } catch (e) {
    console.error(e);
    toast.error("Failed to move some songs");
  } finally {
    selectedSongs.value.clear();
    songsToMove.value = [];
    playlistToMoveFrom.value = null;
  }
};

const startEditing = (playlist: any) => {
  editingPlaylistId.value = playlist.id;
  editingName.value = playlist.name;
  // Focus input on next tick
  setTimeout(() => {
    if (playlistNameInput.value && playlistNameInput.value[0]) {
      playlistNameInput.value[0].focus();
    }
  }, 0);
};

const cancelEdit = () => {
  editingPlaylistId.value = null;
  editingName.value = "";
};

const savePlaylistName = (playlist: any) => {
  if (editingPlaylistId.value !== playlist.id) return;

  const newName = editingName.value.trim();
  if (!newName || newName === playlist.name) {
    cancelEdit();
    return;
  }

  // Optimistic update: close edit mode immediately
  cancelEdit();

  playlistStore
    .updatePlaylist(playlist.id, newName, playlist.description)
    .then(() => {
      toast.success("Playlist renamed");
    })
    .catch(() => {
      // Error is handled in store (reverts change), but we can show a toast
      // toast.error("Failed to rename playlist"); // Store already sets error state, but toast might be good
    });
};

// Close context menu on click outside
onMounted(() => {
  document.addEventListener("click", closeContextMenu);
});

onUnmounted(() => {
  document.removeEventListener("click", closeContextMenu);
});

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
