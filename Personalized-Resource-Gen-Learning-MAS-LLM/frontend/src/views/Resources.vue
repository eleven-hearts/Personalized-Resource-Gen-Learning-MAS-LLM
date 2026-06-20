<template>
  <div class="resources-page">
    <el-row :gutter="20" class="mb-20">
      <el-col :span="16">
        <div class="glass-input-wrapper">
          <el-input
            v-model="searchQuery"
            placeholder="搜索学习资源..."
            :prefix-icon="Search"
            clearable
            class="glass-search"
          />
        </div>
      </el-col>
      <el-col :span="8">
        <el-button type="primary" :icon="Plus" @click="showGenerateDialog = true" class="glass-btn">
          生成新资源
        </el-button>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="6" v-for="resource in filteredResourceList" :key="resource.id">
        <div class="glass-card resource-card" :ref="(el: any) => setCardRef(resource.id, el)">
          <div class="resource-icon">
            <el-icon size="40" :color="resource.color">
              <component :is="resource.icon" />
            </el-icon>
          </div>
          <h4>{{ resource.title }}</h4>
          <p class="resource-desc">{{ resource.description }}</p>
          <div class="resource-meta">
            <el-tag size="small" :type="resource.tagType">{{ resource.type }}</el-tag>
            <span class="resource-date">{{ resource.date }}</span>
          </div>
          <div class="resource-actions">
            <el-button text type="primary" :icon="View" @click="openResource(resource)">
              查看
            </el-button>
            <el-button text type="primary" :icon="Download" @click="downloadResource(resource)">
              下载
            </el-button>
            <el-button text type="warning" :icon="Plus" @click="openAddToPath(resource)">
              加到路径
            </el-button>
            <el-button text type="danger" :icon="Delete" @click="handleDelete(resource)">
              删除
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-empty v-if="!loading && filteredResourceList.length === 0" description="暂无学习资源" />

    <el-dialog v-model="showGenerateDialog" title="生成个性化学习资源" width="600px" class="glass-dialog">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="课程">
          <el-input v-model="generateForm.course" placeholder="如：机器学习基础" />
        </el-form-item>
        <el-form-item label="知识点">
          <el-input v-model="generateForm.topic" placeholder="如：线性回归" />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-checkbox-group v-model="generateForm.types">
            <el-checkbox label="document">讲解文档</el-checkbox>
            <el-checkbox label="mindmap">思维导图</el-checkbox>
            <el-checkbox label="quiz">练习题</el-checkbox>
            <el-checkbox label="reading">拓展阅读</el-checkbox>
            <el-checkbox label="code">代码案例</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="特殊要求">
          <el-input
            v-model="generateForm.requirements"
            type="textarea"
            :rows="3"
            placeholder="描述你对资源的特殊要求..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="generateResource">
          开始生成
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" :title="selectedResource?.title" width="760px" class="glass-dialog">
      <div class="resource-content" v-html="selectedResourceHtml"></div>
    </el-dialog>

    <el-dialog v-model="showAddToPathDialog" title="添加到学习路径" width="500px">
      <el-form label-width="80px">
        <el-form-item label="选择路径">
          <el-select v-model="addToPathForm.pathId" placeholder="选择学习路径" @change="onPathChange" style="width: 100%">
            <el-option v-for="p in availablePaths" :key="p.id" :label="p.title || '未命名路径'" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择节点">
          <el-select v-model="addToPathForm.nodeId" placeholder="选择路径节点" :disabled="!addToPathForm.pathId" style="width: 100%">
            <el-option v-for="n in availableNodes" :key="n.id" :label="`${n.order_index + 1}. ${n.title}`" :value="n.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddToPathDialog = false">取消</el-button>
        <el-button type="primary" :loading="addingToPath" @click="confirmAddToPath" :disabled="!addToPathForm.nodeId">
          确认添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Search, Plus, View, Download, Document, Connection, EditPen, Reading, Monitor, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import { getCurrentUser } from '@/api/auth'
