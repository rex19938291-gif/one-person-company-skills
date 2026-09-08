---
name: html-to-elementor
description: Convert HTML, Open Design (OD) artifacts, static pages, or Elementor JSON parity work into an Elementor-native build blueprint and iteration workflow. Use when the user asks to turn HTML/OD into WordPress Elementor native widgets, avoid full-page HTML widgets, produce editable Elementor sections, map an existing design into Elementor containers/widgets, or fold lessons from an OD-to-Elementor conversion back into a reusable process. Trigger phrases include "HTML to Elementor", "OD to Elementor", "轉 Elementor", "Elementor 原生元件", "不要塞 HTML widget", "native-first Elementor", and "迭代封裝".
---

# HTML To Elementor

Use this skill to turn a designed HTML/OD page into a maintainable Elementor-native plan before any build or import work. The goal is client-editable Elementor structure, not a static webpage wrapped in Elementor.

## Core Rule

Default to native Elementor widgets. Treat a full section or full page inside one HTML widget as a failure unless 你 explicitly approves that exception.

Allowed HTML widget uses:

- A small `<style>` block scoped to a known Elementor element or page wrapper.
- A narrow visual/interaction exception that native Elementor cannot reasonably reproduce.
- Rich tab/accordion content only when the native widget requires HTML strings.
- A temporary form placeholder clearly marked as non-functional.

## Workflow

### 1. Define Scope

State the conversion target in one line:

- Source: OD artifact, local HTML, exported Elementor JSON, URL, screenshot, or pasted code.
- Target: blueprint only, local JSON/package, local WordPress import, or MCP mutation.
- Non-scope: production import, public tunnel, plugin install, credential handling, destructive cleanup, or Chrome/Browser use unless explicitly approved.

If actual Elementor MCP writing is requested, also use the `elementor-mcp` skill and begin with read-only checks (`list-pages`, `get-global-settings`, `get-container-schema`) before any mutation.

### 2. Build The Source Pack

Collect only the sources needed for the active page or section:

- For OD: prefer the full active artifact bundle when Open Design tools are available; otherwise use local HTML/CSS/asset files.
- For HTML: identify the entry file, referenced CSS/JS, image assets, and any generated Elementor JSON.
- For existing Elementor work: inspect the JSON/widget tree and the rendered local preview when available.
- Do not use Chrome, Browser Use, production WordPress, public tunnels, credentials, or customer/private data unless 你 has approved that exact scope.

Record asset URLs or file paths, but do not copy secrets or credentials into the blueprint.

### 3. Inventory Sections

Inventory the page by editable units, not by XML tags.

For each section, capture:

- Purpose and visual role.
- Source selector/class/component, if available.
- Copy blocks and CTAs.
- Media/assets.
- Responsive behavior.
- Repeated patterns that should become one reusable card/container pattern.
- Interaction or animation requirements.

Keep reading order and visual hierarchy, but do not preserve source DOM shape when it would create uneditable Elementor output.

### 4. Map To Native Elementor

Use this default mapping:

| Source pattern | Elementor target |
| --- | --- |
| Page shell | Header/footer templates or reusable sections; do not duplicate drifting shells |
| Section wrapper | Container |
| Layout rows/columns | Nested Containers with flex settings |
| H1-H6 | Heading widget |
| Paragraph/rich copy | Text Editor widget |
| Image/SVG/content icon | Image widget or Icon widget |
| CTA link | Button widget |
| Feature list | Icon List or repeated native rows/cards |
| Card grid | Build one native card, duplicate/update copies |
| Tabs/FAQ | Tabs or Accordion widget |
| Form | Shortcode widget for Fluent Forms/CF7, with scoped CSS if needed |
| Minor styling gap | Style-only HTML widget or scoped CSS |
| Complex custom animation | Explicit exception register, not silent HTML dumping |

Extract site tokens first: colors, typography, spacing, radius, shadows, max widths, breakpoints, and motion rules. Elementor global colors/typography should carry stable brand decisions whenever feasible.

