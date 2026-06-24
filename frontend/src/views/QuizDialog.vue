<template>
  <el-dialog
    v-model="visible"
    :title="`${nodeTitle} - 阶段测验`"
    width="750px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <!-- 加载中 -->
    <div v-if="loading" class="quiz-loading">
      <el-icon class="is-loading" size="40"><Loading /></el-icon>
      <p>{{ loadingText }}</p>
    </div>

    <!-- 答题中 -->
    <div v-else-if="!submitted" class="quiz-body">
      <div class="quiz-progress-bar">
        <span>共 {{ questions.length }} 题，已答 {{ answeredCount }} 题</span>
        <el-progress :percentage="Math.round((answeredCount / questions.length) * 100)" />
      </div>

      <div
        v-for="(q, index) in questions"
        :key="q.id"
        class="quiz-question"
      >
        <div class="question-header">
          <span class="question-number">第 {{ index + 1 }} 题</span>
        </div>
        <div class="question-text">{{ q.question }}</div>
        <el-radio-group
          v-model="userAnswers[q.id]"
          class="question-options"
          @change="onAnswerChange"
        >
          <el-radio
            v-for="(opt, optIdx) in q.options"
            :key="optIdx"
            :value="extractOptionKey(opt)"
            class="option-item"
          >
            {{ opt }}
          </el-radio>
        </el-radio-group>
      </div>

      <div class="quiz-actions">
        <el-button @click="visible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="answeredCount < questions.length"
          :loading="submitting"
          @click="submitAnswers"
        >
          提交答案（{{ answeredCount }}/{{ questions.length }}）
        </el-button>
      </div>
    </div>

    <!-- 结果展示 -->
    <div v-else class="quiz-result">
      <div class="result-header" :class="passed ? 'result-passed' : 'result-failed'">
        <el-icon size="48">
          <CircleCheckFilled v-if="passed" />
          <CircleCloseFilled v-else />
        </el-icon>
        <div class="result-score">
          <span class="score-number">{{ correctCount }}/{{ questions.length }}</span>
          <span class="score-label" v-if="passed">恭喜通过！节点已解锁 ~</span>
          <span class="score-label" v-else>答对 10 题以上即可解锁下一个节点</span>
        </div>
      </div>

      <div class="result-details">
        <div
          v-for="(r, index) in results"
          :key="r.question_id"
          class="result-item"
          :class="r.is_correct ? 'correct' : 'wrong'"
        >
          <div class="result-question">
            <el-tag :type="r.is_correct ? 'success' : 'danger'" size="small">
              {{ r.is_correct ? '正确' : '错误' }}
            </el-tag>
            <span>第 {{ index + 1 }} 题：{{ r.question }}</span>
          </div>
          <div class="result-answers">
            <span>你的答案：{{ r.user_answer || '未作答' }}</span>
            <span v-if="!r.is_correct">正确答案：{{ r.correct_answer }}</span>
          </div>
          <div v-if="r.explanation" class="result-explanation">
            解析：{{ r.explanation }}
          </div>
        </div>
      </div>

      <div class="result-actions">
        <el-button @click="visible = false">{{ passed ? '完成' : '关闭' }}</el-button>
        <el-button v-if="!passed" type="primary" @click="retryQuiz">重新答题</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { generateQuestions, getQuestions, submitQuiz } from '@/api/learning'

const props = defineProps({
  modelValue: Boolean,
  nodeId: Number,
  nodeTitle: String,
})

const emit = defineEmits(['update:modelValue', 'passed', 'quizSubmitted'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const loading = ref(false)
const loadingText = ref('正在生成题目...')
const submitting = ref(false)
const submitted = ref(false)
const questions = ref([])
const userAnswers = ref({})
const results = ref([])
const correctCount = ref(0)
const passed = ref(false)

const answeredCount = computed(() => Object.keys(userAnswers.value).length)

const extractOptionKey = (opt) => {
  const match = String(opt).match(/^([A-Da-d])/)
  return match ? match[1].toUpperCase() : opt[0]?.toUpperCase() || ''
}

const onAnswerChange = () => {
  // 自动滚动或无需额外处理
}

const loadQuestions = async () => {
  loading.value = true
  loadingText.value = '正在加载题目...'
  try {
    // 先尝试获取已有题目
    const data = await getQuestions(props.nodeId)
    if (data.questions && data.questions.length > 0) {
      questions.value = data.questions
    } else {
      // 没有题目则生成
      loadingText.value = 'AI正在生成题目，请耐心等待...'
      const genData = await generateQuestions(props.nodeId)
      questions.value = genData.questions || []
    }
  } catch (e) {
    ElMessage.error('加载题目失败')
    visible.value = false
  } finally {
    loading.value = false
  }
}

const submitAnswers = async () => {
  if (answeredCount.value < questions.value.length) {
    ElMessage.warning('请完成所有题目后再提交')
    return
  }
  submitting.value = true
  try {
    const data = await submitQuiz(props.nodeId, userAnswers.value)
    correctCount.value = data.correct_count
    passed.value = data.passed
    results.value = data.results || []
    submitted.value = true
    if (passed.value) {
      emit('passed', props.nodeId)
    }
    emit('quizSubmitted', {
      nodeId: props.nodeId,
      progress: data.progress,
      correctCount: data.correct_count,
      total: data.total,
      passed: data.passed,
    })
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const retryQuiz = () => {
  submitted.value = false
  userAnswers.value = {}
  results.value = []
  correctCount.value = 0
  passed.value = false
  loadQuestions()
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      submitted.value = false
      userAnswers.value = {}
      results.value = []
      correctCount.value = 0
      passed.value = false
      questions.value = []
      loadQuestions()
    }
  }
)
</script>

<style scoped>
.quiz-loading {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}
.quiz-loading p {
  margin-top: 16px;
  font-size: 15px;
}
.quiz-progress-bar {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #606266;
}
.quiz-progress-bar .el-progress {
  flex: 1;
}
.quiz-question {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}
.question-header {
  margin-bottom: 8px;
}
.question-number {
  font-weight: 600;
  color: #409eff;
  font-size: 14px;
}
.question-text {
  font-size: 15px;
  color: #303133;
  margin-bottom: 12px;
  line-height: 1.6;
}
.question-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.option-item {
  margin-right: 0 !important;
  padding: 8px 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: border-color 0.2s;
}
.option-item:hover {
  border-color: #409eff;
}
.quiz-actions {
  text-align: right;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
.quiz-result {
  padding: 8px 0;
}
.result-header {
  text-align: center;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 20px;
}
.result-passed {
  background: #f0f9eb;
  color: #67c23a;
}
.result-failed {
  background: #fef0f0;
  color: #f56c6c;
}
.result-score {
  margin-top: 8px;
}
.score-number {
  font-size: 36px;
  font-weight: bold;
  display: block;
}
.score-label {
  font-size: 14px;
  margin-top: 4px;
  display: block;
}
.result-details {
  max-height: 400px;
  overflow-y: auto;
}
.result-item {
  margin-bottom: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}
.result-item.correct {
  border-left: 4px solid #67c23a;
}
.result-item.wrong {
  border-left: 4px solid #f56c6c;
}
.result-question {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 1.5;
}
.result-answers {
  font-size: 13px;
  color: #606266;
  display: flex;
  gap: 20px;
  margin-left: 64px;
}
.result-explanation {
  font-size: 13px;
  color: #909399;
  margin-left: 64px;
  margin-top: 4px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}
.result-actions {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
