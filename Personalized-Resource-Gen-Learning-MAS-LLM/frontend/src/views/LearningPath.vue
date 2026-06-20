<template>
  <div class="learning-path-page">
    <!-- 顶部操作栏 -->
    <div class="path-toolbar glass-card">
      <div class="toolbar-left">
        <div class="path-switcher" v-if="paths.length > 0">
          <el-select
            v-model="selectedPathId"
            placeholder="选择学习路径"
            @change="onPathSelect"
            class="glass-select"
            size="large"
          >
            <el-option
              v-for="p in paths"
              :key="p.id"
              :label="p.title || '未命名路径'"
              :value="p.id"
            />
          </el-select>
        </div>
        <h3>我的学习路径</h3>
      </div>
      <div class="toolbar-right">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".pdf"
          :on-change="handleFileChange"
          :show-file-list="false"
        >
          <el-button type="primary" :icon="Upload" :loading="uploadLoading" class="glass-btn">
            上传PDF生成路径
          </el-button>
        </el-upload>
      </div>
    </div>

    <!-- 路径历史列表 -->
    <div v-if="paths.length > 1 && !currentPath" class="path-list">
      <div
        v-for="p in paths" :key="p.id"
        class="glass-card path-card-item"
        @click="selectPath(p)"
      >
        <div class="path-card-title">{{ p.title }}</div>
        <div class="path-card-meta">
          <el-tag size="small" :type="p.source_type === 'pdf' ? 'warning' : 'primary'">
            {{ p.source_type === 'pdf' ? 'PDF导入' : 'AI生成' }}
          </el-tag>
          <span v-if="p.source_name">{{ p.source_name }}</span>
          <span>共 {{ p.nodes?.length || 0 }} 个阶段</span>
        </div>
      </div>
    </div>

    <!-- 当前路径的节点时间线 -->
    <div v-if="currentPath && currentPath.nodes.length > 0" class="path-timeline">
      <div
        v-for="(node, index) in currentPath.nodes"
        :key="node.id"
        class="timeline-node"
        :class="{
          'node-locked': node.status === 'locked',
          'node-active': node.status === 'active',
          'node-completed': node.status === 'completed',
        }"
      >
        <!-- 连接线 -->
        <div class="node-connector" v-if="index > 0">
          <div class="connector-line" :class="node.status === 'locked' ? 'line-locked' : 'line-active'"></div>
        </div>

        <!-- 节点圆点 -->
        <div class="node-dot" @click="toggleNode(node)">
          <el-icon size="20">
            <Lock v-if="node.status === 'locked'" />
            <MoreFilled v-else-if="node.status === 'active'" />
            <CircleCheckFilled v-else />
          </el-icon>
        </div>

        <!-- 节点卡片 -->
        <div
          class="glass-card node-card"
          :class="{ expanded: expandedNodeId === node.id }"
          @click="toggleNode(node)"
        >
          <div class="node-header">
            <div class="node-title-row">
              <span class="node-title">{{ node.title }}</span>
              <el-tag
                size="small"
                :type="node.status === 'completed' ? 'success' : node.status === 'active' ? '' : 'info'"
              >
                {{ node.status === 'completed' ? '已完成' : node.status === 'active' ? '进行中' : '未解锁' }}
              </el-tag>
            </div>
            <div class="node-meta">
              <span v-if="node.duration" class="node-duration">
                <el-icon size="14"><Timer /></el-icon> {{ node.duration }}
              </span>
              <span class="node-progress-text">
                进度 {{ getDisplayProgress(node) }}% | 答题 {{ node.quiz_score }}/{{ node.quiz_total }}
              </span>
            </div>
            <el-progress
              :percentage="getDisplayProgress(node)"
              :status="node.progress === 100 ? 'success' : ''"
              :stroke-width="6"
            />
          </div>

          <!-- 节点资源标签 — 直接显示在卡片上 -->
          <div v-if="node.resources && node.resources.length > 0" class="node-resources-tags">
            <el-tag
              v-for="(res, ri) in node.resources"
              :key="ri"
              size="small"
              type="success"
              class="resource-tag"
            >
              {{ res }}
            </el-tag>
          </div>

          <!-- 灯塔 -->
          <div v-if="node.status === 'completed'" class="lighthouse-area">
            <svg class="lighthouse" viewBox="0 0 80 100" width="50" height="62">
              <g class="light-beams">
                <line x1="40" y1="14" x2="8" y2="40" stroke="var(--lighthouse-gold)" stroke-width="2" opacity="0.5"/>
                <line x1="40" y1="14" x2="72" y2="40" stroke="var(--lighthouse-gold)" stroke-width="2" opacity="0.5"/>
                <line x1="40" y1="14" x2="0" y2="55" stroke="var(--lighthouse-gold)" stroke-width="1.5" opacity="0.25"/>
                <line x1="40" y1="14" x2="80" y2="55" stroke="var(--lighthouse-gold)" stroke-width="1.5" opacity="0.25"/>
              </g>
              <rect x="30" y="14" width="20" height="50" rx="2" fill="var(--primary-light)" opacity="0.7"/>
              <rect x="28" y="14" width="24" height="8" rx="1" fill="var(--primary)"/>
              <rect x="30" y="30" width="20" height="4" fill="white" opacity="0.5"/>
              <rect x="30" y="42" width="20" height="4" fill="white" opacity="0.5"/>
              <rect x="30" y="54" width="20" height="4" fill="white" opacity="0.5"/>
              <circle cx="40" cy="14" r="6" fill="var(--lighthouse-gold)" opacity="0.9"/>
              <circle cx="40" cy="14" r="3" fill="#fff" opacity="0.8"/>
              <rect x="26" y="64" width="28" height="6" rx="3" fill="var(--primary)" opacity="0.6"/>
              <ellipse cx="40" cy="72" rx="18" ry="3" fill="rgba(96,165,250,0.1)"/>
            </svg>
            <span class="lighthouse-text">此阶段已完成</span>
          </div>

          <!-- 展开详情 -->
          <div v-if="expandedNodeId === node.id" class="node-detail">
            <div class="detail-desc">{{ node.description }}</div>
            <div v-if="node.resources && node.resources.length > 0" class="detail-resources">
              <span class="detail-label">推荐资源：</span>
              <el-tag v-for="(res, ri) in node.resources" :key="ri" size="small" type="success" class="resource-tag">
                {{ res }}
              </el-tag>
            </div>
            <div class="detail-actions">
              <el-button
                v-if="node.status !== 'locked'"
                type="primary"
                :icon="EditPen"
                @click.stop="openQuiz(node)"
                class="glass-btn"
              >
                {{ node.quiz_passed ? '重新测验' : '开始测验' }}
              </el-button>
              <el-button v-else disabled :icon="Lock">
                需先完成上一阶段
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!currentPath || currentPath.nodes.length === 0"
      description="还没有学习路径，上传PDF或等待AI生成"
    >
      <el-upload
        :auto-upload="false"
        :limit="1"
        accept=".pdf"
        :on-change="handleFileChange"
        :show-file-list="false"
      >
        <el-button type="primary" :icon="Upload" :loading="uploadLoading">
          上传PDF生成路径
        </el-button>
      </el-upload>
    </el-empty>

    <!-- Quiz 弹窗 -->
    <QuizDialog
      v-model="quizVisible"
      :node-id="quizNodeId"
      :node-title="quizNodeTitle"
      @passed="onQuizPassed"
      @quiz-submitted="onQuizSubmitted"
    />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Upload, Lock, MoreFilled, CircleCheckFilled, Timer, EditPen,
} from '@element-plus/icons-vue'
import { uploadPDF, getLearningPaths, getLearningPath } from '@/api/learning'
import QuizDialog from './QuizDialog.vue'

