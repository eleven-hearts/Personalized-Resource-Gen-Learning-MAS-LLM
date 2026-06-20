import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 卡片液态玻璃高光层 composable
 * 在卡片上叠加 Canvas，鼠标移动时产生镜面高光效果
 *
 * @param {import('vue').Ref<HTMLElement|null>} cardRef
 * @param {{ size?: number, alpha?: number, edgeGlow?: boolean }} [options]
 * @returns {{ cleanup: () => void }}
 */
export function useLiquidGlass(cardRef, options = {}) {
  const {
    size = 260,
    alpha = 0.15,
    edgeGlow = false,
  } = options

  let canvas = null
  let ctx = null
  let animId = null
  let dpr = 1
  // 高光当前位置 / 目标位置
  let cx = -999, cy = -999
  let targetX = -999, targetY = -999

  function initCanvas() {
    const card = cardRef.value
    if (!card) return
    canvas = document.createElement('canvas')
    canvas.className = 'lg-highlight'
    Object.assign(canvas.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      zIndex: '1',
      borderRadius: 'inherit',
    })
    card.style.position = card.style.position || 'relative'
    card.style.overflow = card.style.overflow || 'hidden'
    card.appendChild(canvas)

    dpr = Math.min(window.devicePixelRatio || 1, 2)
    resizeCanvas()
  }

  function resizeCanvas() {
    if (!canvas || !cardRef.value) return
    const rect = cardRef.value.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx = canvas.getContext('2d')
  }

  function draw() {
    if (!ctx || !canvas) return
    const w = canvas.width
    const h = canvas.height

    // 平滑追踪目标位置
    cx += (targetX * dpr - cx) * 0.08
    cy += (targetY * dpr - cy) * 0.08

    ctx.clearRect(0, 0, w, h)

    // 主高光 — 跟随鼠标的径向渐变
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, size * dpr)
    grad.addColorStop(0, `rgba(255,255,255,${alpha * 1.2})`)
    grad.addColorStop(0.3, `rgba(255,255,255,${alpha * 0.5})`)
    grad.addColorStop(0.6, `rgba(200,220,255,${alpha * 0.15})`)
    grad.addColorStop(1, 'rgba(0,0,0,0)')

    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(cx, cy, size * dpr, 0, Math.PI * 2)
    ctx.fill()

    // 边缘虹彩发光（可选）
    if (edgeGlow) {
      ctx.save()
      ctx.globalAlpha = alpha * 0.4
      ctx.strokeStyle = `hsla(${210 + Math.sin(Date.now() * 0.0005) * 30}, 80%, 75%, 0.3)`
      ctx.lineWidth = 1.5 * dpr
      ctx.strokeRect(2 * dpr, 2 * dpr, w - 4 * dpr, h - 4 * dpr)
      ctx.restore()
    }

    animId = requestAnimationFrame(draw)
  }

  function onMouseMove(e) {
    const rect = cardRef.value?.getBoundingClientRect()
    if (!rect) return
    targetX = e.clientX - rect.left
    targetY = e.clientY - rect.top
  }

  function onMouseLeave() {
    // 高光移到卡片外（淡出）
    targetX = -size
    targetY = -size
  }

  function onMouseEnter(e) {
    const rect = cardRef.value?.getBoundingClientRect()
    if (!rect) return
    targetX = e.clientX - rect.left
    targetY = e.clientY - rect.top
    // 直接跳过去，不要从外部渐变过来
    cx = targetX * dpr
    cy = targetY * dpr
  }

  onMounted(() => {
    initCanvas()
    animId = requestAnimationFrame(draw)
    const card = cardRef.value
    if (card) {
      card.addEventListener('mousemove', onMouseMove)
      card.addEventListener('mouseleave', onMouseLeave)
      card.addEventListener('mouseenter', onMouseEnter)
    }
    window.addEventListener('resize', resizeCanvas)
  })

  onUnmounted(() => {
    cancelAnimationFrame(animId)
    const card = cardRef.value
    if (card) {
      card.removeEventListener('mousemove', onMouseMove)
      card.removeEventListener('mouseleave', onMouseLeave)
      card.removeEventListener('mouseenter', onMouseEnter)
    }
    if (canvas && cardRef.value) {
      cardRef.value.removeChild(canvas)
    }
    window.removeEventListener('resize', resizeCanvas)
  })
}
