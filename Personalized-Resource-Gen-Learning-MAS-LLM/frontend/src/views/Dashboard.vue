<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6f7ff; color: #1890ff">
            <el-icon size="32"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.resourceCount }}</div>
            <div class="stat-label">已生成资源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f6ffed; color: #52c41a">
            <el-icon size="32"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.studyHours }}h</div>
            <div class="stat-label">学习时长</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #fff7e6; color: #fa8c16">
            <el-icon size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.mastery }}%</div>
            <div class="stat-label">知识掌握度</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f9f0ff; color: #722ed1">
            <el-icon size="32"><Star /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.score }}</div>
            <div class="stat-label">学习评分</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <el-card title="学习进度">
          <template #header>
            <div class="card-header">
              <span>学习进度</span>
              <el-button text type="primary">查看详情</el-button>
            </div>
          </template>
          <div class="progress-list">
            <div class="progress-item" v-for="item in progressList" :key="item.name">
              <div class="progress-info">
                <span>{{ item.name }}</span>
                <span>{{ item.percent }}%</span>
              </div>
              <el-progress :percentage="item.percent" :color="item.color" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近资源</span>
            </div>
          </template>
          <div class="recent-resources">
            <div class="resource-item" v-for="resource in recentResources" :key="resource.id">
              <el-icon><Document /></el-icon>
              <span>{{ resource.title }}</span>
              <el-tag size="small" type="success">{{ resource.type }}</el-tag>
            </div>
            <el-empty v-if="recentResources.length === 0" description="暂无资源" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getCurrentUser } from '@/api/auth'
import { getResources } from '@/api/resource'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const stats = reactive({
  resourceCount: 0,
  studyHours: 0,
  mastery: 0,
  score: '0.0',
})
const recentResources = ref([])

const progressList = ref([
  { name: '机器学习基础', percent: 75, color: '#409eff' },
  { name: '深度学习原理', percent: 45, color: '#67c23a' },
  { name: '自然语言处理', percent: 30, color: '#e6a23c' },
  { name: '计算机视觉', percent: 20, color: '#f56c6c' },
])

const typeLabels = {
  document: '文档',
  mindmap: '导图',
  quiz: '题库',
  reading: '阅读',
  video: '视频',
  code: '代码',
}

const ensureUserInfo = async () => {
  if (userStore.userInfo) return userStore.userInfo
  const userInfo = await getCurrentUser()
  userStore.setUserInfo(userInfo)
  return userInfo
}

const loadDashboard = async () => {
  const userInfo = await ensureUserInfo()
  const resources = await getResources({ user_id: userInfo.id, limit: 100 })
  stats.resourceCount = resources.length
  stats.studyHours = Math.max(resources.length * 2, 0)
  stats.mastery = resources.length > 0 ? 75 : 0
  stats.score = resources.length > 0 ? '4.5' : '0.0'
  recentResources.value = resources.slice(0, 5).map((resource) => ({
    ...resource,
    type: typeLabels[resource.resource_type] || '资源',
  }))
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
}

.recent-resources {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
}

.resource-item:hover {
  background-color: #f5f7fa;
}

.resource-item span {
  flex: 1;
  font-size: 14px;
}
</style>
