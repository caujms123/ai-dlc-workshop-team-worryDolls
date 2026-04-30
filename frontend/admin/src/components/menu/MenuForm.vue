<template>
  <div class="modal-overlay" @click.self="$emit('close')" data-testid="menu-form-modal">
    <div class="modal-content" role="dialog" aria-label="메뉴 등록/수정">
      <h3>{{ isEdit ? '메뉴 수정' : '메뉴 등록' }}</h3>

      <form @submit.prevent="handleSubmit" data-testid="menu-form">
        <!-- 메뉴명 -->
        <div class="form-group">
          <label for="menu-name">메뉴명 *</label>
          <input
            id="menu-name"
            v-model="form.name"
            type="text"
            minlength="2"
            maxlength="100"
            required
            placeholder="메뉴명 (2~100자)"
            data-testid="menu-name-input"
          />
        </div>

        <!-- 가격 -->
        <div class="form-group">
          <label for="menu-price">가격 (원) *</label>
          <input
            id="menu-price"
            v-model.number="form.price"
            type="number"
            min="0"
            max="10000000"
            required
            placeholder="0"
            data-testid="menu-price-input"
          />
        </div>

        <!-- 카테고리 -->
        <div class="form-group">
          <label for="menu-category">카테고리 *</label>
          <select
            id="menu-category"
            v-model.number="form.category_id"
            required
            data-testid="menu-category-select"
          >
            <option value="" disabled>카테고리를 선택하세요</option>
            <option
              v-for="cat in categories"
              :key="cat.id"
              :value="cat.id"
            >
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- 설명 -->
        <div class="form-group">
          <label for="menu-description">설명</label>
          <textarea
            id="menu-description"
            v-model="form.description"
            maxlength="1000"
            rows="3"
            placeholder="메뉴 설명 (최대 1000자)"
            data-testid="menu-description-input"
          ></textarea>
        </div>

        <!-- 이미지 -->
        <div class="form-group">
          <label for="menu-image">이미지 (JPG, PNG)</label>
          <input
            id="menu-image"
            type="file"
            accept="image/jpeg,image/png"
            @change="handleImageChange"
            data-testid="menu-image-input"
          />
          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="미리보기" />
          </div>
        </div>

        <div class="form-actions">
          <button
            type="button"
            class="btn-cancel"
            @click="$emit('close')"
            data-testid="menu-form-cancel-button"
          >
            취소
          </button>
          <button
            type="submit"
            class="btn-submit"
            data-testid="menu-form-submit-button"
          >
            {{ isEdit ? '수정' : '등록' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const props = defineProps({
  menu: { type: Object, default: null },
  categories: { type: Array, required: true },
  storeId: { type: Number, required: true },
})

const emit = defineEmits(['save', 'close'])

const isEdit = computed(() => !!props.menu)

const form = reactive({
  name: props.menu?.name || '',
  price: props.menu?.price ?? 0,
  description: props.menu?.description || '',
  category_id: props.menu?.category_id || '',
})

const imageFile = ref(null)
const imagePreview = ref(props.menu?.image_path ? `/api/uploads/${props.menu.image_path}` : null)

function handleImageChange(event) {
  const file = event.target.files[0]
  if (!file) return

  // Validate file type
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    alert('JPG 또는 PNG 파일만 업로드 가능합니다.')
    event.target.value = ''
    return
  }

  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

function handleSubmit() {
  if (form.name.length < 2 || form.price < 0 || !form.category_id) return

  emit('save', {
    menuId: props.menu?.id || null,
    menuData: {
      name: form.name,
      price: form.price,
      description: form.description || null,
      category_id: form.category_id,
    },
    imageFile: imageFile.value,
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
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  min-height: 44px;
}

.form-group textarea {
  resize: vertical;
}

.image-preview {
  margin-top: 8px;
}

.image-preview img {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  object-fit: cover;
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