### 5. Produce The Blueprint

When asked for a plan, handoff, or another conversation's continuation packet, read and use `references/elementor-native-blueprint.md`.

The blueprint must include:

- Source pack.
- Design tokens.
- Section inventory.
- Elementor widget tree by section.
- Asset map.
- Responsive rules.
- HTML/CSS/JS exception register.
- Verification checklist.
- Iteration capsule for future skill updates.

### 6. Execute In Loops

When building, work section by section:

1. Create or update global tokens.
2. Build the outer Container and inner layout.
3. Add native widgets for copy, media, CTA, and repeated cards.
4. Add scoped CSS only for gaps that Elementor controls cannot express.
5. Verify the widget tree before moving to the next section.

Prefer generator/import when reproducibility matters and the generator is the source of truth. Prefer direct MCP mutation only when the target element is clear and the mutation is safer than regenerating/importing.

### 7. Verify

Minimum checks before calling the conversion ready:

- No full-page HTML widget embed.
- HTML widget exceptions are listed, justified, and scoped.
- Header/footer shell choice is intentional and does not drift across related pages.
- Main copy, CTAs, and media are present in editable widgets.
- Repeated cards are editable as native structures.
- Desktop/mobile layouts have no horizontal overflow.
- Local preview or rendered output is checked when available.
- Package/export includes JSON, assets, and a short QA note if this is a handoff deliverable.

For 你 OD/UI delivery checks, screenshot or viewport evidence is preferred before signoff. If the in-app preview path is blocked, report the blocker instead of switching to Chrome without permission.

## Iteration Packaging

At the end of each real conversion, write an `Iteration Capsule` into the task handoff or final output:

- New reusable mapping rule.
- New approved exception.
- New failure mode and prevention.
- Verification that caught the issue.
- Whether it belongs in this skill now, later, or only in the project handoff.

Update this skill only when 你 explicitly asks to fold the lesson back in, or when the current task itself includes an explicit `迭代封裝` instruction. Keep additions generic, non-sensitive, and reusable across future HTML/OD to Elementor work.

## Iteration Capsule — 2026-08-18 A 客戶 三頁遠端還原輪（已定案的映射增補）

1. **機械轉換器優先**：整頁（含 27+ 區塊）不要手工映射——用固定分類規則的轉換器（參考 `A 客戶A 客戶/網站與SEO/elementor建置工具/convert.py`）：全元素子節點的區塊標籤→container（**必設 `html_tag` 保留 article/section/nav**），h1-h6→heading，img→image，其餘一律 text-editor **原始 HTML 整段保留（含 class 與行內 style）**。文字葉節點因此天然 100% 保真、仍可在編輯器改文案。
2. **CTA 例外定案**：帶複雜 class 樣式（::after、hover、od-id 裝飾）的 `<a>` 用 text-editor 保留原始錨點，比 Button widget 重刻穩定——Button 的 class 只能掛在包裝層，28 條設計規則會整批落空。列入報告的 native 例外即可。
3. **成敗在 cascade 不在映射**：Elementor 4.x 的容器變數／::before 疊層／widget position:relative／包裝層搶 flex-grid item／object-* 斷鏈，五類干擾與三層特異性架構（compat :is()×3 → 設計 css :is()×3 → 行內衍生 ×4 class）的完整教戰收錄在 `od-elementor-parity-pipeline` skill 的 2026-08-18 節——建置前先讀那節，不要重新發明。
4. **動畫共用一份檔**：設計源的結構型選擇器（nth-child／>div 鏈）要在「設計端」改成 marker（data-od-id＋CSS 變數 delay），讓靜態版與 Elementor 版共用同一份動畫 CSS/JS；Elementor 端用 Pro `_attributes` 補 marker。
5. 遠端站（無本機 WP）可整條走 MCP（execute-php／upload-link），Fluent Forms 用「複製既有表單再剪欄位」最快。營運坑（opcache、sandbox .crashed、lazyload 截圖）同見 pipeline skill。

