<template>
  <div class="admin-manager">
    <div class="page-header">
      <h1>관리자 관리</h1>
    </div>

    <!-- 매장 선택 -->
    <div class="filter-bar">
      <label for="storeSelect">매장 선택:</label>
      <select id="storeSelect" v-model="selectedStoreId" @change="fetchAdmins">
        <option :value="null" disabled>매장을 선택하세요</option>
        <option v-for="store in stores" :key="store.id" :value="store.id">
          {{ store.name }} ({{ store.store_code }})
        </option>
      </select>
      <button
        v-if="selectedStoreId"
        class="btn btn-primary"
        @click="openCreateForm"
      >
        + 관리자 생성
      </button>
    </div>

    <div v-if="isLoading" class="loading">로딩 중...</div>

    <table v-else-if="selectedStoreId" class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>사용자명</th>
          <th>역할</th>
          <th>상태</th>
          <th>등록일</th>
          <th>관리</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="admin in admins" :key="admin.id">
          <td>{{ admin.id }}</td>
          <td>{{ admin.username }}</td>
          <td>{{ admin.role === 'SUPER_ADMIN' ? '슈퍼 관리자' : '매장 관리자' }}</td>
          <td>
            <span :class="['badge', admin.is_active ? 'badge-active' : 'badge-inactive']">
              {{ admin.is_active ? '활성' : '비활성' }}
            </span>
          </td>
          <td>{{ formatDate(admin.created_at) }}</td>
          <td>
            <button
              class="btn btn-sm"
              :class="admin.is_active ? 'btn-danger' : 'btn-primary'"
              @click="toggleStatus(admin)"
            >
              {{ admin.is_active ? '비활성화' : '활성화' }}
            </button>
          </td>
        </tr>
        <tr v-if="admins.length === 0">
          <td colspan="6" class="empty-row">등록된 관리자가 없습니다.</td>
        </tr>
      </tbody>
    </table>

    <div v-else class="empty-state">매장을 선택해주세요.</div>

    <!-- 관리자 생성 모달 -->
    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal" role="dialog" aria-labelledby="admin-form-title">
        <h2 id="admin-form-title">관리자 생성</h2>
        <form @submit.prevent="handleCreate" class="modal-form">
          <div class="form-group">
            <label for="adminUsername">사용자명</label>
            <input
              id="adminUsername"
              v-model="formData.username"
              type="text"
              required
              minlength="2"
              maxlength="50"
            />
          </div>
          <div class="form-group">
            <label for="adminPassword">비밀번호</label>
            <input
              id="adminPassword"
              v-model="formData.password"
              type="password"
              required
              minlength="8"
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeForm">취소</button>
            <button type="submit" class="btn btn-primary" :disabled="isSaving">
              {{ isSaving ? '생성 중...' : '생성' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const stores = ref([])
const admins = ref([])
const selectedStoreId = ref(null)
const isLoading = ref(false)
const showForm = ref(false)
const isSaving = ref(false)
const formData = ref({ username: '', password: '' })

onMounted(fetchStores)

async function fetchStores() {
  try {
    const { data } = await api.get('/stores')
    stores.value = data
  } catch {
    alert('매장 목록을 불러오는데 실패했습니다.')
  }
}

async function fetchAdmins() {
  if (!selectedStoreId.value) return
  isLoading.value = true
  try {
    const { data } = await api.get(`/stores/${selectedStoreId.value}/admins`)
    admins.value = data
  } catch {
    alert('관리자 목록을 불러오는데 실패했습니다.')
  } finally {
    isLoading.value = false
  }
}

function openCreateForm() {
  formData.value = { username: '', password: '' }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

async function handleCreate() {
  isSaving.value = true
  try {
    await api.post(`/stores/${selectedStoreId.value}/admins`, formData.value)
    closeForm()
    await fetchAdmins()
  } catch (err) {
    alert(err.response?.data?.detail || '생성에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

async function toggleStatus(admin) {
  try {
    await api.patch(`/admins/${admin.id}/status`, { is_active: !admin.is_active })
    await fetchAdmins()
  } catch (err) {
    alert(err.response?.data?.detail || '상태 변경에 실패했습니다.')
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ko-KR')
}
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-bar label {
  font-size: 14px;
  font-weight: 500;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-width: 200px;
}

.data-table {
  width: 100%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-active { background: #d1fae5; color: #065f46; }
.badge-inactive { background: #fee2e2; color: #991b1b; }

.btn-sm { padding: 4px 10px; font-size: 12px; }
.empty-row { text-align: center; color: #9ca3af; padding: 40px 16px; }
.empty-state { text-align: center; color: #9ca3af; padding: 60px; font-size: 16px; }
.loading { text-align: center; padding: 40px; color: #6b7280; }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}

.modal {
  background: white; border-radius: 12px; padding: 32px;
  width: 100%; max-width: 420px;
}

.modal h2 { font-size: 20px; margin-bottom: 20px; }
.modal-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 14px; font-weight: 500; }
.form-group input {
  padding: 10px 12px; border: 1px solid #d1d5db;
  border-radius: 6px; font-size: 14px;
}
.form-group input:focus { outline: none; border-color: #4f46e5; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
</style>
