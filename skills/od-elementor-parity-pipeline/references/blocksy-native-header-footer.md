# Elementor 範本 → Blocksy 原生 header/footer

> 由 `SKILL.md` 按需載入。

## Elementor 範本 → Blocksy 佈景主題原生 header/footer（2026-08-21，學院站交付輪）

情境：三頁用 Elementor theme-builder 範本做 header/footer，條件只綁那幾頁 → 其他頁面（首頁、部落格、我的帳號、購物車）掉回佈景主題預設，品牌感斷裂。改用 Blocksy 的 header/footer builder 重做，可全站一致、選單後台可編輯、帳號/登入原生接上。

**這不是搬移，是照著現有視覺重做**：原樣式對著 `data-od-id` 與 Elementor DOM 寫，換成 Blocksy 後 DOM 全變，CSS 一條都不能用。做法＝先從既有頁面量出目標數值（`getComputedStyle` 逐項），再對 Blocksy DOM 重寫，最後逐項比對。本輪 header 高度、背景、blur、邊框、max-width、padding、字級、字重、顏色、CTA 圓角與內距全部一次對上，總高 73px 分毫不差。

### Blocksy 資料結構（踩過才知道）

- 設定在 theme_mod `header_placements` / `footer_placements`，可用程式讀寫，全程不必進後台。
- **header 的 `items` 是 list（`[{id, values}]`），footer 的 `items` 是 dict（`{id: {id, values}}`）**。同一套走訪程式會在其中一邊靜默失敗。
- header 版面：`sections[0].desktop[]` 每列有 `placements[]`，每個 placement 的 `items` 是**元件 id 字串陣列**；footer 版面則是 `rows[].columns[][]`。
- 可用元件：主題有 `logo` `menu` `menu-secondary` `button` `cart` `search` `socials` `text` `trigger` `mobile-menu` `offcanvas`；Blocksy Companion **Pro 另加 `account`**（我的帳號＋登入 modal，連結為 `#account-modal`）。footer 有 `copyright` `menu` `socials` `widget-area-1..6`。

### 三個會讓人白追很久的覆寫

1. **`menu` 元件自帶 `values.menu`（選單 ID），不吃 `nav_menu_locations`**。只改選單位置，前端仍顯示舊選單。
2. **`logo` 元件自帶 `values.blogname`**，覆寫站台名稱；`custom_logo` 也在元件裡（分 desktop/tablet/mobile）。改 `update_option('blogname')` 對它無效。
3. **Blocksy 把動態樣式編譯到 `wp-content/uploads/blocksy/css/global.css`**。改了 theme_mod 但畫面不動＝快取沒重生（例：`--height:75px` 仍是舊值）。處理＝刪掉該檔再打一次頁面即可重建；先備份。**不要用 `do_action('after_switch_theme')` 觸發**——WooCommerce 的 `wc_after_switch_theme()` 需要兩個參數，會直接 fatal。

### 樣式覆寫層

Blocksy 以 CSS 變數輸出配色，一般選擇器壓不過（頁尾底色改不動就是這個）。解法＝在同一條規則裡覆寫變數並補 `!important`：`footer.ct-footer{--theme-palette-color-8:#453739;background-color:#453739!important}`。

樣式寫進 `wp_update_custom_css_post($css, ['stylesheet' => get_stylesheet()])`——即後台「外觀→自訂→額外 CSS」，屬佈景主題層，客戶日後可自行編輯。加分隔註解當標記，重跑時先 `strpos` 切掉舊段落，維持可重複執行。

### 收尾必做

- 移除舊 Elementor 範本的 `_elementor_conditions`（含模板站原有的全站 footer 範本），再 `Conditions_Cache::regenerate()`，否則會同時出現兩個 header。
- 版型為 `elementor_canvas` 的頁面**不會**載入佈景主題 header/footer。全站統一後，這類頁（如感謝頁）要改成 `elementor_header_footer`。
- 逐頁 `curl` 檢查 `class="ct-header"` 與 `elementor-location-header` 的出現次數，確認新的有、舊的沒有。

## 停用 Elementor 範本會連帶炸掉「掛在範本裡的資產載入器」（2026-08-21 實測，最貴的一個坑）

把共用 CSS（`elementor-compat.css` / `shared.css` / `ff-compat.css`）掛在 **header 範本**的 HTML 元件裡，是 Elementor 時期的合理做法——每頁都會載入 header，等於全站共用。

但一旦移除 header 範本的 `_elementor_conditions` 改用佈景主題 header，**那個載入器就不再輸出**，共用層整批消失，而且不會有任何錯誤訊息：

