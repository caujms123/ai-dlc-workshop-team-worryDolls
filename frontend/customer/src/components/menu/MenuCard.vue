<template>
  <div
    class="menu-card"
    @click="$emit('select', menu)"
    role="button"
    tabindex="0"
    :aria-label="`${menu.name} ${formatPrice(menu.price)}원`"
    data-testid="customer-menu-card"
  >
    <div class="card-image">
      <img
        v-if="menu.image_path"
        :src="`/api/uploads/${menu.image_path}`"
        :alt="menu.name"
        loading="lazy"
      />
      <div v-else class="no-image" aria-hidden="true">🍽️</div>
    </div>

    <div class="card-info">
      <h3 class="card-name" data-testid="customer-menu-card-name">{{ menu.name }}</h3>
      <p class="card-price" data-testid="customer-menu-card-price">
        {{ formatPrice(menu.price) }}원
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  menu: { type: Object, required: true },
})

defineEmits(['select', 'add-to-cart'])

function formatPrice(price) {
  return price.toLocaleString('ko-KR')
}
</script>

<style scoped>
.menu-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  min-height: 44px;
}

.menu-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.menu-card:active {
  transform: scale(0.98);
}

.card-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 40px;
}

.card-info {
  padding: 10px 12px;
}

.card-name {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-price {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #e65100;
}
</style>