import { deleteResource, generateResources, getResources } from '@/api/resource'
import { addResourceToNode, getLearningPaths } from '@/api/learning'
import { useUserStore } from '@/stores/user'
import { useLiquidGlass } from '@/composables/useLiquidGlass'

const userStore = useUserStore()
const searchQuery = ref('')
const showGenerateDialog = ref(false)
const showDetailDialog = ref(false)
const generating = ref(false)
const loading = ref(false)
const resourceList = ref([])
const selectedResource = ref(null)

const generateForm = reactive({
  course: '',
  topic: '',
  types: ['document', 'quiz'],
  requirements: '',
})

const typeConfig = {
  document: { label: '文档', tagType: 'primary', icon: 'Document', color: '#3b82c6' },
  mindmap: { label: '思维导图', tagType: 'success', icon: 'Connection', color: '#22c55e' },
  quiz: { label: '题库', tagType: 'warning', icon: 'EditPen', color: '#e6a23c' },
  reading: { label: '阅读', tagType: 'info', icon: 'Reading', color: '#64748b' },
  video: { label: '视频', tagType: 'primary', icon: 'Monitor', color: '#14b8a6' },
  code: { label: '代码', tagType: 'danger', icon: 'Monitor', color: '#ef4444' },
}

/* Canvas 液态玻璃 — 只给前4个资源卡片挂高光 */
const cardRefs = {}
const setCardRef = (id, el) => {
  if (el && !cardRefs[id]) {
    cardRefs[id] = el
  }
}

const ensureUserInfo = async () => {
  if (userStore.userInfo) return userStore.userInfo
  const userInfo = await getCurrentUser()
  userStore.setUserInfo(userInfo)
  return userInfo
}

const formatDate = (value) => {
  if (!value) return ''
  return new Date(value).toLocaleDateString()
}

const normalizeResource = (resource) => {
  const config = typeConfig[resource.resource_type] || typeConfig.document
  const plainContent = (resource.content || '').replace(/[#`*\n]/g, ' ').trim()
  return {
    ...resource,
    description: resource.metadata?.description || plainContent.slice(0, 56) || '暂无描述',
    type: config.label,
    tagType: config.tagType,
    icon: config.icon,
    color: config.color,
    date: formatDate(resource.created_at),
  }
}

const filteredResourceList = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase()
  const normalized = resourceList.value.map(normalizeResource)
  if (!keyword) return normalized
  return normalized.filter((resource) => {
    return [
      resource.title,
      resource.description,
      resource.metadata?.course,
      resource.metadata?.topic,
    ].some((value) => String(value || '').toLowerCase().includes(keyword))
  })
})

const selectedResourceHtml = computed(() => {
  return marked.parse(selectedResource.value?.content || '暂无内容')
})

const fetchResources = async () => {
  loading.value = true
  try {
    const userInfo = await ensureUserInfo()
    resourceList.value = await getResources({ user_id: userInfo.id })
  } catch (err) {
    ElMessage.error('获取资源列表失败')
  } finally {
    loading.value = false
  }
}

const generateResource = async () => {
  if (!generateForm.course.trim() && !generateForm.topic.trim()) {
    ElMessage.warning('请至少填写课程或知识点')
    return
  }
  if (generateForm.types.length === 0) {
    ElMessage.warning('请至少选择一种资源类型')
    return
  }
  generating.value = true
  try {
    const userInfo = await ensureUserInfo()
    await generateResources({
      user_id: userInfo.id,
      course: generateForm.course,
      topic: generateForm.topic,
      types: generateForm.types,
      requirements: generateForm.requirements,
      profile: userInfo.profile || {},
    })
    showGenerateDialog.value = false
    ElMessage.success('资源生成完成')
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || err?.message || '资源生成失败')
  } finally {
    generating.value = false
    await fetchResources()
  }
}

const openResource = (resource) => {
  selectedResource.value = resource
  showDetailDialog.value = true
}