- `elementor-compat.css` 沒了 → `body` 字級回到佈景主題預設（Blocksy 18px，設計是 16px）
- `shared.css` 沒了 → 共用元件樣式（卡片格線、頁尾 emx 類）失效

症狀是**所有區段一起變高**，但 hero 常常剛好不受影響（它多半用固定高度或 svh），很容易誤判成「只有某幾區壞掉」。本輪實測差異：testimonials **+186%**（763→2184，格線塌成單欄全寬）、course-method +27%、free-course +26%、course-solution +21%、target-audience +20%，而 hero 是 0%。

**規則：改用佈景主題 header/footer 之前，先把共用資產載入器搬到每一個頁面**，順序仍是 compat → shared → ff-compat → 頁面 css → 動畫 → overrides。純內容頁（如感謝頁）至少要載入共用三件，否則字級與元件樣式與其他頁不一致。

判別方式：量 `getComputedStyle(document.body).fontSize`，不是設計值就是共用層掉了；再數 `[...document.styleSheets].filter(s=>s.href.includes('<資產目錄>')).length` 對不對。

## 原本補償 fixed header 的 body padding 要一併撤掉

Elementor 版 header 是 `position:fixed`，所以 `overrides.css` 有 `body[data-motion-page]{padding-top:77px}`（手機 69px）補償。換成 Blocksy 的一般定位 header 之後，這段會在頁面最頂端留下一塊空白，且 header 被推到空白下方（實測 `headerBottom` 153 = 77 + 76）。改用佈景主題 header 時要把它註解掉，別直接刪，留註解說明原因。

## 其他

- **`?m=` 不能拿來當 cache-busting 參數**：`m` 是 WordPress 保留的日期查詢參數，`?m=1` 會被解析成年份查詢直接回 404。用 `?v=` / `?chk=` 之類。
- Blocksy 桌機與行動各有一份 header DOM（`[data-device="desktop"]` / `[data-device="mobile"]`），另一份會被 `display:none`。量測**必須先找出當前可見的那一份**，否則會量到高度 0 而誤判「header 不見了」。
- 手機版 CTA 按鈕放在 `offcanvas` 展開面板裡（`placements` 加 `button`），比擠在頂列合理，也符合原設計把 signup 放在 mobile menu panel 的做法。

## 全域調色盤才是藍色的根源（2026-08-22）

選單作用中項目、CTA 按鈕、選取反白、焦點外框全是藍的，逐條寫 CSS 去蓋是治標。根源在 theme_mod **`colorPalette`**（8 色）：

```
color1 主色／連結／按鈕 color2 hover color3 主要文字 color4 次要文字
color5 邊框 color6 淺底 color7 頁面底色 color8 純白
```

Blocksy 預設 `color1:#5391FF`。把 8 色換成設計稿 `:root` 的品牌色票即可全站一致；`linkColor`／`buttonColor`／`formBorderColor` 等元件設定值指回 `var(--theme-palette-color-N)`，就會自動跟著走。

`::selection`、`:focus-visible` 不吃調色盤，要另外寫進自訂 CSS。

**快取有兩層，只清一層不會生效**：transient `blocksy_dynamic_styles_descriptor` **和** `uploads/blocksy/css/*`。兩層都清掉後還要再打一次頁面才會重建。

## PHP 閉包用參考走訪 Elementor 樹：沒宣告回傳參考就是改到複本

```php
// 錯：$main 是複本，改了不會寫回 $data，但計數看起來完全正常
$find = function (&$els) use (&$find) { ... return $e; };
$main = &$find($data);
```

本輪因此回報「已插入、共 9 個區塊」，實際資料庫沒變、前端也沒有。**改用索引操作**（先找出 `$data[$i]`，再直接改 `$data[$i]['elements']`），並且**寫入後重新 `get_post_meta` 讀回驗證**，不要相信記憶體裡的變數。

## 視覺驗證改用無頭 Chrome

內建瀏覽器的分頁常處於 hidden：rAF 凍結（動畫 gate class 不會加）、捲動失效、截圖偶爾全白。改用：

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
 --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
 --window-size=<w>,<整頁高> --virtual-time-budget=15000 \
 --screenshot=out.png "<url>"
```

`--window-size` 的高度要大於整頁高才截得到下半部，再用 `ffmpeg -vf crop=w:h:x:y` 裁出要看的區段，避免整張大圖進對話。原始設計 HTML 用 `python3 -m http.server` 起在 127.0.0.1 再截（`file://` 會載不到圖片與樣式），即可與線上站做同尺寸對照。

注意無頭環境的字型 fallback 與實際瀏覽器不同，**文字換行位置會有差異**；判斷是否溢出要用 `documentElement.scrollWidth > innerWidth` 與元素 `getBoundingClientRect().right`，不要用截圖目測。
