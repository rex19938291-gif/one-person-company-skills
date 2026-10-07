---
name: od-elementor-parity-pipeline
description: Execute a proven OD/HTML → Elementor-native conversion pipeline on 你的 local WordPress OR a remote WP reachable via Novamira-type MCP (execute-php/WP-CLI/upload-link) with 100% visual+animation parity, numeric rhythm QA, and production-ready JSON export. Use when the user asks to 還原/轉換 an Open Design or HTML page into editable native Elementor pages, wants 視覺與動畫 100% 還原, needs Elementor JSON 匯入檔 for a production site, or asks to QA-compare an Elementor build against a reference HTML. Complements the blueprint-level `html-to-elementor` skill (planning) — this skill is the EXECUTION layer: WP-CLI build scripts, Document API saves, theme-builder conditions, CDP QA harness, and import packaging. Trigger phrases: "OD 轉 Elementor 建置", "100% 還原", "Elementor JSON 匯入檔", "節奏比對", "parity pipeline".
---

# OD → Elementor Parity Pipeline

Battle-tested on 2026-07-06 (電商型客戶站 `claude-fable5-od-home`, final parity: full-page height diff +0.1% desktop / -0.2% mobile, per-section ≤2.8%). Reference implementation lives at
`<你的本機路徑>` — read its `scripts/` before writing new ones; copy and adapt rather than reinvent.

## Model-agnostic execution contract（任何 PM／執行模型都適用）

本 skill 會由不同模型輪替擔任 PM（Fable 5 / Opus 4.8）與執行者（Codex / GLM 5.2 / 其他 API 模型）。品質不能依賴模型的聰明程度，必須依賴下列機械規則 — 較弱的模型照抄也能穩定達標：

1. **每一輪開工前重讀本檔的 gate 數字**（兩階門檻、量測有效性規則），不要憑上一輪記憶。長 context 中段的模型（尤其外接 API 模型）最容易忘 gate。
2. **量測有效性由 harness 強制，不靠自律**：`qa-measure.mjs` 內建暖機（預設開）、`--wait-for <selector>` readiness 等待、0 blocks 時 exit code 2。exit 2 ＝該輪量測作廢，重跑；**任何模型都不得根據 exit 2 的輸出開處方**。
3. **每條處方必須是字面值**：selector＋屬性＋目標數值＋出處（reference 行號或量測數字）。「對齊 reference」「調整間距」這類自然語言處方一律退回重寫。這條對 GLM 類模型是硬性：它們對模糊指令的發散率最高。
4. **claim 之前先有證據**：回報「已修好」前必附本輪量測輸出（或無法量測時的 grep 證明＋原因）。任何模型宣稱未量測的 parity 數字＝立即退件。
5. **每完成一步就寫 checkpoint 到 TASK_HANDOFF.md**（改了什麼檔＋量測結果＋下一步），格式照 handoff-template。這讓額度中斷、模型切換、session 重啟都可無損接續 — 輪替使用多模型時這是唯一的共用狀態。
6. **有界批次派工**：給執行者的任務一律「N 步做完即停」，不開放式迴圈。步驟順序固定：量測有效性 → 全域修 → 逐區修 → 再量測 → 停。
7. **工具呼叫低信任預設**（外接模型適用）：派給 GLM／新模型的任務，PM 驗收時必須實際檢查檔案 diff 與量測輸出，不接受執行者的文字描述作為完成證據；`--resume-last` 類續傳指令失敗會偽裝成功，永遠先驗檔案再 rebuild。
8. **沙箱執行者的同等量測能力（共用 CDP 端點）**：執行者沙箱通常不能自己 spawn Chrome（症狀：Chrome「invalid code signature」、Chromium MachPort permission 錯誤 — 2026-07-08 C 客戶 輪 Codex 實測），但通常可連 localhost TCP（Codex 已實證可打 127.0.0.1 的 HTTP）。解法是把「啟動 Chrome」和「量測」解耦：沙箱外先 `scripts/cdp-endpoint.sh start`（headless Chrome，僅綁 127.0.0.1:9223，含 `--allow-file-access-from-files` 供 file:// reference 量測），執行者跑任何 harness 時帶 `--cdp-url http://127.0.0.1:9223`（`qa-measure.mjs` 亦讀 `QA_CDP_URL` env；專案 harness 依此模式支援 `--cdp-url`／專屬 env）。此模式下 harness 只建立並關閉自己的 tab，**絕不 kill 共用瀏覽器**；整輪量測結束由端點擁有者 `stop`。執行者遇到「量不了」時先檢查端點是否在跑（`cdp-endpoint.sh status`），不要嘗試自行啟動瀏覽器或繞道。

