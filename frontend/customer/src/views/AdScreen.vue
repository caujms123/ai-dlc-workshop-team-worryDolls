<template>
  <div class="ad-screen" @click="goToMenu" @touchstart="goToMenu">
    <div v-if="advertisements.length > 0" class="slideshow">
      <transition name="fade" mode="out-in">
        <img
          :key="currentIndex"
          :src="currentAd.image_url"
          :alt="'광고 ' + (currentIndex + 1)"
          class="ad-image"
        />
      </transition>
      <div class="slide-indicators">
        <span
          v-for="(ad, idx) in advertisements"
          :key="idx"
          :class="['dot', { active: idx === currentIndex }]"
        />
      </div>
    </div>
    <div v-else class="default-screen">
      <h1>환영합니다</h1>
      <p>화면을 터치하여 주문을 시작하세요</p>
    </div>
    <p class="touch-hint">화면을 터치하세요</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTableAuthStore } from '../stores/tableAuth'
import axios from 'axios'

const router = useRouter()
const authStore = useTableAuthStore()

const advertisements = ref([])
const currentIndex = ref(0)
let slideTimer = null

const currentAd = computed(() => advertisements.value[currentIndex.value] || {})

async function fetchAdvertisements() {
  try {
    const res = await axios.get(
      `/api/customer/stores/${authStore.storeId}/advertisements`
    )
    advertisements.value = res.data
  } catch {
    advertisements.value = []
  }
}

function startSlideshow() {
  if (advertisements.value.length <= 1) return
  slideTimer = setInterval(() => {
    currentIndex.value =
      (currentIndex.value + 1) % advertisements.value.length
  }, 5000)
}

function goToMenu() {
  router.push('/menu')
}

onMounted(async () => {
  await fetchAdvertisements()
  startSlideshow()
})

onUnmounted(() => {
  clearInterval(slideTimer)
})
</script>
