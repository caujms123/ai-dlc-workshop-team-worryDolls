/**
 * Customer OrderHistoryView 단위 테스트
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// vue-router mock
vi.mock('vue-router', () => ({
  useRouter: () => ({ back: vi.fn() }),
}))

vi.mock('@/services/orderApi', () => ({
  orderApi: {
    getTableOrders: vi.fn().mockResolvedValue([
      {
        id: 1,
        order_number: 'ORD-20260430-0001',
        status: 'PENDING',
        total_amount: 16000,
        ordered_at: '2026-04-30T12:00:00',
        items: [{ id: 1, menu_name: '김치찌개', quantity: 2, subtotal: 16000 }],
      },
    ]),
  },
}))

// EventSource mock
global.EventSource = vi.fn(() => ({
  addEventListener: vi.fn(),
  close: vi.fn(),
  onerror: null,
}))

import OrderHistoryView from '@/views/OrderHistoryView.vue'

describe('Customer OrderHistoryView', () => {
  it('주문 내역 화면이 렌더링된다', () => {
    const wrapper = mount(OrderHistoryView)
    expect(wrapper.find('[data-testid="order-history-view"]').exists()).toBe(true)
  })

  it('뒤로 버튼이 존재한다', () => {
    const wrapper = mount(OrderHistoryView)
    expect(wrapper.find('[data-testid="order-history-back-btn"]').exists()).toBe(true)
  })
})
