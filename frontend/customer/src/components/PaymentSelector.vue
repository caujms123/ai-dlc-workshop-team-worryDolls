<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="payment-modal">
      <div class="modal-header">
        <h3>결제 방식 선택</h3>
        <button class="btn-ladder" @click="showLadder = true" aria-label="사다리 타기">
          🎲
        </button>
      </div>

      <div class="modal-body">
        <p class="total-display">총 금액: {{ totalAmount.toLocaleString() }}원</p>

        <div class="payment-options">
          <button class="btn-payment dutch" @click="$emit('select', 'DUTCH_PAY')">
            <span class="icon">👥</span>
            <span class="label">더치페이</span>
            <span class="desc">1/N 균등 분할</span>
          </button>

          <button class="btn-payment single" @click="$emit('select', 'SINGLE_PAY')">
            <span class="icon">👤</span>
            <span class="label">단독 계산</span>
            <span class="desc">한 명이 전액</span>
          </button>
        </div>
      </div>

      <LadderGame v-if="showLadder" @complete="showLadder = false" @close="showLadder = false" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LadderGame from './LadderGame.vue'

defineProps({
  totalAmount: { type: Number, required: true },
})

defineEmits(['select', 'close'])

const showLadder = ref(false)
</script>
