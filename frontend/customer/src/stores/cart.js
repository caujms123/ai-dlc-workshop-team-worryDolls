import { defineStore } from 'pinia'

const CART_STORAGE_KEY = 'table_order_cart'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || '[]'),
  }),

  getters: {
    totalAmount: (state) => {
      return state.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
    },
    itemCount: (state) => {
      return state.items.reduce((sum, item) => sum + item.quantity, 0)
    },
    isEmpty: (state) => state.items.length === 0,
  },

  actions: {
    addItem(menu) {
      const existing = this.items.find((i) => i.menuId === menu.id)
      if (existing) {
        existing.quantity++
      } else {
        this.items.push({
          menuId: menu.id,
          menuName: menu.name,
          price: menu.price,
          quantity: 1,
          imageUrl: menu.image_path || null,
        })
      }
      this._persist()
    },

    removeItem(menuId) {
      this.items = this.items.filter((i) => i.menuId !== menuId)
      this._persist()
    },

    updateQuantity(menuId, quantity) {
      if (quantity <= 0) {
        this.removeItem(menuId)
        return
      }
      const item = this.items.find((i) => i.menuId === menuId)
      if (item) {
        item.quantity = quantity
        this._persist()
      }
    },

    clearCart() {
      this.items = []
      this._persist()
    },

    _persist() {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(this.items))
    },
  },
})
