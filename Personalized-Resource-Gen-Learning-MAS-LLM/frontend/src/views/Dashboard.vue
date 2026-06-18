<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6f7ff; color: #1890ff">
            <el-icon size="32"><EditPen /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalQuestions }}</div>
            <div class="stat-label">已做题数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f6ffed; color: #52c41a">
            <el-icon size="32"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCorrect }}</div>
            <div class="stat-label">答对数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #fff1f0; color: #f5222d">
            <el-icon size="32"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalWrong }}</div>
            <div class="stat-label">答错数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f9f0ff; color: #722ed1">
            <el-icon size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.accuracy }}%</div>
            <div class="stat-label">准确率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>学习进度</span>
              <el-button text type="primary" @click="$router.push('/path')">查看详情</el-button>
            </div>
          </template>
          <div v-if="pathProgress.length > 0" class="progress-list">
            <div class="progress-item" v-for="item in pathProgress" :key="item.name">
              <div class="progress-info">
                <span>{{ item.name }}</span>
                <span>{{ item.percent }}% ({{ item.completed }}/{{ item.total }} 阶段)</span>
              </div>
              <el-progress :percentage="item.percent" :color="item.color" />
            </div>
          </div>
          <el-empty v-else description="还没有学习路径，上传PDF开始学习吧" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>学习概况</span>
            </div>
          </template>
          <div class="overview-list">
            <div class="overview-item clickable" @click="wrongVisible = true">
              <span class="overview-label">错题本</span>
              <span class="overview-value" style="color: #f56c6c">
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
        </el-card>
      </el-col>
    </el-row>
  </div>
  <WrongAnswerDialog v-model="wrongVisible" />
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { EditPen, CircleCheck, CircleClose, TrendCharts, ArrowRight } from '@element-plus/icons-vue'
import { getDashboardStats } from '@/api/dashboard'
import WrongAnswerDialog from './WrongAnswerDialog.vue'

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

const getColorByProgress = (progress) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 50) return '#409eff'
  if (progress >= 20) return '#e6a23c'
  return '#f56c6c'
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
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-top: 4px;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  color: #303133;
}

.progress-info span:last-child {
  color: #909399;
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
  border-bottom: 1px solid #f0f0f0;
}

.overview-label {
  color: #909399;
  font-size: 14px;
}

.overview-value {
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.overview-item.clickable {
  cursor: pointer;
  border-radius: 4px;
  padding: 8px 4px;
  margin: -4px;
}
.overview-item.clickable:hover {
  background: #fef0f0;
}
</style>
