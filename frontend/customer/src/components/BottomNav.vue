<template>
  <nav class="bottom-nav">
    <router-link to="/menu" class="nav-item" active-class="active">
      <span class="nav-icon">🍽️</span>
      <span class="nav-label">메뉴</span>
    </router-link>
    <router-link to="/cart" class="nav-item" active-class="active">
      <span class="nav-icon">🛒</span>
      <span class="nav-label">장바구니</span>
      <span v-if="cartStore.itemCount > 0" class="badge">
        {{ cartStore.itemCount }}
      </span>
    </router-link>
    <router-link to="/orders" class="nav-item" active-class="active">
      <span class="nav-icon">📋</span>
      <span class="nav-label">주문내역</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useCartStore } from '../stores/cart'
const cartStore = useCartStore()
</script>
