# WP site-ops playbook（Blocksy + Elementor Pro + WP Rocket）

2026-07-12 header/theme 輪定案。適用於 你 的 WP 站上**任何**改動，不只 OD 轉換。
由 `../SKILL.md` 的「WP site-ops playbook」段按需載入；一條規則都沒刪，只是移出主檔。

### The ONLY safe rebuild pipeline (violating the order = stale-cache ghost bugs)
Any Elementor template/page rebuild MUST run these steps in this exact order:
1. `wp --user=<admin> eval-file <build-script>.php` (Document::save needs an editing user)
2. `wp --user=<admin> eval '\Elementor\Plugin::$instance->files_manager->clear_cache();'`
3. `curl -s -o /dev/null <a page using the template>` ← regenerates post-CSS files BEFORE page cache snapshots them
4. `rm -rf wp-content/cache/wp-rocket/* wp-content/cache/min/* wp-content/cache/background-css/*` ← ALL THREE dirs; skipping `min/` means pages keep loading the old minified bundle
5. warm-hit the pages again.
Why: Elementor re-save assigns NEW element IDs; Rocket-cached old HTML + regenerated new CSS = selectors match nothing → layout collapses to defaults (`--display` vars empty → e-con renders inline/column). `rocket_clean_domain()` alone misses non-default host variants (Tailscale IP) — always `rm` the dirs.

**快取外掛的辨識（2026-09-10 兩站實測）**：這套快取外掛在不同站上可能以兩種 slug 安裝——原版 `wp-rocket/wp-rocket.php`，或中文改版「火箭快取」`rocket-cache/rocket-cache.php`。**兩者都會定義 `WP_ROCKET_VERSION`，且快取路徑完全相同**（`WP_ROCKET_CACHE_PATH` 仍指向 `wp-content/cache/wp-rocket/`，`WP_ROCKET_MINIFY_CACHE_PATH` 仍是 `cache/min/`），所以上面第 4 步的 `rm` 指令不必改。

**不必登入就能辨識（2026-09-10 三站實測，最省事）**：抓前台 HTML 看結尾註解。中文改版輸出 `Performance optimized by 火箭快取 - Debug: cached@<timestamp>`；原版輸出 `This website is like a Rocket...`。沒有註解就是該頁沒命中快取（或未安裝）。實測三站：兩站為中文改版（`plugins/rocket-cache`），一站為原版（`plugins/wp-rocket`）——**同一批管理的站台不會一致，每站都要各驗一次，不要沿用上一站的結論**。

要改的是**偵測方式**：`is_plugin_active('wp-rocket/wp-rocket.php')` 在中文改版的站上會回 **false**，據此判斷「沒裝快取」是錯的。一律改用 `defined('WP_ROCKET_VERSION')`，或同時檢查兩個 slug。另外實測到裝了中文改版的站上**仍殘留一個停用的 `wp-rocket/` 目錄**，所以用 `is_dir()` 判斷也不可靠——只有 `active_plugins` 與常數算數。


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
