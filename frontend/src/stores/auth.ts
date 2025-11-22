import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials: any) {
    try {
      const formData = new FormData()
      formData.append('username', credentials.email)
      formData.append('password', credentials.password)

      const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/v1/auth/login`, formData)
      token.value = response.data.access_token
      localStorage.setItem('token', token.value as string)
      router.push('/')
    } catch (error) {
      console.error('Login failed', error)
      throw error
    }
  }

  async function signup(userData: any) {
    try {
      await axios.post(`${import.meta.env.VITE_API_URL}/api/v1/auth/signup`, null, {
        params: {
          email: userData.email,
          password: userData.password
        }
      })
      router.push('/login')
    } catch (error) {
      console.error('Signup failed', error)
      throw error
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { user, token, isAuthenticated, login, signup, logout }
})
