<template>
  <div class="table-manager">
    <div class="page-header">
      <h2>테이블 관리</h2>
      <button class="btn-primary" @click="showForm = true">+ 테이블 추가</button>
    </div>

    <div class="table-list">
      <div v-for="table in tables" :key="table.id" class="table-card">
        <div class="table-info">
          <span class="table-number">{{ table.table_number }}번 테이블</span>
          <span :class="['status', table.current_session ? 'active' : 'idle']">
            {{ table.current_session ? '이용 중' : '대기 중' }}
          </span>
        </div>
        <div class="table-actions">
          <button class="btn-sm" @click="editTable(table)">설정</button>
          <button
            v-if="table.current_session"
            class="btn-sm btn-danger"
            @click="confirmComplete(table)"
          >
            이용 완료
          </button>
        </div>
      </div>
    </div>

    <!-- 테이블 등록/수정 모달 -->
    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal-content">
        <h3>{{ editingTable ? '테이블 수정' : '테이블 추가' }}</h3>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>테이블 번호</label>
            <input
              v-model.number="formData.table_number"
              type="number"
              min="1"
              :disabled="!!editingTable"
              required
            />
          </div>
          <div class="form-group">
            <label>비밀번호</label>
            <input
              v-model="formData.password"
              type="password"
              minlength="4"
              :required="!editingTable"
              :placeholder="editingTable ? '변경 시에만 입력' : '비밀번호 (4자 이상)'"
            />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="closeForm">취소</button>
            <button type="submit" class="btn-primary">
              {{ editingTable ? '수정' : '등록' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 이용 완료 확인 팝업 -->
    <div v-if="confirmingTable" class="modal-overlay" @click.self="confirmingTable = null">
      <div class="modal-content confirm-modal">
        <h3>이용 완료 확인</h3>
        <p>{{ confirmingTable.table_number }}번 테이블의 이용을 완료하시겠습니까?</p>
        <p class="warning">현재 세션의 주문 내역이 과거 이력으로 이동됩니다.</p>
        <div class="form-actions">
          <button class="btn-secondary" @click="confirmingTable = null">취소</button>
          <button class="btn-primary btn-danger" @click="handleComplete">확인</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tables = ref([])
const showForm = ref(false)
const editingTable = ref(null)
const confirmingTable = ref(null)
const formData = ref({ table_number: null, password: '' })
const errorMessage = ref('')

// TODO: storeId는 인증 정보에서 가져와야 함 (Unit 1 연동)
const storeId = 1

async function fetchTables() {
  try {
    const res = await axios.get(`/api/stores/${storeId}/tables`)
    tables.value = res.data
  } catch (err) {
    errorMessage.value = '테이블 목록을 불러오는데 실패했습니다.'
  }
}

function editTable(table) {
  editingTable.value = table
  formData.value = { table_number: table.table_number, password: '' }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingTable.value = null
  formData.value = { table_number: null, password: '' }
}

async function handleSubmit() {
  try {
    if (editingTable.value) {
      if (formData.value.password) {
        await axios.put(`/api/tables/${editingTable.value.id}`, {
          password: formData.value.password,
        })
      }
    } else {
      await axios.post(`/api/stores/${storeId}/tables`, formData.value)
    }
    closeForm()
    await fetchTables()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || '처리에 실패했습니다.'
  }
}

function confirmComplete(table) {
  confirmingTable.value = table
}

async function handleComplete() {
  try {
    await axios.post(`/api/tables/${confirmingTable.value.id}/complete`)
    confirmingTable.value = null
    await fetchTables()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || '이용 완료 처리에 실패했습니다.'
    confirmingTable.value = null
  }
}

onMounted(fetchTables)
</script>
