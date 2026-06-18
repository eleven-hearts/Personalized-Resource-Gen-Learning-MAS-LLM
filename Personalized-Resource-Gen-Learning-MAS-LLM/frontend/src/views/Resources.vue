<template>
  <div class="resources-page">
    <el-row :gutter="20" class="mb-20">
      <el-col :span="16">
        <el-input
          v-model="searchQuery"
          placeholder="搜索学习资源..."
          :prefix-icon="Search"
          clearable
        />
      </el-col>
      <el-col :span="8">
        <el-button type="primary" :icon="Plus" @click="showGenerateDialog = true">
          生成新资源
        </el-button>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="6" v-for="resource in filteredResourceList" :key="resource.id">
        <el-card class="resource-card" shadow="hover">
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
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="!loading && filteredResourceList.length === 0" description="暂无学习资源" />

    <!-- 生成资源对话框 -->
    <el-dialog v-model="showGenerateDialog" title="生成个性化学习资源" width="600px">
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

    <el-dialog v-model="showDetailDialog" :title="selectedResource?.title" width="760px">
      <div class="resource-content" v-html="selectedResourceHtml"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Search, Plus, View, Download, Document, Connection, EditPen, Reading, Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { getCurrentUser } from '@/api/auth'
import { generateResources, getResources } from '@/api/resource'
import { useUserStore } from '@/stores/user'

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
  document: { label: '文档', tagType: 'primary', icon: 'Document', color: '#409eff' },
  mindmap: { label: '思维导图', tagType: 'success', icon: 'Connection', color: '#67c23a' },
  quiz: { label: '题库', tagType: 'warning', icon: 'EditPen', color: '#e6a23c' },
  reading: { label: '阅读', tagType: 'info', icon: 'Reading', color: '#909399' },
  video: { label: '视频', tagType: 'primary', icon: 'Monitor', color: '#13c2c2' },
  code: { label: '代码', tagType: 'danger', icon: 'Monitor', color: '#f56c6c' },
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
    await fetchResources()
    showGenerateDialog.value = false
    ElMessage.success('资源生成完成')
  } finally {
    generating.value = false
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

onMounted(() => {
  fetchResources()
})
</script>

<style scoped>
.mb-20 {
  margin-bottom: 20px;
}

.resource-card {
  text-align: center;
  margin-bottom: 20px;
}

.resource-icon {
  margin-bottom: 12px;
}

.resource-desc {
  color: #606266;
  font-size: 14px;
  margin: 8px 0;
  min-height: 40px;
}

.resource-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
}

.resource-date {
  font-size: 12px;
  color: #909399;
}

.resource-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

.resource-content {
  line-height: 1.7;
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
  background: #f5f7fa;
  border-radius: 6px;
  overflow-x: auto;
  padding: 12px;
}
</style>
