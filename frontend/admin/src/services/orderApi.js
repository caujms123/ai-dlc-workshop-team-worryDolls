/**
 * Admin 주문 API 호출 서비스
 */

const API_BASE = '/api'

function getAuthHeaders() {
  const token = localStorage.getItem('access_token') || ''
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP ${response.status} 오류`)
  }
  if (response.status === 204) return null
  return response.json()
}

export const orderApi = {
  /**
   * 매장 전체 주문 조회 (GET /api/stores/{storeId}/orders)
   */
  async getStoreOrders(storeId) {
    const response = await fetch(`${API_BASE}/stores/${storeId}/orders`, {
      headers: getAuthHeaders(),
    })
    return handleResponse(response)
  },

  /**
   * 테이블 현재 세션 주문 조회 (GET /api/tables/{tableId}/orders)
   */
  async getTableOrders(tableId, sessionId) {
    const response = await fetch(
      `${API_BASE}/tables/${tableId}/orders?session_id=${sessionId}`,
      { headers: getAuthHeaders() }
    )
    return handleResponse(response)
  },

  /**
   * 주문 상태 변경 (PATCH /api/orders/{orderId}/status)
   */
  async updateOrderStatus(orderId, newStatus) {
    const response = await fetch(`${API_BASE}/orders/${orderId}/status`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ status: newStatus }),
    })
    return handleResponse(response)
  },

  /**
   * 주문 삭제 (DELETE /api/orders/{orderId})
   */
  async deleteOrder(orderId) {
    const response = await fetch(`${API_BASE}/orders/${orderId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    })
    return handleResponse(response)
  },

  /**
   * 이용 완료 처리 (POST /api/tables/{tableId}/complete)
   */
  async completeTable(tableId, sessionId) {
    const response = await fetch(
      `${API_BASE}/tables/${tableId}/complete?session_id=${sessionId}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    )
    return handleResponse(response)
  },

  /**
   * 과거 주문 내역 조회 (GET /api/tables/{tableId}/order-history)
   */
  async getOrderHistory(tableId, dateFrom, dateTo) {
    let url = `${API_BASE}/tables/${tableId}/order-history`
    const params = new URLSearchParams()
    if (dateFrom) params.append('date_from', dateFrom)
    if (dateTo) params.append('date_to', dateTo)
    if (params.toString()) url += `?${params.toString()}`

    const response = await fetch(url, { headers: getAuthHeaders() })
    return handleResponse(response)
  },
}
