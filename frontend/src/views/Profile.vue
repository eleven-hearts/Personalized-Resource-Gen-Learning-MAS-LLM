<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左侧：用户信息 -->
      <el-col :span="8">
        <div class="glass-card" ref="userCardRef">
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
        </div>
      </el-col>

      <!-- 右侧：AI画像 -->
      <el-col :span="16">
        <div class="glass-card" ref="profileCardRef">
          <div class="card-header">
            <span>AI 学习画像</span>
            <div class="card-header-right">
              <el-tag v-if="profile.generated_at" size="small" type="info">
                生成于 {{ formatDate(profile.generated_at) }}
              </el-tag>
              <el-button type="primary" :icon="Refresh" :loading="generating" @click="generateProfileAction" class="glass-btn">
                刷新画像
              </el-button>
            </div>
          </div>

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

            <div v-if="profile.suggestions && profile.suggestions.length > 0" class="suggestions">
              <h4>AI 学习建议</h4>
              <ul>
                <li v-for="(s, i) in profile.suggestions" :key="i">{{ s }}</li>
              </ul>
            </div>
          </div>
        </div>
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
import { useLiquidGlass } from '@/composables/useLiquidGlass'

const userStore = useUserStore()
const generating = ref(false)

/* Canvas 液态玻璃高光 */
const userCardRef = ref(null)
const profileCardRef = ref(null)
useLiquidGlass(userCardRef, { size: 280, alpha: 0.14 })
useLiquidGlass(profileCardRef, { size: 350, alpha: 0.14 })

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
  if (score >= 80) return '#22c55e'
  if (score >= 60) return 'var(--primary)'
  if (score >= 40) return '#e6a23c'
  return '#ef4444'
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
  if (profile.value.total_quiz_count > 0 && !hasProfile.value && !generating.value) {
    generateProfileAction()
  }
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

.glass-btn {
  background: rgba(96,165,250,0.15) !important;
  border: 1px solid rgba(96,165,250,0.25) !important;
  color: var(--primary-light) !important;
  box-shadow: none !important;
  transition: all 0.3s;
}

.glass-btn:hover {
  background: var(--primary) !important;
  color: #fff !important;
  box-shadow: 0 0 16px rgba(96,165,250,0.2) !important;
}

.user-avatar {
  text-align: center;
  padding: 16px 0;
}

.user-avatar h3 {
  margin: 12px 0 4px;
  font-size: 18px;
  color: var(--text-primary);
}

.user-avatar p {
  color: var(--text-secondary);
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: rgb(252, 247, 247);
}

.card-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loading-area {
  text-align: center;
  padding: 60px 20px;
  color: rgb(252, 247, 247);
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
  color: var(--text-secondary);
  margin-bottom: 10px;
  font-weight: 500;
}

.dim-value {
  font-size: 12px;
  color: var(--text-secondary);
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
  
}

.suggestions h4 {
  margin: 0 0 12px;
  font-size: 15px;
  color: var(--text-primary);
}

.suggestions ul {
  padding-left: 20px;
  margin: 0;
}

.suggestions li {
  margin-bottom: 8px;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
}
</style>
