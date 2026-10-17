---
name: admin-tutorial-video
description: 把網站後台操作做成真實畫面、推鏡聚光、游標點擊、字卡、逐句旁白與背景音樂的 MP4 教學影片，另附手機畫面與互動教學頁。適用 WordPress、網站管理介面、操作示範與後台教學；admin tutorial video、screen capture、spotlight、cursor animation、HyperFrames、MP4。
---

# 網站後台教學影片

用真實後台畫面說明操作。每支影片是一份可隨時間定位的 HTML 專案，設定、素材與輸出集中在自己的專案資料夾。快速上手見 [README.md](README.md)，完整設定見 [範例](examples/video.config.json)。

## 工具與界線

需要 Node.js 22 以上、Python 3.9 以上、ffmpeg、Chrome／Chromium，以及第三方工具 [HyperFrames](https://hyperframes.dev)。用 `npx hyperframes doctor` 確認環境。影片與混音使用 Python 標準函式庫；手機外框與互動版另需 Pillow。錄音需要 Node.js 22.4 以上的內建 WebSocket，不自動安裝套件。影片內使用 GSAP，範例固定其版本；正式渲染可把字型與程式存成本機素材並修改 `runtime`。

安裝工具、存取登入後台與部署前先取得站方及使用者授權。只拍去個資的本機副本；不自動登入、不發信、不送出正式表單、不建立測試訂單。伺服器範例只供經核准的維運環境使用，不公開成網址。

## 真實畫面鐵則

- 自家網站直接截取真實後台，或保存真正 HTML 與樣式表；不可猜測按鈕位置。需登入的第三方後台（例如通訊軟體管理頁、試算表）改用自製示意頁，角落清楚標「示意畫面」，不用官方商標圖檔，也不做可掃描的真 QR；資料只在本機。示意頁不能當作真實操作成功的證據。
- 按下前 `pre`、展開中 `mid`、按下後 `post` 分別存圖。非點擊步驟也必須有 `post`。記錄焦點矩形，座標用 CSS 像素。
- 狀態模擬只在本機進行，先確認網站的真實結果與原始 markup。範例成功訊息明示為示意狀態，不能當成正式站已儲存的證據。
- 素材拍全視窗，包含工具列與左側選單。支援 1280×860 或 1600×1075、scale 2；後者的 CSS 座標由產生器乘 0.8。不可只拍局部再放大冒充完整視窗。
- 畫面與字卡使用台灣繁體中文。去除私人姓名、聯絡方式、交易紀錄、密碼、權杖、工作階段、隱藏欄位、瀏覽器擴充功能與內部備註；示意商店名稱與人數須標記為示意資料。
- 先整個移除不需要的工具列／選單元素，再替換各欄位的值；不得用正規表示式刪除 HTML 字串內的工具名稱，以免破壞 class 或 href。
- `cleanup` 是可設定的清理清單，不能自動辨識所有個資。存檔、截圖與交付三個階段都須人工檢查；DOM 去 script／nonce 不代表資料已安全公開。

## 拍攝與素材

將已去個資的頁面放入自己的 `real/`，加入 `scripts/real/lib.js` 和步驟檔。頁面先載入從設定檔抽出的 `window.TUTORIAL_CONFIG`，每支步驟檔提供 `PAGE`。設定檔 `capture.pages` 對照頁面，`scenarios` 指定情境、頁面與步數。步數不符、找不到元素、瀏覽器失敗，都記入錯誤清單並繼續其餘情境。最後結束碼為 1，須補拍才可產生影片。

真實後台 HTML 可透過「可在伺服器執行 PHP 的管理工具（例如 WP-CLI 或站方提供的維運外掛）」讀取。`scripts/server-capture.php.txt` 示範短效工作階段、讀取、DOM 清理與 `finally` 撤銷。`real/dom-dump-temp-muplugin.php` 是另一種臨時存檔方式：限管理員、驗 nonce、要求站外私有目錄常數。不要將這兩個範例直接安裝到正式站；先由站方檢查、核准與備份。

正式站的 nonce 只用於授權存檔，不得帶入本機素材。私人暫存目錄不要放在公開 uploads。下載後先去個資、取消表單動作並移除原站 script，再加入教學步驟；拍完停用臨時外掛並封存暫存檔。

## 推鏡與版面

畫布固定 1920×1080。左側顯示情境、步驟清單（目前步驟高亮）、步驟編號與本步說明；右側是 1280×860 的真實後台監看畫面。底部進度條配合時間碼；章節卡時鏡頭拉回全視窗。片尾右側放大字或色塊，避免半邊空白。

- 每步上方以大字顯示位置路徑：`locp` 放前段、`loc` 放目前頁面，可由各步覆寫。每段第一步保持整頁，只框左側選單項目，用 `overview.menu_rect` 或當步 `menu_rect` 指定。
- 放大時角落顯示小地圖，標出目前看到的範圍。推鏡倍率為 `min(設定限制後的建議倍率, 1180/框寬, 780/框高)`，不低於 1；框太大就保持整頁。
- 表格紅框必須同時包含欄名與列名，讓人知道在看哪筆哪欄；框座標由拍攝步驟提供，不猜測表格結構。
- 壓暗預設 `rgba(0,0,0,.16)`，換畫面 0.18 秒。章節卡先鋪滿底色再出字；`.monitor` 設 `z-index:0`；點擊波紋設定 `immediateRender:false`，避免後面步驟提前出現。
- 字卡用 `Intl.Segmenter` 分詞後插 `<wbr>`，搭配 `word-break:keep-all` 避免斷詞。色值集中在 `theme`，換配色只改設定，不改產生器。
- 聚光框、游標與點擊波紋的 z-index 必須高於所有截圖。產生器已保留足夠層級。
- 一次一個焦點：推鏡、聚光、游標配合操作，不要到處都在動。
- 不用漸層背景加置中大標、全部元素一起淡入或角落小標裝飾。不要使用 Inter、Roboto、非繁中字型的 Noto Sans 或 Poppins 當主字型。
- 中文建議 Noto Sans TC，資訊列可用 IBM Plex Mono／JetBrains Mono。正式交付嵌入本機字型，避免遠端字型未載完。
- 左欄約每行 14 字，避免最後一行只剩一至兩個字；優先縮短說明，而不是縮小字。

## 節奏與設定

片頭約 3 秒，章節至少 3 秒，每步約 4.5–5 秒，片尾至少 3 秒。推鏡約 0–0.9 秒，游標約 0.4–1.2 秒，1.3 秒點擊，1.45 秒顯示展開清單，2.4 秒切到操作結果，最後停留閱讀。字多就用覆寫增加秒數。

所有片名、說明、標籤、背景大字、情境名稱、章節必做提示、片尾、色票與資訊列，都來自 `video.config.json`。`overrides` 以「情境識別，零起算步數」為鍵，可設定 `tt`、`dd`、`dur`、`chips`、`vo`、`locp`、`loc`、`menu_rect`；`must` 放在各情境。字卡限純文字，勿放 HTML。

時間與動畫只能由已暫停的 GSAP 時間軸決定，註冊 `window.__timelines["main"]`。不可使用真實時鐘或隨機數決定畫面，確保任意 seek 都一致。

## 逐句旁白與秒數

1. 每步旁白放在 `overrides["情境,步數"].vo`；章節放 `scenarios[].vo`，片頭／片尾放 `voice.intro`、`voice.outro`。一句約 15–40 字；先寫人真的會說的話，再錄音。
2. 數字改成念法，例如「三百九十」、「一點一五倍」。不念斜線、星號、括號等符號；路徑改成「先進入設定，再選一般設定」。代入文字改說「填入你的商店名稱」，不要讀出變數名稱或括號提示。
3. 先跑產生器取得 `vo/lines.json`，再執行 `scripts/vo/tts_gemini_live.mjs`。只從環境變數 `GEMINI_API_KEY` 讀金鑰，不讀金鑰檔、不印金鑰。只傳已核准的旁白文字給 Google；正式錄音可能計費，須先取得同意。
4. Gemini Live WebSocket 使用 BidiGenerateContent，系統指示要求逐字朗讀。模型預設 `models/gemini-3.8-live`、音色 `Achernar`，可用參數或 `VO_MODEL`、`VO_VOICE` 更換。預設是可替換範例，不保證帳戶可用；實際可用名稱以服務文件與權限為準。
5. 輸出逐句 WAV 與 `transcripts.json`；已有錄音且文字、模型、音色相同，秒數檢查通過就跳過。每秒字數＝排除空白及符號後字數÷原始錄音秒數；少於 2.2 或多於 7 就重錄。同句連續兩次失敗停止，勿交付缺句版本。
6. 模型自己的轉寫常漏回傳，不能當唯一證據。一定要聽驗句首句尾、數字與專名；可另用另一個模型獨立轉寫抽驗，但先確認音訊外傳授權。秒數篩檢也不能證明文字完全正確。
7. 錄完重跑產生器。每步秒數＝`max(原秒數, 錄音秒數/1.15+1)`，片頭、章節、片尾同樣保留旁白時間；輸出 `vo/timing.json`。混音固定 `atempo=1.15`，不要再手動挪旁白起點。改稿須重錄再重建影片；混音會拒絕稿件與轉寫不一致的錄音。

## 混音與背景音樂

- `scripts/vo/mix_vo.py` 依 `timing.json` 用 `adelay` 排旁白，旁白 `loudnorm I=-16 LUFS`。背景音樂 `I=-24.7 LUFS`、`TP=-9 dBTP`（這是 ffmpeg 此濾鏡接受的下限，不可再填更低數字），再用 `sidechaincompress threshold=0.03 ratio=3` 自動讓出人聲。
- 用 `STEM=輸出前綴` 同時輸出旁白與壓低後的音樂分軌；逐段量測，不只看全片平均。講話時旁白比音樂大約 15–21 dB、空檔音樂約 −26 dB 可作起點，實際以清楚且舒服的聽感為準，並記錄量測方法。不要把 LUFS、峰值、區段 RMS 混為同一數值。
- `scripts/vo/loop_bgm.py` 以交叉淡化接長、片頭淡入與片尾淡出。混音保留影片 `-c:v copy`，不重壓畫面。工具拒絕覆蓋既有輸出，換新檔名保留上一版。
- 使用真的可合法取得、可改作的免權利金音樂，例如 [Pixabay Music](https://pixabay.com/music/)。[Pixabay 授權摘要](https://pixabay.com/service/license-summary/)允許免費使用、免標註與加工，仍有禁止用途及其他權利限制；以下載當時條款為準。標示 Content ID 的曲上傳 YouTube 可能收到聲明，下載證明不等於不會收到聲明。
- 網站常擋自動下載，請你自己按下載；不要繞過驗證。記錄曲名、來源頁、授權頁、下載日期、條款原文與 Content ID 情形至專案 `LICENSES.md`，格式見本技能 [LICENSES.md](LICENSES.md)。本技能不附任何音樂檔。
- 不建議自己合成背景音樂：合成版容易像催眠曲，有雜訊或節拍器聲。

## 手機與互動版

手機頁以 390×844、scale 3 拍攝，取得 1170×2532 圖。`scripts/compose_phone.py` 用 Pillow 縮成 858×1857，置於 3200×2150 畫布中央並加手機外框；專案 `capture` 設 1600×1075、scale 2。`--rect` 讀手機 CSS 框，`--rect-output` 寫畫布 CSS 框：橫向 `(1171+x*2.2)/2`、縱向 `(146+y*1857/844)/2`；寬高同倍率，產生器再乘 0.8。先完成手機拍攝，這支工具不操作登入瀏覽器。

`python3 scripts/interactive/build.py 專案/video.config.json` 產生互動版，`build_real.py` 是相容入口。每段第一步與每次切步先顯示完整視窗，之後才放大；含位置路徑、小地圖、淡壓暗、鍵盤操作與各自獨立的 JPG。中文最後六字綁在同一段防孤字，不用 `text-wrap:pretty`；焦點一律 `focus({preventScroll:true})`。互動版只示範操作階段，不會送出表單，也不含錄音播放。

## 踩過的坑

- `focus()` 會自動捲動，造成座標偏移；一律用 `focus({preventScroll:true})`。
- 保存 HTML 後的容器結構可能不同；WordPress 通常以 `#wpcontent` 模擬捲動，並把工具列移到 body 下方。先確認完整 DOM。
- 寬表格看右側欄位時，可在 `after` 加 `translateX(-230px)`；量座標之前執行，值依實際欄寬調整。
- 選單位於視窗下方時，內容與左側選單要同步捲動；可用 `afterScroll` 調整 `#adminmenuwrap`。先捲動、再定位、最後量座標。
- `after` 在所有拍攝階段都執行，包含已有 `postView` 的 `post`。
- 原生下拉清單可能截不到，`fakeList` 可在相同位置模擬已驗證的選項；不可新增原網站沒有的功能。
- headless 瀏覽器在受限環境可能無法啟動，包含結束碼 134。先記錄完整失敗來源，改在允許瀏覽器執行的本機環境拍攝，不反覆重試或降低安全限制。同一原因第二次失敗就停手回報。
- 不可將缺圖、負座標或失敗清單當成完成素材；產生器會拒絕不完整 manifest。

## 開工需求單與延伸工具

開新片前先對齊六件事，缺哪項就先問，不要猜：路線（後台教學片＝本技能）、規格（1920×1080、預估長度、旁白／音樂）、節點（情境與每步要按哪裡）、字卡原文（照後台實際用字）、手法（推鏡、聚光、位置路徑）、禁止事項（個資、內部工具、老套版面）。這套拆法取自 HyperFrames 官方的提示寫法。

- **品牌動態規格**：在專案放 `frame.md`（HyperFrames 的 hyperframes-creative 依 frame.md → design.md → DESIGN.md 順序讀取），前置 YAML 記色票與字型，再同步到 `video.config.json` 的色票。同一品牌下一支片直接沿用。
- **點擊與換章音效**：`gen_video.py` 會在輸出資料夾寫 `sfx.json`（點擊步驟在波紋出現時 `click-soft`、章節卡 `whoosh-short`）。渲染出 MP4 後執行 `python3 scripts/add_sfx.py <輸出資料夾>/sfx.json in.mp4 out.mp4`；影片不重壓，原片有旁白就疊在下面，音量預設 0.35。音效資料夾預設為 HyperFrames hyperframes-media 內附的音效庫，也可用 `--sfx-dir` 指定自己的資料夾（檔名＝音效名稱＋`.mp3`）；使用前確認音效授權。
- **片頭與數字卡**：需要更有設計感的片頭或數據卡，可用 HyperFrames 的 motion-graphics 另做獨立場景再放入片頭段。
- **社群短版字幕**：橫式片左欄字卡已足夠；剪 9:16 短版時，旁白逐字字幕可用 HyperFrames 的 embedded-captions。
- **重用**：新片從上一支的 `video.config.json` 複製修改，不從零寫。

## 品質閘門

1. 產生影片專案後跑 `npx hyperframes lint`、`validate`、`inspect`，全部通過。
2. 渲染前用 `npx hyperframes snapshot --at <秒>`，每個情境抽關鍵步驟，再用 ffmpeg 拼成縮圖總覽。
3. 逐格評 1–10 分：焦點、可閱讀時間、遮擋／裁切、畫面狀態是否正確。先修最差三處，全部至少 8 分才渲染 MP4。
4. 渲染後抽查至少三個時間點，確認與總覽一致；用 ffprobe 確認長度、尺寸與影片存在。加了音效時，音軌長度須等於影片長度，並抽聽第一個點擊。
5. 假素材測試只驗證產生器，不替代真實畫面與視覺驗收。

## 交付與部署

任何支援 Range 請求的靜態主機都可使用。部署自己的已核准目標，影片頁用 `<video controls playsinline>`。MP4 須能回應 `206` 和正確 `Content-Range`，否則行動裝置可能無法正常播放。

```bash
curl -I https://tutorial.example.com/
curl -s -D - -o /dev/null -H 'Range: bytes=0-99' https://tutorial.example.com/tutorial.mp4
```

頁面加 `noindex`，回應標頭加 `X-Robots-Tag: noindex, nofollow, noarchive`。noindex 只要求搜尋引擎不索引，不是存取保護，不能代替去個資。

[deploy/worker.js](deploy/worker.js) 與 [設定範例](deploy/wrangler.jsonc) 提供 Cloudflare Workers 靜態資產部署範例。全部資產先通過 Worker 以附加 noindex；MP4 單一 Range 由 Worker 回傳 206，不合法範圍回 416。範例會將整段影片讀入記憶體，只適合小型教學影片；大型影片使用原生支援 Range 的儲存服務。確認自己的平台限制、名稱、網域與授權後才部署。

回報分享網址、影片長度、縮圖評分與 Range 驗證。若尚未部署就交付本機 MP4，不虛構分享網址。其他自動化工具也能接續執行，但須沿用同一份設定與驗收結果。

## 容量與搜尋收錄

[Cloudflare Workers 靜態檔單檔限制](https://developers.cloudflare.com/workers/platform/limits/)為 25 MiB。長片先用 `-crf 27` 或 `28` 重壓，再確認小於 26,214,400 位元組；如果仍超過就拆片，不能只改設定冒充合格。每版換新檔名避免快取。重壓是交付前的獨立步驟，日常混音仍保留影片原編碼。整站回應加 `X-Robots-Tag: noindex, nofollow, noarchive`，每頁也加 meta noindex；這不是登入保護，不可公開私人資料。
