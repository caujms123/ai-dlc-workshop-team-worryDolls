<template>
  <div class="modal-overlay" @click.self="$emit('close')" data-testid="category-form-modal">
    <div class="modal-content" role="dialog" aria-label="카테고리 등록/수정">
      <h3>{{ isEdit ? '카테고리 수정' : '카테고리 등록' }}</h3>

      <form @submit.prevent="handleSubmit" data-testid="category-form">
        <div class="form-group">
          <label for="category-name">카테고리명 *</label>
          <input
            id="category-name"
            v-model="name"
            type="text"
            minlength="2"
            maxlength="50"
            required
            placeholder="카테고리명을 입력하세요 (2~50자)"
            data-testid="category-name-input"
          />
        </div>

        <div class="form-actions">
          <button
            type="button"
            class="btn-cancel"
            @click="$emit('close')"
            data-testid="category-form-cancel-button"
          >
            취소
          </button>
          <button
            type="submit"
            class="btn-submit"
            data-testid="category-form-submit-button"
          >
            {{ isEdit ? '수정' : '등록' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  category: { type: Object, default: null },
  storeId: { type: Number, required: true },
})

const emit = defineEmits(['save', 'close'])

const isEdit = computed(() => !!props.category)
const name = ref(props.category?.name || '')

function handleSubmit() {
  if (name.value.length < 2 || name.value.length > 50) return
  emit('save', {
    id: props.category?.id || null,
    name: name.value,
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 400px;
  max-width: 90vw;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  min-height: 44px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-cancel, .btn-submit {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  min-height: 44px;
}

.btn-cancel {
  background: #eee;
}

.btn-submit {
  background: #4CAF50;
  color: white;
}
</style>
