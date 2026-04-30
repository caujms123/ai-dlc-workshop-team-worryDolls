/**
 * TableOrderCard 컴포넌트 단위 테스트
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TableOrderCard from '@/components/order/TableOrderCard.vue'

const mockTableData = {
  table_id: 1,
  table_number: 3,
  total_amount: 45000,
  order_count: 3,
  latest_orders: [
    { id: 1, order_number: 'ORD-20260430-0001', status: 'PENDING', total_amount: 16000 },
    { id: 2, order_number: 'ORD-20260430-0002', status: 'PREPARING', total_amount: 29000 },
  ],
}

describe('TableOrderCard', () => {
  it('테이블 번호를 표시한다', () => {
    const wrapper = mount(TableOrderCard, {
      props: { tableData: mockTableData, isHighlighted: false },
    })
    expect(wrapper.find('[data-testid="table-card-number"]').text()).toContain('3')
  })

  it('주문 수를 표시한다', () => {
    const wrapper = mount(TableOrderCard, {
      props: { tableData: mockTableData, isHighlighted: false },
    })
    expect(wrapper.find('[data-testid="table-card-order-count"]').text()).toContain('3건')
  })

  it('총 주문액을 표시한다', () => {
    const wrapper = mount(TableOrderCard, {
      props: { tableData: mockTableData, isHighlighted: false },
    })
    expect(wrapper.find('[data-testid="table-card-total-amount"]').text()).toContain('45,000')
  })

  it('클릭 시 select 이벤트를 발생시킨다', async () => {
    const wrapper = mount(TableOrderCard, {
      props: { tableData: mockTableData, isHighlighted: false },
    })
    await wrapper.trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')[0][0]).toEqual(mockTableData)
  })

  it('하이라이트 상태에서 CSS 클래스가 적용된다', () => {
    const wrapper = mount(TableOrderCard, {
      props: { tableData: mockTableData, isHighlighted: true },
    })
    expect(wrapper.classes()).toContain('table-card--highlighted')
  })

  it('최신 주문 미리보기를 최대 3개까지 표시한다', () => {
    const wrapper = mount(TableOrderCard, {
      props: { tableData: mockTableData, isHighlighted: false },
    })
    const previews = wrapper.findAll('.table-card__preview-item')
    expect(previews.length).toBe(2) // mockData에 2개만 있음
  })
})
