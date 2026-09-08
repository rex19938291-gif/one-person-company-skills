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

### The ONLY safe rebuild pipeline (violating the order = stale-cache ghost bugs)
Any Elementor template/page rebuild MUST run these steps in this exact order:
1. `wp --user=<admin> eval-file <build-script>.php` (Document::save needs an editing user)
2. `wp --user=<admin> eval '\Elementor\Plugin::$instance->files_manager->clear_cache();'`
3. `curl -s -o /dev/null <a page using the template>` ← regenerates post-CSS files BEFORE page cache snapshots them
4. `rm -rf wp-content/cache/wp-rocket/* wp-content/cache/min/* wp-content/cache/background-css/*` ← ALL THREE dirs; skipping `min/` means pages keep loading the old minified bundle
5. warm-hit the pages again.
Why: Elementor re-save assigns NEW element IDs; Rocket-cached old HTML + regenerated new CSS = selectors match nothing → layout collapses to defaults (`--display` vars empty → e-con renders inline/column). `rocket_clean_domain()` alone misses non-default host variants (Tailscale IP) — always `rm` the dirs.

### Verification traps (each one produced a false conclusion this round)
- **Sticky/fixed/scroll checks: `window.scrollTo` is a NO-OP on this stack** (body is the scroll container). JS "navTop=0 after scrollTo" is fake data. Verify with REAL mouse-wheel scroll (browser automation `scroll` action) + screenshot/zoom as evidence.
- **Computed-style reads race CSS transitions** (`transition: color/background .25-.35s`): after toggling a class, wait ≥400ms before `getComputedStyle`, or you read the pre-toggle value.
- **Browser memory cache poisons same-URL re-fetches**: after a regen the `?ver=` may not change within the same second; a tab that saw the old bytes keeps them forever. Verify with a cache-buster query param on the PAGE and `curl` the exact versioned CSS URL to compare bytes.
- **The site sends CSP that blocks injected `<style>`** — style-injection probes silently do nothing; test rules by editing the source file through the pipeline instead.
- **`cssText`/stylesheet greps**: browsers normalize `#627CBA` → `rgb(98,124,186)`; grep for both forms.
- **Duplicate menu DOM**: Elementor nav renders main + dropdown clones — `querySelector` may hit the hidden clone; scope with `.elementor-nav-menu--main`.

### position:sticky is DEAD on this theme (Blocksy) — design around it
`#main-container{overflow-x:clip}` + `body{overflow-x:hidden}` make every descendant `position:sticky` inert (Chromium). Rules:
- Site-wide pinned header ⇒ `position:fixed` + `body{padding-top:<navH>}` (immune to ancestor overflow). Never sticky.
- Element-level pinning (sidebars, order cards) ⇒ unlock per page-type first: `body.single-post, body.single-post #main-container{overflow-x:visible}` then `position:sticky;top:<navH+24>px;align-self:flex-start`, and afterwards assert `document.documentElement.scrollWidth<=clientWidth` (no horizontal overflow reintroduced).