### 派量測給沙箱執行者的標準流程（PM 職責，2026-07-08 定案）

「以後派量測給 Codex，先開端點、執行者就能自主量測收斂」是**預設操作模式**，不是特例。PM（Claude／擁有沙箱外殼的一方）每次派量測型任務給沙箱執行者時：

1. **派工前先開端點**：`scripts/cdp-endpoint.sh start`（需 你 一次瀏覽器授權；同一量測輪內只需開一次）。確認 `cdp-endpoint.sh status` 回 200。
2. **派工 prompt 明載端點**：告訴執行者「端點已在 `http://127.0.0.1:9223`，用 `--cdp-url` 跑 harness，只開/關自己的 tab，別 kill 共用瀏覽器」。
3. **執行者自主收斂**：改檔 → 重建 → 帶 `--cdp-url` 重量測 → 讀報告 → 依 gate 開自己的下一步處方 → checkpoint 回 handoff。不需回頭等 PM 量測。
4. **端點生命週期歸 PM**：整輪（含執行者多次重量測）結束後 PM `cdp-endpoint.sh stop`。若執行者回報端點連不上，PM 重開，不由執行者啟動瀏覽器。
5. **額度前置檢查**：派工前查執行者兩個額度窗（`report-current-usage.js`）；週窗吃緊或歸零時，改由 PM 自己做或排程等恢復（見 Quota-aware bounded dispatch 節）。

## Architecture decisions (follow unless 你 overrides)

1. **Build route: WP-CLI + Elementor Document API**, not per-widget MCP calls. One PHP script per document (`wp --user=<admin> eval-file build.php`), rerunnable, deterministic, exportable. MCP is fine for small edits; full pages are 10x faster by script.
2. **Native-first**: every piece of content is a native widget (heading/text-editor/image/button/icon/icon-list/counter/star-rating/accordion/social-icons/nav-menu/container). HTML widgets ONLY for (a) interactions native Elementor can't do (e.g. crossfade scene carousel) and (b) script-only enhancer blocks (no visible markup). Count and document every exception.
3. **Styling: page/template-level Custom CSS** (Elementor Pro native feature, NOT an HTML widget) carrying namespaced classes (e.g. `cfab-*`) set via widget/container class settings. Copy the reference CSS values wholesale, retargeted to Elementor markup.
4. **Header/Footer: Elementor Pro Theme Builder** `elementor_library` posts with `_elementor_template_type` = header/footer, applied per-page via `_elementor_conditions = ["include/singular/page/<ID>"]` — never sitewide until approved. Regenerate Pro conditions cache after setting.
5. **JS behaviors** (reveal, typewriter, marquee, parallax, scroll-state nav): reproduce the reference JS verbatim-adapted in ONE script-only HTML widget per scope (page enhancer on page; nav scroll in header). Progressive enhancement: JS adds a marker class (e.g. `cfab-js` on `<html>`) and hidden-until-reveal CSS only applies under that class.

## Hard-won gotchas (violating these wastes hours)

