<template>
  <div class="menu-browser" data-testid="menu-browser-view">
    <!-- Loading -->
    <div v-if="menuStore.isLoading" class="loading" data-testid="menu-loading">
      메뉴를 불러오는 중...
    </div>

    <!-- Error -->
    <div v-else-if="menuStore.error" class="error" role="alert" data-testid="menu-error">
      {{ menuStore.error }}
    </div>

    <template v-else>
      <!-- Category Tabs -->
      <CategoryTabs
        :categories="menuStore.categories"
        :selected-category-id="menuStore.selectedCategoryId"
        @select="menuStore.selectCategory"
      />

      <!-- Menu Grid -->
      <MenuGrid
        :menus="menuStore.currentMenus"
        @select="menuStore.selectMenu"
        @add-to-cart="handleAddToCart"
      />
    </template>

    <!-- Menu Detail Popup -->
    <MenuDetail
      v-if="menuStore.selectedMenu"
      :menu="menuStore.selectedMenu"
      @add-to-cart="handleAddToCart"
      @close="menuStore.closeMenuDetail()"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useMenuStore } from '../stores/menuStore'
import CategoryTabs from '../components/menu/CategoryTabs.vue'
import MenuGrid from '../components/menu/MenuGrid.vue'
import MenuDetail from '../components/menu/MenuDetail.vue'

const menuStore = useMenuStore()

// TODO: Get storeId from auth context (Unit 1 / Unit 4 integration)
const storeId = 1

onMounted(async () => {
  await menuStore.loadMenus(storeId)
})

function handleAddToCart(menu) {
  // TODO: Integration with Unit 4 CartManager (cartStore.addItem)
  menuStore.closeMenuDetail()
}
</script>

<style scoped>
.menu-browser {
  min-height: 100vh;
  background: #fafafa;
}

.loading, .error {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  font-size: 16px;
}

.error {
  color: #c62828;
}
</style>
