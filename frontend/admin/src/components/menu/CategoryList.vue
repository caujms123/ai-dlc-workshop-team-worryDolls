<template>
  <div class="category-list" data-testid="category-list">
    <div class="category-header">
      <h3>카테고리</h3>
      <button
        class="btn-add"
        @click="$emit('add')"
        data-testid="category-add-button"
        aria-label="카테고리 추가"
      >
        +
      </button>
    </div>

    <ul class="category-items" role="listbox" aria-label="카테고리 목록">
      <li
        v-for="category in categories"
        :key="category.id"
        :class="['category-item', { selected: category.id === selectedCategoryId }]"
        role="option"
        :aria-selected="category.id === selectedCategoryId"
        @click="$emit('select', category.id)"
        data-testid="category-item"
      >
        <span class="category-name">{{ category.name }}</span>
        <div class="category-actions">
          <button
            class="btn-icon"
            @click.stop="$emit('edit', category)"
            data-testid="category-edit-button"
            aria-label="카테고리 수정"
          >
            ✏️
          </button>
          <button
            class="btn-icon"
            @click.stop="$emit('delete', category.id)"
            data-testid="category-delete-button"
            aria-label="카테고리 삭제"
          >
            🗑️
          </button>
        </div>
      </li>
    </ul>

    <button
      v-if="selectedCategoryId"
      class="btn-clear"
      @click="$emit('select', null)"
      data-testid="category-clear-filter-button"
    >
      전체 보기
    </button>
  </div>
</template>

<script setup>
defineProps({
  categories: { type: Array, required: true },
  selectedCategoryId: { type: Number, default: null },
})

defineEmits(['select', 'add', 'edit', 'delete'])
</script>

<style scoped>
.category-list {
  background: #f9f9f9;
  border-radius: 12px;
  padding: 16px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-header h3 {
  margin: 0;
}

.btn-add {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: #4CAF50;
  color: white;
  font-size: 20px;
  cursor: pointer;
}

.category-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  min-height: 44px;
  transition: background 0.2s;
}

.category-item:hover {
  background: #e8e8e8;
}

.category-item.selected {
  background: #e3f2fd;
  font-weight: bold;
}

.category-name {
  flex: 1;
}

.category-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  font-size: 16px;
}

.btn-icon:hover {
  background: #ddd;
}

.btn-clear {
  width: 100%;
  margin-top: 12px;
  padding: 10px;
  border: 1px dashed #999;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  min-height: 44px;
}
</style>