- **Widget custom class key is `_css_classes` (underscore); containers use `css_classes`.** Wrong key = class silently missing.
- `Document::save()` silently returns false without an editing user → always `wp --user=<admin-login> eval-file`.
- Elementor widget background settings (`_background_*`) render on `> .elementor-widget-container` — give that inner div `width/height:100%` via CSS or backgrounds won't be visible.
- Elementor widgets default `width:100%` as flex items → side-by-side layouts need `>*{width:auto}` on the row, and horizontally-scrolling card rows need `.row>.e-con{flex:0 0 <w>px !important}` (container flex vars fight plain shorthand).
- **Elementor lazy-loads backgrounds**: `.e-con.e-parent:nth-of-type(n+2):not(.e-lazyloaded) *{background-image:none!important}` until its JS marks containers on scroll. Any headless/full-page screenshot MUST force-mark `.e-lazyloaded` on all `.e-con.e-parent` first (the bundled QA harness does this) — otherwise you chase phantom "missing background" bugs.
- Page template `elementor_header_footer`, page setting `hide_title: yes`. Section anchors via container `_element_id`.
- SVG icons as media attachments (enable `elementor_unfiltered_files_upload`) feed native Icon widgets and inline with `currentColor`.
- Reset body margin (`html,body{margin:0}`) and zero container default padding/gap on your namespaced classes; rhythm comes from explicit margins copied from the reference.
- If the site URL is a LAN IP, QA against that exact origin — other hosts break font CORS (FontAwesome/eicons) and queue large images.
- **`!important` does not beat specificity.** A convenience reset like `.ns-sec .e-con{width:auto!important}` (0,2,0) silently kills every later single-class override (0,1,0) even with `!important`. Write overrides at ≥ the reset's specificity (e.g. `.ns-sec .e-con.ns-card{...}`), or you get "fix applied but nothing changed" rounds.
- **Elementor's default 10px container padding** stays on every e-con you don't explicitly zero. On a content-dense page this compounds into +10–20% section height. Zero it on all pure-wrapper containers (`.ns-x .e-con.ns-wrapper{padding:0!important}`) and re-add intentional padding explicitly.
- **aspect-ratio cards collapse in grid**: a grid item whose children are all absolutely positioned and whose size comes only from `aspect-ratio` computes ~0 intrinsic width (rendered as a sliver). Give it `width:100%!important;justify-self:stretch`.
- **Data parity before CSS parity**: count repeated items (cards, FAQ entries, plan rows) against the reference data source first. A 12-vs-6 card mismatch can't be fixed by any amount of CSS.
- **Measure, never guess**: converge by comparing computed sub-block heights (this harness `--eval`) against the reference and copying the reference's literal values. Rounds of "tweak and hope" do not converge; every fix should cite a measured number.

## PM/executor split (Claude PM + any executor)

When an executor (Codex / GLM / other API model) executes and Claude verifies: executor sandboxes usually cannot reach the DB socket or a browser — Claude runs `wp eval-file` rebuilds and this harness, the executor edits files. Prescriptions must be literal (exact selectors + values + where to append); "align to reference" instructions without numbers do not converge — weaker executors diverge fastest on vague prescriptions. Send measured facts, receive file edits, rebuild, re-measure. PM always verifies the actual file diff, never the executor's summary.

## Pipeline stages

1. **Recon**: read the reference HTML fully (CSS vars, breakpoints, JS behaviors, asset paths). List sections and map each to native widgets. Check existing slugs/templates so nothing is overwritten.
2. **Setup script**: create page shells (+`-v2` on slug clash), `elementor_library` header/footer posts, WP nav menu, import SVG icons. Persist all IDs to a `state.json` consumed by later scripts. Idempotent.
3. **Build scripts** (one per document): element-tree helpers (`con()`, `w()` with `_css_classes` mapping, unique 7-hex ids), settings + custom CSS from a sibling `.css` file, saved via `documents->get($id)->save(['elements'=>…,'settings'=>…])`.
4. **Finalize script**: set `_elementor_conditions`, regenerate Pro conditions cache, `files_manager->clear_cache()`, export each document to Elementor template-library JSON (`content` + `page_settings` + `type`).
5. **Numeric QA**（節奏通道 — **必要但非充分**，見下方「視覺 100% 還原契約」）: run `scripts/qa-measure.mjs` (bundled here) against reference AND build at 1440 and 390 → compare per-section `top/height` tables. Fix every block >3% until full-page diff <0.5%. Typical culprits: wrapped flex rows, default paddings, button padding variants. **警告（2026-07-09 C 客戶 實案）：36/36 高度全過仍可能整套字型/配色沒搬 — 高度收斂後必跑 style-audit＋截圖親讀兩通道，否則不得宣告視覺 parity。**
6. **Visual QA**: harness `--shot` gives true full-page screenshots (CDP `captureBeyondViewport` + lazyload-marking). Crop-compare sensitive areas (hero, card grids, reviews, footer) desktop+mobile. Also verify interactions live: mobile burger, accordion, carousels, counters, scroll-state nav/FAB, no horizontal overflow at 360/390/768/1280/1440. **截圖必須被 PM「親眼讀過」才算跑過此關**（產出檔案≠驗過）；版面/顏色/圖片類缺陷（按鈕位置、區塊底色、孤立清單符號、圖片消失）只有這一關抓得到，任何 DOM/文字比對都會漏。
7. **Package**: `make-import-package.sh` pattern — zip of `templates/*.json` + all referenced assets at their original `wp-content/uploads/...` relative paths + `IMPORT.md` runbook (upload assets first so JSON URLs resolve; import templates; rebuild menu; remap popup IDs).
8. **Isolation check**: verify pre-existing pages still render their own header/footer and conditions are untouched.
9. **Handoff**: update the project `TASK_HANDOFF.md` (完成/待辦/風險/IDs/paths) per 你的 protocol.

