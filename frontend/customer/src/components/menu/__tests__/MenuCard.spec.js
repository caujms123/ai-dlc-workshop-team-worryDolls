import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MenuCard from '../MenuCard.vue'

const sampleMenu = {
  id: 1,
  name: '김치찌개',
  price: 9000,
  description: '매콤한 김치찌개',
  image_path: null,
}

describe('Customer MenuCard', () => {
  it('renders menu name and price', () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    expect(wrapper.find('[data-testid="customer-menu-card-name"]').text()).toBe('김치찌개')
    expect(wrapper.find('[data-testid="customer-menu-card-price"]').text()).toContain('9,000')
  })

  it('emits select event when card clicked', async () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="customer-menu-card"]').trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')[0][0]).toEqual(sampleMenu)
  })

  it('shows emoji placeholder when no image', () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    expect(wrapper.find('.no-image').exists()).toBe(true)
  })

  it('renders image when image_path provided', () => {
    const menuWithImage = { ...sampleMenu, image_path: 'menus/1/test.jpg' }
    const wrapper = mount(MenuCard, { props: { menu: menuWithImage } })
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('loading')).toBe('lazy')
  })

  it('has proper aria-label for accessibility', () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    const card = wrapper.find('[data-testid="customer-menu-card"]')
    expect(card.attributes('aria-label')).toContain('김치찌개')
    expect(card.attributes('aria-label')).toContain('9,000')
  })
})
