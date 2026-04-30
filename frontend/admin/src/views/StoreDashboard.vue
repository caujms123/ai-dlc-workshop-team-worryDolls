<template>
  <div class="store-dashboard">
    <div class="page-header">
      <h1>매장 관리</h1>
      <button class="btn btn-primary" @click="openCreateForm">+ 매장 등록</button>
    </div>

    <div v-if="isLoading" class="loading">로딩 중...</div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>매장 코드</th>
          <th>매장명</th>
          <th>주소</th>
          <th>전화번호</th>
          <th>상태</th>
          <th>등록일</th>
          <th>관리</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="store in stores" :key="store.id">
          <td>{{ store.id }}</td>
          <td><code>{{ store.store_code }}</code></td>
          <td>{{ store.name }}</td>
          <td>{{ store.address || '-' }}</td>
          <td>{{ store.phone || '-' }}</td>
          <td>
            <span :class="['badge', store.is_active ? 'badge-active' : 'badge-inactive']">
              {{ store.is_active ? '활성' : '비활성' }}
            </span>
          </td>
          <td>{{ formatDate(store.created_at) }}</td>
          <td>
            <button class="btn btn-secondary btn-sm" @click="openEditForm(store)">수정</button>
          </td>
        </tr>
        <tr v-if="stores.length === 0">
          <td colspan="8" class="empty-row">등록된 매장이 없습니다.</td>
        </tr>
      </tbody>
    </table>

    <!-- 매장 등록/수정 모달 -->
    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal" role="dialog" aria-labelledby="form-title">
        <h2 id="form-title">{{ isEdit ? '매장 수정' : '매장 등록' }}</h2>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div v-if="!isEdit" class="form-group">
            <label for="storeCode">매장 코드</label>
            <input
              id="storeCode"
              v-model="formData.store_code"
              type="text"
              required
              minlength="3"
              maxlength="30"
              pattern="[a-z0-9\-]+"
              placeholder="영문소문자, 숫자, 하이픈"
            />
          </div>
          <div class="form-group">
            <label for="storeName">매장명</label>
            <input id="storeName" v-model="formData.name" type="text" required minlength="2" maxlength="100" />
          </div>
          <div class="form-group">
            <label for="storeAddress">주소</label>
            <input id="storeAddress" v-model="formData.address" type="text" maxlength="255" />
          </div>
          <div class="form-group">
            <label for="storePhone">전화번호</label>
            <input id="storePhone" v-model="formData.phone" type="text" maxlength="20" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeForm">취소</button>
            <button type="submit" class="btn btn-primary" :disabled="isSaving">
              {{ isSaving ? '저장 중...' : '저장' }}
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
const isLoading = ref(false)
const showForm = ref(false)
const isEdit = ref(false)
const isSaving = ref(false)
const editingStoreId = ref(null)
const formData = ref({ store_code: '', name: '', address: '', phone: '' })

onMounted(() => fetchStores())

async function fetchStores() {
  isLoading.value = true
  try {
    const { data } = await api.get('/stores')
    stores.value = data
  } catch (err) {
    alert('매장 목록을 불러오는데 실패했습니다.')
  } finally {
    isLoading.value = false
  }
}

function openCreateForm() {
  isEdit.value = false
  editingStoreId.value = null
  formData.value = { store_code: '', name: '', address: '', phone: '' }
  showForm.value = true
}

function openEditForm(store) {
  isEdit.value = true
  editingStoreId.value = store.id
  formData.value = { name: store.name, address: store.address || '', phone: store.phone || '' }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

async function handleSubmit() {
  isSaving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/stores/${editingStoreId.value}`, formData.value)
    } else {
      await api.post('/stores', formData.value)
    }
    closeForm()
    await fetchStores()
  } catch (err) {
    alert(err.response?.data?.detail || '저장에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ko-KR')
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
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
  color: #374151;
}

.data-table code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-active {
  background: #d1fae5;
  color: #065f46;
}

.badge-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}

.empty-row {
  text-align: center;
  color: #9ca3af;
  padding: 40px 16px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 100%;
  max-width: 480px;
}

.modal h2 {
  font-size: 20px;
  margin-bottom: 20px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #4f46e5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}
</style>
