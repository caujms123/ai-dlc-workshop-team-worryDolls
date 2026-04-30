/**
 * Menu and Category API service for admin frontend.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor for auth token (Unit 1 integration)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ============================================================
// Category API
// ============================================================

/**
 * Get all categories for a store.
 * @param {number} storeId
 * @returns {Promise<{categories: Array, total: number}>}
 */
export async function getCategories(storeId) {
  const { data } = await api.get(`/stores/${storeId}/categories`)
  return data
}

/**
 * Create a new category.
 * @param {number} storeId
 * @param {string} name
 * @returns {Promise<Object>}
 */
export async function createCategory(storeId, name) {
  const { data } = await api.post(`/stores/${storeId}/categories`, { name })
  return data
}

/**
 * Update a category.
 * @param {number} categoryId
 * @param {string} name
 * @returns {Promise<Object>}
 */
export async function updateCategory(categoryId, name) {
  const { data } = await api.put(`/categories/${categoryId}`, { name })
  return data
}

/**
 * Delete a category.
 * @param {number} categoryId
 * @returns {Promise<void>}
 */
export async function deleteCategory(categoryId) {
  await api.delete(`/categories/${categoryId}`)
}

// ============================================================
// Menu API
// ============================================================

/**
 * Get menus for a store, optionally filtered by category.
 * @param {number} storeId
 * @param {number|null} categoryId
 * @returns {Promise<{menus: Array, total: number}>}
 */
export async function getMenus(storeId, categoryId = null) {
  const params = categoryId ? { category_id: categoryId } : {}
  const { data } = await api.get(`/stores/${storeId}/menus`, { params })
  return data
}

/**
 * Create a new menu item with optional image.
 * @param {number} storeId
 * @param {Object} menuData - { name, price, description, category_id }
 * @param {File|null} imageFile
 * @returns {Promise<Object>}
 */
export async function createMenu(storeId, menuData, imageFile = null) {
  const formData = new FormData()
  formData.append('name', menuData.name)
  formData.append('price', String(menuData.price))
  formData.append('category_id', String(menuData.category_id))
  if (menuData.description) {
    formData.append('description', menuData.description)
  }
  if (imageFile) {
    formData.append('image', imageFile)
  }

  const { data } = await api.post(`/stores/${storeId}/menus`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

/**
 * Update a menu item with optional image replacement.
 * @param {number} menuId
 * @param {Object} menuData
 * @param {File|null} imageFile
 * @returns {Promise<Object>}
 */
export async function updateMenu(menuId, menuData, imageFile = null) {
  const formData = new FormData()
  if (menuData.name != null) formData.append('name', menuData.name)
  if (menuData.price != null) formData.append('price', String(menuData.price))
  if (menuData.description != null) formData.append('description', menuData.description)
  if (menuData.category_id != null) formData.append('category_id', String(menuData.category_id))
  if (menuData.is_available != null) formData.append('is_available', String(menuData.is_available))
  if (imageFile) {
    formData.append('image', imageFile)
  }

  const { data } = await api.put(`/menus/${menuId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

/**
 * Delete a menu item.
 * @param {number} menuId
 * @returns {Promise<void>}
 */
export async function deleteMenu(menuId) {
  await api.delete(`/menus/${menuId}`)
}

/**
 * Update a menu's display order.
 * @param {number} menuId
 * @param {number} displayOrder
 * @returns {Promise<Object>}
 */
export async function updateMenuOrder(menuId, displayOrder) {
  const { data } = await api.put(`/menus/${menuId}/order`, {
    display_order: displayOrder,
  })
  return data
}
