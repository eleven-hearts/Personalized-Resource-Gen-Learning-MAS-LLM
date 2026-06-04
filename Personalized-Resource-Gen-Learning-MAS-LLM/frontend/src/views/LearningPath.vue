<template>
  <div class="learning-path">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的学习路径</span>
          <el-button type="primary" :icon="Refresh" @click="regeneratePath">
            重新规划
          </el-button>
        </div>
      </template>

      <el-timeline>
        <el-timeline-item
          v-for="(stage, index) in pathStages"
          :key="index"
          :type="stage.status"
          :color="stage.color"
          :icon="stage.icon"
          :timestamp="stage.duration"
        >
          <el-card class="stage-card">
            <h4>{{ stage.title }}</h4>
            <p>{{ stage.description }}</p>
            <div class="stage-resources">
              <el-tag
                v-for="res in stage.resources"
                :key="res"
                size="small"
                class="resource-tag"
              >
                {{ res }}
              </el-tag>
            </div>
            <div class="stage-progress">
              <span>完成度</span>
              <el-progress :percentage="stage.progress" :status="stage.progress === 100 ? 'success' : ''" />
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Refresh, Check, Loading, CircleCheck } from '@element-plus/icons-vue'

const pathStages = ref([
  {
    title: '阶段一：机器学习基础',
    description: '掌握机器学习基本概念、监督学习与无监督学习的区别、模型评估方法',
    duration: '第1-2周',
    status: 'success',
    color: '#67c23a',
    icon: Check,
    resources: ['讲解文档', '思维导图', '基础练习题'],
    progress: 100,
  },
  {
    title: '阶段二：线性模型',
    description: '深入理解线性回归、逻辑回归、正则化方法',
    duration: '第3-4周',
    status: 'primary',
    color: '#409eff',
    icon: Loading,
    resources: ['代码案例', '进阶练习题', '论文阅读'],
    progress: 60,
  },
  {
    title: '阶段三：神经网络基础',
    description: '学习感知机、多层神经网络、反向传播算法',
    duration: '第5-6周',
    status: 'info',
    color: '#909399',
    icon: CircleCheck,
    resources: ['视频讲解', 'PyTorch实战', '项目作业'],
    progress: 0,
  },
  {
    title: '阶段四：深度学习进阶',
    description: '卷积神经网络、循环神经网络、注意力机制',
    duration: '第7-10周',
    status: 'info',
    color: '#909399',
    icon: CircleCheck,
    resources: ['高级案例', '论文精读', '综合项目'],
    progress: 0,
  },
])

const regeneratePath = () => {
  // TODO: 调用API重新规划路径
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stage-card {
  margin-bottom: 10px;
}

.stage-card h4 {
  margin-bottom: 8px;
}

.stage-resources {
  margin: 12px 0;
}

.resource-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

.stage-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.stage-progress span {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.stage-progress .el-progress {
  flex: 1;
}
</style>
