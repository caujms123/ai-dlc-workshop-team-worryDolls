import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MenuCard from '../MenuCard.vue'

const sampleMenu = {
  id: 1,
  name: '김치찌개',
  price: 9000,
  description: '매콤한 김치찌개',
  image_path: null,
  display_order: 0,
  is_available: true,
}

describe('MenuCard', () => {
  it('renders menu name and price', () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    expect(wrapper.find('[data-testid="menu-card-name"]').text()).toBe('김치찌개')
    expect(wrapper.find('[data-testid="menu-card-price"]').text()).toContain('9,000')
  })

  it('shows availability badge as 판매중', () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    expect(wrapper.find('[data-testid="menu-card-availability"]').text()).toBe('판매중')
  })

  it('shows availability badge as 품절 when unavailable', () => {
    const wrapper = mount(MenuCard, {
      props: { menu: { ...sampleMenu, is_available: false } },
    })
    expect(wrapper.find('[data-testid="menu-card-availability"]').text()).toBe('품절')
  })

  it('emits edit event when edit button clicked', async () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="menu-edit-button"]').trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')[0][0]).toEqual(sampleMenu)
  })

  it('emits delete event when delete button clicked', async () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="menu-delete-button"]').trigger('click')
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')[0][0]).toBe(1)
  })

  it('emits move-up event', async () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="menu-move-up-button"]').trigger('click')
    expect(wrapper.emitted('move-up')).toBeTruthy()
  })

  it('emits move-down event', async () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    await wrapper.find('[data-testid="menu-move-down-button"]').trigger('click')
    expect(wrapper.emitted('move-down')).toBeTruthy()
  })

  it('shows no-image placeholder when image_path is null', () => {
    const wrapper = mount(MenuCard, { props: { menu: sampleMenu } })
    expect(wrapper.find('.no-image').exists()).toBe(true)
  })
})
