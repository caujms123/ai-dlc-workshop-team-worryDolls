<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>테이블오더</h2>
      </div>
      <nav class="sidebar-nav">
        <template v-if="authStore.isSuperAdmin">
          <router-link to="/stores" class="nav-item" active-class="active">
            🏪 매장 관리
          </router-link>
          <router-link to="/admins" class="nav-item" active-class="active">
            👤 관리자 관리
          </router-link>
          <router-link to="/advertisements" class="nav-item" active-class="active">
            📢 광고 관리
          </router-link>
        </template>
        <template v-if="authStore.isStoreAdmin">
          <router-link to="/orders" class="nav-item" active-class="active">
            📋 주문 모니터링
          </router-link>
          <router-link to="/menus" class="nav-item" active-class="active">
            🍽️ 메뉴 관리
          </router-link>
          <router-link to="/tables" class="nav-item" active-class="active">
            🪑 테이블 관리
          </router-link>
        </template>
      </nav>
      <div class="sidebar-footer">
        <button class="nav-item logout-btn" @click="handleLogout">
          🚪 로그아웃
        </button>
      </div>
    </aside>

    <main class="main-content">
      <header class="top-header">
        <div class="user-info">
          <span class="user-role">{{ roleLabel }}</span>
          <span class="user-name">{{ authStore.user?.username || '관리자' }}</span>
        </div>
      </header>
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const roleLabel = computed(() => {
  if (authStore.isSuperAdmin) return '슈퍼 관리자'
  if (authStore.isStoreAdmin) return '매장 관리자'
  return ''
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: #1f2937;
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #374151;
}

.sidebar-header h2 {
  font-size: 18px;
  font-weight: 700;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: block;
  padding: 12px 20px;
  color: #d1d5db;
  font-size: 14px;
  transition: all 0.2s;
  background: none;
  text-align: left;
  width: 100%;
}

.nav-item:hover,
.nav-item.active {
  background: #374151;
  color: white;
}

.sidebar-footer {
  border-top: 1px solid #374151;
  padding: 12px 0;
}

.logout-btn {
  color: #f87171;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.user-role {
  background: #4f46e5;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.page-content {
  flex: 1;
  padding: 24px;
}
</style>
