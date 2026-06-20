<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="glass-card stat-card" ref="statCard1">
          <div class="stat-icon" style="background: rgba(96,165,250,0.15); color: var(--primary)">
            <el-icon size="32"><EditPen /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalQuestions }}</div>
            <div class="stat-label">已做题数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="glass-card stat-card" ref="statCard2">
          <div class="stat-icon" style="background: rgba(34,197,94,0.15); color: #22c55e">
            <el-icon size="32"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCorrect }}</div>
            <div class="stat-label">答对数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="glass-card stat-card" ref="statCard3">
          <div class="stat-icon" style="background: rgba(239,68,68,0.15); color: #ef4444">
            <el-icon size="32"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalWrong }}</div>
            <div class="stat-label">答错数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="glass-card stat-card" ref="statCard4">
          <div class="stat-icon" style="background: rgba(139,92,246,0.15); color: #8b5cf6">
            <el-icon size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.accuracy }}%</div>
            <div class="stat-label">准确率</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <div class="glass-card" ref="progressCardRef">
          <div class="glass-card-header">
            <span>学习进度</span>
            <el-button text type="primary" @click="$router.push('/path')">查看详情</el-button>
          </div>
          <div v-if="pathProgress.length > 0" class="progress-list">
            <div class="progress-item" v-for="item in pathProgress" :key="item.name">
              <div class="progress-info">
                <span>{{ item.name }}</span>
                <span>{{ item.percent }}% ({{ item.completed }}/{{ item.total }} 阶段)</span>
              </div>
              <el-progress :percentage="item.percent" :color="item.color" :stroke-width="8" />
            </div>
          </div>
          <el-empty v-else description="还没有学习路径，上传PDF开始学习吧" />
        </div>
      </el-col>
      <el-col :span="8">
        <div class="glass-card" ref="overviewCardRef">
          <div class="glass-card-header">
            <span>学习概况</span>
          </div>
          <div class="overview-list">
            <div class="overview-item clickable" @click="wrongVisible = true">
              <span class="overview-label">错题本</span>
              <span class="overview-value" style="color: #ef4444">
                {{ stats.totalWrong > 0 ? `${stats.totalWrong} 题` : '暂无' }}
                <el-icon size="14"><ArrowRight /></el-icon>
              </span>
            </div>
            <div class="overview-item">
              <span class="overview-label">学习路径</span>
              <span class="overview-value">{{ stats.totalPaths }} 条</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">总节点数</span>
              <span class="overview-value">{{ stats.totalNodes }} 个</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">已完成</span>
              <span class="overview-value">{{ stats.completedNodes }} 个</span>
            </div>
          </div>
          <el-empty v-if="stats.totalNodes === 0" description="暂无数据" />
        </div>
      </el-col>
    </el-row>
    <WrongAnswerDialog v-model="wrongVisible" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { EditPen, CircleCheck, CircleClose, TrendCharts, ArrowRight } from '@element-plus/icons-vue'
import { getDashboardStats } from '@/api/dashboard'
import WrongAnswerDialog from './WrongAnswerDialog.vue'
import { useLiquidGlass } from '@/composables/useLiquidGlass'

const stats = reactive({
  totalQuestions: 0,
  totalCorrect: 0,
  totalWrong: 0,
  accuracy: 0,
  totalPaths: 0,
  totalNodes: 0,
  completedNodes: 0,
})

const pathProgress = ref([])
const wrongVisible = ref(false)

/* Canvas 液态玻璃高光 — 统计卡片 + 两个大卡片 */
const statCard1 = ref(null)
const statCard2 = ref(null)
const statCard3 = ref(null)
const statCard4 = ref(null)
const progressCardRef = ref(null)
const overviewCardRef = ref(null)

useLiquidGlass(statCard1, { size: 200, alpha: 0.15 })
useLiquidGlass(statCard2, { size: 200, alpha: 0.15 })
useLiquidGlass(statCard3, { size: 200, alpha: 0.15 })
useLiquidGlass(statCard4, { size: 200, alpha: 0.15 })
useLiquidGlass(progressCardRef, { size: 300, alpha: 0.14 })
useLiquidGlass(overviewCardRef, { size: 280, alpha: 0.14 })

const getColorByProgress = (progress) => {
  if (progress >= 80) return '#22c55e'
  if (progress >= 50) return 'var(--primary)'
  if (progress >= 20) return '#e6a23c'
  return '#ef4444'
}

const loadDashboard = async () => {
  try {
    const data = await getDashboardStats()
    stats.totalQuestions = data.total_questions_answered || 0
    stats.totalCorrect = data.total_correct || 0
    stats.totalWrong = data.total_wrong || 0
    stats.accuracy = data.accuracy || 0
    stats.totalPaths = data.total_paths || 0
    stats.totalNodes = data.total_nodes || 0
    stats.completedNodes = data.completed_nodes || 0
    pathProgress.value = (data.path_progress || []).map((p) => ({
      name: p.title,
      percent: p.progress,
      completed: p.completed_nodes,
      total: p.total_nodes,
      color: getColorByProgress(p.progress),
    }))
  } catch (e) {
    // 无数据时保持为0
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.glass-card {
  background: rgba(25,34,52,0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--card-radius);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  padding: 20px;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.glass-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  cursor: default;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 13px;
  margin-top: 2px;
}

.mt-20 {
  margin-top: 20px;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-info span:first-child {
  font-weight: 500;
  color: var(--text-primary);
}

.progress-info span:last-child {
  color: var(--text-secondary);
}

.overview-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.overview-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.overview-value {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
}

.overview-item.clickable {
  cursor: pointer;
  border-radius: 6px;
  padding: 8px 6px;
  margin: -4px -2px;
}

.overview-item.clickable:hover {
  background: rgba(239,68,68,0.1);
}
</style>
