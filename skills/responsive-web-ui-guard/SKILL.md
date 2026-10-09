---
name: responsive-web-ui-guard
description: Responsive layout and mobile-reading guardrail for web UI work. Use when Codex builds, edits, reviews, or verifies any website, web app, dashboard, landing page, React/Vite frontend, HTML/CSS UI, table-heavy interface, floating action UI, or responsive/mobile layout, especially when the user asks for web design, app-like mobile UI, readable phone experience, fixed/sticky columns, charts, cards, tabs, headers/footers, or to fix layout overflow/running out of bounds. Also mandatory for any Traditional Chinese web page: iPhone Safari text wrapping (right-side gaps, headings breaking mid-word, 1–2 character orphan lines), centred/left alignment consistency, rounded images clipped square, and final verification on the real WebKit engine with the plain (cache-served) URL.
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

## 中文排版與 iPhone Safari（2026-10 實戰教訓，必守）

Chrome 與桌機看不出來、只在 iPhone 出錯的五類問題。做任何中文網頁都要預先避開，交付前要用下方「必過關卡」實測。

1. **段落不可用 `text-wrap: pretty`**。iPhone Safari 會讓整段每一行都提早換行，右側空一大塊。段落、條列、卡片內文一律 `text-wrap: wrap`。設計稿或框架預設給 `p, li, div { text-wrap: pretty }` 的要覆寫掉。
2. **中文標題要依詞組換行**。中文沒有空格，瀏覽器會在任意兩字之間斷行，例如「適｜合」「購車｜術」。`word-break: keep-all` 在 WebKit 對中文無效，不能靠它。做法：
 - 把標題依標點切成詞組，每組包 `<span style="display:inline-block">`。
 - 斷點放在「，、。？！：；」』》）】｜」之後，或「《「『（【」之前。連續標點（如「）】」）要當成一組。
 - 單一詞組比一行還長時（例如「不確定這套方法能不能幫到你？」），要手動指定詞組內的斷點，否則會剩「你？」一兩個字自成一行。
 - 大字引言常常不是 `<h*>` 標籤（是行內大字級的 `<div>`），也要一起處理。
3. **短句避免最後一行只剩一兩個字**。只在「實際排成兩行」的短句（卡片標題、條列說明、小字），以及 2–6 行的置中段落用 `text-wrap: balance`。三行以上、靠左的段落不可用 balance，否則每行都變短，又出現右側空白。行數要在瀏覽器裡實際量，不要只看字數。
4. **置中與靠左要一致**。區塊是置中排版時，標題、裝飾線（常見 `::after` 用 `position:absolute; left:0`）、說明文字、按鈕要一起置中。裝飾線留在左邊，會讓置中的標題看起來兩側特別空。同一張卡片不可以標題置中、內文靠左。
5. **窄欄標題要換字級，不要接受排成四行窄欄**。標題由幾個長詞組組成時，手機上可能一行只放得下一組，排成又窄又長的一欄、兩側大片留白。解法：
 - 手機版用 `font-size: min(原字級, calc((100vw - 左右總留白) / 每行字數))`，讓兩組詞組剛好排成一行。
 - 改完量實際行數。
6. **圓角圖片不能被直角裁切**。圖片高度大於外框時，外框或進場動畫的 `clip-path: inset(...)` 沒有 `round`，下方圓角就會被切成直角。改法：
 - 圖片高度改成填滿外框。
 - 裁切框加上 `inset(0 round 圓角)`。
7. **權重陷阱**。`:is(a, b, .cls:not(h1))` 的權重取參數中最高的那個，可能把後面才加的修正蓋掉。寫覆寫規則前先算權重，改完要在瀏覽器讀 computed style 確認真的有生效。

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

## 必過關卡（交付前一律執行，沒有證據不算完成）

只要做了網頁、改了版面，或回報「已修好」，都必須跑完以下項目，並把結果寫進回覆和 handoff。你 2026-10-10 要求：排版問題不准再犯，每次都要確實檢查。

1. **用 iPhone 同引擎驗**：系統 WebKit 就是 iPhone Safari 用的引擎，Chrome 和內建瀏覽器的換行行為不同，不能拿來代替。工具在本技能的 `scripts/`：
 ```bash
 swiftc -O scripts/wk-audit.swift -o /tmp/wk-audit # 第一次編譯（暫存路徑可換成 session scratchpad）
 /tmp/wk-audit "<一般網址>" scripts/wk-audit-layout.js <截圖前綴> 390 0 # 溢出／超出畫面／右側留空／字太小／換行設定
 /tmp/wk-audit "<一般網址>" scripts/wk-audit-heading-breaks.js x 390 0 # 列出每個標題的實際斷行，逐句看有沒有斷在詞中間
 /tmp/wk-audit "<一般網址>" scripts/wk-audit-orphans.js x 390 0 # 列出最後一行只剩 1–2 字的段落
 /tmp/wk-audit "<一般網址>" scripts/wk-audit-layout.js <截圖前綴> 414 30 # 逐屏截圖，要親眼看
 ```
2. **寬度至少跑 360、390、414、768、1024、1440**，每一頁都要跑；整站改動就整站跑。
3. **用一般網址驗收**：不可帶 `?ver=`、`?nc=` 這類參數，帶參數會繞過頁面快取，訪客實際看到的可能還是舊頁。改完先清快取（WordPress 的 WP Rocket 用 `rocket_clean_domain()`），再確認 HTML 裡的快取時間（例如 `cached@`）晚於改動時間。
4. **先做陰性對照**：新寫或修改檢查腳本時，先故意加回錯誤（例如強制 `text-wrap: pretty`），確認腳本抓得到，才拿它驗修正結果。
5. **截圖要親眼看過**：以下問題只有截圖看得出來，腳本抓不到：對齊不一致、裝飾線偏移、圓角被裁、標題太窄。逐屏截圖要整理成總覽圖逐張看，有疑點再放大裁切。
6. **誤判要用截圖核對**：全形標點常用備用字型顯示，逐字量位置時會誤判成「標點自成一行」。腳本報這類問題時，先截圖確認再修。
7. **業主用手機回報後**：修完先用一般網址＋Safari 引擎重現他截圖的位置，確認改好了才回報。

Chrome／內建瀏覽器的檢查只能補充，不能取代上面的 Safari 引擎檢查。

### 基本檢查（各寬度都要過）

- Mobile narrow: about `390 x 844`
- Mobile small: about `360 x 740`
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
