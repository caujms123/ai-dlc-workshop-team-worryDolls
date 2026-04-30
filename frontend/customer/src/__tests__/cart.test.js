/**
 * Unit 4: 장바구니 Store 단위 테스트
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from '../stores/cart'

// localStorage mock
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => { store[key] = value }),
    removeItem: vi.fn((key) => { delete store[key] }),
    clear: vi.fn(() => { store = {} }),
  }
})()
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

describe('CartStore', () => {
  let cartStore

  beforeEach(() => {
    localStorageMock.clear()
    setActivePinia(createPinia())
    cartStore = useCartStore()
  })

  describe('addItem', () => {
    it('새 메뉴를 장바구니에 추가한다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000, image_path: null })

      expect(cartStore.items).toHaveLength(1)
      expect(cartStore.items[0].menuId).toBe(1)
      expect(cartStore.items[0].quantity).toBe(1)
    })

    it('동일 메뉴 추가 시 수량이 증가한다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })

      expect(cartStore.items).toHaveLength(1)
      expect(cartStore.items[0].quantity).toBe(2)
    })

    it('localStorage에 저장된다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'table_order_cart',
        expect.any(String)
      )
    })
  })

  describe('updateQuantity', () => {
    it('수량을 변경한다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      cartStore.updateQuantity(1, 3)

      expect(cartStore.items[0].quantity).toBe(3)
    })

    it('수량 0이면 항목이 제거된다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      cartStore.updateQuantity(1, 0)

      expect(cartStore.items).toHaveLength(0)
    })
  })

  describe('removeItem', () => {
    it('항목을 제거한다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      cartStore.addItem({ id: 2, name: '된장찌개', price: 7000 })
      cartStore.removeItem(1)

      expect(cartStore.items).toHaveLength(1)
      expect(cartStore.items[0].menuId).toBe(2)
    })
  })

  describe('clearCart', () => {
    it('장바구니를 비운다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      cartStore.addItem({ id: 2, name: '된장찌개', price: 7000 })
      cartStore.clearCart()

      expect(cartStore.items).toHaveLength(0)
      expect(cartStore.isEmpty).toBe(true)
    })
  })

  describe('getters', () => {
    it('totalAmount를 올바르게 계산한다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      cartStore.addItem({ id: 2, name: '된장찌개', price: 7000 })
      cartStore.updateQuantity(1, 2)

      // 8000*2 + 7000*1 = 23000
      expect(cartStore.totalAmount).toBe(23000)
    })

    it('itemCount를 올바르게 계산한다', () => {
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      cartStore.addItem({ id: 2, name: '된장찌개', price: 7000 })
      cartStore.updateQuantity(1, 3)

      // 3 + 1 = 4
      expect(cartStore.itemCount).toBe(4)
    })

    it('isEmpty가 올바르게 동작한다', () => {
      expect(cartStore.isEmpty).toBe(true)
      cartStore.addItem({ id: 1, name: '김치찌개', price: 8000 })
      expect(cartStore.isEmpty).toBe(false)
    })
  })
})
