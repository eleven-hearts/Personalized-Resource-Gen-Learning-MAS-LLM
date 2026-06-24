<template>
  <LiquidGlassBg />
  <router-view />
</template>

<script setup>
import LiquidGlassBg from '@/components/LiquidGlassBg.vue'
</script>

<style>
:root {
  --glass-bg: rgba(30,37,55,0.55);
  --glass-border: rgba(255,255,255,0.12);
  --glass-shadow: 0 8px 32px rgba(0,0,0,0.25);
  --glass-blur: 20px;
  --sidebar-bg: rgba(15,22,40,0.88);
  --sidebar-text: rgba(190,210,235,0.85);
  --sidebar-active: #60a5fa;
  --primary: #60a5fa;
  --primary-light: #93c5fd;
  --primary-bg: rgba(96,165,250,0.12);
  --ocean-deep: #0f1628;
  --lighthouse-gold: #f5a623;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --page-bg-start: #121828;
  --page-bg-end: #1a2235;
  --card-radius: 16px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #121828;
  min-height: 100vh;
  color: var(--text-primary);
}
</style>
