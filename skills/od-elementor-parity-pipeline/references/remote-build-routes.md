# 遠端建置路線（MCP／SSH-only）

> 由 `SKILL.md` 按需載入。

## 遠端 WP（MCP／無本機 WP）建置路線＋Elementor 4.x 容器包裝層 cascade 教戰（2026-08-18，A 客戶 funnel 輪定案）

本輪把三頁攤平 HTML 100% 還原到「遠端」模板站（無 SSH、無本機 WP），證明整條 pipeline 可以走 Novamira 類 MCP（execute-php／run-wp-cli／write-file／create-upload-link）完成。參考實作與可重用工具：`A 客戶A 客戶/網站與SEO/elementor建置工具/`（funnel-mcp.sh＝JSON-RPC 包裝、fphp.sh＝PHP 執行器、convert.py＝機械轉換器、build/＝產出物）。

### A. 機械轉換器（convert.py）—— 弱模型照抄也能建整頁

分類規則（固定、不憑感覺）：全元素子節點的 div/section/header/footer/nav/main/article/aside → container；h1-h6 → heading widget；img → image widget；其餘（含 p/a/span/ul/details/form 與任何含直接文字者）→ text-editor widget，**原始 HTML 整段保留**（含 class 與行內 style——這是文字葉節點 100% 保真的關鍵，不需要 emx 轉換）。

鐵則：
1. **容器的原始標籤必須用 `html_tag` 保留**（article/section/nav…）。轉成 div 會讓 `[data-od-id] > article`、`section > div` 這類元素型設計選擇器整批斷裂（實案：testimonials 卡片 flex-basis 全失效）。
2. **data-od-id 等自訂屬性用 Pro `_attributes`**（`key|value` 換行分隔），widget 與 container 同 key。動畫 JS 全靠這些 marker 掛載。
3. 行內樣式轉出的規則：容器 → `.emx-N ×4`（四重 class），heading → `.emx-N ×4 .elementor-heading-title`，img → `.emx-N ×4 img`。**四重是算過的**：要壓過 Elementor `.e-con-full.e-flex`（0,3,0）與三倍增幅後的設計規則（見 B）。
4. 元素 id → `_element_id`（錨點 #signup 才會通）。
5. 表單特例：原 form 換成 container＋`[fluentform id=N]` shortcode widget，保留 header/註記文字葉節點。

### B. 特異性架構（三層，順序與倍數都不能改）

載入順序：`elementor-compat.css` → 共用 css → 頁面設計 css（含末尾 emx 生成段）→ 動畫 css。三層權重：
- **compat 層**（`:is(SEL):is(SEL):is(SEL)` 無 scope 三倍 ≈ (0,3,0)，只在目標頁 enqueue 所以不用 body scope）：中和 Elementor 預設。
- **設計 css**：每個選擇器機械改寫成 `:is(S):is(S):is(S)`（偽元素拆出後綴）。(0,1,0) 的原規則升到 (0,3,0)，靠「載入晚於 compat」贏平手。@keyframes 不動、@media 內遞迴處理。
- **emx 行內衍生規則**：四重 class (0,4,0)，永遠壓過前兩層＝重現「行內樣式最大」的原始 cascade。media 內的 `!important` 設計規則維持最高＝原始行為。

### C. Elementor 干擾清單（每一條都是實測踩到，compat 層逐條中和）

1. `.e-con.e-flex` 的 `--flex-direction:column` 等變數＋`.e-con-full.e-flex` 物理規則 → compat 設 display:block＋flex 全屬性 CSS 初始值＋全部 `--` 變數歸零。
2. **`.e-con::before` 背景疊層規則**（content:var(--background-overlay)、width/height:max(100%…)、left/top calc）會把設計的 `::before` 裝飾（光球、圓環）拉成整區大 → compat 加 `::before{content:none;position:static;width:auto;height:auto;left:auto;top:auto;border:0;transition:none;mix-blend-mode:normal;opacity:1}`。**不要**同做 `::after`（低特異性動畫 css 的 ::after 會被誤殺）。
3. `.elementor-widget{position:relative}` 會攔截葉節點裡 absolute 定位的裝飾層（照片陰影 offset 消失）→ compat 設 `position:static`。
4. **包裝層搶走 flex/grid item 身分**（本輪最大宗缺陷類）：
 - 設計把 `grid-column` 寫在內層 p/h3 → 死（secret-row 高度爆增 50%）。
 - inline span 靠 flex item 撐尺寸（9px 紅點）→ 塌成 0。
 - 修法＝**外科手術式** `display:contents`：`.該區塊 :is(.elementor-widget,.elementor-widget-container){display:contents}`。**禁止全域套**——contents 的盒子不存在，包裝層上的 reveal opacity/transform 動畫會全滅。
