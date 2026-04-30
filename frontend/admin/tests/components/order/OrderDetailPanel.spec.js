/**
 * OrderDetailPanel 컴포넌트 단위 테스트
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import OrderDetailPanel from '@/components/order/OrderDetailPanel.vue'

// orderApi mock
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
    updateOrderStatus: vi.fn().mockResolvedValue({}),
    deleteOrder: vi.fn().mockResolvedValue(null),
    completeTable: vi.fn().mockResolvedValue({}),
    getOrderHistory: vi.fn().mockResolvedValue([]),
  },
}))

describe('OrderDetailPanel', () => {
  it('패널이 렌더링된다', () => {
    const wrapper = mount(OrderDetailPanel, {
      props: { tableId: 1, storeId: 1 },
    })
    expect(wrapper.find('[data-testid="order-detail-panel"]').exists()).toBe(true)
  })

  it('닫기 버튼 클릭 시 close 이벤트를 발생시킨다', async () => {
    const wrapper = mount(OrderDetailPanel, {
      props: { tableId: 1, storeId: 1 },
    })
    await wrapper.find('[data-testid="order-panel-close-btn"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('이용 완료 버튼이 존재한다', () => {
    const wrapper = mount(OrderDetailPanel, {
      props: { tableId: 1, storeId: 1 },
    })
    expect(wrapper.find('[data-testid="order-panel-complete-btn"]').exists()).toBe(true)
  })

  it('과거 내역 토글 버튼이 존재한다', () => {
    const wrapper = mount(OrderDetailPanel, {
      props: { tableId: 1, storeId: 1 },
    })
    const btn = wrapper.find('[data-testid="order-panel-history-btn"]')
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toContain('과거 내역')
  })
})
