---
name: responsive-web-ui-guard
description: Responsive layout and mobile-reading guardrail for web UI work. Use when Codex builds, edits, reviews, or verifies any website, web app, dashboard, landing page, React/Vite frontend, HTML/CSS UI, table-heavy interface, floating action UI, or responsive/mobile layout, especially when the user asks for web design, app-like mobile UI, readable phone experience, fixed/sticky columns, charts, cards, tabs, headers/footers, or to fix layout overflow/running out of bounds.
---

# Responsive Web UI Guard

## Purpose

Prevent the recurring failure mode where a desktop-looking web UI breaks on mobile: text wraps awkwardly, numbers overflow cards, fixed columns cover content, floating buttons block controls, charts expose raw values, or the page gains unintended horizontal scroll.

Apply this skill before and after frontend changes. Treat mobile readability as part of the definition of done, not a polishing pass.

## Build Rules

1. Design mobile-first, then expand to desktop.
2. Keep page-level horizontal overflow at zero. Wide data tables may scroll inside their own wrapper, but `html/body/#root/main` should not create horizontal scroll.
3. Use stable dimensions for cards, tabs, tables, charts, floating buttons, and metric blocks so content changes do not shift or break layout.
4. Keep text readable on phones:
 - Use `clamp()` sparingly for numeric display, with a real max size.
 - Avoid viewport-width-only font scaling.
 - Use `font-variant-numeric: tabular-nums` for financial numbers.
 - Set `min-width: 0` on grid/flex children that contain text.
 - Prefer `white-space: nowrap` for money and short metrics, but reduce font size or card columns before allowing ugly number breaks.
5. Avoid nested card stacks unless the UI is a true repeated item, modal, or framed tool.
6. Use tabs, segmented controls, or horizontal paging when a section has too many cards. Do not let one page become a long pile of unrelated sections.
7. For floating actions, respect safe areas:
 - include `env(safe-area-inset-bottom)` where useful.
 - ensure floating controls do not cover critical table rows, chart tooltips, form submit buttons, or browser bottom bars.
8. For sticky columns in tables, fix only what is needed for comparison. If the user asks for only code/symbol fixed, do not also freeze names or expand controls.
9. For charts, do not show persistent dense value labels on every point unless the user explicitly wants that. Prefer hover/tap tooltips and hide private values when privacy mode is active.
10. If the app is dark themed, set controllable surfaces consistently:
 - `html`, `body`, `#root` backgrounds.
 - `theme-color`.
 - `color-scheme: dark`.
 - mobile safe-area padding. Native Safari toolbars cannot be fully recolored by the page; do not promise that.

## Implementation Patterns

Use these CSS patterns when applicable:

```css
html {
 min-height: 100%;
 background: var(--bg);
 color-scheme: dark;
}

body {
 min-height: 100dvh;
 overflow-x: hidden;
 background-color: var(--bg);
}

#root {
 min-height: 100dvh;
 background-color: var(--bg);
}

.app {
 max-width: 100%;
 padding-bottom: calc(96px + env(safe-area-inset-bottom));
}

.gridChild,
.card,
.panel,
.tabContent {
 min-width: 0;
}

.moneyValue {
 white-space: nowrap;
 font-variant-numeric: tabular-nums;
}

.tableWrap {
 overflow-x: auto;
 -webkit-overflow-scrolling: touch;
}
```

For metric cards on phones:

```css
.metrics {
 display: grid;
 grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metric strong,
.metric .moneyValue {
 font-size: clamp(24px, 7vw, 36px);
 line-height: 1.08;
 white-space: nowrap;
 overflow-wrap: normal;
 word-break: keep-all;
 font-variant-numeric: tabular-nums;
}
```

If the number still breaks, change the layout first: reduce columns, shrink max font size, shorten labels, or remove duplicated metrics. Do not accept broken financial numbers as a final state.

## Verification Checklist

Before finishing a frontend task, verify at least these viewports when possible:

- Mobile narrow: about `390 x 844`
- Mobile small: about `360 x 740` if the UI is dense
- Desktop: about `1280 x 800` or the app's common desktop width

Check:

1. No page-level horizontal overflow:
 ```js
 document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1
 ```
2. Text does not escape cards, buttons, tabs, table headers, or metric blocks.
3. Money values do not split into awkward lines.
4. Sticky columns do not overlap scrollable columns.
5. Floating action buttons do not cover essential content or submit buttons.
6. Tooltips/modals stay within the viewport and do not appear off-screen.
7. Chart labels and tooltips are readable on mobile and privacy mode masks values if the app supports privacy hiding.
8. Header/footer/safe-area background does not expose unintended white bands where the page can control the background.

Use the Browser plugin or equivalent local browser verification after meaningful UI changes. A CSS build passing is not enough for this skill.

## Response Expectations

When this skill affects the work, mention the responsive checks briefly in the final answer. If something cannot be fully controlled, such as native iPhone Safari toolbar color, say so plainly and distinguish browser UI from webpage UI.
