/**
 * Menu API service for customer frontend.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor for table auth token (Unit 1 integration)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tableToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Get menus grouped by category for customer view.
 * @param {number} storeId
 * @returns {Promise<{data: Array<{category: Object, menus: Array}>}>}
 */
export async function getCustomerMenus(storeId) {
  const { data } = await api.get(`/customer/stores/${storeId}/menus`)
  return data
}
