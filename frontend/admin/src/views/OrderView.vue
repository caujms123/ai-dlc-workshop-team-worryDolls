<template>
  <div class="order-monitor" data-testid="order-monitor-view">
    <header class="order-monitor__header">
      <h1>실시간 주문 대시보드</h1>
      <div class="order-monitor__filter">
        <input
          v-model="filterTableNumber"
          type="text"
          placeholder="테이블 번호 검색..."
          class="order-monitor__search"
          data-testid="order-monitor-search-input"
        />
      </div>
    </header>

    <div class="order-monitor__grid" data-testid="order-monitor-grid">
      <TableOrderCard
        v-for="table in filteredTables"
        :key="table.table_id"
        :table-data="table"
        :is-highlighted="highlightedTables.has(table.table_id)"
        data-testid="table-order-card"
        @select="onTableSelect"
      />
      <p v-if="filteredTables.length === 0" class="order-monitor__empty">
        표시할 주문이 없습니다.
      </p>
    </div>

    <OrderDetailPanel
      v-if="selectedTable"
      :table-id="selectedTable.table_id"
      :store-id="storeId"
      data-testid="order-detail-panel"
      @close="selectedTable = null"
      @status-changed="onStatusChanged"
      @order-deleted="onOrderDeleted"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useOrderStore } from '@/stores/orderStore'
import TableOrderCard from '@/components/order/TableOrderCard.vue'
import OrderDetailPanel from '@/components/order/OrderDetailPanel.vue'

const orderStore = useOrderStore()

const filterTableNumber = ref('')
const selectedTable = ref(null)
const highlightedTables = ref(new Set())
const storeId = ref(1) // TODO: 로그인 정보에서 가져오기

const filteredTables = computed(() => {
  const tables = orderStore.tables
  if (!filterTableNumber.value) return tables
  return tables.filter((t) =>
    String(t.table_number).includes(filterTableNumber.value)
  )
})

function onTableSelect(tableData) {
  selectedTable.value = tableData
}

function onStatusChanged() {
  // SSE로 자동 업데이트되므로 추가 작업 불필요
}

function onOrderDeleted() {
  // SSE로 자동 업데이트되므로 추가 작업 불필요
}

function highlightTable(tableId) {
  highlightedTables.value.add(tableId)
  setTimeout(() => {
    highlightedTables.value.delete(tableId)
  }, 3000)
}

onMounted(() => {
  orderStore.connectSSE(storeId.value)
  orderStore.fetchStoreOrders(storeId.value)

  // SSE 이벤트 핸들러 등록
  orderStore.onNewOrder = (data) => {
    highlightTable(data.table_id)
  }
})

onUnmounted(() => {
  orderStore.disconnectSSE()
})
</script>

<style scoped>
.order-monitor {
  padding: 1rem;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.order-monitor__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.order-monitor__header h1 {
  font-size: 1.5rem;
  font-weight: 700;
}

.order-monitor__search {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  width: 200px;
}

.order-monitor__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  flex: 1;
  overflow-y: auto;
}

.order-monitor__empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #999;
  padding: 2rem;
}
</style>
