/**
 * Pinia store for customer menu browsing state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as menuApi from '../services/menuApi'

export const useMenuStore = defineStore('customerMenu', () => {
  // State
  const categoriesWithMenus = ref([])
  const selectedCategoryId = ref(null)
  const selectedMenu = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const categories = computed(() =>
    categoriesWithMenus.value.map((item) => item.category)
  )

  const currentMenus = computed(() => {
    if (!selectedCategoryId.value) {
      return categoriesWithMenus.value.flatMap((item) => item.menus)
    }
    const found = categoriesWithMenus.value.find(
      (item) => item.category.id === selectedCategoryId.value
    )
    return found ? found.menus : []
  })

  // Actions

  /**
   * Load menus grouped by category for a store.
   * @param {number} storeId
   */
  async function loadMenus(storeId) {
    isLoading.value = true
    error.value = null
    try {
      const result = await menuApi.getCustomerMenus(storeId)
      categoriesWithMenus.value = result.data
      // Auto-select first category if available
      if (result.data.length > 0 && !selectedCategoryId.value) {
        selectedCategoryId.value = result.data[0].category.id
      }
    } catch (err) {
      error.value = '메뉴를 불러오는데 실패했습니다.'
      console.error('Failed to load menus:', err)
    } finally {
      isLoading.value = false
    }
  }

  function selectCategory(categoryId) {
    selectedCategoryId.value = categoryId
  }

  function selectMenu(menu) {
    selectedMenu.value = menu
  }

  function closeMenuDetail() {
    selectedMenu.value = null
  }

  return {
    // State
    categoriesWithMenus,
    selectedCategoryId,
    selectedMenu,
    isLoading,
    error,
    // Getters
    categories,
    currentMenus,
    // Actions
    loadMenus,
    selectCategory,
    selectMenu,
    closeMenuDetail,
  }
})
