import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";
import router from "@/router";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const token = ref(localStorage.getItem("token"));
  const isAuthenticated = computed(() => !!token.value);

  async function login(credentials: any) {
    try {
      const formData = new FormData();
      formData.append("username", credentials.email);
      formData.append("password", credentials.password);

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/login`,
        formData
      );
      token.value = response.data.access_token;
      localStorage.setItem("token", token.value as string);
      router.push("/");
    } catch (error) {
      console.error("Login failed", error);
      throw error;
    }
  }

  async function signup(userData: any) {
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/signup`,
        null,
        {
          params: {
            email: userData.email,
            password: userData.password,
          },
        }
      );
      // Store success message in sessionStorage to show on login page
      sessionStorage.setItem(
        "signupSuccess",
        "Account created successfully! Please log in."
      );
      router.push("/login");
    } catch (error) {
      console.error("Signup failed", error);
      throw error;
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
    router.push("/login");
  }

  const isTidalConnected = ref(false);

  async function checkTidalConnectionStatus() {
    if (!token.value) return;
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/tidal/status`,
        {
          headers: { Authorization: `Bearer ${token.value}` },
        }
      );
      isTidalConnected.value = response.data.is_connected;
    } catch (error) {
      console.error("Failed to check Tidal connection status", error);
    }
  }

  async function getTidalLoginUrl() {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/v1/auth/tidal/login-url`,
      {
        headers: { Authorization: `Bearer ${token.value}` },
      }
    );
    return response.data; // Returns { url, code_verifier }
  }

  async function handleTidalCallback(code: string, codeVerifier: string) {
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/tidal/callback`,
        {
          code,
          redirect_uri: window.location.origin + "/auth/callback",
          code_verifier: codeVerifier,
        },
        {
          headers: { Authorization: `Bearer ${token.value}` },
        }
      );
      isTidalConnected.value = true;
      return true;
    } catch (error) {
      console.error("Tidal auth failed", error);
      throw error;
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isTidalConnected,
    login,
    signup,
    logout,
    checkTidalConnectionStatus,
    getTidalLoginUrl,
    handleTidalCallback,
  };
});
