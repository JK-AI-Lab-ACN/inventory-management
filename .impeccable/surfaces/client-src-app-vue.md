---
version: 1
slug: "client-src-app-vue"
primary_target: "client/src/App.vue"
related_targets: ["client/src/views"]
---

# App shell and all working screens

Scope: the whole SPA shell (App.vue) and every routed view. Mode: Operate.
Audience and job: supply-chain operations managers scanning stock, orders, demand and spend, and acting on exceptions.
Constraints: behavior, routes, i18n, data flow unchanged. No emojis. Charts stay custom SVG. Direction pinned by the user: Accenture brand, left sidebar, dark sidebar, purple accent.

## Direction contract

THESIS: Accenture's black-and-purple identity as a calm operations console. It refuses the default blue-on-gray SaaS dashboard with a white top bar.

OWN-WORLD: A near-black #0A0011 sidebar with white Graphik-stack type. A white content ground with #F1F1EF panels and #CFCFCF hairlines. Core purple #A100FF for the active item, primary actions, focus and key numbers, with #7500C0 for hover and pressed states and #E6DCFF for selection tint. Square-ish corners (4px), flat fills, no gradients, no glow.

STORY: The manager sees where they are, what's flagged, and acts from the same frame on every page.

FIRST VIEWPORT: A 248px fixed black sidebar with the brand at the top, seven nav items and the language and profile controls at the bottom. On the right, a sticky white top bar with the page title and the global filters. Below it, the content: KPI cards, then the tables.

FORM: Pinned by the user (Accenture brand, sidebar shell). seed: none (unavailable). Signature move: the Accenture greater-than chevron as the active-nav marker and brand mark, in purple.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
