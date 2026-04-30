<template>
  <div class="order-confirm" data-testid="order-confirm-view">
    <!-- 주문 성공 화면 -->
    <div v-if="orderResult" class="order-confirm__success" data-testid="order-success">
      <div class="order-confirm__success-icon">✅</div>
      <h2>주문이 완료되었습니다!</h2>
      <p class="order-confirm__order-number" data-testid="order-number">
        주문번호: {{ orderResult.order_number }}
      </p>
      <p class="order-confirm__redirect-msg">
        {{ redirectCountdown }}초 후 메뉴 화면으로 이동합니다...
      </p>
    </div>

    <!-- 주문 확인 화면 -->
    <div v-else class="order-confirm__form">
      <h1>주문 확인</h1>

      <div class="order-confirm__payment-type" data-testid="payment-type-display">
        <span class="order-confirm__label">결제 방식:</span>
        <span class="order-confirm__value">
          {{ paymentType === 'DUTCH_PAY' ? '더치페이 (1/N)' : '단독 계산' }}
        </span>
      </div>

      <div class="order-confirm__items" data-testid="order-items-list">
        <div
          v-for="item in cartItems"
          :key="item.menu_id"
          class="order-confirm__item"
        >
          <span class="order-confirm__item-name">{{ item.menu_name }}</span>
          <span class="order-confirm__item-qty">x{{ item.quantity }}</span>
          <span class="order-confirm__item-price">
            {{ formatCurrency(item.unit_price) }}
          </span>
          <span class="order-confirm__item-subtotal">
            {{ formatCurrency(item.quantity * item.unit_price) }}
          </span>
        </div>
      </div>

      <div class="order-confirm__total" data-testid="order-total">
        <span>총 금액</span>
        <span class="order-confirm__total-amount">
          {{ formatCurrency(totalAmount) }}
        </span>
      </div>

      <div v-if="errorMessage" class="order-confirm__error" data-testid="order-error">
        {{ errorMessage }}
      </div>

      <div class="order-confirm__actions">
        <button
          class="btn btn--secondary"
          data-testid="order-back-btn"
          @click="goBack"
        >
          뒤로
        </button>
        <button
          class="btn btn--primary"
          :disabled="isSubmitting"
          data-testid="order-submit-btn"
          @click="submitOrder"
        >
          {{ isSubmitting ? '주문 중...' : '주문 확정' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { orderApi } from '@/services/orderApi'

const router = useRouter()
const route = useRoute()

// 장바구니 데이터 (route params 또는 localStorage에서)
const cartItems = ref(JSON.parse(route.query.items || localStorage.getItem('cart_items') || '[]'))
const paymentType = ref(route.query.payment_type || localStorage.getItem('payment_type') || 'SINGLE_PAY')
const tableId = ref(Number(localStorage.getItem('table_id') || '1'))

const isSubmitting = ref(false)
const orderResult = ref(null)
const errorMessage = ref('')
const redirectCountdown = ref(5)
let redirectTimer = null

const totalAmount = computed(() =>
  cartItems.value.reduce((sum, item) => sum + item.quantity * item.unit_price, 0)
)

async function submitOrder() {
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    const result = await orderApi.createOrder({
      table_id: tableId.value,
      payment_type: paymentType.value,
      items: cartItems.value.map((item) => ({
        menu_id: item.menu_id,
        quantity: item.quantity,
      })),
    })
    orderResult.value = result
    // 장바구니 비우기
    localStorage.removeItem('cart_items')
    // 5초 후 메뉴 화면으로 리다이렉트
    startRedirectCountdown()
  } catch (error) {
    errorMessage.value = error.message || '주문에 실패했습니다. 다시 시도해주세요.'
  } finally {
    isSubmitting.value = false
  }
}

function startRedirectCountdown() {
  redirectTimer = setInterval(() => {
    redirectCountdown.value -= 1
    if (redirectCountdown.value <= 0) {
      clearInterval(redirectTimer)
      router.push({ name: 'menu' })
    }
  }, 1000)
}

function goBack() {
  router.back()
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
  }).format(amount)
}

onUnmounted(() => {
  if (redirectTimer) clearInterval(redirectTimer)
})
</script>

<style scoped>
.order-confirm {
  padding: 1.5rem;
  max-width: 480px;
  margin: 0 auto;
}

.order-confirm__success {
  text-align: center;
  padding: 3rem 1rem;
}

.order-confirm__success-icon { font-size: 3rem; margin-bottom: 1rem; }
.order-confirm__success h2 { margin-bottom: 0.5rem; }
.order-confirm__order-number { font-size: 1.2rem; font-weight: 700; color: #3b82f6; }
.order-confirm__redirect-msg { color: #888; margin-top: 1rem; }

.order-confirm__form h1 { font-size: 1.4rem; margin-bottom: 1rem; }

.order-confirm__payment-type {
  background: #f8f9fa;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.order-confirm__label { color: #666; }
.order-confirm__value { font-weight: 600; margin-left: 0.5rem; }

.order-confirm__items { margin-bottom: 1rem; }

.order-confirm__item {
  display: grid;
  grid-template-columns: 1fr auto auto auto;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.order-confirm__item-name { font-weight: 500; }
.order-confirm__item-qty { color: #666; }
.order-confirm__item-price { color: #888; font-size: 0.85rem; }
.order-confirm__item-subtotal { font-weight: 600; text-align: right; }

.order-confirm__total {
  display: flex;
  justify-content: space-between;
  padding: 1rem 0;
  border-top: 2px solid #333;
  font-size: 1.1rem;
  font-weight: 700;
}

.order-confirm__total-amount { color: #ef4444; font-size: 1.3rem; }

.order-confirm__error {
  background: #fef2f2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.order-confirm__actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
}

.btn--primary { background: #3b82f6; color: #fff; }
.btn--primary:disabled { background: #93c5fd; cursor: not-allowed; }
.btn--secondary { background: #f3f4f6; color: #333; }
</style>
