/**
 * Customer 주문 API 호출 서비스
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
   * 주문 생성 (POST /api/orders)
   */
  async createOrder(orderData) {
    const response = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(orderData),
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
}
