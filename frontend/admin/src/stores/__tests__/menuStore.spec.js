import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMenuStore } from '../menuStore'
import * as menuApi from '../../services/menuApi'

vi.mock('../../services/menuApi')

describe('menuStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('loadCategories', () => {
    it('loads categories successfully', async () => {
      const mockCategories = [
        { id: 1, name: '메인', store_id: 1, display_order: 0 },
      ]
      menuApi.getCategories.mockResolvedValue({
        categories: mockCategories,
        total: 1,
      })

      const store = useMenuStore()
      await store.loadCategories(1)

      expect(store.categories).toEqual(mockCategories)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('handles load error', async () => {
      menuApi.getCategories.mockRejectedValue(new Error('Network error'))

      const store = useMenuStore()
      await store.loadCategories(1)

      expect(store.error).toBe('카테고리 목록을 불러오는데 실패했습니다.')
    })
  })

  describe('loadMenus', () => {
    it('loads menus successfully', async () => {
      const mockMenus = [
        { id: 1, name: '김치찌개', price: 9000 },
      ]
      menuApi.getMenus.mockResolvedValue({ menus: mockMenus, total: 1 })

      const store = useMenuStore()
      await store.loadMenus(1)

      expect(store.menus).toEqual(mockMenus)
    })
  })

  describe('addCategory', () => {
    it('adds category to list', async () => {
      const newCategory = { id: 1, name: '메인', store_id: 1, display_order: 0 }
      menuApi.createCategory.mockResolvedValue(newCategory)

      const store = useMenuStore()
      await store.addCategory(1, '메인')

      expect(store.categories).toHaveLength(1)
      expect(store.categories[0].name).toBe('메인')
    })
  })

  describe('removeCategory', () => {
    it('removes category from list', async () => {
      menuApi.deleteCategory.mockResolvedValue()

      const store = useMenuStore()
      store.categories = [
        { id: 1, name: '메인' },
        { id: 2, name: '사이드' },
      ]

      await store.removeCategory(1)

      expect(store.categories).toHaveLength(1)
      expect(store.categories[0].id).toBe(2)
    })

    it('handles 409 conflict error', async () => {
      menuApi.deleteCategory.mockRejectedValue({
        response: { status: 409, data: { detail: '메뉴가 존재합니다' } },
      })

      const store = useMenuStore()
      store.categories = [{ id: 1, name: '메인' }]

      await expect(store.removeCategory(1)).rejects.toBeTruthy()
      expect(store.error).toBe('메뉴가 존재합니다')
    })
  })

  describe('filteredMenus', () => {
    it('returns all menus when no category selected', () => {
      const store = useMenuStore()
      store.menus = [
        { id: 1, category_id: 1 },
        { id: 2, category_id: 2 },
      ]
      store.selectedCategoryId = null

      expect(store.filteredMenus).toHaveLength(2)
    })

    it('filters menus by selected category', () => {
      const store = useMenuStore()
      store.menus = [
        { id: 1, category_id: 1 },
        { id: 2, category_id: 2 },
      ]
      store.selectedCategoryId = 1

      expect(store.filteredMenus).toHaveLength(1)
      expect(store.filteredMenus[0].id).toBe(1)
    })
  })
})
