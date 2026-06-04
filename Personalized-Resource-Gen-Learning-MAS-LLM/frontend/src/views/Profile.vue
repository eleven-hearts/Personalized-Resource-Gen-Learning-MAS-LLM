<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <div class="profile-header">
            <el-avatar :size="80" :icon="UserFilled" />
            <h3>张三</h3>
            <p>计算机科学与技术 | 大三</p>
          </div>
          <el-divider />
          <div class="profile-info">
            <div class="info-item">
              <span class="label">专业</span>
              <span class="value">计算机科学与技术</span>
            </div>
            <div class="info-item">
              <span class="label">年级</span>
              <span class="value">大三</span>
            </div>
            <div class="info-item">
              <span class="label">邮箱</span>
              <span class="value">zhangsan@example.com</span>
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
import { UserFilled, Brain, View, Warning, Timer, Star } from '@element-plus/icons-vue'

const profileDimensions = [
  { name: '知识基础', value: '扎实的数学和编程基础，熟悉Python', score: 85, color: '#409eff', icon: 'Brain' },
  { name: '认知风格', value: '视觉型学习者，偏好图表和代码示例', score: 70, color: '#67c23a', icon: 'View' },
  { name: '易错点偏好', value: '数学推导、概率统计概念', score: 60, color: '#e6a23c', icon: 'Warning' },
  { name: '学习节奏', value: '中等偏快，适合密集型学习', score: 75, color: '#f56c6c', icon: 'Timer' },
  { name: '兴趣方向', value: '深度学习、计算机视觉', score: 90, color: '#722ed1', icon: 'Star' },
  { name: '学习目标', value: '掌握机器学习核心算法，完成2个项目', score: 80, color: '#13c2c2', icon: 'Brain' },
]
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
