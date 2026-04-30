<template>
  <div class="menu-list" data-testid="menu-list">
    <div v-if="menus.length === 0" class="empty-state" data-testid="menu-list-empty">
      등록된 메뉴가 없습니다.
    </div>

    <div v-else class="menu-grid">
      <MenuCard
        v-for="menu in menus"
        :key="menu.id"
        :menu="menu"
        @edit="$emit('edit', menu)"
        @delete="$emit('delete', menu.id)"
        @move-up="$emit('move-up', menu)"
        @move-down="$emit('move-down', menu)"
      />
    </div>
  </div>
</template>

<script setup>
import MenuCard from './MenuCard.vue'

defineProps({
  menus: { type: Array, required: true },
})

defineEmits(['edit', 'delete', 'move-up', 'move-down'])
</script>

<style scoped>
.menu-list {
  min-height: 200px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
</style>
