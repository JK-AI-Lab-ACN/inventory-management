---
name: saas-redesign
description: Redesign a Vue 3 application's UI into a modern, professional SaaS-style interface. It replaces the top navigation bar with a fixed vertical sidebar on the left, introduces a consistent spacing, type and color token scale, and polishes cards, tables, forms and page headers without changing app behavior. Use this skill whenever the user wants to modernize, restyle, "make it look like a real SaaS product", move the nav to a sidebar or left rail, clean up inconsistent spacing, or give a Vue/Vite app a polished dashboard look, even if they don't say "SaaS" or "sidebar" explicitly. Not for backend work, adding new features, or non-Vue frameworks.
---

# SaaS Redesign for Vue 3 Apps

Turn an existing Vue 3 app into a calm, consistent SaaS interface: a left sidebar for navigation, a slim top bar for page context and utilities, and a content area where every page follows the same rhythm.

The redesign is **visual and structural only**. Routes, data fetching, props, emitted events, i18n keys and business logic stay exactly as they are. Users should find every feature in the same place it was, just in a better-looking frame. If a change would alter behavior, leave it out and mention it to the user as a suggestion.

## Workflow

### 1. Survey before touching anything
Read enough to answer these questions, then summarize the answers to the user in a few lines:

- **App shell:** where is the top nav? Usually `App.vue`, sometimes a `components/Header.vue` or `layouts/` file. What does it contain: brand, nav links, filters, language switcher, profile menu, notifications?
- **Routes:** read the router (`main.js`, `router/index.js`) for the list of pages. Each one becomes a sidebar item.
- **Styling approach:** global CSS in `App.vue`, a `style.css`, scoped styles, Tailwind, or a component library (Vuetify, PrimeVue, Element Plus). **Work with the existing approach.** Don't introduce Tailwind or a UI library into an app that doesn't use one, because that adds a dependency and a second styling system.
- **Existing design rules:** check `CLAUDE.md`, `DESIGN.md` or a style guide for colors, "no emojis" rules, fonts. Those rules win over this skill's defaults.
- **Repeated patterns:** the classes many views share (`.card`, `.page-header`, `.stats-grid`, table styles). Restyling those centrally upgrades every page at once. That's the main lever.

If the project's instructions say `.vue` work must go through a specific subagent (for example a `vue-expert`), follow that.

### 2. Introduce design tokens
Add CSS custom properties on `:root` in the global stylesheet, and use them for everything you touch afterwards. Consistency comes from everyone drawing from the same small scale, not from eyeballing pixel values per component. Start from `references/tokens.css` and adapt the colors to the app's existing palette. Keep its brand color if it has one.

The essentials:
- **Spacing:** a 4px-based scale (`--space-1` 4px through `--space-8` 48px). Every padding, margin and gap you write should be a token.
- **Type:** about five sizes (12/13/14/16/20/24px), two or three weights, one font stack.
- **Color:** neutral surface/border/text tones, one accent, and semantic success/warning/danger/info with soft background variants.
- **Shape and depth:** radius `6px`/`10px`, one subtle shadow, hairline borders.
- **Layout:** `--sidebar-width` (about 240px) and `--sidebar-width-collapsed` (about 64px), `--topbar-height` (about 56px), `--content-max` (about 1440px).

### 3. Build the app shell
Restructure the shell into a sidebar, top bar and content area. See `references/shell-pattern.md` for a complete `AppSidebar.vue` and `App.vue` layout to adapt.

- **Sidebar (left, full height, fixed):**
  - Brand at the top.
  - Nav items in the middle, each a `router-link` with an icon and label, the active state shown by accent background tint plus a left indicator bar. Group items under small uppercase section labels if there are more than about 6.
  - Secondary items (settings, help, profile) pinned at the bottom.
- **Top bar (inside the content column, sticky):** the current page title or breadcrumb on the left. Global utilities on the right: filters, search, language switcher, notifications, profile menu. Move these out of the old top nav, keeping their components and props unchanged.
- **Content:** `margin-left: var(--sidebar-width)`, padded with `--space-6`, max width `--content-max`.
- **Icons:** inline SVG components (stroke 1.75, 18px, `currentColor`). Don't add an icon package unless the app already has one. No emojis as icons.
- **Responsive behavior:**
  - Below about 1024px, the sidebar collapses to icons only, with labels as `title`/tooltip.
  - Below about 768px, it becomes an off-canvas drawer opened by a hamburger button in the top bar, with a backdrop, closing on route change and on Escape.
- **Accessibility:**
  - Use `<nav aria-label="Main">`, and add `aria-current="page"` to the active link (`router-link` does this automatically).
  - Keep focus visible on every interactive element.
  - The collapse and drawer buttons need `aria-expanded` and `aria-controls`.

Delete the old top-nav markup and its CSS once the new shell works. Leftover `.top-nav` rules cause confusing overrides later.

### 4. Polish the shared patterns
Restyle the shared classes (not each view's local copy) using tokens, so every page benefits:

| Pattern | Target look |
|---|---|
| Page header | Title 24px/600, a muted one-line description, primary action aligned right, `--space-6` below |
| Cards | White surface, 1px border, radius `--radius-lg`, padding `--space-5`, header row with title 14–16px/600 |
| KPI / stat cards | Label 12px uppercase muted, value 24–28px/600 tabular numbers, optional delta chip |
| Tables | Sticky header with muted 12px uppercase labels, 44–48px rows, hairline row dividers, hover tint, numbers right-aligned with `font-variant-numeric: tabular-nums` |
| Badges | Pill, 12px/500, soft background + strong text from the semantic tokens |
| Buttons | Primary (accent fill), secondary (border), ghost. Height 36px, radius `--radius-md`, visible focus ring |
| Forms / filters | 36px controls, consistent border and focus ring, labels 12–13px above or inline |
| Empty / loading / error | Centered muted text in the card body. Skeleton or spinner, never a bare "Loading..." at page top |

Then do a quick pass over each view for one-off spacing (`margin: 17px`, `padding: 0.8rem`), hard-coded colors and inline styles, and swap them for tokens. Leave a view's scoped styles alone where they're specific to that view (chart internals, special layouts). The goal is consistency, not rewriting every file.

### 5. Verify in the running app
Start the dev server (or use the one that's already running) and check, ideally with screenshots:

1. Every route renders in the new shell, with the correct sidebar item active.
2. Everything that was in the old top nav still works from its new place (filters still filter, language switching still translates, menus open).
3. Widths of about 1440, 1024 and 375 px: expanded sidebar, collapsed rail, drawer.
4. No console errors. Keyboard tab order reaches the sidebar, top bar and content in a sensible order.
5. If the project has tests, run them.

Report what changed (the shell, the token file, which shared patterns were restyled), any behavior you deliberately left untouched, and any suggestions you didn't implement.

## Design principles
These are what make the result feel professional rather than merely different:

- **Restraint.** Neutral surfaces, one accent color, color reserved for meaning (status, active state, primary action). A busy palette reads as amateur.
- **Rhythm.** The same gaps between the same kinds of things on every page. When in doubt, use more whitespace, not less.
- **Hierarchy through weight and size, not boxes.** Avoid nesting cards inside cards. Use a heading and spacing to separate sections instead.
- **Density that fits the data.** Admin and inventory apps are data-heavy. Keep tables compact and scannable, and don't inflate them into marketing-style spacing.
- **Quiet motion.** 150–200ms ease transitions on hover, active and drawer. No bouncing.
