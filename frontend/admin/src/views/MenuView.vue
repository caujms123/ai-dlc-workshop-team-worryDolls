<template>
  <div class="menu-management" data-testid="menu-management-view">
    <h1>메뉴 관리</h1>

    <!-- Error Banner -->
    <div v-if="menuStore.error" class="error-banner" role="alert" data-testid="menu-error-banner">
      <span>{{ menuStore.error }}</span>
      <button @click="menuStore.clearError()" data-testid="menu-error-close-button">닫기</button>
    </div>

    <!-- Loading -->
    <div v-if="menuStore.isLoading" class="loading" data-testid="menu-loading-indicator">
      로딩 중...
    </div>

    <div class="menu-layout" v-else>
      <!-- Left Panel: Categories -->
      <div class="category-panel">
        <CategoryList
          :categories="menuStore.categories"
          :selected-category-id="menuStore.selectedCategoryId"
          @select="handleCategorySelect"
          @add="showCategoryForm = true"
          @edit="handleCategoryEdit"
          @delete="handleCategoryDelete"
        />
      </div>

      <!-- Right Panel: Menus -->
      <div class="menu-panel">
        <div class="menu-panel-header">
          <h2>{{ selectedCategoryName || '전체 메뉴' }}</h2>
          <button
            class="btn-primary"
            @click="openMenuForm(null)"
            data-testid="menu-add-button"
          >
            + 메뉴 등록
          </button>
        </div>

        <MenuList
          :menus="menuStore.filteredMenus"
          @edit="openMenuForm"
          @delete="handleMenuDelete"
          @move-up="handleMoveUp"
          @move-down="handleMoveDown"
        />
      </div>
    </div>

    <!-- Category Form Modal -->
    <CategoryForm
      v-if="showCategoryForm"
      :category="editingCategory"
      :store-id="storeId"
      @save="handleCategorySave"
      @close="closeCategoryForm"
    />

    <!-- Menu Form Modal -->
    <MenuForm
      v-if="showMenuForm"
      :menu="editingMenu"
      :categories="menuStore.categories"
      :store-id="storeId"
      @save="handleMenuSave"
      @close="closeMenuForm"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMenuStore } from '../stores/menuStore'
import CategoryList from '../components/menu/CategoryList.vue'
import CategoryForm from '../components/menu/CategoryForm.vue'
import MenuList from '../components/menu/MenuList.vue'
import MenuForm from '../components/menu/MenuForm.vue'

const menuStore = useMenuStore()

// TODO: Get storeId from auth context (Unit 1 integration)
const storeId = ref(1)

const showCategoryForm = ref(false)
const showMenuForm = ref(false)
const editingCategory = ref(null)
const editingMenu = ref(null)

const selectedCategoryName = computed(() => {
  if (!menuStore.selectedCategoryId) return null
  const cat = menuStore.categories.find((c) => c.id === menuStore.selectedCategoryId)
  return cat?.name || null
})

onMounted(async () => {
  await menuStore.loadCategories(storeId.value)
  await menuStore.loadMenus(storeId.value)
})

// Category handlers
function handleCategorySelect(categoryId) {
  menuStore.selectCategory(categoryId)
}

function handleCategoryEdit(category) {
  editingCategory.value = category
  showCategoryForm.value = true
}

async function handleCategoryDelete(categoryId) {
  if (!confirm('카테고리를 삭제하시겠습니까?')) return
  try {
    await menuStore.removeCategory(categoryId)
  } catch {
    // Error is handled in store
  }
}

async function handleCategorySave({ id, name }) {
  try {
    if (id) {
      await menuStore.editCategory(id, name)
    } else {
      await menuStore.addCategory(storeId.value, name)
    }
    closeCategoryForm()
  } catch {
    // Error is handled in store
  }
}

function closeCategoryForm() {
  showCategoryForm.value = false
  editingCategory.value = null
}

// Menu handlers
function openMenuForm(menu) {
  editingMenu.value = menu
  showMenuForm.value = true
}

async function handleMenuSave({ menuData, imageFile, menuId }) {
  try {
    if (menuId) {
      await menuStore.editMenu(menuId, menuData, imageFile)
    } else {
      await menuStore.addMenu(storeId.value, menuData, imageFile)
    }
    closeMenuForm()
  } catch {
    // Error is handled in store
  }
}

async function handleMenuDelete(menuId) {
  if (!confirm('메뉴를 삭제하시겠습니까?')) return
  try {
    await menuStore.removeMenu(menuId)
  } catch {
    // Error is handled in store
  }
}

async function handleMoveUp(menu) {
  if (menu.display_order <= 0) return
  await menuStore.changeMenuOrder(menu.id, menu.display_order - 1)
  await menuStore.loadMenus(storeId.value, menuStore.selectedCategoryId)
}

async function handleMoveDown(menu) {
  await menuStore.changeMenuOrder(menu.id, menu.display_order + 1)
  await menuStore.loadMenus(storeId.value, menuStore.selectedCategoryId)
}

function closeMenuForm() {
  showMenuForm.value = false
  editingMenu.value = null
}
</script>

<style scoped>
.menu-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.error-banner {
  background: #fee;
  border: 1px solid #fcc;
  color: #c00;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.menu-layout {
  display: flex;
  gap: 24px;
}

.category-panel {
  width: 280px;
  flex-shrink: 0;
}

.menu-panel {
  flex: 1;
}

.menu-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.btn-primary {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  min-height: 44px;
  min-width: 44px;
}

.btn-primary:hover {
  background: #45a049;
}
</style>
