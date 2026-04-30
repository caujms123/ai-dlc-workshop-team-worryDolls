# Unit 4: NFR Design Patterns - 고객 UI + 테이블 관리

---

## 1. 사다리 타기 알고리즘 패턴

### 1.1 사다리 생성
```javascript
function generateLadder(playerCount) {
  const segments = playerCount * 2  // 구간 수
  const ladder = {
    columns: playerCount,
    rows: segments,
    bridges: [],  // [{row, col}] - col과 col+1 사이 가로줄
    loserIndex: Math.floor(Math.random() * playerCount)
  }
  
  for (let row = 0; row < segments; row++) {
    for (let col = 0; col < playerCount - 1; col++) {
      // 인접한 가로줄 겹침 방지
      const prevBridge = ladder.bridges.find(b => b.row === row && (b.col === col - 1 || b.col === col + 1))
      if (!prevBridge && Math.random() < 0.4) {
        ladder.bridges.push({ row, col })
      }
    }
  }
  return ladder
}
```

### 1.2 경로 계산
```javascript
function calculatePath(ladder, startCol) {
  const path = [{ row: 0, col: startCol }]
  let currentCol = startCol
  
  for (let row = 0; row < ladder.rows; row++) {
    // 오른쪽 가로줄 확인
    if (ladder.bridges.find(b => b.row === row && b.col === currentCol)) {
      currentCol++
      path.push({ row, col: currentCol, direction: 'right' })
    }
    // 왼쪽 가로줄 확인
    else if (ladder.bridges.find(b => b.row === row && b.col === currentCol - 1)) {
      currentCol--
      path.push({ row, col: currentCol, direction: 'left' })
    }
    path.push({ row: row + 1, col: currentCol })
  }
  return { path, endCol: currentCol }
}
```

### 1.3 애니메이션 패턴 (Canvas/SVG)
```javascript
function animatePath(ctx, path, duration = 2500) {
  const totalSteps = path.length
  const stepDuration = duration / totalSteps
  let currentStep = 0
  
  function draw() {
    if (currentStep >= totalSteps) {
      showResult()
      return
    }
    // 현재 위치까지 경로 그리기
    drawPathSegment(ctx, path[currentStep - 1], path[currentStep])
    currentStep++
    setTimeout(() => requestAnimationFrame(draw), stepDuration)
  }
  requestAnimationFrame(draw)
}
```

---

## 2. 광고 슬라이드 패턴

### 2.1 자동 슬라이드
```javascript
// Vue Composition API
const currentIndex = ref(0)
const advertisements = ref([])
let slideTimer = null

function startSlideshow() {
  slideTimer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % advertisements.value.length
  }, 5000)  // 5초 간격
}

onMounted(() => {
  fetchAdvertisements().then(() => startSlideshow())
})

onUnmounted(() => {
  clearInterval(slideTimer)
})
```

### 2.2 CSS Transition
```css
.slide-enter-active, .slide-leave-active {
  transition: opacity 0.5s ease;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
}
```

---

## 3. 비활성 감지 패턴

```javascript
// App 레벨에서 비활성 타이머 관리
const INACTIVITY_TIMEOUT = 2 * 60 * 1000  // 2분
let inactivityTimer = null

function resetInactivityTimer() {
  clearTimeout(inactivityTimer)
  inactivityTimer = setTimeout(() => {
    if (router.currentRoute.value.path !== '/') {
      router.push('/')  // 광고 화면으로 복귀
    }
  }, INACTIVITY_TIMEOUT)
}

// 사용자 활동 이벤트 감지
['touchstart', 'click', 'scroll', 'keypress'].forEach(event => {
  document.addEventListener(event, resetInactivityTimer)
})
```

---

## 4. 장바구니 로컬 저장 패턴

```javascript
// Pinia Store with localStorage 동기화
const CART_STORAGE_KEY = 'table_order_cart'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || '[]')
  }),
  actions: {
    addItem(menu) {
      const existing = this.items.find(i => i.menuId === menu.id)
      if (existing) {
        existing.quantity++
      } else {
        this.items.push({ menuId: menu.id, menuName: menu.name, price: menu.price, quantity: 1, imageUrl: menu.image_path })
      }
      this._persist()
    },
    _persist() {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(this.items))
    }
  }
})
```

---

## 5. 효과음 패턴

```javascript
// Web Audio API 기반 효과음
class SoundManager {
  constructor() {
    this.context = new (window.AudioContext || window.webkitAudioContext)()
    this.sounds = {}
  }
  
  async load(name, url) {
    const response = await fetch(url)
    const buffer = await response.arrayBuffer()
    this.sounds[name] = await this.context.decodeAudioData(buffer)
  }
  
  play(name) {
    if (!this.sounds[name]) return
    const source = this.context.createBufferSource()
    source.buffer = this.sounds[name]
    source.connect(this.context.destination)
    source.start(0)
  }
}

// 사다리 타기 효과음
const soundManager = new SoundManager()
soundManager.load('start', '/sounds/start.mp3')
soundManager.load('tick', '/sounds/tick.mp3')
soundManager.load('result', '/sounds/fanfare.mp3')
```
