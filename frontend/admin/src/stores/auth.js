/**
 * 인증 상태 관리 (Pinia Store).
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token'))
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isSuperAdmin = computed(() => user.value?.role === 'SUPER_ADMIN')
  const isStoreAdmin = computed(() => user.value?.role === 'STORE_ADMIN')
  const currentStoreId = computed(() => user.value?.store_id)

  async function login(credentials) {
    const { data } = await api.post('/auth/admin/login', credentials)
    token.value = data.access_token
    user.value = {
      role: data.role,
      store_id: data.store_id,
    }
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(user.value))

    // /me 호출로 상세 정보 보강
    try {
      const meRes = await api.get('/auth/me')
      user.value = { ...user.value, ...meRes.data }
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch {
      // 무시 - 기본 정보로 진행
    }

    return data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isAuthenticated,
    isSuperAdmin,
    isStoreAdmin,
    currentStoreId,
    login,
    logout,
  }
})
