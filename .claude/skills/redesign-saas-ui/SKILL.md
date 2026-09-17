---
name: redesign-saas-ui
description: Redesign this Vue 3 app's UI into a modern SaaS-style interface with a left vertical sidebar nav (replacing the top nav bar), a consistent spacing scale, and a polished professional visual language. Use when asked to redesign the UI, add a sidebar, modernize the look, or give the app a more "SaaS" feel.
---

# Redesign to a SaaS-Style Sidebar UI

This skill turns the app's current top-nav layout into a left-sidebar layout in the style of
modern SaaS products (Linear, Vercel, Stripe dashboard, etc.), while preserving every existing
route, feature, and piece of functionality. It ends with a working, verified app — not just a plan.

Read this whole file before touching anything. The steps are ordered; don't skip the audit.

## Non-negotiables

- **Every existing route, modal, and feature must still work.** This is a visual/structural
  restyle, not a feature change. Do not drop nav items, filters, the language switcher, the
  profile menu, or any modal.
- **Follow CLAUDE.md's mandatory rule**: any creation or significant modification of a `.vue`
  file goes through the `vue-expert` subagent. This skill's job is to audit and design precisely
  enough that you can hand `vue-expert` one complete, unambiguous spec and get a correct result
  in a single pass — not to write `.vue` files yourself.