const uploadLoading = ref(false)
const paths = ref([])
const currentPath = ref(null)
const selectedPathId = ref(null)
const expandedNodeId = ref(null)

const quizVisible = ref(false)
const quizNodeId = ref(null)
const quizNodeTitle = ref('')

const nodeProgressMap = reactive({})

const getDisplayProgress = (node) => {
  const key = node.id
  if (nodeProgressMap[key] === undefined) {
    nodeProgressMap[key] = node.progress || 0
  }
  return nodeProgressMap[key] || 0
}

const animateProgress = (nodeId, fromVal, toVal, duration = 600) => {
  const start = performance.now()
  const step = (now) => {
    const elapsed = now - start
    const p = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - p, 3)
    nodeProgressMap[nodeId] = Math.round(fromVal + (toVal - fromVal) * eased)
    if (p < 1) {
      requestAnimationFrame(step)
    } else {
      nodeProgressMap[nodeId] = toVal
    }
  }
  requestAnimationFrame(step)
}

const onQuizSubmitted = ({ nodeId, progress }) => {
  const fromVal = nodeProgressMap[nodeId] || 0
  animateProgress(nodeId, fromVal, progress)
  setTimeout(() => onQuizPassed(nodeId), 800)
}

const toggleNode = (node) => {
  expandedNodeId.value = expandedNodeId.value === node.id ? null : node.id
}

const openQuiz = (node) => {
  quizNodeId.value = node.id
  quizNodeTitle.value = node.title
  quizVisible.value = true
}

const onQuizPassed = async () => {
  if (currentPath.value) {
    const data = await getLearningPath(currentPath.value.id)
    currentPath.value = data.path || data
    const idx = paths.value.findIndex((p) => p.id === currentPath.value.id)
    if (idx >= 0) {
      paths.value[idx] = currentPath.value
    }
  }
}