const downloadResource = (resource) => {
  const blob = new Blob([resource.content || ''], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${resource.title}.md`
  link.click()
  URL.revokeObjectURL(url)
}

const handleDelete = async (resource) => {
  try {
    await ElMessageBox.confirm('确定要删除该资源吗？', '确认删除')
    await deleteResource(resource.id)
    ElMessage.success('已删除')
    await fetchResources()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败，请重试')
    }
  }
}

const showAddToPathDialog = ref(false)
const addingToPath = ref(false)
const selectedResourceForPath = ref(null)
const availablePaths = ref([])
const availableNodes = ref([])
const addToPathForm = reactive({ pathId: null, nodeId: null })

const openAddToPath = async (resource) => {
  selectedResourceForPath.value = resource
  addToPathForm.pathId = null
  addToPathForm.nodeId = null
  availableNodes.value = []
  try {
    const paths = await getLearningPaths()
    availablePaths.value = Array.isArray(paths) ? paths : (paths.paths || [])
  } catch {
    ElMessage.error('获取学习路径失败')
    return
  }
  if (availablePaths.value.length === 0) {
    ElMessage.warning('暂无学习路径，请先上传PDF或生成学习路径')
    return
  }
  showAddToPathDialog.value = true
}

const onPathChange = async (pathId) => {
  addToPathForm.nodeId = null
  availableNodes.value = []
  const path = availablePaths.value.find(p => p.id === pathId)
  if (path?.nodes) {
    availableNodes.value = path.nodes
  }
}

const confirmAddToPath = async () => {
  addingToPath.value = true
  try {
    await addResourceToNode(addToPathForm.nodeId, selectedResourceForPath.value.id)
    ElMessage.success('资源已添加到学习路径')
    showAddToPathDialog.value = false
  } catch {
    ElMessage.error('添加失败，请重试')
  } finally {
    addingToPath.value = false
  }
}

onMounted(() => {
  fetchResources()
})
</script>

<style scoped>
.mb-20 {
  margin-bottom: 20px;
}

.glass-card {
  background: rgba(25,34,52,0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--card-radius);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
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

.glass-input-wrapper :deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.06);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: none !important;
}

.glass-input-wrapper :deep(.el-input__inner) {
  color: var(--text-primary);
}

.glass-input-wrapper :deep(.el-input__wrapper:hover) {
  border-color: rgba(96,165,250,0.4);
}

.glass-input-wrapper :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary);
  background: rgba(255,255,255,0.1);
}

.resource-icon {
  margin-bottom: 12px;
}

h4 {
  color: var(--text-primary);
  margin: 0 0 8px;
}

.resource-desc {
  color: var(--text-secondary);
  font-size: 13px;
  margin: 8px 0;
  min-height: 36px;
  line-height: 1.5;
}

.resource-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
}

.resource-date {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 重写卡片 overflow 防止按钮被裁剪 */
.resource-card {
  overflow: visible !important;
}

.resource-card .glass-card-header,
.resource-card .resource-icon,
.resource-card h4,
.resource-card .resource-desc,
.resource-card .resource-meta {
  position: relative;
  z-index: 1;
}

.resource-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2px;
  border-top: 1px solid rgba(8, 8, 8, 0.06);
  padding-top: 10px;
  margin-top: 4px;
}

.resource-actions :deep(.el-button) {
  font-size: 12px;
  padding: 4px 8px;
}

.resource-content {
  line-height: 1.7;
  color: #070707;
}

.resource-content :deep(h1),
.resource-content :deep(h2),
.resource-content :deep(h3) {
  margin: 12px 0 8px;
}

.resource-content :deep(ul),
.resource-content :deep(ol) {
  padding-left: 22px;
}

.resource-content :deep(pre) {
  background: rgba(8, 7, 7, 0.2);
  border-radius: 6px;
  overflow-x: auto;
  padding: 12px;
}
</style>
