import { defineStore } from "pinia";
import axios from "axios";
import { ref } from "vue";
import { useAuthStore } from "./auth";

interface Song {
  id?: number;
  tidal_id: number;
  title: string;
  artist: string;
  album: string;
  cover_url?: string;
  is_available?: boolean;
}

interface Playlist {
  id: number;
  user_id: number;
  tidal_id?: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  last_synced_at?: string;
  songs?: Song[];
}

export const usePlaylistStore = defineStore("playlists", () => {
  const playlists = ref<Playlist[]>([]);
  const currentPlaylist = ref<Playlist | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const authStore = useAuthStore();

  const getHeaders = () => {
    return {
      Authorization: `Bearer ${authStore.token}`,
    };
  };

  const fetchPlaylists = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/`,
        {
          headers: getHeaders(),
        }
      );
      playlists.value = response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to fetch playlists";
    } finally {
      loading.value = false;
    }
  };

  const fetchPlaylistsDetailed = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/detailed`,
        {
          headers: getHeaders(),
        }
      );
      playlists.value = response.data;
    } catch (err: any) {
      error.value =
        err.response?.data?.detail || "Failed to fetch detailed playlists";
    } finally {
      loading.value = false;
    }
  };

  const fetchPlaylist = async (id: number) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/${id}`,
        {
          headers: getHeaders(),
        }
      );
      currentPlaylist.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to fetch playlist";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const createPlaylist = async (name: string, description?: string) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/`,
        { name, description },
        { headers: getHeaders() }
      );
      playlists.value.push(response.data);
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to create playlist";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deletePlaylist = async (id: number) => {
    loading.value = true;
    error.value = null;
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/${id}`,
        {
          headers: getHeaders(),
        }
      );
      playlists.value = playlists.value.filter((p) => p.id !== id);
      if (currentPlaylist.value?.id === id) {
        currentPlaylist.value = null;
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to delete playlist";
    } finally {
      loading.value = false;
    }
  };

  const updatePlaylist = async (
    id: number,
    name: string,
    description?: string
  ) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/${id}`,
        { name, description },
        { headers: getHeaders() }
      );
      const index = playlists.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        playlists.value[index] = response.data;
      }
      if (currentPlaylist.value?.id === id) {
        currentPlaylist.value = { ...currentPlaylist.value, ...response.data };
      }
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to update playlist";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const addSong = async (playlistId: number, song: Song) => {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/${playlistId}/songs`,
        song,
        { headers: getHeaders() }
      );
      const addedSong = response.data;

      // Update local state
      const playlist = playlists.value.find((p) => p.id === playlistId);
      if (playlist) {
        if (!playlist.songs) playlist.songs = [];
        if (!playlist.songs.some((s) => s.id === addedSong.id)) {
          playlist.songs.push(addedSong);
        }
      }

      // Update currentPlaylist if it matches
      if (currentPlaylist.value?.id === playlistId) {
        if (!currentPlaylist.value.songs) currentPlaylist.value.songs = [];
        if (!currentPlaylist.value.songs.some((s) => s.id === addedSong.id)) {
          currentPlaylist.value.songs.push(addedSong);
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to add song";
      throw err;
    }
  };

  const removeSong = async (playlistId: number, songId: number) => {
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/${playlistId}/songs/${songId}`,
        { headers: getHeaders() }
      );

      // Update current playlist if it's the one being modified
      if (
        currentPlaylist.value &&
        currentPlaylist.value.id === playlistId &&
        currentPlaylist.value.songs
      ) {
        currentPlaylist.value.songs = currentPlaylist.value.songs.filter(
          (s) => s.id !== songId
        );
      }

      // Update the playlist in the playlists list
      const playlistIndex = playlists.value.findIndex(
        (p) => p.id === playlistId
      );
      if (playlistIndex !== -1 && playlists.value[playlistIndex].songs) {
        playlists.value[playlistIndex].songs = playlists.value[
          playlistIndex
        ].songs.filter((s) => s.id !== songId);
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to remove song";
      throw err;
    }
  };

  const reorderSongs = async (playlistId: number, songIds: number[]) => {
    try {
      await axios.put(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/${playlistId}/songs/reorder`,
        songIds, // Send array directly as body
        { headers: getHeaders() }
      );
      // No need to fetch if we just reordered locally, but to be safe we could.
      // For now, assume local state is already updated by UI (drag and drop) or we just fetch.
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to reorder songs";
      throw err;
    }
  };

  const refreshSong = async (songId: number) => {
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/songs/${songId}/refresh`,
        {},
        { headers: getHeaders() }
      );
      // We should probably update the song in the current playlist if it's there
      if (currentPlaylist.value && currentPlaylist.value.songs) {
        // We could fetch the song again or just fetch the playlist
        // Fetching playlist is easier to ensure consistency
        if (currentPlaylist.value.id) {
          await fetchPlaylist(currentPlaylist.value.id);
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to refresh song";
      throw err;
    }
  };

  const syncData = async (
    syncType: "playlists" | "tracks" | "mixes" = "playlists"
  ) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/sync/?sync_type=${syncType}`,
        {},
        { headers: getHeaders() }
      );
      // Refresh playlists after sync
      await fetchPlaylists();
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to sync data";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const syncPlaylist = async (playlistId: number) => {
    loading.value = true;
    error.value = null;
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/playlists/${playlistId}/sync`,
        {},
        { headers: getHeaders() }
      );
      // Refresh playlist to get updated last_synced_at
      await fetchPlaylist(playlistId);
      // Also refresh detailed playlists if we are in QuickEditView
      await fetchPlaylistsDetailed();
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to sync playlist";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    playlists,
    currentPlaylist,
    loading,
    error,
    fetchPlaylists,
    fetchPlaylistsDetailed,
    fetchPlaylist,
    createPlaylist,
    updatePlaylist,
    deletePlaylist,
    addSong,
    removeSong,
    reorderSongs,
    refreshSong,
    syncData,
    syncPlaylist,
  };
});
