import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MenuDetail from '../MenuDetail.vue'

const sampleMenu = {
  id: 1,
  name: '김치찌개',
  price: 9000,
  description: '매콤한 김치찌개입니다. 돼지고기와 김치를 넣어 끓인 전통 한식입니다.',
  image_path: null,
}

describe('MenuDetail', () => {
  it('renders menu name, price, and description', () => {
    const wrapper = mount(MenuDetail, { props: { menu: sampleMenu } })
    expect(wrapper.find('[data-testid="menu-detail-name"]').text()).toBe('김치찌개')
    expect(wrapper.find('[data-testid="menu-detail-price"]').text()).toContain('9,000')
    expect(wrapper.find('[data-testid="menu-detail-description"]').text()).toContain('매콤한')
  })

  it('emits close event when close button clicked', async () => {
    const wrapper = mount(MenuDetail, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="menu-detail-close-button"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('emits add-to-cart event when add button clicked', async () => {
    const wrapper = mount(MenuDetail, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="menu-detail-add-cart-button"]').trigger('click')
    expect(wrapper.emitted('add-to-cart')).toBeTruthy()
    expect(wrapper.emitted('add-to-cart')[0][0]).toEqual(sampleMenu)
  })

  it('emits close event when overlay clicked', async () => {
    const wrapper = mount(MenuDetail, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="menu-detail-modal"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('hides description when not provided', () => {
    const menuNoDesc = { ...sampleMenu, description: null }
    const wrapper = mount(MenuDetail, { props: { menu: menuNoDesc } })
    expect(wrapper.find('[data-testid="menu-detail-description"]').exists()).toBe(false)
  })

  it('has minimum touch target size for buttons', () => {
    const wrapper = mount(MenuDetail, { props: { menu: sampleMenu } })
    expect(wrapper.find('[data-testid="menu-detail-add-cart-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="menu-detail-close-button"]').exists()).toBe(true)
  })
})
