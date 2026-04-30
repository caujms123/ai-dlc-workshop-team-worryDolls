<template>
  <div id="customer-app" @touchstart="resetInactivity" @click="resetInactivity">
    <router-view />
    <BottomNav v-if="showNav" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BottomNav from './components/BottomNav.vue'

const router = useRouter()
const route = useRoute()

const INACTIVITY_TIMEOUT = 2 * 60 * 1000 // 2분
let inactivityTimer = null

const showNav = computed(() => {
  return route.path !== '/' && route.path !== '/setup'
})

function resetInactivity() {
  clearTimeout(inactivityTimer)
  inactivityTimer = setTimeout(() => {
    if (route.path !== '/' && route.path !== '/setup') {
      router.push('/')
    }
  }, INACTIVITY_TIMEOUT)
}

onMounted(() => {
  resetInactivity()
})

onUnmounted(() => {
  clearTimeout(inactivityTimer)
})
</script>
