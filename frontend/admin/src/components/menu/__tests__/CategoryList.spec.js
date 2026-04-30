import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CategoryList from '../CategoryList.vue'

const sampleCategories = [
  { id: 1, name: '메인 메뉴', store_id: 1, display_order: 0 },
  { id: 2, name: '사이드', store_id: 1, display_order: 1 },
]

describe('CategoryList', () => {
  it('renders category items', () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    const items = wrapper.findAll('[data-testid="category-item"]')
    expect(items).toHaveLength(2)
    expect(items[0].text()).toContain('메인 메뉴')
    expect(items[1].text()).toContain('사이드')
  })

  it('highlights selected category', () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: 1 },
    })
    const items = wrapper.findAll('[data-testid="category-item"]')
    expect(items[0].classes()).toContain('selected')
    expect(items[1].classes()).not.toContain('selected')
  })

  it('emits select event when category clicked', async () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    await wrapper.findAll('[data-testid="category-item"]')[0].trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')[0][0]).toBe(1)
  })

  it('emits add event when add button clicked', async () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    await wrapper.find('[data-testid="category-add-button"]').trigger('click')
    expect(wrapper.emitted('add')).toBeTruthy()
  })

  it('emits edit event when edit button clicked', async () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    await wrapper.findAll('[data-testid="category-edit-button"]')[0].trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')[0][0]).toEqual(sampleCategories[0])
  })

  it('emits delete event when delete button clicked', async () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    await wrapper.findAll('[data-testid="category-delete-button"]')[0].trigger('click')
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')[0][0]).toBe(1)
  })

  it('shows clear filter button when category is selected', () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: 1 },
    })
    expect(wrapper.find('[data-testid="category-clear-filter-button"]').exists()).toBe(true)
  })

  it('hides clear filter button when no category selected', () => {
    const wrapper = mount(CategoryList, {
      props: { categories: sampleCategories, selectedCategoryId: null },
    })
    expect(wrapper.find('[data-testid="category-clear-filter-button"]').exists()).toBe(false)
  })
})
