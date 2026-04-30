/**
 * Customer orderStore Pinia Store 단위 테스트
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useOrderStore } from '@/stores/orderStore'

vi.mock('@/services/orderApi', () => ({
  orderApi: {
    getTableOrders: vi.fn().mockResolvedValue([
      {
        id: 1,
        order_number: 'ORD-20260430-0001',
        status: 'PENDING',
        total_amount: 16000,
      },
    ]),
    createOrder: vi.fn().mockResolvedValue({
      id: 1,
      order_number: 'ORD-20260430-0001',
    }),
  },
}))

// EventSource mock
global.EventSource = vi.fn(() => ({
  addEventListener: vi.fn(),
  close: vi.fn(),
  onerror: null,
}))

describe('Customer orderStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('초기 상태가 올바르다', () => {
    const store = useOrderStore()
    expect(store.orders).toEqual([])
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetchOrders가 주문 목록을 가져온다', async () => {
    const store = useOrderStore()
    await store.fetchOrders(1, 1)
    expect(store.orders.length).toBe(1)
    expect(store.orders[0].order_number).toBe('ORD-20260430-0001')
  })

  it('createOrder가 주문을 생성한다', async () => {
    const store = useOrderStore()
    const result = await store.createOrder({
      table_id: 1,
      payment_type: 'SINGLE_PAY',
      items: [{ menu_id: 1, quantity: 2 }],
    })
    expect(result.order_number).toBe('ORD-20260430-0001')
  })
})