## Bundled tools

- `scripts/qa-measure.mjs` — CDP section-rhythm metrics + full-page screenshots (Node ≥22, no deps). Usage:
 `node qa-measure.mjs --url <URL> --width 1440 [--height 900] [--selector '.sec'] [--shot out.png] [--eval '<js>'] [--wait 8000] [--wait-for '<selector>'] [--warmup false]`
 It force-marks `.e-lazyloaded`, supports async `--eval`, kills its own Chrome. Built-in validity enforcement: warms up the URL once before measuring (default on), waits on `readyState==='complete'` plus optional `--wait-for` selector visibility (max 30s) instead of trusting a fixed sleep, and exits with code 2 when 0 blocks matched — treat exit 2 as "measurement invalid, retry", never as data. Sandboxed-executor mode: `--cdp-url http://127.0.0.1:9223` (or `QA_CDP_URL` env) connects to an already-running shared endpoint instead of spawning Chrome; creates/closes only its own tab.
- `scripts/cdp-endpoint.sh start|stop|status` — shared headless-Chrome CDP endpoint (default 127.0.0.1:9223, `CDP_PORT` env to override) for executors whose sandbox cannot launch Chrome. Start it OUTSIDE the sandbox; harnesses connect via `--cdp-url`.
- `scripts/qa-style-audit.mjs` — 電腦樣式逐元素比對（視覺契約通道 2）：以文字配對 source↔build，只量最內層文字元素（自動跳過 wrapper 假差），比 font/size/weight/style/lh/ls/color/bg/align。`node qa-style-audit.mjs --cdp-url http://127.0.0.1:9223 --a <sourceURL> --b <buildURL> [--width 1440] [--max 60]`。內建 per-URL watchdog＋finally 關 tab（重頁不 hang 不漏 tab）。
- `scripts/qa-crops.mjs` — 定點 viewport 截圖（視覺契約通道 3 的審修迴圈用）：`node qa-crops.mjs --cdp-url … --url <buildURL> --out <dir> --find "文字1" --find "文字2"` → 每個文字錨點 scrollIntoView 後截一張 viewport 圖（不用 captureBeyondViewport，快且不 hang），給 PM 親讀。
- Reference build/export/package scripts: `<你的本機路徑>`

## Guardrails

Never touch production, existing pages/templates, or the static homepage without explicit approval. No public tunnels, no credentials in output. HTML-widget exceptions must be listed in the final report with reasons. Report the parity numbers honestly (per-section table), never claim unmeasured "100%".

## Executor self-review checklist（任何執行者：Codex / GLM / 其他模型，交付前逐項自檢，任一不過就先修再回報）

本清單來自實案退回記錄（2026-07-07 電商型客戶站 Phase 2/B），每一條都對應一次真實退件：

1. **內容值不可自創**：任何文案/選項/價格/名稱，必須逐字來自 SPEC 或 reference 原始碼，回報時附「值的出處行號」。（退件案例：表單方案選項自創名稱，與內頁真實方案不符）
2. **禁 mega-shortcode / 整版 markup**：loop item、single 範本、卡片一律原生元素樹＋欄位級動態（Dynamic Tags 或欄位 shortcode 僅作為文字內容）。「先守視覺」不是繞過可編輯性的理由。（退件案例：loop/single 用單一 shortcode 吐整頁）
3. **覆寫規則自查特異性**：新增的每條 override，確認特異性 ≥ 既有 reset（尤其 `.ns .e-con{...!important}` 是 (0,2,0)）。`!important` 不能補特異性差距。（退件案例：兩輪「修了沒效」）
4. **Elementor 文件四件套**：程式建立任何 elementor_library/popup 文件必設 `_elementor_edit_mode=builder`＋`_elementor_template_type`＋type term；popup 另需 `_elementor_conditions`（否則不載入）；新 CPT 記得 rewrite flush。（案例：範本與 popup 渲染空白）
5. **交付前自證**：除 `php -l` 外，列出「我改了什麼→預期哪個量測值變化→為什麼」；不能跑瀏覽器/DB 時，用 grep 證明規則存在於輸出物、用 reference 行號證明數值來源。
6. **回報格式**：改動點對照任務書編號逐條列（做了/沒做/理由），沒做的不可留白。

