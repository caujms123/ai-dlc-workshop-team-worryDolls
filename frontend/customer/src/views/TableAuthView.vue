<template>
  <div class="auth-container">
    <h1>테이블 설정</h1>
    <form @submit.prevent="handleLogin" class="auth-form">
      <div class="form-group">
        <label for="storeCode">매장 코드</label>
        <input
          id="storeCode"
          v-model="storeCode"
          type="text"
          placeholder="매장 코드를 입력하세요"
          required
        />
      </div>
      <div class="form-group">
        <label for="tableNumber">테이블 번호</label>
        <input
          id="tableNumber"
          v-model.number="tableNumber"
          type="number"
          placeholder="테이블 번호"
          min="1"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">비밀번호</label>
        <input
          id="password"
          v-model="password"
          type="password"
          placeholder="비밀번호"
          required
        />
      </div>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <button type="submit" :disabled="isLoading" class="btn-primary">
        {{ isLoading ? '로그인 중...' : '설정 완료' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTableAuthStore } from '../stores/tableAuth'

const router = useRouter()
const authStore = useTableAuthStore()

const storeCode = ref('')
const tableNumber = ref(null)
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  const success = await authStore.autoLogin()
  if (success) {
    router.push('/')
  }
})

async function handleLogin() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    await authStore.login(storeCode.value, tableNumber.value, password.value)
    router.push('/')
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail || '로그인에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>
