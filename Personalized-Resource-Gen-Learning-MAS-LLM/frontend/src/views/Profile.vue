<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左侧：用户信息 -->
      <el-col :span="8">
        <el-card>
          <div class="user-avatar">
            <el-avatar :size="80" :icon="UserFilled" />
            <h3>{{ displayName }}</h3>
            <p>{{ userInfo?.major || '专业未设置' }} | {{ userInfo?.grade || '年级未设置' }}</p>
          </div>
          <el-divider />
          <el-descriptions :column="1" border>
            <el-descriptions-item label="邮箱">{{ userInfo?.email }}</el-descriptions-item>
            <el-descriptions-item label="专业">{{ userInfo?.major || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="年级">{{ userInfo?.grade || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="总做题数">{{ profile.total_quiz_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="总体准确率">{{ profile.overall_accuracy || 0 }}%</el-descriptions-item>
            <el-descriptions-item label="综合评分">{{ profile.evaluation_score || 0 }} 分</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右侧：AI画像 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>AI 学习画像</span>
              <div class="card-header-right">
                <el-tag v-if="profile.generated_at" size="small" type="info">
                  生成于 {{ formatDate(profile.generated_at) }}
                </el-tag>
                <el-button type="primary" :icon="Refresh" :loading="generating" @click="generateProfileAction">
                  刷新画像
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="generating" class="loading-area">
            <el-icon class="is-loading" size="36"><Loading /></el-icon>
            <p>AI 正在分析答题数据，生成个性化画像...</p>
          </div>

          <div v-else-if="!hasProfile" class="empty-profile">
            <el-empty description="尚未生成学习画像">
              <el-button type="primary" @click="generateProfileAction">
                立即生成
              </el-button>
            </el-empty>
          </div>

          <div v-else class="profile-content">
            <!-- 六维评分 -->
            <div class="dimensions-grid">
              <div v-for="(value, key) in profile.dimensions" :key="key" class="dimension-item">
                <div class="dim-label">{{ dimensionLabels[key] || key }}</div>
                <el-progress type="circle" :percentage="value" :color="getColorByScore(value)" :width="100" />
                <div class="dim-value">{{ value }}分</div>
              </div>
            </div>

            <el-divider />

            <!-- AI文字描述 -->
            <div class="profile-descriptions">
              <div class="desc-item">
                <el-tag>知识基础</el-tag>
                <span>{{ profile.knowledge_base || '--' }}</span>
              </div>
              <div class="desc-item">
                <el-tag type="success">认知风格</el-tag>
                <span>{{ profile.cognitive_style || '--' }}</span>
              </div>
              <div class="desc-item">
                <el-tag type="warning">薄弱点</el-tag>
                <span>{{ formatList(profile.error_prone_points) || '--' }}</span>
              </div>
              <div class="desc-item">
                <el-tag type="danger">学习节奏</el-tag>
                <span>{{ profile.learning_pace || '--' }}</span>
              </div>
              <div class="desc-item">
                <el-tag type="info">兴趣方向</el-tag>
                <span>{{ formatList(profile.interest_direction) || '--' }}</span>
              </div>
              <div class="desc-item">
                <el-tag type="">学习目标</el-tag>
                <span>{{ formatList(profile.learning_goals) || '--' }}</span>
              </div>
            </div>

            <el-divider v-if="profile.suggestions && profile.suggestions.length > 0" />

            <!-- AI建议 -->
            <div v-if="profile.suggestions && profile.suggestions.length > 0" class="suggestions">
              <h4>AI 学习建议</h4>
              <ul>
                <li v-for="(s, i) in profile.suggestions" :key="i">{{ s }}</li>
              </ul>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled, Refresh, Loading } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { generateProfile } from '@/api/learning'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const generating = ref(false)

const userInfo = computed(() => userStore.userInfo)
const displayName = computed(() => userInfo.value?.full_name || userInfo.value?.username || '学生')
const profile = computed(() => userInfo.value?.profile || {})
const hasProfile = computed(() => {
  const p = profile.value
  return p.dimensions && typeof p.dimensions === 'object' && Object.keys(p.dimensions).length > 0
})

const dimensionLabels = {
  knowledge_mastery: '知识掌握度',
  cognitive_ability: '认知能力',
  learning_efficiency: '学习效率',
  weakness_awareness: '薄弱点意识',
  consistency: '学习一致性',
  growth_potential: '成长潜力',
}

const formatList = (arr) => {
  if (!Array.isArray(arr)) return ''
  return arr.join('；')
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleString()
}

const getColorByScore = (score) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

const loadCurrentUser = async () => {
  if (!userStore.userInfo) {
    const info = await getCurrentUser()
    userStore.setUserInfo(info)
  }
}

const generateProfileAction = async () => {
  generating.value = true
  try {
    await generateProfile()
    const userInfoUpdated = await getCurrentUser()
    userStore.setUserInfo(userInfoUpdated)
    ElMessage.success('学习画像已更新')
  } catch (e) {
    ElMessage.error('画像生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  await loadCurrentUser()
  // 有答题数据但无画像时自动生成
  if (profile.value.total_quiz_count > 0 && !hasProfile.value && !generating.value) {
    generateProfileAction()
  }
})
</script>

<style scoped>
.user-avatar {
  text-align: center;
  padding: 16px 0;
}
.user-avatar h3 {
  margin: 12px 0 4px;
  font-size: 18px;
}
.user-avatar p {
  color: #909399;
  font-size: 14px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.loading-area {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}
.loading-area p {
  margin-top: 16px;
  font-size: 15px;
}
.empty-profile {
  padding: 40px;
}
.dimensions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  justify-items: center;
}
.dimension-item {
  text-align: center;
}
.dim-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 10px;
  font-weight: 500;
}
.dim-value {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
.profile-descriptions {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.desc-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  line-height: 1.7;
}
.desc-item .el-tag {
  flex-shrink: 0;
  margin-top: 2px;
}
.desc-item span {
  font-size: 14px;
  color: #303133;
}
.suggestions h4 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #303133;
}
.suggestions ul {
  padding-left: 20px;
  margin: 0;
}
.suggestions li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}
</style>