- **No new npm dependencies** (no icon libraries, no UI kits) unless the user explicitly asks.
  Use inline SVG for icons, matching the minimal inline-SVG style already used in this codebase
  (see `BacklogDetailModal.vue`'s close icon for the pattern).
- **Don't invent new brand colors.** Reuse the app's existing palette (see Design Tokens below)
  unless the user asks for a different look — this is a structural + polish pass, not a rebrand.

## Step 0 — Audit the current UI

Before designing anything, read:

1. `client/src/App.vue` — the current shell: top-nav markup, the global `<style>` block (this is
   where most shared classes live: `.card`, `.stat-card`, `.badge`, `.page-header`, table styles,
   etc.), and what else renders alongside `<router-view>` (FilterBar, modals, ProfileMenu,
   LanguageSwitcher).
2. `client/src/main.js` — the full, authoritative list of routes and their components. Every one
   of these becomes a sidebar link. Don't rely on what App.vue currently renders as nav links;
   cross-check against the router in case they've drifted.
3. Two or three files in `client/src/views/` — to see current page structure conventions
   (`.page-header`, `.stats-grid`, `.card`), so the redesign's spacing/typography changes apply
   uniformly instead of guessing.
4. `client/src/components/` — anything currently living in the top nav (ProfileMenu,
   LanguageSwitcher, FilterBar) so you know what needs a new home in the sidebar layout.

Write down (mentally or in a scratch note, not a file): the exact list of nav items + routes +
labels (including i18n keys, e.g. `t('nav.orders')`), and every non-route element currently in
the header.

## Step 1 — Design the sidebar

Design (don't yet implement) a new `client/src/components/Sidebar.vue`:

- **Structure, top to bottom**: brand/logo block → vertical list of nav links (one per route from
  Step 0, in the same order, using the same i18n keys) → a spacer that pushes remaining content
  down → a footer area for whatever doesn't belong in the nav list itself (e.g. the profile menu,
  if it makes sense to relocate it there — otherwise keep it in a slim top bar, see Step 2).
- **Behavior**: fixed to the left edge, full viewport height, independent scroll from the main
  content. Active route gets a highlighted background + accent-colored text + left accent bar
  (3–4px), matching the accent treatment the current top nav already uses for its active tab —
  carry that visual idea over, don't invent a new one.
- **Icons**: a small inline SVG per nav item (16–20px, stroke-based, 1.5–2px stroke width) if you
  add icons at all. Keep them minimal and consistent — same stroke width and visual weight across
  all of them. It's fine to ship without icons (label-only) if a coherent icon set can't be
  produced quickly and consistently; a plain, consistent sidebar beats a mismatched icon set.
- **Width**: 240–260px fixed. Don't build a collapse/expand toggle unless asked — that's scope
  creep for a first pass. Do make sure the layout degrades reasonably on narrow viewports (stack
  or hide the sidebar behind a simple toggle only if you have time; at minimum, don't let it break
  the page).

## Step 2 — Restructure the app shell

Plan the `App.vue` changes:

- Replace the horizontal `<header class="top-nav">` structure with a flex layout:
  `.app-shell { display: flex }` containing `Sidebar` and a `.app-main` column
  (`flex: 1; min-width: 0; display: flex; flex-direction: column`) that holds whatever needs to
  stay above the routed content (FilterBar, and a slim top bar for LanguageSwitcher/ProfileMenu if
  those didn't move into the sidebar footer) plus `<router-view>`.
- `.app-main` scrolls independently if needed; the sidebar itself does not scroll with the page.
- Carry over every existing modal (`ProfileDetailsModal`, `TasksModal`, etc.) unchanged — they're
  teleported to `<body>` already in most cases, so they're unaffected by the shell restructure.
- Update the global `<style>` block in `App.vue` for the new layout and the spacing/polish pass
  below. Don't fork these shared styles into per-view scoped CSS — views rely on the global
  classes (`.card`, `.stat-card`, `.badge`, table styles) staying centrally defined.

## Step 3 — Consistent spacing & professional polish

Apply a single 8px-based spacing scale everywhere touched by this pass (page padding, card
padding, gaps between stat cards, gaps in the sidebar nav list): use `4px, 8px, 12px, 16px, 24px,
32px` — no ad hoc values like `13px` or `22px`. Specifically:

- Page content padding: `24px` (`1.5rem`) on all sides of `.app-main`'s content area.
- Card padding: `20–24px`.
- Gaps in grids (`.stats-grid`, etc.): `16–20px`.
- Sidebar nav item padding: `10px 16px`, `4px` vertical gap between items.

Visual refinement, applied consistently rather than per-component:

- Border radius: `10–12px` for cards/panels, `6–8px` for buttons/inputs/badges. Pick one value per
  tier and use it everywhere — don't let radius vary card to card.
- Shadows: subtle by default (`0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06)`), slightly
  more pronounced on hover for interactive cards. Avoid heavy/dark drop shadows — this is a light,
  clean SaaS look, not skeuomorphic.
- Borders: `1px solid` with the app's existing light border color (see tokens below) — keep using
  borders + subtle shadow together, not shadow alone, matching the app's current card style.
- Transitions: `0.15–0.2s ease` on hover/active state changes, nothing longer (snappy, not showy).

## Design tokens (reuse, verify against current App.vue first)

These are the app's existing colors per its design system — confirm they still match what's in
`App.vue` before reusing, in case they've drifted since this skill was written:

- Ink / primary text: `#0f172a`
- Secondary / muted text: `#64748b`
- Borders / dividers: `#e2e8f0`
- Accent (active nav, links, primary actions): `#2563eb`, with a light tint `#eff6ff` for active
  backgrounds
- Surface: `#ffffff` cards on `#f8fafc` page background
- Status colors: green (success/delivered), amber (warning/processing), red (danger/backordered),
  blue (info/shipped) — reuse the existing `.badge` modifier colors as-is, don't redefine them.

## Step 4 — Implement via vue-expert

Hand `vue-expert` one complete spec covering, in a single delegation (don't split into multiple
round-trips unless it reports something needs clarifying):

1. Create `client/src/components/Sidebar.vue` per Step 1, with the exact nav item list (labels +
   i18n keys + routes) you gathered in Step 0.
2. Rewrite `App.vue`'s template/shell per Step 2, and its global `<style>` block per Step 3 and the
   design tokens above — explicitly tell it to preserve every modal, the FilterBar, and all
   existing global classes views depend on (`.card`, `.stat-card`, `.badge`, `.page-header`, table
   styles) rather than renaming them, since views reference them and are out of scope for this
   pass.
3. Call out any view-level assumption that will break with the new shell (e.g. a view that assumed
   a full-width sticky top nav for its own sticky headers) so it can fix those in the same pass
   instead of leaving a visual regression.

Explicitly tell `vue-expert`: no new dependencies, inline SVG only for icons, and match the
Composition API style already used in each file it touches (views use `export default { setup() }`
per the existing convention in this codebase).

## Step 5 — Verify and report

1. Make sure both dev servers are running (`server/`: `uv run python main.py` on :8001;
   `client/`: `npm run dev` on :3000). Start them if they're not — see `.claude/skills/start` in
   this repo.
2. Confirm the app loads (`curl -s -o /dev/null -w '%{http_code}' http://localhost:3000` should be
   `200`) and, if Playwright MCP tools are connected, navigate to a couple of routes and take a
   snapshot to sanity-check the sidebar renders, the active-route highlight works, and no view
   looks visually broken (overlapping content, missing padding). If Playwright isn't connected,
   say so plainly and ask the user to eyeball it instead of claiming it was visually verified.
3. Report back concisely: files changed/created, any design calls you made without asking (icon
   choice or its absence, sidebar width, what moved into the sidebar footer vs. stayed in a top
   bar), and anything you deliberately left out of scope (e.g. a collapse/expand toggle, mobile
   hamburger behavior) so the user can ask for it as a follow-up if they want it.
