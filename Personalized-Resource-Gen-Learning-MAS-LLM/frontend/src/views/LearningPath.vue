<template>
  <div class="learning-path-page">
    <!-- 顶部操作栏 -->
    <div class="path-toolbar">
      <div class="toolbar-left">
        <h3 v-if="currentPath">{{ currentPath.title }}</h3>
        <h3 v-else>我的学习路径</h3>
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
          <el-button type="primary" :icon="Upload" :loading="uploadLoading">
            上传PDF生成路径
          </el-button>
        </el-upload>
      </div>
    </div>

    <!-- 路径历史列表（多条路径时显示） -->
    <div v-if="paths.length > 1 && !currentPath" class="path-list">
      <el-card v-for="p in paths" :key="p.id" class="path-card-item" shadow="hover" @click="selectPath(p)">
        <div class="path-card-title">{{ p.title }}</div>
        <div class="path-card-meta">
          <el-tag size="small" :type="p.source_type === 'pdf' ? 'warning' : 'primary'">
            {{ p.source_type === 'pdf' ? 'PDF导入' : 'AI生成' }}
          </el-tag>
          <span v-if="p.source_name">{{ p.source_name }}</span>
          <span>共 {{ p.nodes?.length || 0 }} 个阶段</span>
        </div>
      </el-card>
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
        <el-card
          class="node-card"
          :class="{ expanded: expandedNodeId === node.id }"
          shadow="hover"
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

          <!-- 展开详情 -->
          <div v-if="expandedNodeId === node.id" class="node-detail">
            <div class="detail-desc">{{ node.description }}</div>

            <!-- 推荐资源 -->
            <div v-if="node.resources && node.resources.length > 0" class="detail-resources">
              <span class="detail-label">推荐资源：</span>
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

            <!-- 操作按钮 -->
            <div class="detail-actions">
              <el-button
                v-if="node.status !== 'locked'"
                type="primary"
                :icon="EditPen"
                @click.stop="openQuiz(node)"
              >
                {{ node.quiz_passed ? '重新测验' : '开始测验' }}
              </el-button>
              <el-button v-else disabled :icon="Lock">
                需先完成上一阶段
              </el-button>
            </div>
          </div>
        </el-card>
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
const expandedNodeId = ref(null)

// Quiz dialog
const quizVisible = ref(false)
const quizNodeId = ref(null)
const quizNodeTitle = ref('')

// 进度条动画
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
    const eased = 1 - Math.pow(1 - p, 3) // easeOutCubic
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

const onQuizPassed = async (nodeId) => {
  // 刷新路径数据
  if (currentPath.value) {
    const data = await getLearningPath(currentPath.value.id)
    currentPath.value = data.path || data
    // 更新 paths 中对应路径的数据
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
    // 重新加载路径列表
    await loadAllPaths()
    // 自动选中新生成的路径
    if (data.path) {
      currentPath.value = data.path
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
    }
  } catch (e) {
    // 无路径时不报错
  }
}

const selectPath = (path) => {
  currentPath.value = path
}

onMounted(() => {
  loadAllPaths()
})
</script>

<style scoped>
.learning-path-page {
  max-width: 800px;
  margin: 0 auto;
}
.path-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.toolbar-left h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
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
  transition: box-shadow 0.2s;
}
.path-card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}
.path-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #909399;
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
  background: #409eff;
  transition: background 0.3s;
}
.line-locked {
  background: #dcdfe6;
}
.line-active {
  background: #409eff;
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
  transition: transform 0.2s;
}
.node-dot:hover {
  transform: scale(1.15);
}
.node-locked .node-dot {
  background: #c0c4cc;
}
.node-active .node-dot {
  background: #409eff;
}
.node-completed .node-dot {
  background: #67c23a;
}
.node-card {
  cursor: pointer;
  margin-bottom: 0;
  border-left: 4px solid transparent;
  transition: border-color 0.3s;
}
.node-active .node-card {
  border-left-color: #409eff;
}
.node-completed .node-card {
  border-left-color: #67c23a;
}
.node-locked .node-card {
  border-left-color: #dcdfe6;
  opacity: 0.7;
}
.node-header {
  padding: 4px 0;
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
  color: #303133;
}
.node-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
}
.node-duration {
  display: flex;
  align-items: center;
  gap: 4px;
}
.node-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e4e7ed;
  cursor: default;
}
.detail-desc {
  font-size: 14px;
  color: #606266;
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
  color: #909399;
}
.resource-tag {
  margin: 0;
}
.detail-actions {
  text-align: right;
}
</style>
