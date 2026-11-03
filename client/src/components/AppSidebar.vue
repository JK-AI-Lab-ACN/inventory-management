<template>
  <aside id="app-sidebar" class="sidebar" :class="{ open }" :aria-hidden="isDrawer && !open ? 'true' : null">
    <router-link to="/" class="sidebar-brand">
      <svg class="brand-mark" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M5 3l14 9-14 9v-4.6L12.2 12 5 7.6z" />
      </svg>
      <span class="brand-text">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-sub">{{ t('nav.subtitle') }}</span>
      </span>
    </router-link>

    <nav class="sidebar-nav" :aria-label="t('nav.mainNavigation')">
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="sidebar-link"
        :class="{ active: isActive(item.to) }"
        :aria-current="isActive(item.to) ? 'page' : null"
      >
        <svg class="sidebar-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path v-for="(d, i) in icons[item.icon]" :key="i" :d="d" />
        </svg>
        <span class="sidebar-label">{{ t(item.label) }}</span>
        <svg class="active-chevron" viewBox="0 0 12 12" aria-hidden="true">
          <path d="M3 1.5l6 4.5-6 4.5" />
        </svg>
      </router-link>
    </nav>
  </aside>
</template>

<script>
import { useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'

// Stroke icons on a 24px grid, drawn for this app (one weight, round caps)
const icons = {
  overview: ['M4 4h7v7H4z', 'M13 4h7v4h-7z', 'M13 10h7v10h-7z', 'M4 13h7v7H4z'],
  inventory: ['M3 8l9-5 9 5v8l-9 5-9-5z', 'M3 8l9 5 9-5', 'M12 13v8'],
  orders: ['M6 3h12v18l-3-2-3 2-3-2-3 2z', 'M9 8h6', 'M9 12h6'],
  finance: ['M4 20V10', 'M10 20V4', 'M16 20v-7', 'M21 20H3'],
  demand: ['M3 17l5-5 4 3 8-8', 'M15 7h5v5'],
  restocking: ['M4 12a8 8 0 0 1 13.7-5.6L20 9', 'M20 4v5h-5', 'M20 12a8 8 0 0 1-13.7 5.6L4 15', 'M4 20v-5h5'],
  reports: ['M6 3h9l4 4v14H6z', 'M14 3v5h5', 'M9 13h7', 'M9 17h5']
}

export default {
  name: 'AppSidebar',
  props: {
    items: { type: Array, required: true },
    open: { type: Boolean, default: false },
    isDrawer: { type: Boolean, default: false }
  },
  setup() {
    const route = useRoute()
    const { t } = useI18n()

    const isActive = (to) => (to === '/' ? route.path === '/' : route.path.startsWith(to))

    return { t, icons, isActive }
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 200;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--color-shell);
  color: var(--color-shell-text);
  padding: var(--space-5) var(--space-3);
  overflow-y: auto;
  transition: transform var(--transition-slow);
}

.sidebar-brand {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: 0 var(--space-3) var(--space-6);
  text-decoration: none;
  color: var(--color-shell-strong);
}

.brand-mark {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  margin-top: 1px;
  fill: var(--color-accent);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.brand-name {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  letter-spacing: -0.01em;
  line-height: 1.25;
}

.brand-sub {
  font-size: var(--text-xs);
  color: var(--color-shell-muted);
  line-height: 1.35;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 40px;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--color-shell-text);
  text-decoration: none;
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  transition: background var(--transition), color var(--transition);
}

.sidebar-link:hover {
  background: var(--color-shell-hover);
  color: var(--color-shell-strong);
}

.sidebar-link.active {
  background: var(--color-shell-active);
  color: var(--color-shell-strong);
}

.sidebar-link:focus-visible {
  outline: 2px solid var(--color-accent-light);
  outline-offset: -2px;
}

.sidebar-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.75;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.sidebar-link.active .sidebar-icon {
  stroke: var(--color-accent-light);
}

.sidebar-label {
  flex: 1;
  min-width: 0;
}

/* Signature move: the Accenture greater-than marks where you are */
.active-chevron {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  fill: none;
  stroke: var(--color-accent);
  stroke-width: 2.25;
  stroke-linecap: square;
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity var(--transition), transform var(--transition);
}

.sidebar-link.active .active-chevron {
  opacity: 1;
  transform: none;
}

@media (max-width: 960px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: none;
    box-shadow: 8px 0 24px rgba(10, 0, 17, 0.25);
  }
}

@media (prefers-reduced-motion: reduce) {
  .sidebar,
  .active-chevron {
    transition: none;
  }
}
</style>