5. **object-fit/object-position 寫在圖片 od-id 上** → 屬性掛在包裝層碰不到 img → compat 加繼承鏈（中間隔層必補）：`.elementor-widget-image .elementor-widget-container, .elementor-widget-image img{object-fit:inherit;object-position:inherit}`。img 自身行內值（emx (0,4,0)）照樣蓋過＝正確。
6. 佈景基礎字級（18px vs 設計 16px）→ compat `body{font-size:16px}`；heading 用 `.elementor-heading-title{font-*:inherit;line-height:inherit;…}` 讓包裝層 class 規則靠繼承生效（Elementor 的 line-height:1 會毀 CJK 標題）。
7. 動畫 JS 的結構型選擇器（`>div>div:first-child>*:nth-child(n)`）進 Elementor 必斷 → **設計源頭改 marker 式**（od-id＋CSS 變數 delay），兩邊共用同一份動畫檔。JS 對 e-con-inner 加一層「單一子元素就下探」容錯。

### D. 遠端站營運坑

- **Novamira sandbox 有 `.crashed` 標記就整個 sandbox 不載入**（一個檔 fatal、全部陪葬）。排查 loader 不生效先看 sandbox 目錄有無 `.crashed`；處理＝disable 肇事檔＋刪標記。交付前用「刪除」不是「停用」。
- **PHP opcache 咬住 sandbox loader**：edit-file 改版本號後頁面不動＝opcache；每次改 loader 或 css 後固定三連發：bump `$v` → `opcache_reset()` → `rocket_clean_domain()`。
- 圖片：`media_handle_sideload` 站對站抓最省事；注意最佳化外掛會把 png 轉 jpg（URL 副檔名以回傳值為準）。srcset 縮圖比例同原圖即可接受。
- Fluent Forms 快速建表：複製既有表單 row＋form_meta；按鈕文字藏在 fields 裡的 `custom_submit_button`（不只 root submitButton）；多餘欄位（驗證碼）記得剪；label placement 用 CSS grid 強制上下排最穩。
- Body 屬性（data-motion-page 等）：`wp_body_open` 印 `<script>document.body.setAttribute(...)</script>`，首繪前生效；WP Rocket 用 `rocket_delay_js_exclusions`＋`rocket_exclude_defer_js` 排除動畫 JS。
- 統一 vs 逐頁 header：設計逐頁差異（CTA 文案、aria-current）若業主要求統一 → 單一範本＋剝掉 aria-current＋`body[data-motion-page=…] a[href=…]` 重現作用中樣式（CTA 記得 `:not()` 排除）。

### E. QA 增補（遠端站無頭量測）

- 全頁截圖前用 **adoptedStyleSheets 注入**強制顯示（CSP 擋 `<style>` 注入、CSSOM 不受擋）：reveal 元素 opacity/transform 歸位＋clip-path 解除。
- **`100svh` 陷阱**：qa-measure 的 shot 路徑把視窗撐到整頁高 → svh 型 hero 撐爆、以下全部「看似空白」。注入 `min-height:<原視口高-header>px!important` 固定再截。
- lazyload 圖在無頭截圖不觸發 → 注入時把 `data-src/срcset` 手動搬回 `src/srcset` 再等 2 秒。
- 內建瀏覽器 App 分頁背景時 **rAF 凍結**：`motion-started` 沒加、transition currentTime 卡 0＝環境問題不是頁面 bug，截一張圖強制渲染即恢復；分頁曾出現 viewport 0×0（量測全部失真），resize_window 重設後再量。
- 比對節奏基準：兩站同視口逐 section 高度，粗門檻 ±10%、目標 ±3%；**字級/欄寬型全域偏差先修**（一條 body font-size 就能同時收斂多個 section），再逐區。

## SSH-only 遠端站建置路線（2026-08-19，品牌站新架構輪定案）

繼 8/18「無 SSH 走 Novamira MCP」之後的第三種環境：**有 SSH，但沒有 MCP、也沒有 php／wp-cli／mysql**。主機商（品牌站 wpsite.pro 型）給的是只掛網站目錄的側車容器，`command -v php wp mysql` 全空——只有 tar/gzip/unzip/find/grep/sed/wget/scp/nano。

