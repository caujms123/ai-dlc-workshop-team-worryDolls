/**
 * Unit 4: 테이블 인증 Store 단위 테스트
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTableAuthStore } from '../stores/tableAuth'

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

// axios mock
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    defaults: { headers: { common: {} } },
  },
}))

import axios from 'axios'

describe('TableAuthStore', () => {
  let authStore

  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
    setActivePinia(createPinia())
    authStore = useTableAuthStore()
  })

  describe('초기 상태', () => {
    it('토큰이 없으면 미인증 상태이다', () => {
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.token).toBeNull()
    })
  })

  describe('login', () => {
    it('로그인 성공 시 토큰과 정보가 저장된다', async () => {
      axios.post.mockResolvedValue({
        data: {
          access_token: 'test-token',
          store_id: 1,
          table_id: 5,
        },
      })

      await authStore.login('store1', 3, '1234')

      expect(authStore.isAuthenticated).toBe(true)
      expect(authStore.token).toBe('test-token')
      expect(authStore.storeId).toBe(1)
      expect(authStore.tableId).toBe(5)
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'table_order_token',
        'test-token'
      )
    })

    it('로그인 실패 시 에러가 발생한다', async () => {
      axios.post.mockRejectedValue({
        response: { data: { detail: '인증 실패' } },
      })

      await expect(
        authStore.login('store1', 3, 'wrong')
      ).rejects.toBeDefined()

      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('logout', () => {
    it('로그아웃 시 상태가 초기화된다', async () => {
      // 먼저 로그인
      axios.post.mockResolvedValue({
        data: { access_token: 'test-token', store_id: 1, table_id: 5 },
      })
      await authStore.login('store1', 3, '1234')

      // 로그아웃
      authStore.logout()

      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.token).toBeNull()
      expect(authStore.storeId).toBeNull()
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('table_order_token')
    })
  })

  describe('autoLogin', () => {
    it('저장된 토큰이 없으면 false를 반환한다', async () => {
      const result = await authStore.autoLogin()
      expect(result).toBe(false)
    })

    it('유효한 토큰이 있으면 자동 로그인 성공', async () => {
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'table_order_token') return 'valid-token'
        return null
      })

      axios.get.mockResolvedValue({
        data: { id: 5, store_id: 1, table_number: 3 },
      })

      // 새 store 인스턴스 (토큰 있는 상태)
      setActivePinia(createPinia())
      const store = useTableAuthStore()
      store.token = 'valid-token'

      const result = await store.autoLogin()

      expect(result).toBe(true)
      expect(store.storeId).toBe(1)
    })
  })
})
