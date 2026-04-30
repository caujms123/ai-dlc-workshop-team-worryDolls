import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMenuStore } from '../menuStore'
import * as menuApi from '../../services/menuApi'

vi.mock('../../services/menuApi')

describe('Customer menuStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('loadMenus', () => {
    it('loads menus grouped by category', async () => {
      const mockData = {
        data: [
          {
            category: { id: 1, name: '메인', store_id: 1, display_order: 0 },
            menus: [
              { id: 1, name: '김치찌개', price: 9000, description: null, image_path: null },
              { id: 2, name: '된장찌개', price: 8000, description: null, image_path: null },
            ],
          },
          {
            category: { id: 2, name: '사이드', store_id: 1, display_order: 1 },
            menus: [
              { id: 3, name: '감자튀김', price: 5000, description: null, image_path: null },
            ],
          },
        ],
      }
      menuApi.getCustomerMenus.mockResolvedValue(mockData)

      const store = useMenuStore()
      await store.loadMenus(1)

      expect(store.categoriesWithMenus).toHaveLength(2)
      expect(store.categories).toHaveLength(2)
      expect(store.isLoading).toBe(false)
    })

    it('auto-selects first category', async () => {
      const mockData = {
        data: [
          {
            category: { id: 1, name: '메인' },
            menus: [{ id: 1, name: '김치찌개', price: 9000 }],
          },
        ],
      }
      menuApi.getCustomerMenus.mockResolvedValue(mockData)

      const store = useMenuStore()
      await store.loadMenus(1)

      expect(store.selectedCategoryId).toBe(1)
    })

    it('handles error', async () => {
      menuApi.getCustomerMenus.mockRejectedValue(new Error('Network error'))

      const store = useMenuStore()
      await store.loadMenus(1)

      expect(store.error).toBe('메뉴를 불러오는데 실패했습니다.')
    })
  })

  describe('currentMenus', () => {
    it('returns menus for selected category', async () => {
      const mockData = {
        data: [
          {
            category: { id: 1, name: '메인' },
            menus: [{ id: 1, name: '김치찌개', price: 9000 }],
          },
          {
            category: { id: 2, name: '사이드' },
            menus: [{ id: 2, name: '감자튀김', price: 5000 }],
          },
        ],
      }
      menuApi.getCustomerMenus.mockResolvedValue(mockData)

      const store = useMenuStore()
      await store.loadMenus(1)
      store.selectCategory(2)

      expect(store.currentMenus).toHaveLength(1)
      expect(store.currentMenus[0].name).toBe('감자튀김')
    })
  })

  describe('selectMenu / closeMenuDetail', () => {
    it('manages selected menu state', () => {
      const store = useMenuStore()
      const menu = { id: 1, name: '김치찌개', price: 9000 }

      store.selectMenu(menu)
      expect(store.selectedMenu).toEqual(menu)

      store.closeMenuDetail()
      expect(store.selectedMenu).toBeNull()
    })
  })
})