## 中文斷行驗收標準（你 2026-08-20 定案，所有頁面交付前必過）

**標準：任何一行都不可以只剩單一個字，也不可以留下不成句的殘詞。**
具體是三條，缺一不可：

1. 最後一行不得只有 1-3 個中文字（例：標題斷成「…創作AI音樂最高效方」／「法，」）。
2. 任何一行不得 ≤3 字（例：清單前導符號「★」自成一行、「學費、」自成一行）。
3. 不得在詞中間斷（例：「免/費分享？」「成/為」「機/會」）——這條比前兩條優先，
 為了消掉孤字而把片段合併到過長，反而會製造詞中斷行，是負分。

### 機械做法（照抄即可，不要自己發明）

把文字依標點切成子句、每個子句包 `<span class="線上課程型客戶站-seg">` 並設 `display:inline-block`，
瀏覽器就只會在子句之間換行。關鍵在三個參數與兩個例外：

- **合併門檻**：任何 <8 字的片段往鄰居併，但**併完的上限要跟著容器寬度走**：
 `上限 = clamp(8, 16, floor(容器寬 / 字級) - 2)`。
 只設下限不設上限是實測過的錯誤：門檻拉到 8 而不設上限時，窄容器（卡片、手機）
 的長片段會在內部隨便斷，缺陷數從 4 個變成 18 個，還出現「免/費分享？」這種詞中斷行。
- **不要強制把最後一段併回去**（試過、退回了）：孤字尾行確實是最後一段造成的，
 但強制併會讓最後一段變長、在片段內部再斷一次，又生出新的短尾行
 （實測 plan4 1440px 從 0 個變成 2 個）。尾行問題交給 `text-wrap:pretty` 與文案。
- **收斂會停在某個數字，這是正常的**：機械分段沒辦法在所有寬度都歸零。
 本案收斂到 plan4 0/0/0/8、sign4 3/4/9/4（1440/1024/768/390），
 剩下的多半是專有名詞（Spotify）、驚嘆句尾（歌曲！）、清單前導符號。
 **再往下要改文案或該區塊字級，那是業主的決定，不要自己動內容。**
- **`text-wrap:pretty`** 同時套在 `.線上課程型客戶站-seg` 與所有標題／段落，讓引擎自己再避一次短尾行。
 注意 inline-block 片段之間的斷行**引擎管不到**，所以這條是補強不是主力。
- **超短獨立文字節點不切**：像「★ 」這種前導符號常常自成一個文字節點，包成 inline-block
 就一定掉一行。<4 字的單一片段不包 span，並把結尾空白換成 ` ` 黏住後面的字。
- **`background-clip:text` 的節點一律跳過**（漸層字）。切成 inline-block 子節點後漸層
 不再被文字裁切，整段字會消失只剩色塊。切之前從文字節點往上檢查 computed style。
- **內容保持純文字**：不要把 `<span class="nowrap">` 這類結構寫進 heading/text 的內容，
 你 是在 Elementor 面板裡改文案的，寫死斷行等於把版面鎖住。

### 驗收（不是看截圖，是量）

用字元級 Range 量測還原每個標題／段落的實際行，統計違規元素數，
**四個寬度（1440 / 1024 / 768 / 390）都要 0** 才算過。
可重用腳本：`~/Documents/線上課程型客戶站 線上課程型客戶站文創行銷/elementor建置工具/qa/lines.js`
（貼進 `qa-measure.mjs --eval` 執行，回傳 `{bad, items[]}`）。
改動前先量一次原始頁當基準——本案原始頁在四個寬度分別有 2 / 11 / 19 / 11 個違規，
不是「原本很好被我改壞」，是原本就有，收斂到 0 才是交付標準。

### 量測陷阱二：`vertical-align` 造成的假違規

