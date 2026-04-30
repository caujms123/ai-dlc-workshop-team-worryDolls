/**
 * Vue Router 설정.
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('../views/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/stores',
      },
      {
        path: 'stores',
        name: 'Stores',
        component: () => import('../views/StoreDashboard.vue'),
        meta: { roles: ['SUPER_ADMIN'] },
      },
      {
        path: 'admins',
        name: 'Admins',
        component: () => import('../views/AdminManagerView.vue'),
        meta: { roles: ['SUPER_ADMIN'] },
      },
      {
        path: 'advertisements',
        name: 'Advertisements',
        component: () => import('../views/AdManagerView.vue'),
        meta: { roles: ['SUPER_ADMIN'] },
      },
      {
        path: 'menu',
        name: 'MenuManagement',
        component: () => import('../views/MenuView.vue'),
        meta: { roles: ['SUPER_ADMIN', 'STORE_ADMIN'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.requiresAuth === false && authStore.isAuthenticated) {
    return next('/')
  }

  if (to.meta.roles && !to.meta.roles.includes(authStore.user?.role)) {
    return next('/')
  }

  next()
})

export default router
