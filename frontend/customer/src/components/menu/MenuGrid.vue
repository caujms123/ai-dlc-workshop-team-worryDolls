<template>
  <div class="menu-grid" data-testid="menu-grid">
    <div v-if="menus.length === 0" class="empty-state" data-testid="menu-grid-empty">
      메뉴가 없습니다.
    </div>

    <div v-else class="grid">
      <MenuCard
        v-for="menu in menus"
        :key="menu.id"
        :menu="menu"
        @select="$emit('select', menu)"
        @add-to-cart="$emit('add-to-cart', menu)"
      />
    </div>
  </div>
</template>

<script setup>
import MenuCard from './MenuCard.vue'

defineProps({
  menus: { type: Array, required: true },
})

defineEmits(['select', 'add-to-cart'])
</script>

<style scoped>
.menu-grid {
  padding: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
</style>
