# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Supply-chain operations managers at Catalyst Components, a component manufacturer. They work at a desk on laptops and large monitors, in English or Japanese, and check stock, orders, demand and spend several times a day. Their job is to spot exceptions (low stock, backorders, rising demand, overspend) and act on them.

## Product Purpose
A factory inventory management system: one place to monitor inventory across warehouses, track customer orders, read demand forecasts, place restocking orders against a budget, and review spending and reports. Success means a manager can see what needs attention and act on it without leaving the app.

## Operating Context
- Global filters (time period, warehouse, category, order status) scope every page.
- Tabs: Overview, Inventory, Orders, Finance, Demand Forecast, Restocking, Reports.
- Language switch between English and Japanese, which also switches the currency display between USD and JPY.
- A profile menu with a tasks list.

## Capabilities and Constraints
- Vue 3 SPA with a FastAPI backend. Data is in-memory mock JSON, with no database or authentication.
- Charts are hand-built SVG, with no chart library.
- Workshop demo repository, public on GitHub.

## Brand Commitments
- Accenture brand styling, per the user's direction to follow accenture.com: Graphik typeface, with Accenture purple #A100FF as the core accent and the purple spectrum #460073 / #7500C0 / #A100FF / #C2A3FF / #E6DCFF.
- Neutrals: #000000, #818180, #CFCFCF, #F1F1EF, #FFFFFF.
- Product name in the UI stays "Catalyst Components / Inventory Management System".
- No emojis in the UI.

## Evidence on Hand
- Mock data in `server/data/*.json`.
- There are no real customers, testimonials or logos. Don't fabricate any.

## Product Principles
1. Exceptions first: what needs action is more visible than what is fine.
2. Numbers are the content. Make them scannable, aligned and comparable.
3. One consistent frame across every page, so moving between tabs costs no reorientation.
4. Bilingual by default: every label goes through i18n, and layouts tolerate longer Japanese and English strings.
