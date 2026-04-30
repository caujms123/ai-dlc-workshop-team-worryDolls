<template>
  <div class="order-panel" data-testid="order-detail-panel">
    <div class="order-panel__overlay" @click="$emit('close')" />
    <div class="order-panel__content">
      <header class="order-panel__header">
        <h2>테이블 {{ tableId }} - 주문 상세</h2>
        <button
          class="order-panel__close-btn"
          data-testid="order-panel-close-btn"
          @click="$emit('close')"
        >
          ✕
        </button>
      </header>

      <div class="order-panel__actions">
        <button
          class="btn btn--danger"
          data-testid="order-panel-complete-btn"
          @click="confirmComplete"
        >
          이용 완료
        </button>
        <button
          class="btn btn--secondary"
          data-testid="order-panel-history-btn"
          @click="toggleHistory"
        >
          {{ showHistory ? '현재 주문' : '과거 내역' }}
        </button>
      </div>

      <!-- 날짜 필터 (과거 내역) -->
      <div v-if="showHistory" class="order-panel__date-filter">
        <input
          v-model="dateFilter"
          type="date"
          data-testid="order-panel-date-filter"
        />
      </div>

      <!-- 현재 주문 목록 -->
      <div v-if="!showHistory" class="order-panel__list">
        <div
          v-for="order in orders"
          :key="order.id"
          class="order-card"
          data-testid="order-card"
        >
          <div class="order-card__header">
            <span class="order-card__number">{{ order.order_number }}</span>
            <span
              class="order-card__status"
              :class="`status--${order.status.toLowerCase()}`"
            >
              {{ statusLabel(order.status) }}
            </span>
          </div>
          <div class="order-card__time">
            {{ formatTime(order.ordered_at) }}
          </div>
          <ul class="order-card__items">
            <li v-for="item in order.items" :key="item.id">
              {{ item.menu_name }} x{{ item.quantity }}
              ({{ formatCurrency(item.subtotal) }})
            </li>
          </ul>
          <div class="order-card__footer">
            <span class="order-card__total">
              {{ formatCurrency(order.total_amount) }}
            </span>
            <div class="order-card__buttons">
              <button
                v-if="order.status === 'PENDING'"
                class="btn btn--primary btn--sm"
                data-testid="order-card-prepare-btn"
                @click="changeStatus(order.id, 'PREPARING')"
              >
                준비 시작
              </button>
              <button
                v-if="order.status === 'PREPARING'"
                class="btn btn--success btn--sm"
                data-testid="order-card-complete-btn"
                @click="changeStatus(order.id, 'COMPLETED')"
              >
                완료
              </button>
              <button
                class="btn btn--danger btn--sm"
                data-testid="order-card-delete-btn"
                @click="confirmDelete(order.id)"
              >
                삭제
              </button>
            </div>
          </div>
        </div>
        <p v-if="orders.length === 0" class="order-panel__empty">
          현재 주문이 없습니다.
        </p>
      </div>

      <!-- 과거 내역 목록 -->
      <div v-if="showHistory" class="order-panel__list">
        <div
          v-for="history in historyOrders"
          :key="history.id"
          class="order-card order-card--history"
          data-testid="history-card"
        >
          <div class="order-card__header">
            <span class="order-card__number">{{ history.order_number }}</span>
            <span class="order-card__time">
              {{ formatTime(history.completed_at) }}
            </span>
          </div>
          <div class="order-card__total">
            {{ formatCurrency(history.total_amount) }}
          </div>
        </div>
        <p v-if="historyOrders.length === 0" class="order-panel__empty">
          과거 내역이 없습니다.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { orderApi } from '@/services/orderApi'

const props = defineProps({
  tableId: { type: Number, required: true },
  storeId: { type: Number, required: true },
})

const emit = defineEmits(['close', 'statusChanged', 'orderDeleted'])

const orders = ref([])
const showHistory = ref(false)
const historyOrders = ref([])
const dateFilter = ref('')

async function fetchOrders() {
  try {
    // TODO: session_id를 실제 세션에서 가져오기
    orders.value = await orderApi.getTableOrders(props.tableId, 1)
  } catch (error) {
    console.error('주문 조회 실패:', error)
  }
}

async function fetchHistory() {
  try {
    historyOrders.value = await orderApi.getOrderHistory(
      props.tableId,
      dateFilter.value || undefined
    )
  } catch (error) {
    console.error('이력 조회 실패:', error)
  }
}

async function changeStatus(orderId, newStatus) {
  try {
    await orderApi.updateOrderStatus(orderId, newStatus)
    emit('statusChanged')
    await fetchOrders()
  } catch (error) {
    console.error('상태 변경 실패:', error)
    alert('상태 변경에 실패했습니다.')
  }
}

async function confirmDelete(orderId) {
  if (!confirm('이 주문을 삭제하시겠습니까?')) return
  try {
    await orderApi.deleteOrder(orderId)
    emit('orderDeleted')
    await fetchOrders()
  } catch (error) {
    console.error('주문 삭제 실패:', error)
    alert('주문 삭제에 실패했습니다.')
  }
}

async function confirmComplete() {
  if (!confirm('이 테이블의 이용을 완료하시겠습니까? 모든 주문이 이력으로 이동됩니다.')) return
  try {
    await orderApi.completeTable(props.tableId, 1) // TODO: session_id
    emit('close')
  } catch (error) {
    console.error('이용 완료 실패:', error)
    alert('이용 완료 처리에 실패했습니다.')
  }
}

function toggleHistory() {
  showHistory.value = !showHistory.value
  if (showHistory.value) fetchHistory()
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
  }).format(amount)
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function statusLabel(status) {
  const labels = { PENDING: '대기중', PREPARING: '준비중', COMPLETED: '완료' }
  return labels[status] || status
}

watch(dateFilter, () => {
  if (showHistory.value) fetchHistory()
})

onMounted(fetchOrders)
</script>

<style scoped>
.order-panel {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  justify-content: flex-end;
}

.order-panel__overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
}

.order-panel__content {
  position: relative;
  width: 420px;
  max-width: 90vw;
  background: #fff;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  padding: 1.5rem;
  overflow-y: auto;
}

.order-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.order-panel__header h2 { font-size: 1.2rem; }

.order-panel__close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem;
}

.order-panel__actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.order-panel__date-filter { margin-bottom: 1rem; }
.order-panel__date-filter input {
  padding: 0.4rem;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.order-panel__list { display: flex; flex-direction: column; gap: 0.75rem; }
.order-panel__empty { text-align: center; color: #999; padding: 2rem; }

.order-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.75rem;
}

.order-card__header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.order-card__number { font-weight: 600; font-size: 0.9rem; }
.order-card__time { color: #888; font-size: 0.8rem; }

.order-card__items {
  list-style: none;
  padding: 0;
  margin: 0.4rem 0;
  font-size: 0.85rem;
  color: #555;
}

.order-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.order-card__total { font-weight: 700; }
.order-card__buttons { display: flex; gap: 0.3rem; }

.btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
}

.btn--sm { padding: 0.25rem 0.5rem; font-size: 0.75rem; }
.btn--primary { background: #3b82f6; color: #fff; }
.btn--success { background: #10b981; color: #fff; }
.btn--danger { background: #ef4444; color: #fff; }
.btn--secondary { background: #f3f4f6; color: #333; }

.status--pending { color: #f59e0b; font-weight: 600; }
.status--preparing { color: #3b82f6; font-weight: 600; }
.status--completed { color: #10b981; font-weight: 600; }
</style>