### Dual-mode global header pattern (hero-transparent / solid-white)
- Hero detection: JS `document.querySelector('.cfab-hero,.cfab2-hero,.cfab2d-detail-hero')` + CSS `body:not(:has(<same list>))`. Keep BOTH (JS adds `body.cfab-nav-offset` for engines without :has; CSS covers pre-JS paint since Rocket delays JS until first interaction).
- Adding a new hero-style page ⇒ its hero container class MUST be appended to both lists, or the page gets the solid header.
- Elementor kit default container row-gap (20px) inflates wrapper containers that hold a hidden script widget → `gap:0!important` on the nav container; verify nav height (64px) and per-child vertical centering.
- Two-state styling lives on `.cfab-nav.scrolled` AND the solid-mode selectors — every visual token (bg, link color #595757, active #627CBA, CTA solid #004298, no hairline in shadow) must be written to BOTH.

### Blocksy theme specifics
- Customizer settings live in `theme_mods_<stylesheet-folder-name>`; a local child theme MUST use the exact prod folder name (`blocksy-child`) to read prod's 336 mods from a cloned DB.
- Blocksy compiles mods to `wp-content/uploads/blocksy/css/global.css`; after theme switch / palette anomalies (orange defaults instead of brand blue) delete that dir and hit a page to regenerate. Verify `--theme-palette-color-1` in the regenerated file.
- Blocksy yields its header/footer to Elementor Pro theme-builder locations (no double header) — but verify `header#header.ct-header` is absent after applying a location template site-wide.
- lrm login plugin: local port-suffixed hosts trip its domain check alert → mu-plugin `add_filter('lrm/need_validate_domain','__return_false')` LOCAL ONLY.

### Prod-parity method (when 你 says "跟原始/正式站一致")
Never eyeball: load the prod page, read computed values (font-size/weight, colors, element tops, gaps), copy the literal numbers into the build script, rebuild via the pipeline, then measure local the same way. Match content-start positions by the GAP below the header (prod header bottom → first content), not by absolute viewport offsets — different header heights make absolute matching wrong.

### Editor-editable text contract + CJK line-breaking (2026-07-12, 你 rule — supersedes span-chunking)
**你 edits copy in the Elementor panel (WYSIWYG). Text content in widgets must stay PLAIN: only `<br>` and `<b>/<em>` allowed.** Never bake `<span class="nowrap">` chunking or structural markup into heading/paragraph content — it locks line breaks away from the editor. (nowrap spans are acceptable ONLY for immutable tokens like `2 戶成團`/`95 折` numbers-with-units, and sparingly.)
Achieve mobile break quality WITHOUT touching content:
- `text-wrap:pretty` on CJK heading classes — the engine itself prevents single-character orphan lines (「中」 alone) no matter what the editor later types. Note it must be declared AFTER any site-wide `text-wrap:balance` rule of equal specificity, and `balance` is inert on headings containing `<br>` anyway.
- Tune the font-size clamp floor (e.g. `clamp(22px,5.9vw,40px)`) so each `<br>` segment fits 1–2 lines at 375px; adjust the floor, not the markup.
- Verify at 375px by walking text nodes with per-char Range rects (grouping by line top) — screenshots alone can miss 1-char orphans.
- If a specific break is still ugly, fix the COPY (with 你) or the font size — not with spans.

### Header account dropdown = WP-menu-driven + Nav Menu Roles (2026-07-12, 你 rule: menus must be editable in 外觀→選單)
Never hardcode nav/account links in an HTML widget. Pattern proven on 電商型客戶站:
- Main nav: Elementor Pro `nav-menu` widget bound to a WP menu slug — already editor-editable; keep design via scoped CSS on the widget wrapper class.
- Account dropdown (我的帳號): a small **production-deployable** mu-plugin (`電商型客戶站-header-account-menu.php`) registers `[cfab_account_menu]` which wraps `wp_nav_menu(['menu'=>'cfab-account-menu','container'=>false,'menu_class'=>'cfab-haccount-list','depth'=>1,'fallback_cb'=>'__return_empty_string','echo'=>false])` inside the original `<details class="cfab-haccount">` markup; header build script uses a `shortcode` widget (settings key `shortcode`), NOT an html widget.
- Logged-in/out variants: Nav Menu Roles plugin — set item meta `_nav_menu_role` = `'in'` / `'out'` (or array of roles) + `_nav_menu_role_display_mode` = `'show'`. Create items via `wp_update_nav_menu_item` then `update_post_meta`.
- lrm login popup triggers on `[class*="lrm-login"]` (delegated) — the class on the menu item `<li>` works; no need to class the anchor.
- CSS additions: flatten the ul (`.cfab-haccount-list{list-style:none;margin:0;padding:0}`) and make anchors `display:block`; existing `.cfab-haccount-menu a` styles then apply unchanged.
- Verify both states WITHOUT browser login: `wp eval 'echo do_shortcode("[cfab_account_menu]"); wp_set_current_user(username_exists("<admin>")); echo do_shortcode("[cfab_account_menu]");'`. Page cache (WP Rocket) serves logged-out HTML only; logged-in users bypass it, so the dynamic variant renders correctly.

### WP Rocket delay-JS verification trap (2026-07-12)
`wpr_delay_js`（看 `<meta name="generator" ... data-wpr-features>`）會把所有內嵌 script 延到**真實你互動**才執行。用 CDP/javascript_tool 派發的 `change`/`Event` 不會觸發載入 → 頁內互動 JS（篩選、reveal）看似全掛。判別法：手動 `eval` 同一段 script 文字，若立即正常＝Rocket 延遲假象，不是程式壞。驗互動功能時先派發一次 `window.dispatchEvent(new MouseEvent('mousedown'))` 觸發 Rocket 載入延遲腳本、等 1-2 秒再測；或以 `?nowprocket=1` 開頁繞過 Rocket。

### Loop-grid 客端分頁＋動態計數（2026-07-12）
- 卡片一多不要用 Elementor loop-grid 伺服端分頁——會跟客端篩選互斥（篩選只看得到當頁 DOM）。正解：loop-grid `posts_per_page` 拉大一次輸出全部，enhancer JS 統一做「篩選→切頁」：run() 先算 matched 陣列，再以 `matched.slice(page*N,(page+1)*N)` 顯示、其餘加 off class；頁碼 UI 由 JS 生成插在 grid 後（換頁 scrollTo 記得同時打 window 與 document.scrollingElement，此站 body 是捲動容器）。翻頁顯示的卡要補 `.in`（reveal 類）否則透明。
- 標題裡的統計數字用 shortcode（如 `[電商型客戶站_community_count]`＝published community 數）——此站 heading 元件經 mu-plugin 的 render_content filter 會跑 do_shortcode，數字隨資料自動更新、後台仍可編輯文字。
- php -S 單執行緒 dev server 可能被逾時外連請求連帶終止（log 見 Requests/Curl.php Fatal）→ 站台 000 全掛時先 `lsof -iTCP:8108` 確認，重啟：`cd 電商型客戶站-wp-local && nohup php -S 0.0.0.0:8108 -t public >> php-server.log 2>&1 &`。

### text-editor 內容只剩單一 shortcode 時 <p> 會被剝掉（2026-07-13）
WP `shortcode_unautop` 會把「整段只有一個 shortcode」的 `<p>` 拆掉 → 掛在 `.xxx p` 的字級/顏色規則全部落空、文字變預設大字。對策：這類動態文字的 CSS 一律同時寫 `.xxx p, .xxx .elementor-widget-container`；或在 shortcode 前後保留實字避免 unautop。

### Sticky 卡片視窗貼合縮放（2026-07-13）
- 縮放 sticky 卡片用 `zoom` 細階梯（依視窗高度 media query），**不要用 transform:scale**——reveal 類（.cfab2d-reveal）自帶 transform 會互相覆蓋；也不要 JS 動態設 inline top+zoom（Chromium sticky 互動不穩）。
- 階梯計算：先實測一檔（如 z=.78 時 sticky top 實際值），推出幾何式（此站 909z ≤ vh-8）再展開檔位。
- **驗 sticky 的陷阱**：捲超過 sticky 容器（主欄）底部後卡片會停靠容器底、隨頁面上移——這是正常行為不是 sticky 壞掉；要在容器範圍內取樣。另此站 scroll-behavior:smooth，設 scrollTop 後要等 700ms 再量。

### 電商型客戶站 內頁字級 8 級制（2026-07-13 你 定案，之後新區塊一律取用）
12.5（說明/章標/眉標）｜14（小字/次要按鈕）｜15（內文）｜16（項目標題/FAQ/CTA）｜18（強調數字/副價）｜24（區塊小標/倒數）｜32（區塊大標）｜40（主價格/裝飾編號）。hero 展示型 clamp 除外。改字級鐵則：grep 全檔「所有」出現點（基礎+media+檔尾 !important 覆寫段）一次改齊；live 驗證前先改 Elementor post CSS 的 ver 參數（全站固定值，瀏覽器不會自動重抓）。

### 本機 php -S Fatal（Curl 30s 死鎖）根因與根除（2026-07-13）
- 症狀：前台白屏 Fatal「Maximum execution time 30s exceeded in Requests/src/Transport/Curl.php」、curl 回 000、站台卡死。
- 根因：WP Rocket（Remove Unused CSS／預載）發「站台自我 curl 自己」的 loopback；`php -S` 單執行緒回不了自己的請求→死鎖 30s。正式站 PHP-FPM 不會。
- 根除：mu-plugin 加 `pre_http_request`（priority 1）短路——`is_local_site() && is_internal_url()` 時立即回 `new WP_Error`，讓 loopback 最佳化在本機略過；外部 timeout cap 收到 1.5s。本機限定檔、勿部署。
- 判別：`curl ?nowprocket=1` 快（繞 Rocket）、一般網址慢/Fatal＝Rocket 快取生成路徑的自我 loopback。重啟：kill 8108 listener 後 `nohup php -S 0.0.0.0:8108 -t public`。

### SEO 寫進建置腳本（2026-07-13）
Rank Math SEO 不另設獨立步驟——各頁 meta title/description 直接 append 在該頁建置腳本末尾（`update_post_meta($pid,'rank_math_title'/'rank_math_description',…)`，接在 cfab_save_document 之後）；CPT 全域標題格式（`rank-math-options-titles` 的 `pt_<cpt>_title`/`_description`）寫進 01-setup。這樣重建/遷移自動帶 SEO，且值就近好維護。CPT 格式用短品牌結尾，勿用 %sitename%（會展開超長站名被 Google 截斷）。

## 遠端建置路線（MCP／SSH-only）（詳見 `references/remote-build-routes.md`）

Novamira 類 MCP 與 SSH-only 兩種遠端環境的完整教戰：機械轉換器規則、Elementor 4.x 特異性三層架構、干擾清單、mu-plugin 橋接、視覺驗收與 parity 量測。

## Elementor 頁面自訂 CSS 與 widget 的十一個硬坑（2026-08-20 起，線上課程型客戶站 plan4/sign4 實測）

把「整段 HTML 塞在 html widget」的頁面就地換成原生元素樹時，這四條各害過一輪來回；
照抄即可，弱模型不必自己診斷。最終結果：兩頁 1440/390 雙視口逐區 0.0%、整頁 0.00%、
樣式逐元素 0 差異。可重用工具鏈在 `~/Documents/線上課程型客戶站 線上課程型客戶站文創行銷/elementor建置工具/`
（`build-page.py` 是本節所有規則的實作）。

1. **頁面自訂 CSS 的選擇器清單不能跨行**。Elementor 存 `_elementor_page_settings.custom_css`
 時，`.a,\n.b{...}` 只會留下最後一個選擇器，前面的靜默消失（症狀：規則明明在檔案裡、
 `el.matches()` 也成立，但 `getComputedStyle` 不變）。輸出前一律
 `re.sub(r',\s*\n\s*', ',', css)`，compat 層每條規則自己一行。
2. **頁面上任何 widget 的自訂 CSS 若有語法殘渣，會吃掉頁面自訂 CSS 的第一條規則**。
 本案 countdown widget 的自訂 CSS 尾端留了裸字 `showaftercountdown`，
 瀏覽器把它跟下一條規則併成 `showaftercountdown .emxw.emxw.emxw{...}` 而整條失效。
 對策：頁面自訂 CSS **開頭固定放一條犧牲規則**（如 `.線上課程型客戶站-css-guard{color:inherit}`）。
 判別法：`document.styleSheets` 裡該規則的 `selectorText` 前面多了不明前綴。
3. **heading widget 的 `title` 會過 `wp_kses_post`**，行內 style 只留 WordPress 白名單屬性：
 `-webkit-background-clip` / `-webkit-text-fill-color` 直接被剝掉 →
 漸層字（`background:linear-gradient` + `background-clip:text`）變成**實心色塊、文字消失**。
 text-editor widget 不受影響（不過 kses）。對策：轉換時把 heading 內層元素的行內 style
 一律改成 class ＋ 頁面 CSS 規則（`inline_to_class()`）。這種缺陷高度／樣式比對都抓不到，
 **只有截圖親讀會發現**。
4. **`:first-child` / `:last-child` / `:only-child` 會因 Elementor 包裝層失效**
 （每個葉節點都是自己 widget div 的唯一子節點 → 每個都是 last-child）。
 對策：轉換時依「設計樹的兄弟順序」打上 `emxfirst`/`emxlast`/`emxonly` 標記 class，
 再把 CSS 裡的這三個偽類機械替換成對應 class。

另外三條同輪的實作要點：

- **原 html widget 的 `_padding`/`_margin`/`_element_width`/`_element_custom_width`/
 `_flex_align_self`（含 `_tablet`/`_mobile`）必須還原**：把轉出來的元素樹包進一個容器，
 並把這些設定翻成該容器的 CSS（tablet ≤1024、mobile ≤767）。不還原會同時吃掉
 垂直間距與寬度（實測 `align-self:center` 沒還原時，區塊從 588px 撐成 1440px）。
- **`.elementor-heading-title` 的 line-height 要用「原頁實測值」**，不要用 `1`（Elementor 預設，
 標題會短掉約 1/3）、不要用 `normal`（差 2-3px）、也不要用 `inherit`
 （會吃到佈景 body 的值，本案 1.65 vs 實際 1.5）。做法：先量原頁三種標題的
 `lineHeight/fontSize`，取共同比值寫死。
- **包裝層中和用 `display:contents!important` 且要 3 個 class 疊特異性**
 （`.emxw.emxw.emxw`）；`p:only-child` 的中和要加 `:not([class]):not([style])`，
 否則會把設計自己的 `<p>` 的 margin 一起殺掉（實測整頁短 5%）。

5. **boxed 容器（`e-con-boxed`）的 `--content-width` 會在窄螢幕把內容鎖死**。
 響應式想把雙欄改直向，只改 `flex-direction:column` 完全沒用——內容仍被鎖在
 `--content-width`（本案 58% → 346px），標題一行只剩 14 字。
 正確寫法（2026-08-23 實測）：
 ```css
 @media(max-width:1024px){
 .elementor-element-<id>{--content-width:100%!important}
 .elementor-element-<id> > .e-con-inner{flex-direction:column!important;width:100%!important;max-width:100%!important}
 }
 ```
 子容器若還是不滿版，補 `width/max-width/--width:100%!important`（Elementor 的欄寬走 `--width`）。
6. **button widget 的字級要打 `.elementor-button-text`，打 `p` 一點作用都沒有**。
 你 的頁面常把整段文案做成 button widget（帶星號 icon 的稀缺說明就是），
 看起來像段落但 DOM 裡沒有 `<p>`。同理它的內距在 `.elementor-button`（本案 `20px 50px`，
 左右內距吃掉 100px 可用寬度，一行只剩 16 字，18 字的子句必被切開）。
 量到「字級改了沒反應」時先 `getComputedStyle` 確認實際承載文字的元素是誰。

7. **上傳型部署（Novamira upload-link 這類）權杖過期時不會失敗**。`curl -sS` 仍 exit 0，
 伺服器上的 bundle 保持舊版，接著套用就是把舊內容再寫一次——症狀是「CSS 明明改了但畫面沒變」，
 很容易被誤判成選擇器/優先權問題而愈改愈亂（2026-08-23 實際踩過一輪）。
 **鐵則：每次部署後回讀伺服器上的 `_elementor_page_settings.custom_css`，
 確認新規則字串真的在裡面，再開始量測。** 順手比對 bundle 檔的 `filemtime` 與現在時間。
8. **只給圖片 `max-width` 沒有用**。Elementor 會另外輸出 `width`，實際寬度仍是你寫的上限值，
 在比它窄的欄位裡就衝出容器。正確：`width:auto!important;height:auto!important;
 max-width:min(<上限>,100%)!important`。

9. **沒包在媒體查詢裡的 `!important` 會壓掉 `@media` 裡的同權重規則**。媒體查詢不影響優先權，
 同選擇器同 `!important` 時是「後者勝」。桌機專用的 flex 值（`align-items` / `align-self` /
 `flex`）一定要包在 `@media(min-width:…)` 裡，否則平板、手機會跟著吃到，
 症狀是「只有其中一欄沒對齊」（2026-08-23 實測）。
 另注意：直向堆疊時 cross axis 變成水平，`align-self:flex-start` 會讓該欄靠左而不是靠上。

10. **容器的自訂 class 用 `css_classes`，widget 用 `_css_classes`**。給容器寫 `_css_classes`
 不會輸出到 HTML，class 整個消失、樣式靜默失效（2026-08-23 實測）。
 驗證要用 `curl` 抓正式頁 grep class 名，不要只在瀏覽器裡量——瀏覽器會用自己的 HTTP 快取，
 同一個網址量到的可能是部署前的舊版。**任何部署後驗證一律加 `?v=<timestamp>`。**

11. **Blocksy 的動態 CSS 重生必須跟設定寫入分成兩個 request**。同一個 request 內先
 `update_option('theme_mods_...')` 再 `do_action('blocksy:dynamic-css:refresh-caches')`，
 產生器讀到的是該 request 已載入的舊值，`uploads/blocksy/css/global.css` 會被用舊內容重寫一次——
 mtime 會更新、色碼替換若等長則檔案大小也不變，非常難察覺（2026-08-23 實測）。
 做法：第一次請求存設定，第二次請求觸發重生，然後**回讀檔案 grep 新色碼**確認。
 另注意：手機選單／頁首的顏色多半不在 `colorPalette` 裡，而是硬編碼在 `header_placements`
 的每個頁首設定內（`offcanvasBackground` / `menuFontColor` / `triggerIconColor`），
 改調色盤不會動到它們，要逐一指定路徑替換（不要做全域字串取代——同一個色碼可能同時當背景與前景用）。

## 中文斷行腳本（線上課程型客戶站-cjk-wrap）不可切的節點（2026-08-20）

把文字切成 `.線上課程型客戶站-seg{display:inline-block}` 片段來控制 CJK 換行時，
**`background-clip:text` / `-webkit-text-fill-color:transparent` 的節點必須跳過**——
子節點一旦變成 inline-block，漸層就不再被文字裁切，整段字消失只剩色塊。
做法：切之前從文字節點的 parent 往上走到目標元素，命中就 return。
驗收掃描（0 才算過）：
`[...document.querySelectorAll("*")].filter(e=>{const c=getComputedStyle(e);
return c.backgroundImage.includes("gradient") && (c.webkitTextFillColor==="rgba(0, 0, 0, 0)")
&& c.webkitBackgroundClip!=="text"}).length`
另外腳本要留一個停用開關（本案 `?線上課程型客戶站-noseg=1`），否則做純還原比對時
斷行改動會混進高度差，看起來像 parity 沒收斂（實測會製造 ±10% 的假差距）。


## Elementor 範本 → Blocksy 原生 header/footer（詳見 `references/blocksy-native-header-footer.md`）

header/footer 從 Elementor theme-builder 改為佈景主題原生的完整做法：Blocksy 資料結構、三個會覆寫你設定的元件欄位、動態 CSS 快取重生、樣式覆寫層與收尾檢查。

## 圖片減重（同 html-to-elementor 2026-09-01 條目）
（2026-09-01 制度化，你 指示傳承；Claude 與 Codex 一體適用）

**教訓**：線上課程型客戶站 sign4 頁曾因單張 2.2MB PNG＋全頁圖片 4.6MB，在記憶體緊的機器上捲動閃白、載入緩慢；EWWW 外掛雖開 webp 但無損模式只壓 27% 且前台改寫吃不到 Elementor 輸出＝形同沒壓。

**規則（建頁/轉換時強制執行）**：
1. 任何要進 Elementor／uploads 的圖，先壓成 **WebP quality 80**；寬度超過 1600px 一律縮到 1600（LOGO/圖示縮到實際顯示尺寸）。指令：`magick in.png -resize '1600>' -quality 80 out.webp`（伺服器端用 Imagick 同參數）。
2. 交付前量整頁圖片總重：抓 HTML 內所有 img src 做 HEAD 加總，**目標 <500KB**，超過 1MB 不得交付。
3. 不可依賴站上的壓縮外掛「有裝」就當作「有效」——實測前台 HTML 是否真的載 webp 才算數。
4. WP 會自動產 PNG 尺寸變體進 srcset，只換主圖沒用；每個變體都要有同名 .webp，或在站上部署「存在同名 webp 即改寫」的輸出層過濾器（線上課程型客戶站 已有：`wp-content/novamira-sandbox/webp-srcset-cleanup.php` v4 全站版，可整份複製到其他 novamira 站）。
5. 深色設計的頁面必須給 html/body 明確深色 `background-color`——快速捲動時未繪製區域才不會閃白（參考 線上課程型客戶站 `dark-bg-antiflash.php`）。
