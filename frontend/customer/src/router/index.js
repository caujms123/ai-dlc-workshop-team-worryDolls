import { createRouter, createWebHistory } from 'vue-router'
import { useTableAuthStore } from '../stores/tableAuth'

const routes = [
  {
    path: '/',
    name: 'ad',
    component: () => import('../views/AdScreen.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/setup',
    name: 'setup',
    component: () => import('../views/TableAuthView.vue'),
  },
  {
    path: '/menu',
    name: 'menu',
    component: () => import('../views/MenuView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('../views/CartView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/order/confirm',
    name: 'orderConfirm',
    component: () => import('../views/OrderConfirmView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/orders',
    name: 'orders',
    component: () => import('../views/OrderHistoryView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const authStore = useTableAuthStore()
    if (!authStore.isAuthenticated) {
      next('/setup')
      return
    }
  }
  next()
})

export default router
