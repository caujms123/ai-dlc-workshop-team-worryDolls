<template>
  <div class="order-confirm-widget" data-testid="order-confirm-widget">
    <h3>주문 요약</h3>
    <ul class="order-confirm-widget__items">
      <li v-for="item in items" :key="item.menu_id">
        {{ item.menu_name }} x{{ item.quantity }}
        — {{ formatCurrency(item.quantity * item.unit_price) }}
      </li>
    </ul>
    <div class="order-confirm-widget__total">
      총 {{ formatCurrency(total) }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
})

const total = computed(() =>
  props.items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0)
)

function formatCurrency(amount) {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
  }).format(amount)
}
</script>

<style scoped>
.order-confirm-widget { padding: 1rem; background: #f8f9fa; border-radius: 8px; }
.order-confirm-widget h3 { margin-bottom: 0.5rem; font-size: 1rem; }
.order-confirm-widget__items { list-style: none; padding: 0; margin: 0 0 0.5rem; font-size: 0.9rem; }
.order-confirm-widget__total { font-weight: 700; text-align: right; }
</style>
