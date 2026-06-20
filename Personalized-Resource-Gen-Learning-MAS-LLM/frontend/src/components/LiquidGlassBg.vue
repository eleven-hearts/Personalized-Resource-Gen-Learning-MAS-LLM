<template>
  <canvas ref="canvasRef" class="liquid-glass-bg" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let ctx = null
let width = 0
let height = 0
let dpr = 1
let animId = null
// 预存渐变色定义，省去每帧分配
const spots = []
const arcs = []

// ---------- 光斑生成 ----------
function createSpots() {
  const colors = [
    [59, 130, 246],    // blue
    [139, 92, 246],    // violet
    [99, 102, 241],    // indigo
    [6, 182, 212],     // cyan
    [167, 139, 250],   // lavender
    [56, 189, 248],    // sky
    [192, 132, 252],   // purple
    [94, 234, 212],    // teal
  ]
  spots.length = 0
  for (let i = 0; i < 8; i++) {
    spots.push({
      x: Math.random() * width,
      y: Math.random() * height,
      r: (120 + Math.random() * 180) * dpr,
      dx: (Math.random() - 0.5) * 0.25,
      dy: (Math.random() - 0.5) * 0.25,
      color: colors[i],
      phase: Math.random() * Math.PI * 2,
    })
  }
}

// ---------- 光弧生成 ----------
function createArcs() {
  arcs.length = 0
  for (let i = 0; i < 2; i++) {
    const baseY = height * (0.25 + i * 0.4)
    arcs.push({
      baseY,
      amplitude: 80 * dpr,
      period: 0.0005 + Math.random() * 0.0003,
      phase: Math.random() * Math.PI * 2,
      width: width * 0.7,
      offsetX: width * 0.15,
      hue: 220 + i * 40,
    })
  }
}

// ---------- 绘制光斑 ----------
function drawSpots() {
  for (const s of spots) {
    const cx = s.x + Math.sin(s.phase) * 40 * dpr
    const cy = s.y + Math.cos(s.phase * 0.7) * 30 * dpr

    // 使用径向渐变
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, s.r)
    grad.addColorStop(0, `rgba(${s.color[0]},${s.color[1]},${s.color[2]},0.18)`)
    grad.addColorStop(0.4, `rgba(${s.color[0]},${s.color[1]},${s.color[2]},0.08)`)
    grad.addColorStop(0.7, `rgba(${s.color[0]},${s.color[1]},${s.color[2]},0.02)`)
    grad.addColorStop(1, 'rgba(0,0,0,0)')

    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(cx, cy, s.r, 0, Math.PI * 2)
    ctx.fill()
  }
}

// ---------- 绘制光弧 ----------
function drawArcs() {
  for (const a of arcs) {
    ctx.save()
    ctx.globalAlpha = 0.07
    ctx.strokeStyle = `hsla(${a.hue},60%,70%,0.5)`
    ctx.lineWidth = 1.5 * dpr
    ctx.beginPath()

    const segments = 80
    for (let i = 0; i <= segments; i++) {
      const t = i / segments
      const x = a.offsetX + t * a.width
      const y = a.baseY + Math.sin(t * Math.PI * 2 + a.phase) * a.amplitude
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    ctx.stroke()
    ctx.restore()
  }
}

// ---------- 动画循环 ----------
function animate() {
  // 不可见时暂停
  if (document.hidden) {
    animId = requestAnimationFrame(animate)
    return
  }

  ctx.clearRect(0, 0, width, height)

  // 缓慢移动光斑
  for (const s of spots) {
    s.x += s.dx
    s.y += s.dy
    s.phase += 0.003
    if (s.x < -s.r) s.x = width + s.r
    if (s.x > width + s.r) s.x = -s.r
    if (s.y < -s.r) s.y = height + s.r
    if (s.y > height + s.r) s.y = -s.r
  }
  // 光弧相位
  for (const a of arcs) {
    a.phase += 0.002
  }

  drawArcs()
  drawSpots()

  animId = requestAnimationFrame(animate)
}

// ---------- 初始化 ----------
function init() {
  const canvas = canvasRef.value
  if (!canvas) return
  dpr = Math.min(window.devicePixelRatio || 1, 2) / 2
  ctx = canvas.getContext('2d')
  resize()
}

function resize() {
  const canvas = canvasRef.value
  if (!canvas) return
  width = window.innerWidth
  height = window.innerHeight
  canvas.width = width * dpr
  canvas.height = height * dpr
  canvas.style.width = width + 'px'
  canvas.style.height = height + 'px'
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  createSpots()
  createArcs()
}

onMounted(() => {
  init()
  animId = requestAnimationFrame(animate)
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  window.removeEventListener('resize', resize)
})
</script>

<style scoped>
.liquid-glass-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
</style>
