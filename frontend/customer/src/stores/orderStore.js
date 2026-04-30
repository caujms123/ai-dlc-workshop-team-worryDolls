/**
 * Customer 주문 Pinia Store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { orderApi } from '@/services/orderApi'

export const useOrderStore = defineStore('customerOrder', () => {
  const orders = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  let sseConnection = null

  async function fetchOrders(tableId, sessionId) {
    isLoading.value = true
    error.value = null
    try {
      orders.value = await orderApi.getTableOrders(tableId, sessionId)
    } catch (err) {
      error.value = err.message
    } finally {
      isLoading.value = false
    }
  }

  async function createOrder(orderData) {
    try {
      const result = await orderApi.createOrder(orderData)
      return result
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  function connectSSE(tableId) {
    if (sseConnection) sseConnection.close()
    const url = `/api/sse/customer/tables/${tableId}/orders`
    sseConnection = new EventSource(url)

    sseConnection.addEventListener('order_status_changed', (event) => {
      const data = JSON.parse(event.data)
      const order = orders.value.find((o) => o.id === data.order_id)
      if (order) order.status = data.new_status
    })

    sseConnection.onerror = () => {
      console.warn('고객 SSE 연결 오류')
    }
  }

  function disconnectSSE() {
    if (sseConnection) {
      sseConnection.close()
      sseConnection = null
    }
  }

  return {
    orders,
    isLoading,
    error,
    fetchOrders,
    createOrder,
    connectSSE,
    disconnectSSE,
  }
})