判別：`ssh <alias> 'for c in wp php mysql; do command -v $c || echo -; done'` 全空 ＝ 走本節；有 wp-cli ＝ 走既有 WP-CLI 路線。

### A. 橋接原理：mu-plugin 一次性執行器

Elementor 頁面在資料庫（`_elementor_data` post meta），SSH 只給檔案 → **靠 `wp-content/mu-plugins/` 取得 PHP 執行權**：上傳 mu-plugin → HTTP 觸發 → 寫結果 JSON → `@unlink(__FILE__)` 自刪 → SSH 取回結果並清乾淨。等於臨時自建 Novamira，用完即銷毀。

可重用工具（正本）：`~/Documents/WP-SSH橋接工具/bin/wp-exec.sh`
用法 `wp-exec.sh <ssh-alias> <site-url> <php片段檔> [out.json]`；片段直接寫 PHP、用 `return` 回傳（自動 JSON 序列化，含 `echo`／`error` 欄位）。payload 範例放 `payloads/`。

### B. 三個必踩的坑（每一條都實測撞過）

1. **SSH 路徑 ≠ PHP 路徑**。同一份檔案，SSH 看到 `/data/...`，PHP 的 `ABSPATH` 是 `/var/www/html/`（兩個容器掛同一卷、掛載點不同）。結果檔的寫入路徑**一律用 `ABSPATH . '檔名'`**，本機再從 SSH 的網站根目錄讀。硬編 SSH 路徑進 PHP＝檔案寫到不存在的地方，症狀是「HTTP 200 但永遠等不到結果」。
2. **WP Rocket 快取會讓觸發無效**。打首頁若命中快取，PHP 根本不執行，mu-plugin 不會被載入。觸發網址**固定帶隨機參數**（`?wpx=<token>`）繞開快取。
3. **mu-plugin 載入極早**，外掛常數尚未定義。邏輯掛在 `add_action('init', …, 1)` 裡跑，才拿得到 `ELEMENTOR_VERSION`／`FLUENTFORM_VERSION`／已註冊的 CPT。

### C. 安全契約（你 2026-08-19 授權範圍）

- 一次性程式**跑完必須自刪**，結果檔取回後立刻 `rm`；收工前 `ls /data/wp-content/mu-plugins/` 確認沒有殘留 `.wpx-*`。
- 腳本正本留本機重用，**網站上不留任何常駐檔**。
- 「能寫檔進網站目錄」＝「能執行 PHP」。所以 SSH 面板的「停止 SSH」不是可有可無：維運結束就請 你 按掉，這比 Novamira 常駐權杖更容易被忽略。
- 主機商重啟 SSH 後 IP／port 可能改變，但 `authorized_keys` 在網站持久卷（`$HOME=/data`）不會掉——只需更新 `~/.ssh/config` 的 HostName/Port，不必重跑 ssh-copy-id。

### D. 跨站搬運前的相容性閘（先驗版本，再動工）

來源站與目標站的 Elementor 大版本可能不同（實案：funnel 站 4.2.2／Pro 4.2.1 → 學院站 3.34.3／Pro 3.32.1）。**動工前先數元件**：

```
preg_match_all('/"widgetType":"([a-z0-9_\-]+)"/i', $data, $m); // 統計用到哪些 widget
```

只用到 `container` ＋ `text-editor`／`image`／`heading`／`shortcode` ＝ 3.6+ 全支援，跨大版本安全（本輪即是此情況）。出現 v4 atomic widgets（`e-heading`、`e-div-block` 等）＝ 3.x 吃不下，必須先在來源站降級重建或改走 HTML 重轉。

另查目標站缺哪些外掛：來源表單掛了 FluentCRM／ActiveCampaign feed，目標站沒裝就會斷——搬運前逐項確認要不要一起帶，你 明確說不用的就從 form_meta 剔除，不要整包照搬。

### E. 視覺驗收：文字檢查不算驗證（2026-08-19，學院站輪實測）

**執行前置（缺一結果就是假的，這輪三個都踩過）**：量測前必須 `tabs_select` 把分頁移到**前景**、`resize_window` 給**明確數值**、先 `computer{action:"screenshot"}` 強制渲染一次。背景分頁同時製造兩種假象：

- **rAF 凍結** → 動畫 gate class（本案 `emil-v2-start`，首頁另需 `motion-started`）永遠不會被加上 → 全部元素停在 `opacity:0`。本輪為此追了一小時「動畫壞掉」，實際 `document.hidden===true` 而已，分頁一 front 就正常。
- **viewport 0×0** → 所有 `getBoundingClientRect` 高度失真。本輪來源站首頁一度量到 20902px（行動版佈局），實際 1440 寬是 6506px。

