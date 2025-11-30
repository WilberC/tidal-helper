import { defineStore } from "pinia";
import axios from "axios";
import { ref } from "vue";
import { useAuthStore } from "./auth";

interface Playlist {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export const usePlaylistStore = defineStore("playlists", () => {
  const playlists = ref<Playlist[]>([]);
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
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Failed to update playlist";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    playlists,
    loading,
    error,
    fetchPlaylists,
    createPlaylist,
    updatePlaylist,
    deletePlaylist,
  };
});