PM 對應義務：處方必附實測數字與逐字內容；退回時引用本清單條號，讓失誤可歸類、可追蹤。

## Typography QA (added 2026-07-07, C4 round)

- **Programmatic line-break scan beats screenshots**: run the harness with `--eval "$(cat typo-check.js)"` where typo-check.js walks headings/paragraphs, uses Range API per-character rects to reconstruct line boxes, and flags (a) last line with ≤1 CJK char (孤字尾行), (b) lines starting with CJK punctuation. Reference copy: `elementor-templates/claude-fable5-od-20260706/qa/c4/typo-check.js`. Exclude intentional label-value two-line pairs before prescribing.
- Fix order: `text-wrap:balance` (headings) → `<span class="ns-nowrap">` on tail phrases/label-colon groups (deterministic) → max-width tuning (last resort; re-measure rhythm after).
- Verify gate: re-scan to count=0 AND page rhythm drift ≤1% (text-wrap fixes must not shift section heights). If a page mounts a NON-branch template (e.g. site footer 28088 on the thanks page), its issues are out of scope — do not restyle foreign templates.
- **zsh does NOT word-split unquoted variables**: `for spec in "a b"; do set -- $spec` silently passes the whole string as $1 (loop appears to hang/fail). Use explicit function args or arrays.
- CDP full-page screenshots can hang on very tall pages (home@1440) in the viewport-grow path; the --eval path is unaffected. Prefer eval-based checks; screenshot only the pages that need visual proof.

## Editor-compatibility gotchas (2026-07-07, G-round)

