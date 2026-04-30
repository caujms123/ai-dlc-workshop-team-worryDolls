import { defineStore } from 'pinia'
import axios from 'axios'

const TOKEN_KEY = 'table_order_token'
const CREDENTIALS_KEY = 'table_order_credentials'

export const useTableAuthStore = defineStore('tableAuth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || null,
    storeId: null,
    tableId: null,
    tableNumber: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(storeCode, tableNumber, password) {
      const response = await axios.post('/api/auth/table/login', {
        store_code: storeCode,
        table_number: tableNumber,
        password: password,
      })

      const data = response.data
      this.token = data.access_token
      this.storeId = data.store_id
      this.tableId = data.table_id
      this.tableNumber = tableNumber

      localStorage.setItem(TOKEN_KEY, data.access_token)
      localStorage.setItem(CREDENTIALS_KEY, JSON.stringify({
        storeCode, tableNumber,
      }))

      // axios 기본 헤더 설정
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    },

    async autoLogin() {
      const token = localStorage.getItem(TOKEN_KEY)
      if (!token) return false

      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const response = await axios.get('/api/auth/me')
        this.token = token
        this.storeId = response.data.store_id
        this.tableId = response.data.id
        this.tableNumber = response.data.table_number
        return true
      } catch {
        // 토큰 만료 시 로그아웃 → 초기 설정 화면으로 이동
        this.logout()
        return false
      }
    },

    logout() {
      this.token = null
      this.storeId = null
      this.tableId = null
      this.tableNumber = null
      localStorage.removeItem(TOKEN_KEY)
      delete axios.defaults.headers.common['Authorization']
    },
  },
})
