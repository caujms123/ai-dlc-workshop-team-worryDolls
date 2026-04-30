<template>
  <div class="cart-container">
    <h2>장바구니</h2>

    <div v-if="cartStore.isEmpty" class="empty-cart">
      <p>장바구니가 비어있습니다.</p>
      <router-link to="/menu" class="btn-secondary">메뉴 보기</router-link>
    </div>

    <div v-else>
      <div class="cart-items">
        <div v-for="item in cartStore.items" :key="item.menuId" class="cart-item">
          <div class="item-info">
            <span class="item-name">{{ item.menuName }}</span>
            <span class="item-price">{{ item.price.toLocaleString() }}원</span>
          </div>
          <div class="item-controls">
            <button
              class="btn-qty"
              @click="cartStore.updateQuantity(item.menuId, item.quantity - 1)"
              aria-label="수량 감소"
            >−</button>
            <span class="qty">{{ item.quantity }}</span>
            <button
              class="btn-qty"
              @click="cartStore.updateQuantity(item.menuId, item.quantity + 1)"
              aria-label="수량 증가"
            >+</button>
          </div>
          <span class="item-subtotal">
            {{ (item.price * item.quantity).toLocaleString() }}원
          </span>
        </div>
      </div>

      <div class="cart-summary">
        <button class="btn-clear" @click="cartStore.clearCart()">
          장바구니 비우기
        </button>
        <div class="total">
          <span>총 금액</span>
          <strong>{{ cartStore.totalAmount.toLocaleString() }}원</strong>
        </div>
        <button class="btn-primary btn-order" @click="showPayment = true">
          주문하기 ({{ cartStore.itemCount }}개)
        </button>
      </div>
    </div>

    <PaymentSelector
      v-if="showPayment"
      :total-amount="cartStore.totalAmount"
      @select="handlePaymentSelect"
      @close="showPayment = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import PaymentSelector from '../components/PaymentSelector.vue'

const router = useRouter()
const cartStore = useCartStore()
const showPayment = ref(false)

function handlePaymentSelect(paymentType) {
  showPayment.value = false
  router.push({
    name: 'orderConfirm',
    query: { paymentType },
  })
}
</script>
