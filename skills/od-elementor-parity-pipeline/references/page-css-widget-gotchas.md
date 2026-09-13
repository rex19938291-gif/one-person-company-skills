# 頁面自訂 CSS／widget 硬坑、CJK 斷行、圖片減重

`od-elementor-parity-pipeline` 的按需參考檔（2026-09-13 從 SKILL.md 原樣搬出，內容一字未改）。
把 HTML widget 就地換成原生元素樹、或處理 CJK 斷行與圖片重量時讀這一份。

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

## 圖片減重（同 html-to-elementor 2026-09-01 條目）
（2026-09-01 制度化，你 指示傳承；Claude 與 Codex 一體適用）

**教訓**：線上課程型客戶站 sign4 頁曾因單張 2.2MB PNG＋全頁圖片 4.6MB，在記憶體緊的機器上捲動閃白、載入緩慢；EWWW 外掛雖開 webp 但無損模式只壓 27% 且前台改寫吃不到 Elementor 輸出＝形同沒壓。

**規則（建頁/轉換時強制執行）**：
1. 任何要進 Elementor／uploads 的圖，先壓成 **WebP quality 80**；寬度超過 1600px 一律縮到 1600（LOGO/圖示縮到實際顯示尺寸）。指令：`magick in.png -resize '1600>' -quality 80 out.webp`（伺服器端用 Imagick 同參數）。
2. 交付前量整頁圖片總重：抓 HTML 內所有 img src 做 HEAD 加總，**目標 <500KB**，超過 1MB 不得交付。
3. 不可依賴站上的壓縮外掛「有裝」就當作「有效」——實測前台 HTML 是否真的載 webp 才算數。
4. WP 會自動產 PNG 尺寸變體進 srcset，只換主圖沒用；每個變體都要有同名 .webp，或在站上部署「存在同名 webp 即改寫」的輸出層過濾器（線上課程型客戶站 已有：`wp-content/novamira-sandbox/webp-srcset-cleanup.php` v4 全站版，可整份複製到其他 novamira 站）。
5. 深色設計的頁面必須給 html/body 明確深色 `background-color`——快速捲動時未繪製區域才不會閃白（參考 線上課程型客戶站 `dark-bg-antiflash.php`）。