字元級 Range 掃描是用 y 座標分行的。`★ <span class="線上課程型客戶站-seg">…</span>` 這種
「純文字 ＋ inline-block 片段」並排時，兩者基線不同 → y 差一兩個 px → 掃描器判成兩行，
回報「★ 單獨一行」。**同一行的假違規只能靠截圖確認**，不要為了消掉它去改版面。
判別法：該元素寬度遠大於文字寬度卻仍回報多行，先截圖看。

### 單字元文字節點不可跳過（2026-08-23）

斷行腳本常見的 `if(node.nodeValue.trim().length>1)` 過濾會漏掉「★ 」「※ 」這種
前導符號自成的文字節點——漏掉就吃不到「把尾端空白換成 `\u00A0`」的處理，
符號會被後面的 inline-block 片段擠成真的單獨一行。門檻要用 `>0`。

### 長文案被做成 button widget 時也要斷行（2026-08-23）

斷行腳本通常會排除 `button, .elementor-button`（避免切壞按鈕文字）。
但 你 的頁面常把整段稀缺說明做成帶 icon 的 button widget，排除掉就會出現
「教學品／質」這種詞中斷行。規則：`.elementor-button` 內文字去空白後 **超過 24 字**
就視為段落，照常斷行；選擇器要另外加上 `.elementor-button-text`。

### 量測陷阱：先確認被量的內容真的看得見

頁面若有「倒數計時前先隱藏下方區塊」這類閘門，掃描器只會量到沒被隱藏的那一小塊，
然後回報一個很漂亮的 0。本案就這樣誤判過一輪。量之前先確認：
可見區塊數／頁高與正常瀏覽時一致（例如手動加上解鎖 class 再量）。

## 圖片減重（2026-09-01 制度化，你 指示傳承；Claude 與 Codex 一體適用）

**教訓**：線上課程型客戶站 sign4 頁曾因單張 2.2MB PNG＋全頁圖片 4.6MB，在記憶體緊的機器上捲動閃白、載入緩慢；EWWW 外掛雖開 webp 但無損模式只壓 27% 且前台改寫吃不到 Elementor 輸出＝形同沒壓。

**規則（建頁/轉換時強制執行）**：
1. 任何要進 Elementor／uploads 的圖，先壓成 **WebP quality 80**；寬度超過 1600px 一律縮到 1600（LOGO/圖示縮到實際顯示尺寸）。指令：`magick in.png -resize '1600>' -quality 80 out.webp`（伺服器端用 Imagick 同參數）。
2. 交付前量整頁圖片總重：抓 HTML 內所有 img src 做 HEAD 加總，**目標 <500KB**，超過 1MB 不得交付。
3. 不可依賴站上的壓縮外掛「有裝」就當作「有效」——實測前台 HTML 是否真的載 webp 才算數。
4. WP 會自動產 PNG 尺寸變體進 srcset，只換主圖沒用；每個變體都要有同名 .webp，或在站上部署「存在同名 webp 即改寫」的輸出層過濾器（線上課程型客戶站 已有：`wp-content/novamira-sandbox/webp-srcset-cleanup.php` v4 全站版，可整份複製到其他 novamira 站）。
5. 深色設計的頁面必須給 html/body 明確深色 `background-color`——快速捲動時未繪製區域才不會閃白（參考 線上課程型客戶站 `dark-bg-antiflash.php`）。
6. **動畫 GIF 轉 webp 絕不可用伺服器 Imagick**（2026-09-01 事故實證）：行銷團隊 伺服器 Imagick 產出的動畫 webp 全數無法被 Chrome 解碼（靜態圖正常、僅動畫壞），頁面該區直接空白。正解：本機 `gif2webp -lossy -q 55 -m 4 in.gif -o out.webp`（漏 `-lossy` 會變無損反而更大），轉完**必須在真實瀏覽器 `img.decode()` 驗證**才可上站。截圖驗證時注意：內建瀏覽器面板隱藏或進場動畫未觸發時會拍到空白，那是假象——以 `naturalWidth`／decode 結果為準，配合捲動觸發後再拍。
