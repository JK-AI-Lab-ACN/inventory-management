# App shell pattern

A reference implementation to adapt, not copy blindly. Match the app's component style (Options API vs `<script setup>`), i18n helper (`t('nav.x')`) and existing components (language switcher, profile menu, filter bar).

## App.vue layout

```vue
<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed, 'drawer-open': drawerOpen }">
    <AppSidebar
      id="app-sidebar"
      :items="navItems"
      :collapsed="collapsed"
      @toggle-collapse="collapsed = !collapsed"
    />
    <div v-if="drawerOpen" class="sidebar-backdrop" @click="drawerOpen = false" />

    <div class="app-main">
      <header class="topbar">
        <button
          class="icon-btn drawer-toggle"
          aria-controls="app-sidebar"
          :aria-expanded="drawerOpen"
          aria-label="Open navigation"
          @click="drawerOpen = !drawerOpen"
        >
          <IconMenu />
        </button>
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div class="topbar-actions">
          <!-- Existing global utilities move here unchanged -->
          <!-- <FilterBar /> <LanguageSwitcher /> <ProfileMenu ... /> -->
        </div>
      </header>

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'

const route = useRoute()
const collapsed = ref(false)
const drawerOpen = ref(false)

// One entry per route; icon is a small inline-SVG component
const navItems = [
  { to: '/', label: 'Overview', icon: 'home', section: 'Main' },
  // ...
]

const currentTitle = computed(
  () => navItems.find(i => i.to === route.path)?.label ?? ''
)

// Close the mobile drawer on navigation and on Escape
watch(() => route.path, () => { drawerOpen.value = false })
const onKey = e => { if (e.key === 'Escape') drawerOpen.value = false }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>
```

## AppSidebar.vue

```vue
<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-brand">
      <span class="brand-mark" aria-hidden="true">C</span>
      <span v-if="!collapsed" class="brand-name">Company</span>
    </div>

    <nav class="sidebar-nav" aria-label="Main">
      <template v-for="group in groups" :key="group.name">
        <div v-if="!collapsed && group.name" class="sidebar-section">{{ group.name }}</div>
        <router-link
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          class="sidebar-link"
          :title="collapsed ? item.label : null"
          exact-active-class="active"
        >
          <component :is="iconFor(item.icon)" class="sidebar-icon" aria-hidden="true" />
          <span v-if="!collapsed" class="sidebar-label">{{ item.label }}</span>
        </router-link>
      </template>
    </nav>

    <div class="sidebar-footer">
      <button
        class="sidebar-link collapse-btn"
        :aria-expanded="!collapsed"
        aria-controls="app-sidebar"
        @click="$emit('toggle-collapse')"
      >
        <IconChevron class="sidebar-icon" :class="{ flipped: collapsed }" aria-hidden="true" />
        <span v-if="!collapsed" class="sidebar-label">Collapse</span>
      </button>
    </div>
  </aside>
</template>
```

Group `items` by `section` in a computed. Icons: tiny functional components returning an `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">`.

## Shell CSS

```css
.app-shell { min-height: 100vh; background: var(--color-bg); }

.sidebar {
  position: fixed; inset: 0 auto 0 0; z-index: 40;
  width: var(--sidebar-width);
  display: flex; flex-direction: column;
  background: var(--sidebar-bg); color: var(--sidebar-text);
  padding: var(--space-4) var(--space-3);
  transition: width var(--transition), transform var(--transition);
}
.sidebar.collapsed { width: var(--sidebar-width-collapsed); }
.sidebar-brand { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-2) var(--space-6); }
.sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: 2px; overflow-y: auto; }
.sidebar-section {
  margin: var(--space-5) var(--space-3) var(--space-2);
  font-size: 11px; font-weight: var(--weight-semibold); letter-spacing: .06em;
  text-transform: uppercase; color: var(--sidebar-section-label);
}
.sidebar-link {
  position: relative; display: flex; align-items: center; gap: var(--space-3);
  height: 36px; padding: 0 var(--space-3); border-radius: var(--radius-md);
  color: var(--sidebar-text); text-decoration: none; font-size: var(--text-base);
  background: none; border: 0; width: 100%; cursor: pointer;
  transition: background var(--transition), color var(--transition);
}
.sidebar-link:hover { background: var(--sidebar-item-hover); color: var(--sidebar-text-active); }
.sidebar-link.active { background: var(--sidebar-item-active); color: var(--sidebar-text-active); font-weight: var(--weight-medium); }
.sidebar-link.active::before {
  content: ""; position: absolute; left: calc(-1 * var(--space-3)); top: 8px; bottom: 8px;
  width: 3px; border-radius: 0 3px 3px 0; background: var(--color-accent);
}
.sidebar-link:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.sidebar-icon { width: 18px; height: 18px; flex-shrink: 0; }

.app-main { margin-left: var(--sidebar-width); transition: margin-left var(--transition); }
.is-collapsed .app-main { margin-left: var(--sidebar-width-collapsed); }

.topbar {
  position: sticky; top: 0; z-index: 30;
  height: var(--topbar-height);
  display: flex; align-items: center; gap: var(--space-4);
  padding: 0 var(--space-6);
  background: rgba(255,255,255,.9); backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
}
.topbar-title { font-size: var(--text-md); font-weight: var(--weight-semibold); margin: 0; }
.topbar-actions { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }
.drawer-toggle { display: none; }

.content { padding: var(--space-6); max-width: var(--content-max); }

/* Tablet: icon rail */
@media (max-width: 1024px) {
  .sidebar { width: var(--sidebar-width-collapsed); }
  .app-main { margin-left: var(--sidebar-width-collapsed); }
  /* hide .sidebar-label / .sidebar-section via the collapsed prop or here */
}

/* Mobile: off-canvas drawer */
@media (max-width: 768px) {
  .sidebar { width: var(--sidebar-width); transform: translateX(-100%); }
  .drawer-open .sidebar { transform: none; box-shadow: var(--shadow-md); }
  .app-main, .is-collapsed .app-main { margin-left: 0; }
  .drawer-toggle { display: inline-flex; }
  .sidebar-backdrop { position: fixed; inset: 0; z-index: 35; background: rgba(15,23,42,.4); }
  .content { padding: var(--space-4); }
}
```

At tablet width, drive labels off a computed `effectiveCollapsed = collapsed || isTablet` (a `matchMedia` listener) rather than relying on CSS alone. That keeps the tooltip `title` and the hidden labels in sync.
