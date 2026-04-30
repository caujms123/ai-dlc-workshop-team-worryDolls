/**
 * Pinia store for menu management state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as menuApi from '../services/menuApi'

export const useMenuStore = defineStore('menu', () => {
  // State
  const categories = ref([])
  const menus = ref([])
  const selectedCategoryId = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const filteredMenus = computed(() => {
    if (!selectedCategoryId.value) return menus.value
    return menus.value.filter((m) => m.category_id === selectedCategoryId.value)
  })

  const categoryCount = computed(() => categories.value.length)
  const menuCount = computed(() => menus.value.length)

  // Actions

  /**
   * Load categories for a store.
   * @param {number} storeId
   */
  async function loadCategories(storeId) {
    isLoading.value = true
    error.value = null
    try {
      const result = await menuApi.getCategories(storeId)
      categories.value = result.categories
    } catch (err) {
      error.value = '카테고리 목록을 불러오는데 실패했습니다.'
      console.error('Failed to load categories:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load menus for a store, optionally filtered by category.
   * @param {number} storeId
   * @param {number|null} categoryId
   */
  async function loadMenus(storeId, categoryId = null) {
    isLoading.value = true
    error.value = null
    try {
      const result = await menuApi.getMenus(storeId, categoryId)
      menus.value = result.menus
    } catch (err) {
      error.value = '메뉴 목록을 불러오는데 실패했습니다.'
      console.error('Failed to load menus:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new category.
   * @param {number} storeId
   * @param {string} name
   */
  async function addCategory(storeId, name) {
    error.value = null
    try {
      const category = await menuApi.createCategory(storeId, name)
      categories.value.push(category)
      return category
    } catch (err) {
      error.value = '카테고리 등록에 실패했습니다.'
      throw err
    }
  }

  /**
   * Update a category.
   * @param {number} categoryId
   * @param {string} name
   */
  async function editCategory(categoryId, name) {
    error.value = null
    try {
      const updated = await menuApi.updateCategory(categoryId, name)
      const idx = categories.value.findIndex((c) => c.id === categoryId)
      if (idx !== -1) categories.value[idx] = updated
      return updated
    } catch (err) {
      error.value = '카테고리 수정에 실패했습니다.'
      throw err
    }
  }

  /**
   * Delete a category.
   * @param {number} categoryId
   */
  async function removeCategory(categoryId) {
    error.value = null
    try {
      await menuApi.deleteCategory(categoryId)
      categories.value = categories.value.filter((c) => c.id !== categoryId)
      if (selectedCategoryId.value === categoryId) {
        selectedCategoryId.value = null
      }
    } catch (err) {
      if (err.response?.status === 409) {
        error.value = err.response.data.detail
      } else {
        error.value = '카테고리 삭제에 실패했습니다.'
      }
      throw err
    }
  }

  /**
   * Create a new menu item.
   * @param {number} storeId
   * @param {Object} menuData
   * @param {File|null} imageFile
   */
  async function addMenu(storeId, menuData, imageFile = null) {
    error.value = null
    try {
      const menu = await menuApi.createMenu(storeId, menuData, imageFile)
      menus.value.push(menu)
      return menu
    } catch (err) {
      error.value = '메뉴 등록에 실패했습니다.'
      throw err
    }
  }

  /**
   * Update a menu item.
   * @param {number} menuId
   * @param {Object} menuData
   * @param {File|null} imageFile
   */
  async function editMenu(menuId, menuData, imageFile = null) {
    error.value = null
    try {
      const updated = await menuApi.updateMenu(menuId, menuData, imageFile)
      const idx = menus.value.findIndex((m) => m.id === menuId)
      if (idx !== -1) menus.value[idx] = updated
      return updated
    } catch (err) {
      error.value = '메뉴 수정에 실패했습니다.'
      throw err
    }
  }

  /**
   * Delete a menu item.
   * @param {number} menuId
   */
  async function removeMenu(menuId) {
    error.value = null
    try {
      await menuApi.deleteMenu(menuId)
      menus.value = menus.value.filter((m) => m.id !== menuId)
    } catch (err) {
      error.value = '메뉴 삭제에 실패했습니다.'
      throw err
    }
  }

  /**
   * Update menu display order.
   * @param {number} menuId
   * @param {number} newOrder
   */
  async function changeMenuOrder(menuId, newOrder) {
    error.value = null
    try {
      const updated = await menuApi.updateMenuOrder(menuId, newOrder)
      const idx = menus.value.findIndex((m) => m.id === menuId)
      if (idx !== -1) menus.value[idx] = updated
      return updated
    } catch (err) {
      error.value = '순서 변경에 실패했습니다.'
      throw err
    }
  }

  function selectCategory(categoryId) {
    selectedCategoryId.value = categoryId
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    categories,
    menus,
    selectedCategoryId,
    isLoading,
    error,
    // Getters
    filteredMenus,
    categoryCount,
    menuCount,
    // Actions
    loadCategories,
    loadMenus,
    addCategory,
    editCategory,
    removeCategory,
    addMenu,
    editMenu,
    removeMenu,
    changeMenuOrder,
    selectCategory,
    clearError,
  }
})