- **NEVER place a widget at the document ROOT level** (directly in the `$elements` array). Front-end renders it fine, but the Elementor editor's preview view only resolves container/section children at root — a bare root widget makes `buildChildView` throw `TypeError: T is not a constructor` and the editor hangs at LOADING forever. Always wrap script-only enhancer HTML widgets in a container (`display:contents` keeps zero layout impact).
- **Third-party `elementor/widget/print_template` filters can kill the editor after an Elementor upgrade**: softlite-io-integration's button-template str_replace broke against Elementor 3.30's button template (SyntaxError in Marionette compileTemplate → same eternal-LOADING symptom). Diagnose by iterating all `script[type=text/template]` through `Marionette.TemplateCache.prototype.compileTemplate` to find the one that fails; counter with a mu-plugin that removes the offending filter by scanning `$wp_filter` (don't edit the third-party plugin).
- Debug order for eternal-LOADING: console error? → template compile scan → per-child `getPreviewView().getChildView(model)` scan (finds bad root elements) → plugin bisect. `elementor.loaded` can be `true` while the overlay never hides — the crash is in preview render, not asset loading.
- `codex-companion task --resume-last` can fail with "No previous Codex task thread was found" — the dispatch LOOKS successful but does nothing. Always verify the files actually changed before rebuilding; re-dispatch as a fresh task on failure.

## Measured-loop iteration protocol (2026-07-08, C 客戶 round)

本節來自 C 客戶 HTML → 行銷團隊 Elementor 嚴格 parity 輪（Claude 當 PM/QA、Codex 執行、以 TASK_HANDOFF.md 為共用白板）。每條都對應一次實際踩坑或一次有效收斂。

### Measurement validity gate（先驗證量測，再驗證頁面）

- **固定 waitMs 在冷啟動本機 WP 上會產出無效量測**：本機 restore 冷請求 6–11 秒，harness 固定等 7 秒曾量出 build=1519px vs source=10374px、0 個 section 對上（同 URL 手機視口卻正常 — 這種「同 URL 不同視口一好一壞」是時序 flake 的簽名，不是 CSS bug）。
- 規則（自 2026-07-08 起由 harness 內建強制：暖機預設開、`--wait-for` readiness 等待、0 blocks → exit 2）：(a) 量測前先對每個 URL 暖機一次丟棄；(b) 等 readiness 條件而非固定秒數；(c) 任何比對 0 matched rows／exit 2 一律視為無效、重跑一次；**絕不根據無效量測開處方** — 否則會去追一個不存在的 -85% 幻影差距。

### Systematic-before-per-section triage（先全域後逐區）

- 讀報告先看「方向與量級的分布」：多個 section 同方向、相近量級偏移（例：6 個 section 在雙視口一致比 source 矮 30–46%）＝全域 spacing 對映缺失（source 的 `py-12/20/24` 等 utility class 沒對映到 Elementor section padding）。處方是**在 importer/build script 做一次全域對映、量一次**，預期整批一起收斂 — 不要逐 section 慢慢戳。
- 反方向的離群值（例：hero +66% 過高，多半是圖片尺寸或欄位堆疊）是另一種病因，**留到全域 pass 之後單獨診斷**，不要混在同一輪。

### Two-tier acceptance gates（門檻分兩階）

- 結構收斂階段用粗門檻：每個可見 section |heightDiffPct| ≤10%（1440x900 與 390x844 雙視口）、整頁 ±5%、無橫向溢出、widget audit 維持 `html=0`。
- 粗門檻全過後才進本 skill 原有的精修門檻（區塊 >3% 逐一修到整頁 <0.5%）。互動 QA（modal/reveal/lightbox/表單送出）在 rhythm 收斂後跑一次即可，不必每輪重跑。

### Quota-aware bounded dispatch（額度感知的有界派工）

- 派重活（Browser/CDP 迴圈）前先查執行方**兩個窗**的額度：5 小時窗 90% 時週窗可能只剩 2% — 昨晚的擋單就是這樣來的。
- 週窗吃緊時把派工收緊成**有界 N 步批次**（修 harness → 量測 → 一個全域修正 → 再量測 → 停），明說「做完即停、不要開放式迴圈」，並要求**每完成一步就把 checkpoint 寫回 TASK_HANDOFF.md** — 中途被額度擋掉時已完成的步驟不白跑，任何 session 可無損接續。

### PM guidance placement（指導落點）

- PM 的指導寫進 handoff 的「待 Codex 執行」區：編號條列、每條=「量測事實 → 字面處方 → 驗收數字」，並標明執行順序（量測有效性 → 全域修 → 逐區修）；派工 prompt 只放一段短指針指向該區，不重複內文。
- 同輪順手同步三份狀態：TASK_HANDOFF.md、任務卡（blocker/next step/restart prompt）、CODEX_TASK_INDEX.md — restart prompt 直接內嵌門檻數字與執行順序，讓任何新對話一貼即可開跑。
- ~~待辦：readiness-wait 補進 `scripts/qa-measure.mjs`~~ 已完成（2026-07-08）：`--wait-for`＋暖機＋exit 2 無效量測判定皆已內建。

### Sandbox-equivalent measurement（2026-07-08 追加，源自 Codex step-2 環境阻擋）

- Codex 沙箱跑 `qa-reference-parity.mjs` 時無法啟動任何瀏覽器（系統 Chrome 簽章無效、快取 Chromium MachPort 權限錯誤）→ 量測從此走**共用 CDP 端點**模式（契約規則 8）：沙箱外 `cdp-endpoint.sh start`，harness 帶 `--cdp-url`。
- 兩支 harness 已支援：skill 的 `qa-measure.mjs`（`--cdp-url`／`QA_CDP_URL`）與 C 客戶 專案的 `qa-reference-parity.mjs`（`--cdp-url`／`C 客戶_QA_CDP_URL`）。新專案 harness 一律照抄此雙模式（spawn 或 connect-existing）。
- 端點生命週期歸沙箱外的一方（你 或 PM）管理：量測輪開始前 start、結束後 stop；執行者只建/關自己的 tab。

## 視覺 100% 還原契約（2026-07-10 定案，源自 C 客戶 視覺重開輪 — 高度節奏 ≠ 視覺還原）

實案教訓：C 客戶 輪曾同時達成「36/36 section 高度 ±10% 全過＋互動 QA 全過」，但成品完全沒載 source 字型、沒定義任何 `:root` token，配色/字體整層缺失，你 一眼退件。**節奏數值只是四通道之一；缺了本節規則，任何模型都會做出「高度對了、長相不對」的頁面。** 本節為機械規則，弱模型照抄也能達標。

### A. Design-system-first（建置期硬規則，先於一切逐區修）

1. build 的第一步就把 source 設計系統**逐字**搬進去：① Google Fonts link 原句 — 用 mu-plugin `wp_enqueue_style` 掛載（比 Elementor page CSS 內 @import 可靠；page CSS 頂端仍保留 @import 當雙保險，@import 必須位於所有規則之前）；② 完整 `:root` token 區塊（顏色/漸層/陰影/字型/type-scale 一個不漏）；③ base 規則（body/h1-h5/p/a）scoped 在頁面 wrapper class 下；④ 所有 widget 層 typography/color 一律採 token 對應的 source 字面值 — 禁止近似色、禁止留 Elementor/佈景預設字型。
2. 元件級重現：source 每一種元件樣式（eyebrow/kicker、section-title、card-title、testimonial-title、編號清單、小註/免責、深色區文字、FAQ toggle、CTA 按鈕⋯）各配一個 namespaced class＋一條照抄 source 值的規則 — **靠全域 base 級聯「順便蓋到」是已被否證的路徑**。text-editor widget 裡的裸 `<p>`/`<ul>` 沒 class 就回 builder 的 HTML 字串補 class，否則永遠無法精準 target；裸 `<ul>` 會吃預設 disc 圓點（置中卡片上圓點孤立在最左）— 必須顯式 `list-style:none`。
3. Elementor 蓋寫力學（override 塊為何必勝）：Elementor per-widget typography CSS **不帶 !important** → 元件規則放 page CSS 末端、高特異性＋!important 即穩定獲勝。規則必須打到**內層實際渲染元素**（`.elementor-heading-title`、`.elementor-widget-container p`）— 只打 widget wrapper class 無效（wrapper 不承載文字樣式）。

### B. 四通道 QA（缺一不可；宣告 parity 前四關全過）

1. **節奏**（qa-measure／專案 harness）：高度收斂 — 必要非充分。
2. **電腦樣式比對**（`qa-style-audit.mjs`）：以文字配對 source↔build，**只量「最內層承載文字」的元素**（子元素含相同文字＝wrapper，跳過）。wrapper 假差是實測過的大坑：C 客戶 曾因掃到 wrapper 虛報 205/305 項差異、差點整輪誤修。門檻：真差 ≈ 0（font/size/weight/style/lh/ls/color/bg/align）。
3. **截圖親讀**：唯一能抓版面/顏色/圖片缺陷的通道（按鈕位置、區塊底色、孤立清單符號、圖片消失）。審修迴圈用 `qa-crops.mjs` 定點 viewport 圖（快、不 hang）；全頁圖留給交付。**PM 沒讀過圖＝這關沒跑。**
4. **斷行掃描**（typo-check）＋互動 QA：rhythm＋樣式收斂後各跑一次。
最終 gate 永遠是 你 肉眼；四通道只是把一次過的機率拉滿，不得以通道數據代替人工 sign-off 宣告「100%」。

### C. 全頁截圖強韌化（capture-hang 實測解法）

- `captureBeyondViewport` 在寬幅重頁（1440×10k+、含 iframe）會 hang，且**時好時壞**：① 量測完成後、截圖前把所有 iframe 換成同尺寸佔位 div＋暫停 video（版高不變，parity 數字不受影響）；② 截圖 timeout 走環境變數（勿硬編 20s）；③ 超大 bitmap 用 deviceScaleFactor 0.5/0.75 縮圖 — **同組 source/build 必須同 scale 才公平**；④ 提供 `--only <page>`／`--only-viewport` 過濾，補截不清掉已成功的圖；⑤ **截完必查輸出檔 mtime** — capture 逾時會默默留下舊檔，一不查就把「修正前」的圖交出去（實案發生過）。
- 鎖網域 Vimeo 在 localhost 401 → compositor 卡死＋console 噪音：環境限制非缺陷，截圖時中和、報告註明。
- macOS 無 `timeout` 指令（`gtimeout` 或 node 端 watchdog）。audit/probe 類 harness 必須內建 per-navigation 硬逾時＋finally 關 tab — 否則重頁一 hang 就零輸出＋漏 tab（`qa-style-audit.mjs` 已內建）。

### D. 委派配方增補（已驗證✅／已否證❌）

- ✅ **跨目錄委派**：companion 把 workspaceRoot 綁在「發起 session 的 cwd」且無 `--cwd` 旗標 → 在 `~/.codex/config.toml` `[sandbox_workspace_write]` 加 `writable_roots=["<work-package 目錄>"]`（DB 留在 root 外 → rebuild 仍 PM-only）。config 免重啟，per-spawn 重讀。
- ✅ **批次大小 × effort**：單頁/單主題 bounded＋`--effort high` → 2.5-6 分鐘穩定完成；❌ 12 元件大批次在預設 xhigh 下 hang（同一 executor）。派工詞必含「做完即停、禁開放式迴圈」。
- ✅ **harness 不可靠時**：PM 把量測值字面寫進派工、**明令「禁跑該 harness」**；❌ 讓 executor 對 flaky harness 自量（會卡整輪）。
- ⚠️ Codex 背景 job 完成**不會**通知 PM：PM 自掛輪詢。進度 log 靜默 ≠ 掛掉 — 先查目標檔 mtime/diff 再判生死；hang 掉但已寫入的部分成果可先 rebuild 搶救。重複 Resume 撞 job 的 failed 無害，`status --all` 找真 job。
- PM 派工前自查：executor 寫得到目標檔嗎（smoke test 一個 write）？endpoint 通嗎？quota 兩窗夠嗎？三項任一不確定就先驗再派 — 每次盲派失敗浪費 15-30 分鐘。

### E. 交付前驗收清單（每輪逐項，任一不過先修再報）

- [ ] `:root` token＋字型 link 存在於**實際供應**的產出（fetch 渲染頁與 post-*.css 驗證，不只 grep importer 原始碼）
- [ ] style-audit 真差 ≈ 0（wrapper 假差已用最內層規則排除）
- [ ] PM 已親讀全頁圖／關鍵 crop：按鈕位置、區塊底色、清單符號、圖片齊全
- [ ] 所有截圖 mtime 屬於本輪（無逾時殘留舊檔）
- [ ] 同組 source/build 截圖同 scale
- [ ] html=0、rebuild JSON 正常、DB 本輪備份存在
- [ ]你指過的每一個缺陷都有對應的截圖證據證明已修

## WP site-ops playbook (2026-07-12, header/theme round — applies to ALL edits on 你的 WP stack: Blocksy + Elementor Pro + WP Rocket)

重建管線順序、驗證陷阱、Blocksy sticky 失效、雙模態 header、WP Rocket delay-JS、可編輯文字與 CJK 斷行、選單權限、Loop-grid 分頁、電商型客戶站 字級 8 級制、本機 php -S Fatal —— 全部在 `references/wp-site-ops-playbook.md`，改 你 的 WP 站之前先讀那一份。

### SEO 寫進建置腳本（2026-07-13）
Rank Math SEO 不另設獨立步驟——各頁 meta title/description 直接 append 在該頁建置腳本末尾（`update_post_meta($pid,'rank_math_title'/'rank_math_description',…)`，接在 cfab_save_document 之後）；CPT 全域標題格式（`rank-math-options-titles` 的 `pt_<cpt>_title`/`_description`）寫進 01-setup。這樣重建/遷移自動帶 SEO，且值就近好維護。CPT 格式用短品牌結尾，勿用 %sitename%（會展開超長站名被 Google 截斷）。

## 遠端建置路線（MCP／SSH-only）（詳見 `references/remote-build-routes.md`）

Novamira 類 MCP 與 SSH-only 兩種遠端環境的完整教戰：機械轉換器規則、Elementor 4.x 特異性三層架構、干擾清單、mu-plugin 橋接、視覺驗收與 parity 量測。

## 頁面自訂 CSS／widget 硬坑、CJK 斷行、圖片減重（詳見 `references/page-css-widget-gotchas.md`）

HTML widget 就地換成原生元素樹時踩過的十一個硬坑（頁面 CSS 選擇器不能跨行、widget CSS 殘渣吃掉第一條規則、
heading 過 kses 剝掉漸層字、`:first-child` 因包裝層失效、boxed 容器 `--content-width` 鎖死響應式、
button 字級要打 `.elementor-button-text`、上傳型部署權杖過期不報錯、`!important` 壓掉 `@media`、
容器用 `css_classes` 而 widget 用 `_css_classes`、Blocksy 動態 CSS 要兩個 request）、
`線上課程型客戶站-cjk-wrap` 不可切的節點，以及圖片一律 WebP q80／整頁 <500KB 的減重規則。

## Elementor 範本 → Blocksy 原生 header/footer（詳見 `references/blocksy-native-header-footer.md`）

header/footer 從 Elementor theme-builder 改為佈景主題原生的完整做法：Blocksy 資料結構、三個會覆寫你設定的元件欄位、動態 CSS 快取重生、樣式覆寫層與收尾檢查。
