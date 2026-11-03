<template>
  <div class="app-shell">
    <AppSidebar :items="navItems" :open="drawerOpen" :is-drawer="isDrawer" />
    <div v-if="drawerOpen" class="sidebar-backdrop" @click="drawerOpen = false"></div>

    <div class="app-main">
      <header class="topbar">
        <div class="topbar-row">
          <button
            type="button"
            class="drawer-toggle"
            aria-controls="app-sidebar"
            :aria-expanded="drawerOpen ? 'true' : 'false'"
            :aria-label="t('nav.openNavigation')"
            @click="drawerOpen = !drawerOpen"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" /></svg>
          </button>
          <div class="topbar-title">{{ currentTitle }}</div>
          <div class="topbar-actions">
            <LanguageSwitcher />
            <ProfileMenu
              @show-profile-details="showProfileDetails = true"
              @show-tasks="showTasks = true"
            />
          </div>
        </div>
        <FilterBar />
      </header>

      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AppSidebar from './components/AppSidebar.vue'

const navItems = [
  { to: '/', label: 'nav.overview', icon: 'overview' },
  { to: '/inventory', label: 'nav.inventory', icon: 'inventory' },
  { to: '/orders', label: 'nav.orders', icon: 'orders' },
  { to: '/spending', label: 'nav.finance', icon: 'finance' },
  { to: '/demand', label: 'nav.demandForecast', icon: 'demand' },
  { to: '/restocking', label: 'nav.restocking', icon: 'restocking' },
  { to: '/reports', label: 'nav.reports', icon: 'reports' }
]

// Matches the sidebar's drawer breakpoint in AppSidebar.vue
const DRAWER_QUERY = '(max-width: 960px)'

