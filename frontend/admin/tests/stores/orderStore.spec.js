/**
 * Admin orderStore Pinia Store 단위 테스트
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useOrderStore } from '@/stores/orderStore'

vi.mock('@/services/orderApi', () => ({
  orderApi: {
    getStoreOrders: vi.fn().mockResolvedValue([
      {
        id: 1,
        order_number: 'ORD-20260430-0001',
        table_id: 1,
        total_amount: 16000,
        status: 'PENDING',
        ordered_at: '2026-04-30T12:00:00',
        items: [],
      },
      {
        id: 2,
        order_number: 'ORD-20260430-0002',
        table_id: 1,
        total_amount: 9000,
        status: 'PREPARING',
        ordered_at: '2026-04-30T12:05:00',
        items: [],
      },
    ]),
  },
}))

describe('Admin orderStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('초기 상태가 올바르다', () => {
    const store = useOrderStore()
    expect(store.tables).toEqual([])
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetchStoreOrders가 주문을 테이블별로 그룹화한다', async () => {
    const store = useOrderStore()
    await store.fetchStoreOrders(1)
    expect(store.tables.length).toBe(1)
    expect(store.tables[0].table_id).toBe(1)
    expect(store.tables[0].order_count).toBe(2)
    expect(store.tables[0].total_amount).toBe(25000)
  })

  it('totalOrders가 전체 주문 수를 반환한다', async () => {
    const store = useOrderStore()
    await store.fetchStoreOrders(1)
    expect(store.totalOrders).toBe(2)
  })
})
