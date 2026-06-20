<template>
  <el-dialog
    v-model="visible"
    title="错题本"
    width="800px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div v-if="loading" class="loading-area">
      <el-icon class="is-loading" size="36"><Loading /></el-icon>
      <p>加载错题中...</p>
    </div>

    <div v-else-if="groups.length === 0">
      <el-empty description="暂无错题记录，继续加油！" />
    </div>

    <div v-else class="wrong-list">
      <div class="wrong-summary">
        共 <strong>{{ totalWrong }}</strong> 道错题，分布在 <strong>{{ groups.length }}</strong> 个节点
      </div>

      <el-collapse v-model="activeGroups" accordion>
        <el-collapse-item
          v-for="group in groups"
          :key="group.node_id"
          :name="String(group.node_id)"
        >
          <template #title>
            <div class="group-title">
              <span class="group-name">{{ group.node_title }}</span>
              <el-tag size="small" type="danger">{{ group.count }} 题</el-tag>
            </div>
          </template>

          <div
            v-for="(item, idx) in group.items"
            :key="item.id"
            class="wrong-item"
            :class="{ killing: killingIds.has(item.id) }"
          >
            <div class="wrong-question">
              <el-tag type="danger" size="small">错题 {{ idx + 1 }}</el-tag>
              <span>{{ item.question }}</span>
              <el-button
                :icon="Close"
                circle
                size="small"
                type="danger"
                :loading="killingIds.has(item.id)"
                @click="handleKill(item.id)"
                class="kill-btn"
              />
            </div>
            <div class="wrong-detail">
              <div class="wrong-row">
                <span class="wrong-label wrong-answer">你的答案：{{ item.user_answer || '未作答' }}</span>
                <span class="wrong-label wrong-correct">正确答案：{{ item.correct_answer }}</span>
              </div>
              <div class="wrong-options" v-if="item.options && item.options.length > 0">
                <span
                  v-for="(opt, oi) in item.options"
                  :key="oi"
                  class="wrong-opt"
                  :class="{
                    'opt-correct': extractKey(opt) === item.correct_answer,
                    'opt-wrong': extractKey(opt) === item.user_answer && extractKey(opt) !== item.correct_answer,
                  }"
                >
                  {{ opt }}
                </span>
              </div>
              <div v-if="item.explanation" class="wrong-explanation">
                <span class="explain-label">解析：</span>{{ item.explanation }}
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Loading, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getWrongAnswers, deleteWrongAnswer } from '@/api/dashboard'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const loading = ref(false)
const groups = ref([])
const totalWrong = ref(0)
const activeGroups = ref([])
const killingIds = ref(/** @type {Set<number>} */ (new Set()))

const extractKey = (opt) => {
  const match = String(opt).match(/^([A-Da-d])/)
  return match ? match[1].toUpperCase() : ''
}

const handleKill = async (id) => {
  killingIds.value = new Set(killingIds.value).add(id)
  try {
    await deleteWrongAnswer(id)
    // 等待消失动画播放
    await new Promise((r) => setTimeout(r, 500))
    // 移除该错题
    removeWrongItem(id)
    ElMessage.success('错题已消灭')
  } catch {
    ElMessage.error('消灭失败')
  } finally {
    const next = new Set(killingIds.value)
    next.delete(id)
    killingIds.value = next
  }
}

const removeWrongItem = (id) => {
  const newGroups = []
  let total = 0
  for (const g of groups.value) {
    const items = g.items.filter((i) => i.id !== id)
    if (items.length > 0) {
      newGroups.push({ ...g, count: items.length, items })
      total += items.length
    }
  }
  groups.value = newGroups
  totalWrong.value = total
}

const loadWrongAnswers = async () => {
  loading.value = true
  try {
    const data = await getWrongAnswers()
    groups.value = data.groups || []
    totalWrong.value = data.total_wrong || 0
  } catch (e) {
    groups.value = []
    totalWrong.value = 0
  } finally {
    loading.value = false
  }
}

watch(() => props.modelValue, (val) => {
  if (val) loadWrongAnswers()
})
</script>

<style scoped>
.loading-area { text-align: center; padding: 40px; color: #909399; }
.loading-area p { margin-top: 12px; }
.wrong-summary {
  margin-bottom: 16px; padding: 12px; background: #fef0f0;
  border-radius: 8px; color: #f56c6c; font-size: 14px;
}
.group-title { display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 500; }
.wrong-item { padding: 12px 0; border-bottom: 1px dashed #ebeef5; }
.wrong-item:last-child { border-bottom: none; }
.wrong-question { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px; font-size: 14px; line-height: 1.5; }
.wrong-question .el-tag { flex-shrink: 0; }
.wrong-detail { margin-left: 68px; }
.wrong-row { display: flex; gap: 20px; margin-bottom: 6px; }
.wrong-label { font-size: 13px; }
.wrong-answer { color: #f56c6c; }
.wrong-correct { color: #67c23a; }
.wrong-options { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }
.wrong-opt { font-size: 12px; padding: 2px 8px; border-radius: 4px; background: #f5f7fa; color: #909399; }
.opt-correct { background: #f0f9eb; color: #67c23a; font-weight: 500; }
.opt-wrong { background: #fef0f0; color: #f56c6c; text-decoration: line-through; }
.wrong-explanation { font-size: 13px; color: #606266; padding: 8px; background: #f5f7fa; border-radius: 4px; line-height: 1.6; }
.explain-label { color: #409eff; font-weight: 500; }

/* 消灭按钮 */
.kill-btn {
  flex-shrink: 0;
  margin-left: auto;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.wrong-item:hover .kill-btn {
  opacity: 1;
}

/* 消灭动画 */
.wrong-item.killing {
  animation: killAnim 0.5s ease-out forwards;
  pointer-events: none;
}

@keyframes killAnim {
  0% {
    opacity: 1;
    transform: scale(1);
    filter: brightness(1);
    background: transparent;
  }
  15% {
    filter: brightness(1.5);
    background: rgba(245, 108, 108, 0.15);
    box-shadow: 0 0 20px rgba(245, 108, 108, 0.3);
  }
  100% {
    opacity: 0;
    transform: scale(0.85) translateY(-10px);
    filter: brightness(0.5);
  }
}
</style>
