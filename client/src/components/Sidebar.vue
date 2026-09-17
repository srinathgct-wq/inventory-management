<template>
  <aside class="sidebar" :class="{ collapsed }">
    <button
      v-if="!isSmallScreen"
      type="button"
      class="collapse-toggle"
      :class="{ 'collapse-toggle-collapsed': collapsed }"
      :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      @click="toggleCollapsed"
    >
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M9 2.5L4.5 7L9 11.5" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <div class="brand">
      <template v-if="!collapsed">
        <h1>{{ t('nav.companyName') }}</h1>
        <span class="subtitle">{{ t('nav.subtitle') }}</span>
      </template>
      <div v-else class="brand-monogram" :title="t('nav.companyName')">
        {{ companyInitial }}
      </div>
    </div>

    <nav class="side-nav">
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }" :title="t('nav.overview')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="nav-icon">
          <rect x="2.5" y="2.5" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/>
          <rect x="9.5" y="2.5" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/>
          <rect x="2.5" y="9.5" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/>
          <rect x="9.5" y="9.5" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        <span v-if="!collapsed">{{ t('nav.overview') }}</span>
      </router-link>

      <router-link to="/inventory" class="nav-item" :class="{ active: $route.path === '/inventory' }" :title="t('nav.inventory')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="nav-icon">
          <path d="M2.5 5.5L9 2.5L15.5 5.5V12.5L9 15.5L2.5 12.5V5.5Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M2.5 5.5L9 8.5M9 8.5L15.5 5.5M9 8.5V15.5" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
        </svg>
        <span v-if="!collapsed">{{ t('nav.inventory') }}</span>
      </router-link>

      <router-link to="/orders" class="nav-item" :class="{ active: $route.path === '/orders' }" :title="t('nav.orders')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="nav-icon">
          <path d="M5 2.5H13C13.5523 2.5 14 2.94772 14 3.5V15.5L9 13.5L4 15.5V3.5C4 2.94772 4.44772 2.5 5 2.5Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M6.5 7H11.5M6.5 9.5H11.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span v-if="!collapsed">{{ t('nav.orders') }}</span>
      </router-link>

      <router-link to="/spending" class="nav-item" :class="{ active: $route.path === '/spending' }" :title="t('nav.finance')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="nav-icon">
          <circle cx="9" cy="9" r="6.5" stroke="currentColor" stroke-width="1.5"/>
          <path d="M9 5.5V12.5M11 7C11 6.17157 10.1046 5.5 9 5.5C7.89543 5.5 7 6.17157 7 7C7 7.82843 7.89543 8.5 9 8.5C10.1046 8.5 11 9.17157 11 10C11 10.8284 10.1046 11.5 9 11.5C7.89543 11.5 7 10.8284 7 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span v-if="!collapsed">{{ t('nav.finance') }}</span>
      </router-link>

      <router-link to="/demand" class="nav-item" :class="{ active: $route.path === '/demand' }" :title="t('nav.demandForecast')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="nav-icon">
          <path d="M2.5 14.5H15.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M3 12L7 8L10 10.5L15 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M11.5 5H15V8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span v-if="!collapsed">{{ t('nav.demandForecast') }}</span>
      </router-link>

      <router-link to="/restocking" class="nav-item" :class="{ active: $route.path === '/restocking' }" :title="t('nav.restocking')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="nav-icon">
          <path d="M15 9C15 12.3137 12.3137 15 9 15C6.5 15 4.35 13.5 3.4 11.3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M3 9C3 5.68629 5.68629 3 9 3C11.5 3 13.65 4.5 14.6 6.7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M15 6V9.5H11.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M3 12V8.5H6.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span v-if="!collapsed">{{ t('nav.restocking') }}</span>
      </router-link>

      <router-link to="/reports" class="nav-item" :class="{ active: $route.path === '/reports' }" title="Reports">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="nav-icon">
          <path d="M5 2.5H11L14 5.5V14.5C14 15.0523 13.5523 15.5 13 15.5H5C4.44772 15.5 4 15.0523 4 14.5V3.5C4 2.94772 4.44772 2.5 5 2.5Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M11 2.5V5.5H14" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M6.5 9H11.5M6.5 11.5H11.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span v-if="!collapsed">Reports</span>
      </router-link>
    </nav>

    <div class="sidebar-spacer"></div>

    <div class="sidebar-footer">
      <LanguageSwitcher :compact="collapsed" />
      <ProfileMenu
        :compact="collapsed"
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import ProfileMenu from './ProfileMenu.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'

defineEmits(['show-profile-details', 'show-tasks'])

const { t } = useI18n()

const companyInitial = computed(() => {
  const name = t('nav.companyName') || ''
  return name.charAt(0).toUpperCase()
})

const readStoredCollapsed = () => {
  try {
    return localStorage.getItem('sidebar-collapsed') === 'true'
  } catch (err) {
    return false
  }
}

const manualCollapsed = ref(readStoredCollapsed())
const isSmallScreen = ref(typeof window !== 'undefined' ? window.innerWidth <= 1024 : false)

const collapsed = computed(() => manualCollapsed.value || isSmallScreen.value)

const toggleCollapsed = () => {
  manualCollapsed.value = !collapsed.value
  try {
    localStorage.setItem('sidebar-collapsed', String(manualCollapsed.value))
  } catch (err) {
    // ignore storage failures
  }
}

const handleResize = () => {
  isSmallScreen.value = window.innerWidth <= 1024
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.sidebar {
  width: 256px;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.2s ease;
}

.sidebar.collapsed {
  width: 72px;
}

.collapse-toggle {
  position: absolute;
  right: -12px;
  top: 24px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.12);
  z-index: 10;
  padding: 0;
  transition: transform 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.collapse-toggle:hover {
  color: #2563eb;
  border-color: #cbd5e1;
}

.collapse-toggle svg {
  transition: transform 0.2s ease;
}

.collapse-toggle-collapsed svg {
  transform: rotate(180deg);
}

.brand {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 24px 16px;
  min-height: 32px;
}

.sidebar.collapsed .brand {
  align-items: center;
  padding: 24px 8px;
}

.brand h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.subtitle {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 400;
}

.brand-monogram {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #2563eb;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.938rem;
}

.side-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  border-radius: 8px;
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 10px 8px;
}

.nav-icon {
  flex-shrink: 0;
}

.nav-item:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.nav-item.active {
  color: #2563eb;
  background: #eff6ff;
  border-left-color: #2563eb;
}

.sidebar-spacer {
  flex: 1;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 12px 24px;
  border-top: 1px solid #e2e8f0;
}

.sidebar.collapsed .sidebar-footer {
  padding: 16px 8px 24px;
}

.sidebar-footer :deep(.language-switcher),
.sidebar-footer :deep(.profile-menu) {
  width: 100%;
}

.sidebar-footer :deep(.language-button),
.sidebar-footer :deep(.profile-button) {
  width: 100%;
}
</style>
