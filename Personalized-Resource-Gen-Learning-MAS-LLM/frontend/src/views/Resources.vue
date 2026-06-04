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

    <el-row :gutter="20">
      <el-col :span="6" v-for="resource in resourceList" :key="resource.id">
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
            <el-button text type="primary" :icon="View">查看</el-button>
            <el-button text type="primary" :icon="Download">下载</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

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
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Search, Plus, View, Download, Document, Connection, EditPen, Reading, Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const searchQuery = ref('')
const showGenerateDialog = ref(false)
const generating = ref(false)

const generateForm = reactive({
  course: '',
  topic: '',
  types: ['document', 'quiz'],
  requirements: '',
})

const resourceList = ref([
  { id: 1, title: '机器学习概述', description: '机器学习基本概念与发展历程', type: '文档', tagType: 'primary', icon: 'Document', color: '#409eff', date: '2026-04-01' },
  { id: 2, title: '监督学习知识图谱', description: '监督学习核心知识点思维导图', type: '思维导图', tagType: 'success', icon: 'Connection', color: '#67c23a', date: '2026-04-01' },
  { id: 3, title: '线性回归练习题', description: '包含20道难度递进的练习题', type: '题库', tagType: 'warning', icon: 'EditPen', color: '#e6a23c', date: '2026-04-02' },
  { id: 4, title: '深度学习论文推荐', description: '5篇必读的深度学习经典论文', type: '阅读', tagType: 'info', icon: 'Reading', color: '#909399', date: '2026-04-02' },
  { id: 5, title: '神经网络实现', description: '使用PyTorch实现神经网络', type: '代码', tagType: 'danger', icon: 'Monitor', color: '#f56c6c', date: '2026-04-03' },
])

const generateResource = async () => {
  generating.value = true
  // TODO: 调用API生成资源
  setTimeout(() => {
    generating.value = false
    showGenerateDialog.value = false
    ElMessage.success('资源生成任务已启动，请稍后查看')
  }, 1000)
}
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
</style>
