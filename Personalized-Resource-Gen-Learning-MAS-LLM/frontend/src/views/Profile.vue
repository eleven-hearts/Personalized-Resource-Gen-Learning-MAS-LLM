<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <div class="profile-header">
            <el-avatar :size="80" :icon="UserFilled" />
            <h3>{{ displayName }}</h3>
            <p>{{ userInfo?.major || '未填写专业' }} | {{ userInfo?.grade || '未填写年级' }}</p>
          </div>
          <el-divider />
          <div class="profile-info">
            <div class="info-item">
              <span class="label">专业</span>
              <span class="value">{{ userInfo?.major || '未填写' }}</span>
            </div>
            <div class="info-item">
              <span class="label">年级</span>
              <span class="value">{{ userInfo?.grade || '未填写' }}</span>
            </div>
            <div class="info-item">
              <span class="label">邮箱</span>
              <span class="value">{{ userInfo?.email || '未填写' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card title="学习画像">
          <template #header>
            <div class="card-header">
              <span>学习画像</span>
              <el-tag type="success">动态更新中</el-tag>
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="12" v-for="(item, index) in profileDimensions" :key="index">
              <div class="dimension-card">
                <div class="dimension-header">
                  <el-icon size="24" :color="item.color"><component :is="item.icon" /></el-icon>
                  <span class="dimension-title">{{ item.name }}</span>
                </div>
                <p class="dimension-value">{{ item.value }}</p>
                <el-progress
                  v-if="item.score !== undefined"
                  :percentage="item.score"
                  :color="item.color"
                  :show-text="false"
                />
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="mt-20">
          <template #header>
            <div class="card-header">
              <span>能力雷达图</span>
            </div>
          </template>
          <div class="radar-placeholder">
            <p>（此处可集成 ECharts 雷达图展示多维度能力评估）</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { UserFilled } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const profile = computed(() => userStore.userInfo?.profile || {})
const displayName = computed(() => {
  return userInfo.value?.full_name || userInfo.value?.username || '学生用户'
})

const formatList = (value, fallback) => {
  if (Array.isArray(value) && value.length > 0) return value.join('；')
  return value || fallback
}

const profileDimensions = computed(() => [
  { name: '知识基础', value: profile.value.knowledge_base || '尚未形成明确判断，可通过智能对话补充。', score: 65, color: '#409eff', icon: 'Reading' },
  { name: '认知风格', value: profile.value.cognitive_style || '偏好结合讲解、示例和练习进行学习', score: 70, color: '#67c23a', icon: 'View' },
  { name: '易错点偏好', value: formatList(profile.value.error_prone_points, '暂无明显易错点记录'), score: 55, color: '#e6a23c', icon: 'Warning' },
  { name: '学习节奏', value: profile.value.learning_pace || '中等', score: 75, color: '#f56c6c', icon: 'Timer' },
  { name: '兴趣方向', value: profile.value.interest_direction || '尚未记录兴趣方向', score: 70, color: '#722ed1', icon: 'Star' },
  { name: '学习目标', value: formatList(profile.value.learning_goals, '尚未记录学习目标'), score: 70, color: '#13c2c2', icon: 'Reading' },
])

const loadCurrentUser = async () => {
  const latestUserInfo = await getCurrentUser()
  userStore.setUserInfo(latestUserInfo)
}

onMounted(() => {
  loadCurrentUser()
})
</script>

<style scoped>
.profile-header {
  text-align: center;
  padding: 20px 0;
}

.profile-header h3 {
  margin: 12px 0 4px;
}

.profile-header p {
  color: #909399;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.info-item .label {
  color: #909399;
}

.info-item .value {
  color: #303133;
  font-weight: 500;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dimension-card {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 16px;
}

.dimension-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.dimension-title {
  font-weight: 600;
}

.dimension-value {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
  min-height: 40px;
}

.mt-20 {
  margin-top: 20px;
}

.radar-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  background: #f5f7fa;
  border-radius: 8px;
}
</style>
