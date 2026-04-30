/**
 * Customer OrderView (주문 확정) 단위 테스트
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// vue-router mock
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  useRoute: () => ({ query: { items: '[]', payment_type: 'SINGLE_PAY' } }),
}))

vi.mock('@/services/orderApi', () => ({
  orderApi: {
    createOrder: vi.fn().mockResolvedValue({
      id: 1,
      order_number: 'ORD-20260430-0001',
    }),
  },
}))

import OrderView from '@/views/OrderView.vue'

describe('Customer OrderView', () => {
  it('주문 확인 화면이 렌더링된다', () => {
    const wrapper = mount(OrderView)
    expect(wrapper.find('[data-testid="order-confirm-view"]').exists()).toBe(true)
  })

  it('주문 확정 버튼이 존재한다', () => {
    const wrapper = mount(OrderView)
    expect(wrapper.find('[data-testid="order-submit-btn"]').exists()).toBe(true)
  })

  it('뒤로 버튼이 존재한다', () => {
    const wrapper = mount(OrderView)
    expect(wrapper.find('[data-testid="order-back-btn"]').exists()).toBe(true)
  })

  it('장바구니가 비어있을 때 총 금액이 0이다', () => {
    const wrapper = mount(OrderView)
    expect(wrapper.find('[data-testid="order-total"]').text()).toContain('₩0')
  })
})
