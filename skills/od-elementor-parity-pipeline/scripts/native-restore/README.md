# 原生可編輯還原工具（2026-10-17 實戰參考實作）

規格見 `../../references/native-editable-restore-spec.md`。這些是實戰用過的版本，新專案複製到專案工作夾後依下表調整，不要直接在這裡執行。

| 檔案 | 用途 | 新專案要改的地方 |
|---|---|---|
| `dom.py` | 可逐字往返的 HTML 解析器 | 不用改 |
| `nconv.py` | 文字編輯器裡的網頁碼 → 原生元件（含自我檢查、逐列樣板、元素 ID 不重複） | 舊專案的整段網頁碼元件類別（`nr-u`）、新元件標記（`nr-n`） |
| `edcss.py`、`edcompat.css` | 產生只在編輯畫面生效的預覽樣式（相容層＋逐元素規則） | 通常不用改 |
| `nr-native.reference.php` | 站點外掛的前台組回、編輯預覽補載樣式、問答結構化資料、後台頁首頁尾入口、Rank Math 組織合併、IG 範例 | 函式前綴 `nr_`、站點判斷函式 `nr_site_render()`／`nr_site_view()`、檔頭常數（品牌名、IG 版型 ID、IG 帳號）；IG 那段只是範例 |
| `mkdraft.py` | 產生建草稿的 execute-php 片段（複製 meta、noindex、寫元素樹與編輯 CSS） | 呼叫方式見檔頭 |
| `render-cmp.php`、`rcmp.py`、`rdiff.py` | 伺服器端以暫時登入憑證渲染正式頁與草稿並逐行比對 | 維護帳號 ID |
| `owner_diff.py` | 切換前比對業主有沒有在面板改過（以上次寫入的版本為基準） | 頁面 ID 清單 |
| `backup.php`、`apply.php`、`rollback.php` | 備份／切換／還原（NRIDS、NRPAIRS、NRTAG 由呼叫端替換） | 不用改 |
| `orphanfix.py` | 依 WebKit 孤字結果在句尾加不斷行 | 結果檔路徑 |
| `edshot.mjs` | 無頭 Chrome 帶登入憑證開編輯器、執行 JS、分段截圖 | 不用改 |
| `pubshot.mjs`、`netlist.mjs` | 一般網址分段截圖（支援頁面內捲動容器）、列出所有程式請求與來源 | 不用改 |
| `test-render.php`、`test-faq.php` | 組回與問答的本機測試（假 WordPress 函式） | 隨外掛修改補測 |

安全：暫時登入憑證只存 600 權限檔、用完撤銷並移到垃圾桶；網站上的備份只放 `wp-content/updraft/` 或開頭 `<?php exit; ?>` 的 .php，部署後確認網址不是 200。
