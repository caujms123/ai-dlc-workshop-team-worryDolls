<template>
  <div class="ladder-overlay" @click.self="$emit('close')">
    <div class="ladder-modal">
      <!-- Phase 1: 인원 선택 -->
      <div v-if="phase === 'select'" class="phase-select">
        <h3>인원 수를 선택하세요</h3>
        <div class="player-buttons">
          <button
            v-for="n in 9"
            :key="n + 1"
            class="btn-player"
            :class="{ selected: playerCount === n + 1 }"
            @click="playerCount = n + 1"
          >
            {{ n + 1 }}명
          </button>
        </div>
        <button
          class="btn-primary btn-start"
          :disabled="!playerCount"
          @click="startGame"
        >
          시작!
        </button>
      </div>

      <!-- Phase 2: 사다리 진행 -->
      <div v-else-if="phase === 'playing' || phase === 'result'" class="phase-game">
        <canvas
          ref="canvasRef"
          :width="canvasWidth"
          :height="canvasHeight"
          class="ladder-canvas"
        />

        <!-- 결과 표시 -->
        <div v-if="phase === 'result'" class="result-overlay">
          <div class="result-card" :class="{ show: phase === 'result' }">
            <span class="result-text">🎉 꽝! 🎉</span>
            <span class="result-player">{{ loser + 1 }}번</span>
            <span class="countdown">{{ countdown }}초 후 돌아갑니다</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, nextTick } from 'vue'

const emit = defineEmits(['complete', 'close'])

const phase = ref('select') // select | playing | result
const playerCount = ref(null)
const loser = ref(null)
const countdown = ref(5)
const canvasRef = ref(null)

const canvasWidth = 350
const canvasHeight = 450

let ladder = null
let countdownTimer = null

function generateLadder(count) {
  const segments = count * 2
  const bridges = []
  const loserIdx = Math.floor(Math.random() * count)

  for (let row = 0; row < segments; row++) {
    for (let col = 0; col < count - 1; col++) {
      const hasPrev = bridges.some(
        (b) => b.row === row && (b.col === col - 1 || b.col === col + 1)
      )
      if (!hasPrev && Math.random() < 0.4) {
        bridges.push({ row, col })
      }
    }
  }

  return { columns: count, rows: segments, bridges, loserIdx }
}

function calculatePath(ladderData, startCol) {
  let currentCol = startCol
  const path = [{ row: 0, col: currentCol }]

  for (let row = 0; row < ladderData.rows; row++) {
    const rightBridge = ladderData.bridges.find(
      (b) => b.row === row && b.col === currentCol
    )
    const leftBridge = ladderData.bridges.find(
      (b) => b.row === row && b.col === currentCol - 1
    )

    if (rightBridge) {
      currentCol++
    } else if (leftBridge) {
      currentCol--
    }
    path.push({ row: row + 1, col: currentCol })
  }

  return { path, endCol: currentCol }
}

function drawLadder(ctx, ladderData) {
  const colSpacing = canvasWidth / (ladderData.columns + 1)
  const rowSpacing = (canvasHeight - 80) / (ladderData.rows + 1)
  const topOffset = 40

  ctx.clearRect(0, 0, canvasWidth, canvasHeight)

  // 참가자 번호 (상단)
  ctx.fillStyle = '#333'
  ctx.font = 'bold 16px sans-serif'
  ctx.textAlign = 'center'
  for (let i = 0; i < ladderData.columns; i++) {
    const x = colSpacing * (i + 1)
    ctx.fillText(`${i + 1}`, x, 25)
  }

  // 세로줄
  ctx.strokeStyle = '#666'
  ctx.lineWidth = 2
  for (let i = 0; i < ladderData.columns; i++) {
    const x = colSpacing * (i + 1)
    ctx.beginPath()
    ctx.moveTo(x, topOffset)
    ctx.lineTo(x, topOffset + rowSpacing * (ladderData.rows + 1))
    ctx.stroke()
  }

  // 가로줄
  ctx.strokeStyle = '#999'
  ctx.lineWidth = 2
  for (const bridge of ladderData.bridges) {
    const x1 = colSpacing * (bridge.col + 1)
    const x2 = colSpacing * (bridge.col + 2)
    const y = topOffset + rowSpacing * (bridge.row + 1)
    ctx.beginPath()
    ctx.moveTo(x1, y)
    ctx.lineTo(x2, y)
    ctx.stroke()
  }

  // 하단 결과 (꽝 표시)
  const bottomY = topOffset + rowSpacing * (ladderData.rows + 1) + 20
  for (let i = 0; i < ladderData.columns; i++) {
    const x = colSpacing * (i + 1)
    if (i === ladderData.loserIdx) {
      ctx.fillStyle = '#e74c3c'
      ctx.font = 'bold 14px sans-serif'
      ctx.fillText('꽝', x, bottomY)
    } else {
      ctx.fillStyle = '#27ae60'
      ctx.font = '14px sans-serif'
      ctx.fillText('✓', x, bottomY)
    }
  }
}

function animatePaths(ctx, ladderData, paths) {
  const colSpacing = canvasWidth / (ladderData.columns + 1)
  const rowSpacing = (canvasHeight - 80) / (ladderData.rows + 1)
  const topOffset = 40
  const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
                  '#1abc9c', '#e67e22', '#e91e63', '#00bcd4', '#ff5722']

  let step = 0
  const maxSteps = paths[0].path.length

  function drawStep() {
    if (step >= maxSteps) {
      phase.value = 'result'
      // 꽝 결정
      for (let i = 0; i < paths.length; i++) {
        if (paths[i].endCol === ladderData.loserIdx) {
          loser.value = i
          break
        }
      }
      startCountdown()
      return
    }

    // 각 참가자의 현재 위치까지 경로 그리기
    for (let p = 0; p < paths.length; p++) {
      if (step >= paths[p].path.length) continue
      const point = paths[p].path[step]
      const x = colSpacing * (point.col + 1)
      const y = topOffset + rowSpacing * point.row

      ctx.fillStyle = colors[p % colors.length]
      ctx.beginPath()
      ctx.arc(x, y, 6, 0, Math.PI * 2)
      ctx.fill()

      // 이전 점과 연결선
      if (step > 0 && step < paths[p].path.length) {
        const prev = paths[p].path[step - 1]
        const px = colSpacing * (prev.col + 1)
        const py = topOffset + rowSpacing * prev.row
        ctx.strokeStyle = colors[p % colors.length]
        ctx.lineWidth = 3
        ctx.beginPath()
        ctx.moveTo(px, py)
        ctx.lineTo(x, y)
        ctx.stroke()
      }
    }

    step++
    setTimeout(() => requestAnimationFrame(drawStep), 100)
  }

  requestAnimationFrame(drawStep)
}

async function startGame() {
  phase.value = 'playing'
  ladder = generateLadder(playerCount.value)

  await nextTick()
  const ctx = canvasRef.value?.getContext('2d')
  if (!ctx) return

  drawLadder(ctx, ladder)

  // 모든 참가자의 경로 계산
  const paths = []
  for (let i = 0; i < ladder.columns; i++) {
    paths.push(calculatePath(ladder, i))
  }

  // 애니메이션 시작 (약간의 딜레이)
  setTimeout(() => animatePaths(ctx, ladder, paths), 500)
}

function startCountdown() {
  countdown.value = 5
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      emit('complete')
    }
  }, 1000)
}

onUnmounted(() => {
  clearInterval(countdownTimer)
})
</script>
