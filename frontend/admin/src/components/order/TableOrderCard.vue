<template>
  <div
    class="table-card"
    :class="{ 'table-card--highlighted': isHighlighted }"
    data-testid="table-order-card"
    @click="$emit('select', tableData)"
  >
    <div class="table-card__header">
      <span class="table-card__number" data-testid="table-card-number">
        테이블 {{ tableData.table_number }}
      </span>
      <span class="table-card__count" data-testid="table-card-order-count">
        {{ tableData.order_count }}건
      </span>
    </div>
    <div class="table-card__amount" data-testid="table-card-total-amount">
      {{ formatCurrency(tableData.total_amount) }}
    </div>
    <ul class="table-card__preview">
      <li
        v-for="order in previewOrders"
        :key="order.id"
        class="table-card__preview-item"
      >
        <span class="table-card__preview-number">{{ order.order_number }}</span>
        <span
          class="table-card__preview-status"
          :class="`status--${order.status.toLowerCase()}`"
        >
          {{ statusLabel(order.status) }}
        </span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tableData: { type: Object, required: true },
  isHighlighted: { type: Boolean, default: false },
})

defineEmits(['select'])

const previewOrders = computed(() => {
  return (props.tableData.latest_orders || []).slice(0, 3)
})

function formatCurrency(amount) {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
  }).format(amount)
}

function statusLabel(status) {
  const labels = { PENDING: '대기중', PREPARING: '준비중', COMPLETED: '완료' }
  return labels[status] || status
}
</script>

<style scoped>
.table-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.table-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.table-card--highlighted {
  animation: pulse 3s ease-in-out;
  border-color: #ff6b35;
  background: #fff8f5;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 107, 53, 0); }
  50% { box-shadow: 0 0 0 8px rgba(255, 107, 53, 0.2); }
}

.table-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.table-card__number {
  font-weight: 700;
  font-size: 1.1rem;
}

.table-card__count {
  color: #666;
  font-size: 0.85rem;
}

.table-card__amount {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.75rem;
}

.table-card__preview {
  list-style: none;
  padding: 0;
  margin: 0;
}

.table-card__preview-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  padding: 0.2rem 0;
  color: #666;
}

.status--pending { color: #f59e0b; }
.status--preparing { color: #3b82f6; }
.status--completed { color: #10b981; }
</style>
