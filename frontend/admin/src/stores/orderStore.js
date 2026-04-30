/**
 * Admin 주문 Pinia Store
 * SSE 연결 관리 및 주문 상태 관리
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { orderApi } from '@/services/orderApi'

export const useOrderStore = defineStore('order', () => {
  // ── State ──
  const tables = ref([])
  const selectedTable = ref(null)
  const sseConnection = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // 외부에서 등록 가능한 이벤트 핸들러
  let onNewOrder = null

  // ── Getters ──
  const totalOrders = computed(() =>
    tables.value.reduce((sum, t) => sum + t.order_count, 0)
  )

  // ── Actions ──

  /**
   * 매장 전체 주문 조회 및 테이블별 그룹화
   */
  async function fetchStoreOrders(storeId) {
    isLoading.value = true
    error.value = null
    try {
      const orders = await orderApi.getStoreOrders(storeId)
      tables.value = groupOrdersByTable(orders)
    } catch (err) {
      error.value = err.message
      console.error('매장 주문 조회 실패:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 주문 목록을 테이블별로 그룹화
   */
  function groupOrdersByTable(orders) {
    const tableMap = new Map()
    for (const order of orders) {
      if (!tableMap.has(order.table_id)) {
        tableMap.set(order.table_id, {
          table_id: order.table_id,
          table_number: order.table_id, // TODO: 실제 테이블 번호 매핑
          total_amount: 0,
          order_count: 0,
          latest_orders: [],
        })
      }
      const table = tableMap.get(order.table_id)
      table.total_amount += order.total_amount
      table.order_count += 1
      table.latest_orders.push(order)
    }
    // 최신 주문 3개만 유지
    for (const table of tableMap.values()) {
      table.latest_orders = table.latest_orders
        .sort((a, b) => new Date(b.ordered_at) - new Date(a.ordered_at))
        .slice(0, 3)
    }
    return Array.from(tableMap.values())
  }

  /**
   * SSE 연결 시작
   */
  function connectSSE(storeId) {
    if (sseConnection.value) {
      sseConnection.value.close()
    }

    const token = localStorage.getItem('access_token') || ''
    const url = `/api/sse/admin/stores/${storeId}/orders`
    const eventSource = new EventSource(url)

    eventSource.addEventListener('new_order', (event) => {
      const data = JSON.parse(event.data)
      handleNewOrder(data)
      if (onNewOrder) onNewOrder(data)
    })

    eventSource.addEventListener('order_status_changed', (event) => {
      const data = JSON.parse(event.data)
      handleStatusChanged(data)
    })

    eventSource.addEventListener('order_deleted', (event) => {
      const data = JSON.parse(event.data)
      handleOrderDeleted(data)
    })

    eventSource.addEventListener('table_completed', (event) => {
      const data = JSON.parse(event.data)
      handleTableCompleted(data)
    })

    eventSource.onerror = () => {
      console.warn('SSE 연결 오류, 자동 재연결 시도...')
    }

    sseConnection.value = eventSource
  }

  /**
   * SSE 연결 해제
   */
  function disconnectSSE() {
    if (sseConnection.value) {
      sseConnection.value.close()
      sseConnection.value = null
    }
  }

  // ── SSE 이벤트 핸들러 ──

  function handleNewOrder(data) {
    const tableId = data.table_id
    const existing = tables.value.find((t) => t.table_id === tableId)
    if (existing) {
      existing.total_amount += data.total_amount || 0
      existing.order_count += 1
      existing.latest_orders.unshift({
        id: data.order_id,
        order_number: data.order_number,
        status: data.status,
        total_amount: data.total_amount,
        ordered_at: data.ordered_at,
      })
      if (existing.latest_orders.length > 3) {
        existing.latest_orders.pop()
      }
    } else {
      tables.value.push({
        table_id: tableId,
        table_number: tableId,
        total_amount: data.total_amount || 0,
        order_count: 1,
        latest_orders: [
          {
            id: data.order_id,
            order_number: data.order_number,
            status: data.status,
            total_amount: data.total_amount,
            ordered_at: data.ordered_at,
          },
        ],
      })
    }
  }

  function handleStatusChanged(data) {
    for (const table of tables.value) {
      const order = table.latest_orders.find((o) => o.id === data.order_id)
      if (order) {
        order.status = data.new_status
        break
      }
    }
  }

  function handleOrderDeleted(data) {
    const table = tables.value.find((t) => t.table_id === data.table_id)
    if (table) {
      table.latest_orders = table.latest_orders.filter(
        (o) => o.id !== data.order_id
      )
      table.order_count = Math.max(0, table.order_count - 1)
      // 총액은 서버에서 재계산 필요 → 다음 fetch에서 갱신
    }
  }

  function handleTableCompleted(data) {
    tables.value = tables.value.filter((t) => t.table_id !== data.table_id)
  }

  return {
    tables,
    selectedTable,
    sseConnection,
    isLoading,
    error,
    totalOrders,
    onNewOrder,
    fetchStoreOrders,
    connectSSE,
    disconnectSSE,
  }
})
