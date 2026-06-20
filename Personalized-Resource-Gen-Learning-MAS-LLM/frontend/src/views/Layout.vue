<template>
  <el-container class="layout-container">
    <el-aside width="230px" class="sidebar">
      <!-- Logo -->
      <div class="logo">
        <svg class="logo-ship" viewBox="0 0 48 48" width="32" height="32">
          <path d="M24 8 L36 34 L24 30 L12 34 Z" fill="var(--sidebar-active)" opacity="0.9"/>
          <rect x="22" y="34" width="4" height="6" fill="var(--sidebar-text)"/>
          <circle cx="24" cy="6" r="2.5" fill="var(--lighthouse-gold)"/>
        </svg>
        <span>远航智学</span>
      </div>

      <!-- Menu -->
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
        background-color="transparent"
        text-color="rgba(190,210,235,0.8)"
        active-text-color="#fff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>学习概览</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能对话</span>
        </el-menu-item>
        <el-menu-item index="/resources">
          <el-icon><Document /></el-icon>
          <span>学习资源</span>
        </el-menu-item>
        <el-menu-item index="/path">
          <el-icon><MapLocation /></el-icon>
          <span>学习路径</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>学习画像</span>
        </el-menu-item>
      </el-menu>

      <!-- Wave decoration -->
      <div class="sidebar-wave">
        <svg viewBox="0 0 200 30" preserveAspectRatio="none">
          <path d="M0,15 C30,5 70,25 100,15 C130,5 170,25 200,15 L200,30 L0,30 Z"
                fill="rgba(96,165,250,0.06)" />
          <path d="M0,20 C40,10 80,30 120,20 C160,10 180,25 200,20 L200,30 L0,30 Z"
                fill="rgba(96,165,250,0.04)" class="wave-anim" />
        </svg>
      </div>
    </el-aside>

    <el-container>
      <!-- Header -->
      <el-header class="header">
        <div class="header-title">{{ $route.meta.title }}</div>
        <div class="header-actions">
          <el-button type="primary" :icon="Plus" @click="startNewChat" class="glass-btn">
            新建对话
          </el-button>
          <el-dropdown @command="handleUserCommand">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span>{{ displayName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Main Content -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, UserFilled, ArrowDown } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const displayName = computed(() => {
  return userStore.userInfo?.full_name || userStore.userInfo?.username || '学生用户'
})

const startNewChat = () => {
  router.push('/chat')
}

const loadCurrentUser = async () => {
  if (!userStore.token || userStore.userInfo) return
  const userInfo = await getCurrentUser()
  userStore.setUserInfo(userInfo)
}

const handleUserCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
    return
  }
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  loadCurrentUser()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  position: relative;
  z-index: 1;
}

/* ====== Sidebar ====== */
.sidebar {
  position: relative;
  background: linear-gradient(180deg,
    rgba(15,22,40,0.94) 0%,
    rgba(18,28,48,0.92) 60%,
    rgba(12,20,38,0.95) 100%);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-right: 1px solid rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(96,165,250,0.06), transparent);
}

.logo-ship {
  filter: drop-shadow(0 0 8px rgba(96,165,250,0.4));
}

/* Menu */
.menu {
  flex: 1;
  border-right: none;
  padding-top: 8px;
}

.menu :deep(.el-menu-item) {
  margin: 2px 8px;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-size: 14px;
  color: var(--sidebar-text) !important;
}

.menu :deep(.el-menu-item:hover) {
  background: rgba(255,255,255,0.06) !important;
}

.menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(96,165,250,0.25), rgba(147,197,253,0.1)) !important;
  border-radius: 10px;
  box-shadow: inset 0 0 0 1px rgba(96,165,250,0.25);
}

/* Sidebar wave */
.sidebar-wave {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  pointer-events: none;
}

.sidebar-wave svg {
  width: 100%;
  height: 100%;
}

.wave-anim {
  animation: wave-float 4s ease-in-out infinite;
}

@keyframes wave-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* ====== Header ====== */
.header {
  background: rgba(20,28,45,0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 1px 12px rgba(0,0,0,0.2);
  position: relative;
  z-index: 1;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.glass-btn {
  background: rgba(96,165,250,0.12) !important;
  border: 1px solid rgba(96,165,250,0.25) !important;
  color: var(--primary-light) !important;
  box-shadow: none !important;
  transition: all 0.3s;
}

.glass-btn:hover {
  background: var(--primary) !important;
  color: #fff !important;
  border-color: var(--primary) !important;
  box-shadow: 0 0 16px rgba(96,165,250,0.2) !important;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px 4px 4px;
  border-radius: 20px;
  transition: background 0.2s;
  color: var(--text-secondary);
}

.user-info:hover {
  background: rgba(255,255,255,0.05);
  color: var(--text-primary);
}

/* ====== Main Content ====== */
.main-content {
  background: transparent;
  padding: 20px;
  overflow-y: auto;
}
</style>
