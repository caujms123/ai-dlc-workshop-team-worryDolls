<template>
  <div
    class="detail-overlay"
    @click.self="$emit('close')"
    data-testid="menu-detail-modal"
  >
    <div class="detail-content" role="dialog" :aria-label="menu.name">
      <!-- Image -->
      <div class="detail-image">
        <img
          v-if="menu.image_path"
          :src="`/api/uploads/${menu.image_path}`"
          :alt="menu.name"
        />
        <div v-else class="no-image" aria-hidden="true">🍽️</div>
      </div>

      <!-- Info -->
      <div class="detail-info">
        <h2 class="detail-name" data-testid="menu-detail-name">{{ menu.name }}</h2>
        <p class="detail-price" data-testid="menu-detail-price">
          {{ formatPrice(menu.price) }}원
        </p>
        <p
          v-if="menu.description"
          class="detail-description"
          data-testid="menu-detail-description"
        >
          {{ menu.description }}
        </p>
      </div>

      <!-- Actions -->
      <div class="detail-actions">
        <button
          class="btn-close"
          @click="$emit('close')"
          data-testid="menu-detail-close-button"
        >
          닫기
        </button>
        <button
          class="btn-add-cart"
          @click="$emit('add-to-cart', menu)"
          data-testid="menu-detail-add-cart-button"
        >
          장바구니에 추가
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  menu: { type: Object, required: true },
})

defineEmits(['add-to-cart', 'close'])

function formatPrice(price) {
  return price.toLocaleString('ko-KR')
}
</script>

<style scoped>
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.detail-content {
  background: white;
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
}

.detail-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 60px;
}

.detail-info {
  padding: 20px;
}

.detail-name {
  margin: 0 0 8px;
  font-size: 22px;
}

.detail-price {
  margin: 0 0 16px;
  font-size: 24px;
  font-weight: bold;
  color: #e65100;
}

.detail-description {
  margin: 0;
  font-size: 15px;
  color: #666;
  line-height: 1.6;
}

.detail-actions {
  display: flex;
  gap: 12px;
  padding: 16px 20px 24px;
}

.btn-close, .btn-add-cart {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  min-height: 52px;
}

.btn-close {
  background: #eee;
  color: #333;
}

.btn-add-cart {
  background: #4CAF50;
  color: white;
}

.btn-add-cart:active {
  background: #45a049;
}
</style>
