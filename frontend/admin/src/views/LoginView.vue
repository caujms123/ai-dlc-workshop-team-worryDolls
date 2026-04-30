<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">테이블오더 관리자</h1>

      <!-- 로그인 유형 탭 -->
      <div class="tab-group">
        <button
          :class="['tab', { active: loginType === 'super' }]"
          @click="loginType = 'super'"
        >
          슈퍼 관리자
        </button>
        <button
          :class="['tab', { active: loginType === 'store' }]"
          @click="loginType = 'store'"
        >
          매장 관리자
        </button>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <!-- 매장 코드 (매장 관리자만) -->
        <div v-if="loginType === 'store'" class="form-group">
          <label for="storeCode">매장 코드</label>
          <input
            id="storeCode"
            v-model="storeCode"
            type="text"
            placeholder="매장 코드 입력"
            required
            minlength="3"
            maxlength="30"
          />
        </div>

        <div class="form-group">
          <label for="username">사용자명</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="사용자명 입력"
            required
            minlength="2"
            maxlength="50"
          />
        </div>

        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="비밀번호 입력"
            required
            minlength="8"
          />
        </div>

        <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>

        <button type="submit" class="btn btn-primary login-btn" :disabled="isLoading">
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginType = ref('super')
const storeCode = ref('')
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const credentials = {
      username: username.value,
      password: password.value,
    }
    if (loginType.value === 'store') {
      credentials.store_code = storeCode.value
    }

    await authStore.login(credentials)
    router.push('/')
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || '로그인에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #1f2937;
}

.tab-group {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.tab {
  flex: 1;
  padding: 10px;
  font-size: 14px;
  font-weight: 500;
  background: #f9fafb;
  color: #6b7280;
  transition: all 0.2s;
}

.tab.active {
  background: #4f46e5;
  color: white;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.error-message {
  color: #ef4444;
  font-size: 14px;
  text-align: center;
}

.login-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  margin-top: 8px;
}
</style>
