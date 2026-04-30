<template>
  <nav
    class="category-tabs"
    role="tablist"
    aria-label="메뉴 카테고리"
    data-testid="category-tabs"
  >
    <button
      v-for="category in categories"
      :key="category.id"
      :class="['tab-button', { active: category.id === selectedCategoryId }]"
      role="tab"
      :aria-selected="category.id === selectedCategoryId"
      @click="$emit('select', category.id)"
      :data-testid="`category-tab-${category.id}`"
    >
      {{ category.name }}
    </button>
  </nav>
</template>

<script setup>
defineProps({
  categories: { type: Array, required: true },
  selectedCategoryId: { type: Number, default: null },
})

defineEmits(['select'])
</script>

<style scoped>
.category-tabs {
  display: flex;
  overflow-x: auto;
  gap: 8px;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #eee;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.tab-button {
  flex-shrink: 0;
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 24px;
  background: white;
  font-size: 15px;
  cursor: pointer;
  white-space: nowrap;
  min-height: 44px;
  min-width: 44px;
  transition: all 0.2s;
}

.tab-button.active {
  background: #333;
  color: white;
  border-color: #333;
}

.tab-button:not(.active):hover {
  background: #f5f5f5;
}
</style>
