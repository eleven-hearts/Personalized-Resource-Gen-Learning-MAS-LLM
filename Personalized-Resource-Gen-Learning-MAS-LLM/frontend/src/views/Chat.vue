<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesRef">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']"
      >
        <el-avatar
          :size="36"
          :icon="msg.role === 'user' ? UserFilled : ChatLineRound"
          :style="{ background: msg.role === 'user' ? '#409eff' : '#67c23a' }"
        />
        <div class="message-content">
          <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
      <div v-if="loading" class="message ai-message">
        <el-avatar :size="36" :icon="ChatLineRound" style="background: #67c23a" />
        <div class="message-content">
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
      />
      <el-button type="primary" :icon="Promotion" :loading="loading" @click="sendMessage">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { UserFilled, ChatLineRound, Promotion } from '@element-plus/icons-vue'
import { marked } from 'marked'

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

  // TODO: 调用后端API进行对话
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      content: '我已收到你的需求，正在为你分析学习画像并生成个性化资源...',
      time: new Date().toLocaleTimeString(),
    })
    loading.value = false
    scrollToBottom()
  }, 1500)
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
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
  border-radius: 12px;
  background: #f5f7fa;
}

.user-message .message-content {
  background: #e6f7ff;
}

.message-text {
  line-height: 1.6;
}

.message-text :deep(p) {
  margin: 0 0 8px;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
}

.chat-input .el-textarea {
  flex: 1;
}

.chat-input .el-button {
  align-self: flex-end;
}
</style>
