<template>
  <div class="menu-card" data-testid="menu-card">
    <div class="menu-image">
      <img
        v-if="menu.image_path"
        :src="`/api/uploads/${menu.image_path}`"
        :alt="menu.name"
        loading="lazy"
      />
      <div v-else class="no-image">이미지 없음</div>
    </div>

    <div class="menu-info">
      <h4 class="menu-name" data-testid="menu-card-name">{{ menu.name }}</h4>
      <p class="menu-price" data-testid="menu-card-price">
        {{ formatPrice(menu.price) }}원
      </p>
      <p v-if="menu.description" class="menu-description">
        {{ menu.description }}
      </p>
      <span
        :class="['availability-badge', menu.is_available ? 'available' : 'unavailable']"
        data-testid="menu-card-availability"
      >
        {{ menu.is_available ? '판매중' : '품절' }}
      </span>
    </div>

    <div class="menu-actions">
      <div class="order-buttons">
        <button
          class="btn-order"
          @click="$emit('move-up', menu)"
          data-testid="menu-move-up-button"
          aria-label="위로 이동"
        >
          ▲
        </button>
        <button
          class="btn-order"
          @click="$emit('move-down', menu)"
          data-testid="menu-move-down-button"
          aria-label="아래로 이동"
        >
          ▼
        </button>
      </div>
      <div class="crud-buttons">
        <button
          class="btn-edit"
          @click="$emit('edit', menu)"
          data-testid="menu-edit-button"
          aria-label="메뉴 수정"
        >
          수정
        </button>
        <button
          class="btn-delete"
          @click="$emit('delete', menu.id)"
          data-testid="menu-delete-button"
          aria-label="메뉴 삭제"
        >
          삭제
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  menu: { type: Object, required: true },
})

defineEmits(['edit', 'delete', 'move-up', 'move-down'])

function formatPrice(price) {
  return price.toLocaleString('ko-KR')
}
</script>

<style scoped>
.menu-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.menu-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.menu-image {
  height: 160px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #999;
  font-size: 14px;
}

.menu-info {
  padding: 12px 16px;
}

.menu-name {
  margin: 0 0 4px;
  font-size: 16px;
}

.menu-price {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: bold;
  color: #e65100;
}

.menu-description {
  margin: 0 0 8px;
  font-size: 13px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.availability-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.availability-badge.available {
  background: #e8f5e9;
  color: #2e7d32;
}

.availability-badge.unavailable {
  background: #fce4ec;
  color: #c62828;
}

.menu-actions {
  display: flex;
  justify-content: space-between;
  padding: 8px 16px 12px;
}

.order-buttons, .crud-buttons {
  display: flex;
  gap: 4px;
}

.btn-order {
  width: 36px;
  height: 36px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.btn-edit, .btn-delete {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  min-height: 36px;
}

.btn-edit {
  background: #e3f2fd;
  color: #1565c0;
}

.btn-delete {
  background: #fce4ec;
  color: #c62828;
}
</style>
