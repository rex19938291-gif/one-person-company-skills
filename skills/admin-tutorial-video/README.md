# 網站後台教學影片

把真實後台畫面做成推鏡、聚光、游標點擊與字卡的 MP4。內容與色票由專案設定檔控制，不需要修改產生器。也能產生逐步切換的互動教學頁。

## 需求

- Node.js 22 以上、Python 3.9 以上、ffmpeg、Chrome／Chromium。
- 第三方工具 [HyperFrames](https://hyperframes.dev)，指令為 `npx hyperframes`。安裝前取得你授權，完成後先跑 `npx hyperframes doctor`。
- 影片使用 GSAP；完整範例提供固定版本的程式與字型網址。離線使用時改成專案內的素材路徑，並把檔案放到影片輸出目錄。此技能不會自動下載或安裝依賴。
- Pillow 選用；沒有 Pillow 仍能產生影片，互動版則直接複製 PNG。影片產生器保留兩倍解析度，不壓縮原始素材。
- 已去個資的真實後台 HTML 與樣式。這個資料夾不含登入資料，不會登入網站、送出表單或自動部署。

## 專案準備

以下以技能位於目前資料夾、作品放在 `project/` 為例。所有設定內的檔案路徑，都相對於 `video.config.json` 所在的目錄；從任何位置呼叫腳本，結果一致。

```bash
mkdir -p project/real
cp examples/video.config.json project/video.config.json
cp scripts/real/lib.js scripts/real/example-steps.js project/real/
```

將已去個資的真實 WordPress 一般設定頁存為 `project/real/settings.html`，保留真正版面與樣式，但移除原網站 script、行內事件、nonce、密碼、個資與表單動作。樣式與圖片另存本機並修正路徑，避免載入原站私人資產。範例使用 `#blogname`、`#start_of_week` 與 `#submit`；依自己的真實頁面調整選擇器。

產生本機拍攝頁的清理設定：

```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('project')
c = json.loads((p / 'video.config.json').read_text(encoding='utf-8'))
s = json.dumps({'capture': c['capture'], 'cleanup': c['cleanup']}, ensure_ascii=False).replace('<', '\\u003c')
(p / 'real/config.js').write_text('window.TUTORIAL_CONFIG = ' + s + ';', encoding='utf-8')
PY
```

在保存頁面 `</body>` 之前加入以下三行。清理設定與步驟腳本必須來自自己的專案；不要從外部頁面執行未檢查的程式。

```html
<script data-tutorial-runtime src="config.js"></script>
<script data-tutorial-runtime src="lib.js"></script>
<script data-tutorial-runtime src="example-steps.js"></script>
```

修改 `capture.browser` 為已安裝瀏覽器的執行檔，或系統能找到的 `chromium`／`google-chrome` 指令。瀏覽器使用獨立暫存設定檔，不借用自己的已登入設定檔。

## 三步驟：拍攝 → 產生 → 渲染

### １．拍攝

在另一個終端機開本機伺服器，只綁定本機位址：

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory project
```

確認 `capture.base_url` 的連接埠相符，再執行：

```bash
python3 scripts/capture_real.py project/video.config.json
```

輸出 `project/captures/`、`project/manifest.json` 與 `project/manifest-errors.json`。拍攝逐步續行，任何失敗都寫入錯誤清單，最後回傳非零結束碼。清單有失敗時先檢查對应頁面，不要渲染。每次重拍前備份既有素材與清單，避免覆蓋唯一驗收版本。完成後關閉自己啟動的本機伺服器。

### ２．產生

```bash
python3 scripts/gen_video.py project/video.config.json
python3 scripts/build_real.py project/video.config.json
```

影片專案：`project/video/index.html`。互動教學：`project/walkthrough/index.html` 與其 `assets/`，整包一起交付。互動版預設含素材上限 6 MB，超過時先壓縮或拆情境。

快速測試產生器可用假的純色素材，完全不讀真實後台：

```bash
python3 scripts/make_fixture.py project/video.config.json
python3 scripts/gen_video.py project/video.config.json
```

假素材會清楚標示在清單內，僅供程式測試，不能用作正式教學影片；請在空白測試專案執行。

### ３．檢查與渲染

```bash
cd project/video
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect
npx hyperframes snapshot --at 5,10,15
```

依實際時間挑每個情境的關鍵步驟，用 ffmpeg 拼縮圖總覽。每格評 1–10 分，先修最差三處，全部至少 8 分後才渲染：

```bash
npx hyperframes render --output tutorial.mp4 --fps 30 --crf 23
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 tutorial.mp4
ffmpeg -ss 1.8 -i tutorial.mp4 -frames:v 1 cover.jpg
```

渲染後再抽三個時間點確認焦點、字卡與畫面狀態。純色假素材測試不涵蓋這項視覺驗收。

## 設定欄位

| 欄位 | 用途 |
|---|---|
| `title`、`sub`、`tags`、`ghost` | 片頭與背景文字 |
| `labels` | 資訊列、監看標籤、章節格式與片尾註記 |
| `scenarios` | `id`、`mark`、`title`、`description`、`page`、`count`、選用 `must` |
| `overrides` | 鍵如 `settings,1`，第二個值從零起算；可覆寫 `tt`、`dd`、`dur`、`chips` |
| `outro_h`、`outro`、`outro_panel` | 片尾標題、提醒與右側大字 |
| `theme` | 範例完整列出產生器所需的全部色值；保留鍵名，只改值 |
| `timing`、`zoom` | 秒數與推鏡限制；每步須留足閱讀時間 |
| `capture.pages` | 頁面鍵對照本機 HTML 相對路徑 |
| `capture.phase_pages` | 選用 `settings,1,post` 對照另一個頁面鍵 |
| `cleanup` | 移除／隱藏選擇器、示意文字替換與清空欄位；仍須人工去個資 |
| `manifest`、`imgdir`、`out`、`interactive` | 同一專案內的清單、素材、影片與互動版路徑 |
| `runtime` | 字型樣式與 GSAP 位址，可改為本機素材 |

manifest 每個情境包含 `h`、`p` 與 `steps`。每步包含 `tt`、`dd`、`click`、`z`、可選 `spotZ` 與 `live`。`pre`、`post` 必填；`live` 為真時 `mid` 也必填。每張圖包含 `img` 與 `r`：`x`、`y`、`w`、`h` 均為 1280×860 視窗的 CSS 像素，不是兩倍圖檔像素。

完整方法、步驟鉤子與拍攝常見問題見 [SKILL.md](SKILL.md)。

## 分享與部署

任何支援 Range 的靜態主機都能放影片。這個範例不會幫你部署或開新資源。先建立自己的、已核准的部署目標，再複製 [deploy](deploy/) 範例到部署資料夾。

`deploy/public/` 放已驗收的影片與播放頁；設定的名稱、網域自行替換。頁面用 `<video controls playsinline src="tutorial.mp4">`，加 `<meta name="robots" content="noindex,nofollow">`。平台若需要命令工具，另行取得安裝及部署授權。

```bash
curl -s -D - -o /dev/null -H 'Range: bytes=0-99' https://tutorial.example.com/tutorial.mp4
```

確認 206 與 `Content-Range: bytes 0-99/…`，一般頁面也應有 `X-Robots-Tag`。noindex 不是權限保護，不能上傳仍含私人資料的影片。大型影片不要使用範例 Worker 的全檔記憶體切片方式。

## 腳本

| 檔案 | 用途 |
|---|---|
| `scripts/common.py` | 設定、專案路徑與素材座標檢查 |
| `scripts/capture_real.py` | 本機全視窗兩倍拍攝，失敗留紀錄並續行 |
| `scripts/gen_video.py` | 從設定與素材產生可 seek 的影片專案 |
| `scripts/build_real.py` | 產生可切步驟與拍攝階段的互動教學頁 |
| `scripts/make_fixture.py` | 產生三張假圖与測試清單，不讀後台 |
| `scripts/real/lib.js` | 清理、捲動、焦點座標與 render 鉤子 |
| `scripts/real/example-steps.js` | 真實一般設定頁的本機示意操作 |
| `scripts/real/dom-dump-temp-muplugin.php` | 受管理員與 nonce 保護的臨時私有存檔範例 |
| `scripts/server-capture.php.txt` | 短效工作階段讀取與撤銷範例，不會自動執行 |
| `deploy/worker.js` | Range 與 noindex 回應範例 |

不含任何原案例素材、正式設定或帳號資料。舊的單一情境步驟、平台專用圖片轉檔、舊版組裝與播放器模板未帶入。
