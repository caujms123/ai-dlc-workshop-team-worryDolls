import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/menu',
    name: 'MenuBrowser',
    component: () => import('../views/MenuView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