export default {
  name: 'App',
  components: {
    AppSidebar,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    // App shell: page title in the top bar and the off-canvas drawer on narrow screens
    const route = useRoute()
    const drawerOpen = ref(false)
    const isDrawer = ref(false)

    const currentTitle = computed(() => {
      const item = navItems.find(i => (i.to === '/' ? route.path === '/' : route.path.startsWith(i.to)))
      return item ? t(item.label) : ''
    })

    watch(() => route.path, () => { drawerOpen.value = false })

    const onKeydown = (e) => {
      if (e.key === 'Escape') drawerOpen.value = false
    }

    let mediaQuery = null
    const syncDrawer = () => {
      isDrawer.value = mediaQuery.matches
      if (!mediaQuery.matches) drawerOpen.value = false
    }

    onMounted(() => {
      window.addEventListener('keydown', onKeydown)
      mediaQuery = window.matchMedia(DRAWER_QUERY)
      syncDrawer()
      mediaQuery.addEventListener('change', syncDrawer)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('keydown', onKeydown)
      mediaQuery?.removeEventListener('change', syncDrawer)
    })

    return {
      t,
      navItems,
      currentTitle,
      drawerOpen,
      isDrawer,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/* Design tokens: Accenture palette (purple spectrum + brand neutrals) */
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-7: 32px;
  --space-8: 48px;

  --font-sans: "Graphik", Arial, Helvetica, sans-serif;
  --text-xs: 0.75rem;
  --text-sm: 0.8125rem;
  --text-base: 0.875rem;
  --text-md: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.625rem;
  --text-2xl: 2rem;
  --weight-regular: 400;
  --weight-medium: 500;
  --weight-semibold: 600;

  --color-accent: #a100ff;
  --color-accent-strong: #7500c0;
  --color-accent-deep: #460073;
  --color-accent-light: #c2a3ff;
  --color-accent-soft: #e6dcff;
  --color-accent-wash: #f6f1ff;

  --color-bg: #f7f7f5;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f1ef;
  --color-border: #e4e4e1;
  --color-border-strong: #cfcfcf;
  --color-text: #0a0011;
  --color-text-body: #33303a;
  --color-text-muted: #68646f;
  --color-text-subtle: #8f8b96;

  --color-shell: #0a0011;
  --color-shell-text: #c9c4d1;
  --color-shell-strong: #ffffff;
  --color-shell-muted: #8a8494;
  --color-shell-hover: rgba(255, 255, 255, 0.06);
  --color-shell-active: rgba(161, 0, 255, 0.2);

  --color-success: #0b7a4b;
  --color-success-soft: #e3f4ec;
  --color-warning: #a64b00;
  --color-warning-soft: #fdf0e1;
  --color-danger: #c4122f;
  --color-danger-soft: #fde8eb;
  --color-info: #224bff;
  --color-info-soft: #e7ecff;

  --radius-sm: 4px;
  --radius-md: 6px;
  --shadow-sm: 0 1px 2px rgba(10, 0, 17, 0.05);
  --shadow-md: 0 6px 20px rgba(10, 0, 17, 0.08);
  --focus-ring: 0 0 0 3px rgba(161, 0, 255, 0.28);

  --sidebar-width: 248px;
  --topbar-height: 60px;
  --content-max: 1520px;

  --transition: 160ms cubic-bezier(0.2, 0, 0, 1);
  --transition-slow: 240ms cubic-bezier(0.2, 0, 0, 1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.5;
  background: var(--color-bg);
  color: var(--color-text-body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

::selection {
  background: var(--color-accent-soft);
  color: var(--color-text);
}

:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

input[type="checkbox"],
input[type="radio"],
input[type="range"] {
  accent-color: var(--color-accent);
}

/* App shell */
.app-main {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.topbar-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  height: var(--topbar-height);
  padding: 0 var(--space-7);
  border-bottom: 1px solid var(--color-border);
}

/* The page header already names the page on wide screens; the bar repeats it only beside the drawer toggle */
.topbar-title {
  display: none;
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}

.topbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.drawer-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  margin-left: calc(-1 * var(--space-2));
  background: none;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--color-text);
  cursor: pointer;
}

.drawer-toggle:hover {
  background: var(--color-surface-muted);
}

.drawer-toggle svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.75;
  stroke-linecap: round;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  z-index: 150;
  background: rgba(10, 0, 17, 0.45);
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  padding: var(--space-7);
}

@media (max-width: 960px) {
  .app-main {
    margin-left: 0;
  }

  .drawer-toggle {
    display: inline-flex;
  }

  .topbar-title {
    display: block;
  }

  .topbar-row,
  .main-content {
    padding-left: var(--space-5);
    padding-right: var(--space-5);
  }
}

@media (max-width: 600px) {
  .main-content {
    padding: var(--space-5) var(--space-4);
  }

  .topbar-row {
    padding: 0 var(--space-4);
    gap: var(--space-2);
  }

  /* On phones the four filters would pin half the screen; let the header scroll away */
  .topbar {
    position: static;
  }

  .topbar-title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .topbar-actions {
    gap: var(--space-2);
  }

  /* Icon-only utilities: the language code and avatar stay, the long labels go */
  .topbar .profile-name,
  .topbar .language-label {
    display: none;
  }
}

/* Page header */
.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1.2;
  margin-bottom: var(--space-1);
}

.page-header p {
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

/* KPI cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  position: relative;
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: border-color var(--transition), box-shadow var(--transition);
}

.stat-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-sm);
}

.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1.15;
  font-variant-numeric: tabular-nums;
}

/* Status shows as a small square before the label plus the value color, so tinted cards still read as one family */
.stat-card.warning .stat-label::before,
.stat-card.success .stat-label::before,
.stat-card.danger .stat-label::before,
.stat-card.info .stat-label::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: var(--space-2);
  background: var(--stat-tone);
  vertical-align: 1px;
}

.stat-card.warning { --stat-tone: var(--color-warning); }
.stat-card.success { --stat-tone: var(--color-success); }
.stat-card.danger { --stat-tone: var(--color-danger); }
.stat-card.info { --stat-tone: var(--color-accent); }

.stat-card.warning .stat-value { color: var(--color-warning); }
.stat-card.success .stat-value { color: var(--color-success); }
.stat-card.danger .stat-value { color: var(--color-danger); }
.stat-card.info .stat-value { color: var(--color-accent-strong); }

/* Cards */
.card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-6);
  border: 1px solid var(--color-border);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  letter-spacing: -0.01em;
}

/* Tables */
.table-container {
  overflow-x: auto;
  margin: 0 calc(-1 * var(--space-6));
  padding: 0 var(--space-6);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

thead {
  background: var(--color-surface-muted);
}

th {
  text-align: left;
  padding: var(--space-3);
  font-weight: var(--weight-semibold);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

td {
  padding: var(--space-3);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-body);
  font-size: var(--text-base);
}

tbody tr {
  transition: background-color var(--transition);
}

tbody tr:hover {
  background: var(--color-accent-wash);
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.badge.success,
.badge.increasing,
.badge.low {
  background: var(--color-success-soft);
  color: var(--color-success);
}

.badge.warning,
.badge.medium {
  background: var(--color-warning-soft);
  color: var(--color-warning);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}

.badge.info {
  background: var(--color-info-soft);
  color: var(--color-info);
}

.badge.stable {
  background: var(--color-accent-soft);
  color: var(--color-accent-deep);
}

/* States */
.loading {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.error {
  background: var(--color-danger-soft);
  border: 1px solid #f5c2cb;
  color: var(--color-danger);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-sm);
  margin: var(--space-4) 0;
  font-size: var(--text-base);
}
</style>
