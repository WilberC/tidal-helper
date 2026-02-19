import { createApp } from "vue";
import { createPinia } from "pinia";
import Toast, { useToast } from "vue-toastification";
import "vue-toastification/dist/index.css";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Global axios interceptor: auto-refresh token on 401/403, redirect to login if refresh fails
let isRefreshing = false;
let pendingRequests: Array<(token: string) => void> = [];

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    // Only handle auth errors for non-auth endpoints (avoid infinite loops)
    if (
      (status === 401 || status === 403) &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/api/v1/auth/")
    ) {
      if (isRefreshing) {
        // Queue the request until refresh completes
        return new Promise((resolve) => {
          pendingRequests.push((newToken: string) => {
            originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
            resolve(axios(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const authStore = useAuthStore();
        await authStore.refresh();
        const newToken = authStore.token as string;

        // Flush queued requests
        pendingRequests.forEach((cb) => cb(newToken));
        pendingRequests = [];

        originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
        return axios(originalRequest);
      } catch {
        pendingRequests = [];
        const authStore = useAuthStore();
        authStore.logout();
        useToast().warning("Session expired — please log in again.");
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
app.use(Toast, {
  position: "top-right",
  timeout: 4000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
  transition: "Vue-Toastification__bounce",
  maxToasts: 3,
  newestOnTop: true,
});

app.mount("#app");
