<template>
  <div class="ad-manager">
    <div class="page-header">
      <h1>광고 관리</h1>
    </div>

    <!-- 매장 선택 -->
    <div class="filter-bar">
      <label for="adStoreSelect">매장 선택:</label>
      <select id="adStoreSelect" v-model="selectedStoreId" @change="fetchAds">
        <option :value="null" disabled>매장을 선택하세요</option>
        <option v-for="store in stores" :key="store.id" :value="store.id">
          {{ store.name }} ({{ store.store_code }})
        </option>
      </select>
      <label v-if="selectedStoreId" class="upload-btn btn btn-primary">
        📤 이미지 업로드
        <input type="file" accept=".jpg,.jpeg,.png" hidden @change="handleUpload" />
      </label>
    </div>

    <div v-if="isLoading" class="loading">로딩 중...</div>

    <div v-else-if="selectedStoreId" class="ad-grid">
      <div v-for="ad in ads" :key="ad.id" class="ad-card">
        <div class="ad-image-wrapper">
          <img :src="`/uploads/${ad.image_path}`" :alt="`광고 ${ad.display_order + 1}`" />
          <span class="ad-order">{{ ad.display_order + 1 }}</span>
        </div>
        <div class="ad-actions">
          <button class="btn btn-sm btn-secondary" @click="moveOrder(ad, -1)" :disabled="ad.display_order === 0">
            ▲
          </button>
          <button class="btn btn-sm btn-secondary" @click="moveOrder(ad, 1)">
            ▼
          </button>
          <button
            class="btn btn-sm"
            :class="ad.is_active ? 'btn-secondary' : 'btn-primary'"
            @click="toggleStatus(ad)"
          >
            {{ ad.is_active ? '비활성' : '활성' }}
          </button>
          <button class="btn btn-sm btn-danger" @click="handleDelete(ad)">삭제</button>
        </div>
      </div>
      <div v-if="ads.length === 0" class="empty-state">등록된 광고가 없습니다.</div>
    </div>

    <div v-else class="empty-state">매장을 선택해주세요.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const stores = ref([])
const ads = ref([])
const selectedStoreId = ref(null)
const isLoading = ref(false)

onMounted(fetchStores)

async function fetchStores() {
  try {
    const { data } = await api.get('/stores')
    stores.value = data
  } catch {
    alert('매장 목록을 불러오는데 실패했습니다.')
  }
}

async function fetchAds() {
  if (!selectedStoreId.value) return
  isLoading.value = true
  try {
    const { data } = await api.get(`/admin/stores/${selectedStoreId.value}/advertisements`)
    ads.value = data
  } catch {
    alert('광고 목록을 불러오는데 실패했습니다.')
  } finally {
    isLoading.value = false
  }
}

async function handleUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    await api.post(`/stores/${selectedStoreId.value}/advertisements`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    await fetchAds()
  } catch (err) {
    alert(err.response?.data?.detail || '업로드에 실패했습니다.')
  }
  event.target.value = ''
}

async function moveOrder(ad, direction) {
  const newOrder = ad.display_order + direction
  if (newOrder < 0) return
  try {
    await api.put(`/advertisements/${ad.id}/order`, { display_order: newOrder })
    await fetchAds()
  } catch {
    alert('순서 변경에 실패했습니다.')
  }
}

async function toggleStatus(ad) {
  try {
    await api.patch(`/advertisements/${ad.id}/status`, { is_active: !ad.is_active })
    await fetchAds()
  } catch {
    alert('상태 변경에 실패했습니다.')
  }
}

async function handleDelete(ad) {
  if (!confirm('이 광고를 삭제하시겠습니까?')) return
  try {
    await api.delete(`/advertisements/${ad.id}`)
    await fetchAds()
  } catch {
    alert('삭제에 실패했습니다.')
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 24px; font-weight: 700; }

.filter-bar {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
  background: white; padding: 16px; border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.filter-bar label { font-size: 14px; font-weight: 500; }
.filter-bar select {
  padding: 8px 12px; border: 1px solid #d1d5db;
  border-radius: 6px; font-size: 14px; min-width: 200px;
}

.upload-btn { cursor: pointer; }

.ad-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.ad-card {
  background: white; border-radius: 8px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.ad-image-wrapper {
  position: relative; aspect-ratio: 16/9; overflow: hidden;
}

.ad-image-wrapper img {
  width: 100%; height: 100%; object-fit: cover;
}

.ad-order {
  position: absolute; top: 8px; left: 8px;
  background: rgba(0,0,0,0.6); color: white;
  padding: 2px 8px; border-radius: 4px; font-size: 12px;
}

.ad-actions {
  display: flex; gap: 4px; padding: 12px; flex-wrap: wrap;
}

.btn-sm { padding: 4px 10px; font-size: 12px; }
.loading { text-align: center; padding: 40px; color: #6b7280; }
.empty-state { text-align: center; color: #9ca3af; padding: 60px; font-size: 16px; }
</style>
