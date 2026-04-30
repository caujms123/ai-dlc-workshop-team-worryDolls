/**
 * Admin OrderView 단위 테스트
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import OrderView from '@/views/OrderView.vue'

// 하위 컴포넌트 stub
vi.mock('@/components/order/TableOrderCard.vue', () => ({
  default: { template: '<div data-testid="table-order-card" />', props: ['tableData', 'isHighlighted'] },
}))
vi.mock('@/components/order/OrderDetailPanel.vue', () => ({
  default: { template: '<div data-testid="order-detail-panel" />', props: ['tableId', 'storeId'] },
}))

// orderStore mock
vi.mock('@/stores/orderStore', () => ({
  useOrderStore: () => ({
    tables: [],
    connectSSE: vi.fn(),
    disconnectSSE: vi.fn(),
    fetchStoreOrders: vi.fn(),
  }),
}))

describe('Admin OrderView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('대시보드가 렌더링된다', () => {
    const wrapper = mount(OrderView)
    expect(wrapper.find('[data-testid="order-monitor-view"]').exists()).toBe(true)
  })

  it('검색 입력 필드가 존재한다', () => {
    const wrapper = mount(OrderView)
    expect(wrapper.find('[data-testid="order-monitor-search-input"]').exists()).toBe(true)
  })

  it('주문이 없을 때 빈 메시지를 표시한다', () => {
    const wrapper = mount(OrderView)
    expect(wrapper.text()).toContain('표시할 주문이 없습니다')
  })
})