**量最終狀態，不要等動畫播完**：注入 `adoptedStyleSheets` 把 `transition/animation` 全部關掉，再手動補上 gate class 與 `data-emil-visible`／`data-emil-item-visible`，即可直接讀到收斂後的值。CSP 擋 `<style>` 注入但不擋 CSSOM。

**Parity 用逐段高度**：來源站與目標站同視口各跑一次，兩份 `sectionHeights` 逐 `data-od-id` 相減。粗門檻 ±10%、目標 ±3%。本輪首頁 12 個受測區段 11 個 0% 差異、`free-course` -2.8%、總頁高 -0.26%。

#### 原始教訓


本輪犯過的錯：只用 `curl` + `grep` 數 HTTP 狀態、位元組數、CSS link 數量，就回報「三頁已完成」。實際開畫面才發現**佈景預設 header 蓋在上面、自訂 header 範本根本沒套用**，表單也沒渲染。**grep 命中不等於畫面正確**——宣告還原完成前一定要開瀏覽器看。

可重用腳本：`~/Documents/WP-SSH橋接工具/qa/visual-check.js`（貼進內建瀏覽器 `javascript_tool` 執行，單頁回傳結構化結果），門檻寫在同目錄 `README.md`。

四個必踩的量測坑：

1. **`naturalWidth === 0` 判破圖，必先關掉 lazyload**，否則 100% 假陽性。本輪一度誤報「15 張圖有 10 張破圖」，實際 `curl` 每張都是 200，只是 `loading="lazy"` 且在視窗外。正解＝先 `img.loading='eager'` 並重設一次 `src`（`i.src=''; i.src=s;` 強制重新請求），等 2.5 秒再判。單純捲動全頁**不夠**——捲回頂端後瀏覽器會取消未完成的請求。
2. **`currentSrc` 在圖片載入前是空字串**，別拿它判斷 src 是否存在，要看 `outerHTML` 或 `getAttribute('src')`。
3. **範本是否套用要正反雙驗**：只驗「自訂 header 存在」會漏掉「佈景預設 header 也在」的情況。必須同時檢查 `customHeader === true` **且** `themeDefaultHeader === false`（Blocksy 是 `header.ct-header`）。
4. **shortcode 回傳空字串不會留痕跡**：頁面上既看不到表單、也看不到 `[fluentform id=...]` 原文。所以要同時驗 `form.rendered === true` 與 `rawShortcodeLeaked === null`，兩者都不成立才代表真的渲染成功。

另有一個 shell 層的坑：**把含中文的 HTML 存進 shell 變數再 grep，zsh 會噴 `character not in range` 並回傳假數據**（本輪一度誤判整頁只有 2.3KB，實際 216KB）。一律 `curl -o 檔案` 後對檔案操作，不要用 `H=$(curl ...)`。

### F. SSH 連線頻率會被主機端掐斷（2026-08-19）

`wp-exec.sh` 每次執行開 4 條 SSH 連線（scp、輪詢、取回、清除）。密集連續執行約 20 次後，品牌站端開始在 kex 階段直接 reset：**port 仍通（`nc` 成功）但 `ssh` 握手被拒**，且不會自行恢復。判別＝`kex_exchange_identification: read: Connection reset by peer`。

處理：不要重試轟炸（會延長封鎖）。請 你 到面板停止再啟動 SSH；`authorized_keys` 在 `$HOME=/data` 的持久卷上不會掉，重啟後只需確認 IP／port 有無變動並更新 `~/.ssh/config`，金鑰不必重設。

預防（已內建於 `wp-exec.sh`，不需要另外設定）：連線重用參數直接寫在腳本裡，不依賴 `~/.ssh/config`——

```
-o ControlMaster=auto -o "ControlPath=$HOME/.ssh/cm-%r@%h-%p"
-o ControlPersist=10m -o ServerAliveInterval=30
```

多次 ssh/scp 共用同一條實體連線；「取回結果」與「清除暫存」也合併成一次遠端指令。此外仍應把多個步驟合併成單一 payload，不要一個小查詢就跑一次。

跨代理版本（Codex 也讀得到）記在 `~/.ai/LESSONS.md`「SSH 連客戶站：每次操作開多條連線會被主機端限流鎖死」；工具說明書在 `~/Documents/WP-SSH橋接工具/README.md`。
