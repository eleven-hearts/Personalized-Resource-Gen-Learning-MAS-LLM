<template>
  <div class="login-container">
    <div class="login-glass-card" ref="loginCardRef">
      <!-- Header -->
      <div class="login-header">
        <svg class="login-ship" viewBox="0 0 64 64" width="56" height="56">
          <circle cx="32" cy="32" r="30" fill="none" stroke="var(--primary-light)" stroke-width="1.5" opacity="0.5"/>
          <path d="M32 14 L44 40 L32 35 L20 40 Z" fill="var(--primary)" opacity="0.85"/>
          <rect x="29" y="40" width="6" height="8" fill="var(--primary)" opacity="0.6"/>
          <circle cx="32" cy="10" r="3.5" fill="var(--lighthouse-gold)"/>
        </svg>
        <h2>远航智学</h2>
        <p>扬帆起航，智慧学习</p>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" stretch class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                :prefix-icon="User"
                size="large"
                class="glass-input"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                class="glass-input"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                :loading="loginLoading"
                @click="handleLogin"
                class="glass-submit"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef">
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                :prefix-icon="User"
                size="large"
                class="glass-input"
              />
            </el-form-item>
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱"
                :prefix-icon="Message"
                size="large"
                class="glass-input"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                class="glass-input"
              />
            </el-form-item>
            <el-form-item prop="major">
              <el-input
                v-model="registerForm.major"
                placeholder="专业"
                :prefix-icon="Reading"
                size="large"
                class="glass-input"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                :loading="registerLoading"
                @click="handleRegister"
                class="glass-submit"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Reading } from '@element-plus/icons-vue'
import { getCurrentUser, login, register } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { useLiquidGlass } from '@/composables/useLiquidGlass'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('login')
const loginFormRef = ref()
const registerFormRef = ref()
const loginLoading = ref(false)
const registerLoading = ref(false)

/* Canvas 液态玻璃高光 */
const loginCardRef = ref(null)
useLiquidGlass(loginCardRef, { size: 300, alpha: 0.18, edgeGlow: true })

const loginForm = reactive({
  username: '',
  password: '',
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  major: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  await loginFormRef.value.validate()
  loginLoading.value = true
  try {
    const result = await login(loginForm)
    userStore.setToken(result.access_token)
    const userInfo = await getCurrentUser()
    userStore.setUserInfo(userInfo)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loginLoading.value = false
  }
}

const handleRegister = async () => {
  await registerFormRef.value.validate()
  registerLoading.value = true
  try {
    await register(registerForm)
    ElMessage.success('注册成功，请登录')
    loginForm.username = registerForm.username
    loginForm.password = registerForm.password
    activeTab.value = 'login'
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
  position: relative;
  z-index: 1;
}

/* Glass card */
.login-glass-card {
  position: relative;
  width: 420px;
  background: rgba(25,32,50,0.55);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow:
    0 8px 32px rgba(0,0,0,0.3),
    0 2px 8px rgba(0,0,0,0.15),
    inset 0 1px 0 rgba(255,255,255,0.05);
  padding: 36px 36px 28px;
  overflow: hidden;
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.login-ship {
  filter: drop-shadow(0 2px 8px rgba(96,165,250,0.3));
}

.login-header h2 {
  margin: 10px 0 6px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--text-primary);
}

.login-header p {
  color: var(--text-secondary);
  font-size: 14px;
  letter-spacing: 1px;
}

.login-tabs :deep(.el-tabs__item) {
  color: var(--text-secondary);
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary-light);
}

.login-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--primary);
}

.login-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(255,255,255,0.06);
}

.glass-input :deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.06);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: none !important;
  transition: all 0.3s;
}

.glass-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(96,165,250,0.4);
  background: rgba(255,255,255,0.1);
}

.glass-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary);
  background: rgba(255,255,255,0.12);
  box-shadow: 0 0 0 1px rgba(96,165,250,0.2) !important;
}

.glass-input :deep(input) {
  color: var(--text-primary);
}

.glass-submit {
  background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
  border: none !important;
  border-radius: 12px !important;
  font-size: 16px !important;
  letter-spacing: 2px;
  transition: all 0.3s;
}

.glass-submit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(96,165,250,0.35) !important;
}
</style>
