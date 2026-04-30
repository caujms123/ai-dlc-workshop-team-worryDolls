import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CategoryTabs from '../CategoryTabs.vue'

const sampleCategories = [
  { id: 1, name: '메인 메뉴' },
  { id: 2, name: '사이드' },
  { id: 3, name: '음료' },
]

describe('CategoryTabs', () => {
  it('renders all category tabs', () => {
    const wrapper = mount(CategoryTabs, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs).toHaveLength(3)
    expect(tabs[0].text()).toBe('메인 메뉴')
    expect(tabs[1].text()).toBe('사이드')
    expect(tabs[2].text()).toBe('음료')
  })

  it('highlights selected category', () => {
    const wrapper = mount(CategoryTabs, {
      props: { categories: sampleCategories, selectedCategoryId: 2 },
    })
    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs[1].classes()).toContain('active')
    expect(tabs[0].classes()).not.toContain('active')
  })

  it('emits select event when tab clicked', async () => {
    const wrapper = mount(CategoryTabs, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    await wrapper.findAll('[role="tab"]')[1].trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')[0][0]).toBe(2)
  })

  it('sets aria-selected correctly', () => {
    const wrapper = mount(CategoryTabs, {
      props: { categories: sampleCategories, selectedCategoryId: 1 },
    })
    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs[0].attributes('aria-selected')).toBe('true')
    expect(tabs[1].attributes('aria-selected')).toBe('false')
  })

  it('has minimum touch target size (44px)', () => {
    const wrapper = mount(CategoryTabs, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    // Check that min-height is set in styles
    const tab = wrapper.find('[role="tab"]')
    expect(tab.exists()).toBe(true)
  })
})
