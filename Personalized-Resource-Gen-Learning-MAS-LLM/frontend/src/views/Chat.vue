<template>
  <div class="chat-container glass-card" ref="chatCardRef">
    <div class="chat-messages" ref="messagesRef">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']"
      >
        <el-avatar
          :size="36"
          :icon="msg.role === 'user' ? UserFilled : ChatLineRound"
          :style="{ background: msg.role === 'user' ? 'var(--primary)' : '#22c55e' }"
        />
        <div class="message-content" :class="msg.role === 'user' ? 'user-bubble' : 'ai-bubble'">
          <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
      <div v-if="loading" class="message ai-message">
        <el-avatar :size="36" :icon="ChatLineRound" style="background: #22c55e" />
        <div class="message-content ai-bubble">
          <el-skeleton :rows="2" animated />
        </div>
      </div>
    </div>
    <div class="chat-input">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="请输入你的学习需求或问题，系统将自动构建你的学习画像..."
        @keydown.enter.prevent="sendMessage"
        class="glass-textarea"
      />
      <el-button type="primary" :icon="Promotion" :loading="loading" @click="sendMessage" class="send-btn">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { UserFilled, ChatLineRound, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { sendChatMessage } from '@/api/chat'
import { useUserStore } from '@/stores/user'
import { useLiquidGlass } from '@/composables/useLiquidGlass'

const userStore = useUserStore()
const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是你的智能学习助手。请告诉我你的专业、学习目标，以及你感兴趣的课程内容，我会为你生成个性化的学习资源和路径规划。',
    time: new Date().toLocaleTimeString(),
  },
])
const inputMessage = ref('')
const loading = ref(false)
const messagesRef = ref()

/* Canvas 液态玻璃高光 */
const chatCardRef = ref(null)
useLiquidGlass(chatCardRef, { size: 350, alpha: 0.12, edgeGlow: true })

const renderMarkdown = (text) => {
  return marked.parse(text)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMsg = inputMessage.value
  messages.value.push({
    role: 'user',
    content: userMsg,
    time: new Date().toLocaleTimeString(),
  })
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const result = await sendChatMessage({ content: userMsg })
    if (result.profile_update && userStore.userInfo) {
      userStore.setUserInfo({
        ...userStore.userInfo,
        profile: result.profile_update,
      })
    }
    messages.value.push({
      role: 'assistant',
      content: result.response,
      time: new Date().toLocaleTimeString(),
    })
  } catch (error) {
    ElMessage.error('消息发送失败，请稍后重试')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  padding: 0 !important;
  overflow: hidden;
}

.glass-card {
  background: rgba(25,34,52,0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--card-radius);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  position: relative;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 14px;
}

.user-bubble {
  background: rgba(96,165,250,0.18);
  border: 1px solid rgba(96,165,250,0.25);
  border-radius: 14px 4px 14px 14px;
}

.ai-bubble {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 4px 14px 14px 14px;
}

.message-text {
  line-height: 1.6;
  font-size: 14px;
  color: var(--text-primary);
}

.message-text :deep(p) {
  margin: 0 0 8px;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
  text-align: right;
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(0,0,0,0.15);
}

.chat-input :deep(.el-textarea__inner) {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  resize: none;
  font-size: 14px;
  color: var(--text-primary);
}

.chat-input :deep(.el-textarea__inner:focus) {
  border-color: var(--primary);
  background: rgba(255,255,255,0.08);
}

.chat-input :deep(.el-textarea__inner::placeholder) {
  color: var(--text-secondary);
}

.send-btn {
  align-self: flex-end;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
  border: none !important;
}
</style>
