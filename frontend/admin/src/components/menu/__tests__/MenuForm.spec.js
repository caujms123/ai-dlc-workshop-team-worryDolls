import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MenuForm from '../MenuForm.vue'

const sampleCategories = [
  { id: 1, name: '메인 메뉴', store_id: 1, display_order: 0 },
  { id: 2, name: '사이드', store_id: 1, display_order: 1 },
]

describe('MenuForm', () => {
  it('renders create form when no menu prop', () => {
    const wrapper = mount(MenuForm, {
      props: { menu: null, categories: sampleCategories, storeId: 1 },
    })
    expect(wrapper.text()).toContain('메뉴 등록')
    expect(wrapper.find('[data-testid="menu-form-submit-button"]').text()).toBe('등록')
  })

  it('renders edit form when menu prop provided', () => {
    const menu = {
      id: 1,
      name: '김치찌개',
      price: 9000,
      description: '매콤한 김치찌개',
      category_id: 1,
      image_path: null,
    }
    const wrapper = mount(MenuForm, {
      props: { menu, categories: sampleCategories, storeId: 1 },
    })
    expect(wrapper.text()).toContain('메뉴 수정')
    expect(wrapper.find('[data-testid="menu-name-input"]').element.value).toBe('김치찌개')
    expect(wrapper.find('[data-testid="menu-price-input"]').element.value).toBe('9000')
  })

  it('renders category options', () => {
    const wrapper = mount(MenuForm, {
      props: { menu: null, categories: sampleCategories, storeId: 1 },
    })
    const options = wrapper.find('[data-testid="menu-category-select"]').findAll('option')
    // 1 disabled placeholder + 2 categories
    expect(options).toHaveLength(3)
  })

  it('emits close event when cancel clicked', async () => {
    const wrapper = mount(MenuForm, {
      props: { menu: null, categories: sampleCategories, storeId: 1 },
    })
    await wrapper.find('[data-testid="menu-form-cancel-button"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('emits close event when overlay clicked', async () => {
    const wrapper = mount(MenuForm, {
      props: { menu: null, categories: sampleCategories, storeId: 1 },
    })
    await wrapper.find('[data-testid="menu-form-modal"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