const handleFileChange = async (file) => {
  uploadLoading.value = true
  try {
    const data = await uploadPDF(file.raw)
    ElMessage.success('PDF解析完成，学习路径已生成')
    await loadAllPaths()
    if (data.path) {
      currentPath.value = data.path
      selectedPathId.value = data.path.id
    }
  } catch (e) {
    ElMessage.error('PDF上传或解析失败，请重试')
  } finally {
    uploadLoading.value = false
  }
}

const loadAllPaths = async () => {
  try {
    const data = await getLearningPaths()
    paths.value = Array.isArray(data) ? data : (data.paths || [])
    if (paths.value.length > 0 && !currentPath.value) {
      currentPath.value = paths.value[0]
      selectedPathId.value = paths.value[0].id
    }
  } catch (e) {
    // 无路径时不报错
  }
}

const selectPath = (path) => {
  currentPath.value = path
  selectedPathId.value = path.id
}

const onPathSelect = (pathId) => {
  const found = paths.value.find((p) => p.id === pathId)
  if (found) {
    currentPath.value = found
    selectedPathId.value = pathId
  }
}

onMounted(() => {
  loadAllPaths()
})
</script>

<style scoped>
.learning-path-page {
  max-width: 840px;
  margin: 0 auto;
}

.glass-card {
  background: rgba(25,34,52,0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--card-radius);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
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

.path-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
}

.toolbar-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.path-switcher {
  min-width: 240px;
}

.glass-select {
  width: 100%;
}

:deep(.glass-select .el-input__wrapper) {
  background: rgba(25, 34, 52, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
  border-radius: 10px !important;
  transition: all 0.3s;
}

:deep(.glass-select .el-input__wrapper:hover) {
  border-color: rgba(96, 165, 250, 0.4) !important;
  box-shadow: 0 4px 16px rgba(96, 165, 250, 0.15) !important;
}

:deep(.glass-select .el-input__wrapper.is-focus) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 1px var(--primary) inset, 0 4px 16px rgba(96, 165, 250, 0.2) !important;
}

:deep(.glass-select .el-input__inner) {
  color: var(--text-primary) !important;
}

:deep(.glass-select .el-input__suffix .el-icon) {
  color: var(--text-secondary) !important;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.path-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.path-card-item {
  cursor: pointer;
  padding: 16px 20px;
  transition: transform 0.2s;
}

.path-card-item:hover {
  transform: translateY(-1px);
}

.path-card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.path-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.path-timeline {
  position: relative;
  padding-left: 40px;
}

.timeline-node {
  position: relative;
  margin-bottom: 4px;
}

.node-connector {
  position: absolute;
  left: 19px;
  top: -20px;
  bottom: 60%;
  width: 2px;
}

.connector-line {
  width: 100%;
  height: 100%;
  background: var(--primary);
  transition: background 0.3s;
}

.line-locked {
  background: #475569;
}

.line-active {
  background: var(--primary);
}

.node-dot {
  position: absolute;
  left: -40px;
  top: 18px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  z-index: 2;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.node-dot:hover {
  transform: scale(1.15);
}

.node-locked .node-dot {
  background: #475569;
}

.node-active .node-dot {
  background: var(--primary);
  box-shadow: 0 0 16px rgba(96,165,250,0.4);
}

.node-completed .node-dot {
  background: #22c55e;
  box-shadow: 0 0 16px rgba(34,197,94,0.4);
}

.node-card {
  cursor: pointer;
  padding: 16px 20px;
  position: relative;
  overflow: hidden;
}

.node-active .node-card {
  border-left: 4px solid var(--primary) !important;
}

.node-completed .node-card {
  border-left: 4px solid #22c55e !important;
}

.node-locked .node-card {
  border-left: 4px solid #475569 !important;
  opacity: 0.5;
}

.node-header {
  padding: 2px 0;
}

.node-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.node-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.node-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.node-duration {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 节点资源标签 */
.node-resources-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.06);
}

.resource-tag {
  margin: 0;
}

/* Lighthouse */
.lighthouse-area {
  text-align: center;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed rgba(96,165,250,0.15);
}

.lighthouse {
  display: inline-block;
  filter: drop-shadow(0 0 8px rgba(245,166,35,0.3));
}

.light-beams {
  animation: beam-rotate 8s linear infinite;
  transform-origin: 40px 14px;
}

@keyframes beam-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.lighthouse-text {
  display: block;
  font-size: 12px;
  color: var(--lighthouse-gold);
  margin-top: 4px;
  letter-spacing: 1px;
}

.node-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed rgba(255,255,255,0.08);
  cursor: default;
}

.detail-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 12px;
}

.detail-resources {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.detail-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.resource-tag {
  margin: 0;
}

.detail-actions {
  text-align: right;
}
</style>
