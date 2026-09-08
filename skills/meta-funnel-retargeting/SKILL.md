---
name: meta-funnel-retargeting
description: 用 TOF/MOF/BOF 三層漏斗與 24 個素材切角，替 你 的高單價服務（線上課程、講座導流、顧問式服務）建立 Meta 再行銷廣告：盤點既有貼文、建立分層自訂受眾、用貼文 ID 建成暫停的廣告草稿。當 你 說「建再行銷廣告」「全方位廣告策略」「24 切角」「TOF MOF BOF」「用貼文建廣告」「建廣告受眾」「Advantage+ / ASC」「把貼文拿去投」時使用。只建暫停草稿，投放與預算一律由 你 決定。
---

# Meta 全方位漏斗再行銷

## 這套策略在解決什麼

高單價服務（課程、講座、顧問）不會有人第一次看到就買。所以不是「做一支好廣告」，
而是**讓同一批人在不同溫度時看到不同任務的素材**。一支素材只做一件事，
用它贏不贏來反推市場在乎什麼。

來源：《零基礎 AI 音樂圓夢計畫》Meta 廣告素材漏斗策略
（Google Doc `106uTbhYpS35LCeg7C7kZH1xO0ZxpKfd7wqiLcKxQePI`）
＋ 24 切角規格庫 `~/Documents/線上課程型客戶站-fb-ads-ai-music/spec/creatives.json`。

## 三層的分工

| 層 | 受眾心理 | 素材任務 | CTA | 看哪個數字 |
|---|---|---|---|---|
| **TOF** | 我也許可以試試看 | 喚醒渴望、降低門檻 | 領資料／看影片 | 停留、互動、影片觀看、低成本名單 |
| **MOF** | 這方法真做得到嗎 | 展示流程、破除疑慮、建立信任 | 看課綱／了解流程 | 名單領取、頁面停留、留言問題 |
| **BOF** | 現在加入值得嗎 | 限額、價值堆疊、身份轉換 | 立即報名／折扣碼 | 購買、結帳啟動、單支 CPA |

**MOF 是高單價案子的勝負點**，它負責把「有興趣」變成「相信方法」。素材不足時優先補這層。

## 再行銷池：越久的越不能硬賣

| 名單年齡 | 打什麼 |
|---|---|
| 0–7 天 | BOF ＋ 強 MOF，推立即行動 |
| 8–30 天 | MOF 教育 ＋ BOF 輕急迫 |
| 31–90 天 | 流程、信任、避坑，重建方法可信度 |
| 91–180 天 | 價值提醒、成果想像，降低拖延 |
| 181–365 天 | 圓夢、身份、故事型，重新喚醒 |
| 366 天以上 | 先用 TOF/MOF 暖回來，不要一開始就賣 |

所有再行銷受眾**一律排除已購買者**。

## 三個操作原則

1. **不要太早細分人工受眾。** 把三層素材丟進少數 Advantage+/ASC，讓系統判斷意圖。
 高單價案子過早拆會把學習訊號切碎。
2. **一支素材只講一個切角。** 30 秒內不要同時講願景、方法、價格、贈品。
3. **用哪支贏反推市場在乎什麼**，再往那個方向加碼下一輪素材。

---

# 執行流程

## 開始前的三個檢查（缺一項就先講，不要硬做）

1. **轉換事件 Meta 看得到嗎？** 如果報名／成交發生在 LINE、Messenger 這類站外，
 Meta 收不到轉換訊號，ASC 學不起來，BOF 會很不準。
 要嘛在報名頁埋 Pixel + Lead 事件，要嘛先講清楚這一輪只能買互動。
2. **素材數量夠不夠？** 三層至少各 5 支才有東西輪替。不足時先說要補哪一層。
3. **廣告地區能不能設台灣？** 台灣廣告主驗證未完成前不能設台灣
 （見 `線上課程型客戶站-fb-ads-ai-music/state/*_setup.md` 的 `tw_verified`）。

## 工具與憑證

- `~/Documents/線上課程型客戶站-fb-ads-ai-music/fbads.py` — `fbads.call(path, params, method, data)` 打 Graph API，
 唯讀免問、寫入要 `--yes`、輸出經 `scrub()` 遮權杖
- 同目錄 `social.py` — `page_token(page_id)` 取粉專權杖、`pcall()` 用粉專權杖呼叫
- 權杖在 `.env` 的 `FB_ACCESS_TOKEN`。要換發看 `PROJECT.md`（**Generate 出來是短效的，
 一定要按 ⓘ→延長存取權杖**）

## 步驟一：盤點可用貼文，取得 post id

```python
import sys; sys.path.insert(0, "<你的本機路徑>")
import social
tok = social.page_token(PAGE_ID)
d = social.pcall(tok, f"{PAGE_ID}/posts",
 {"fields": "id,created_time,message,permalink_url", "limit": "50"})
```

回傳的 `id` 就是 `<page_id>_<post_id>` 格式，**那個完整字串就是後面要用的 `object_story_id`**。

把每則貼文對應到它的漏斗層。如果專案有內容矩陣（例如 A 客戶 的
`1UsGj3PaVrpPbRqtL_t62XcqoKiByG_RO6wOJXSfeHnU`），用「廣告漏斗層」欄；
沒有的話依內容判斷：純故事不推＝TOF、拆解方法＝MOF、限額成交＝BOF。

## 步驟二：建立分層自訂受眾

**先讀現況**，不要重複建：

```python
import fbads
fbads.call(f"{ACCOUNT}/customaudiences", {"fields": "id,name,subtype,retention_days"})
```

互動型受眾（不需要 Pixel，這是站外轉換案子唯一能用的）：

```python
rule = {"inclusions": {"operator": "or", "rules": [{
 "event_sources": [{"type": "page", "id": PAGE_ID}],
 "retention_seconds": DAYS * 86400,
 "filter": {"operator": "and", "filters": [
 {"field": "event", "operator": "eq", "value": "page_engaged"}]},
 "template": "ENGAGEMENT_EVENT"}]}}
fbads.call(f"{ACCOUNT}/customaudiences", method="POST", data={
 "name": f"{品牌}-粉專互動-{DAYS}天", "subtype": "ENGAGEMENT",
 "rule": json.dumps(rule)})
```

依再行銷池建 6 個：7 / 30 / 90 / 180 / 365 天，加一個「已購買」用來排除。

**保留天數的實證**（2026-08-16 讀線上課程型客戶站帳號 `act_995573331430126` 的 50 個受眾）：
互動型（ENGAGEMENT）實際看到 30／180／365 天，**365 是上限**；
網站型（WEBSITE）有 730 天的（已購買排除名單）。所以「730 天」只適用網站型，
互動型不要照抄。**以 API 回應為準。**

**這段 payload 我還沒親手用 API 建過**（線上課程型客戶站那些受眾多半是在廣告管理員介面建的）。
第一次執行**先只建一個 7 天的受眾**，確認回傳有 id 再建其餘。

**⚠ 最容易踩的坑：受眾建得出來，不代表投得出去。**
線上課程型客戶站那 50 個裡有 12 個是「廣告受眾範圍太小，無法用來建立行銷活動」，
連粉專互動 30 天那個都是。Meta 大約要 1000 人以上才讓你投。
**新粉專／小粉專的互動受眾在頭幾個月一定會是這個狀態**——這不是設定錯誤，是量體不夠。
遇到時要明講「這個受眾現在投不出去，要先養」，不要建完就回報成功。

## 步驟三：用貼文 ID 建廣告

**關鍵：用 `object_story_id` 指向既有貼文，不要重建 creative。**
這樣按讚、留言、分享會累積在同一則貼文上，而不是散在各個廣告版本裡。
`social.py` 的 `cmd_ad` 就是這個寫法，照抄它：

```python
# 1) 活動
fbads.call(f"{ACCOUNT}/campaigns", method="POST", data={
 "name": ..., "objective": OBJECTIVE, "status": "PAUSED",
 "special_ad_categories": "[]", "daily_budget": ..., 
 "bid_strategy": "LOWEST_COST_WITHOUT_CAP"})
# 2) 廣告組合（帶 custom_audiences 做分層）
targeting = {"geo_locations": {"countries": ["TW"], "location_types": ["home", "recent"]},
 "custom_audiences": [{"id": AUD_ID}],
 "excluded_custom_audiences": [{"id": 已購買_AUD_ID}]}
# 3) 素材：直接指既有貼文
fbads.call(f"{ACCOUNT}/adcreatives", method="POST", data={
 "name": ..., "object_story_id": "<page_id>_<post_id>"})
# 4) 廣告
fbads.call(f"{ACCOUNT}/ads", method="POST", data={
 "name": ..., "adset_id": ..., "creative": json.dumps({"creative_id": cr}),
 "status": "PAUSED"})
```

建完抓 `preview_shareable_link` 給 你 審。

## 步驟四：落地與回報

每次執行都要把結果寫進專案的台帳（例如 `state/ledger.json` 或該專案的成效追蹤資料夾），
**一行一次執行，含失敗**。只在對話回報而不落地＝下一個接手的人查不到。

回報時給：建了哪些受眾（名稱＋id）、哪幾則貼文變成廣告、預覽連結、目前狀態（一律暫停）。

---

# 運作模式：架構先立，素材逐月疊加

**不要等素材湊滿 24 支才開始**（你 2026-08-16 指定）。正確做法是三層的活動架構一次建好，
之後每個月把新發布的貼文加進對應那一層，讓受眾與素材同時長大。

## 長期架構（建一次，之後只加素材）

| 活動 | 受眾 | 素材來源 | 何時跑得動 |
|---|---|---|---|
| **A｜TOF 冷受眾開發** | 廣泛／Advantage+，不設自訂受眾 | 共鳴故事型貼文 | **第一個月就能跑** |
| **B｜MOF 再教育** | 粉專互動 30／90 天、影片觀看 | 方法拆解型貼文 | 等互動受眾過門檻 |
| **C｜BOF 收網** | 互動 7／30 天、未來的網站訪客、排除已購買 | 收網型貼文 | 等受眾過門檻＋有轉換事件 |

小粉專初期只有 A 跑得動。**B、C 的廣告組合照樣先建好並保持暫停**，受眾一到門檻就能開，
不用臨時補設定。

## 每月例行動作（新貼文發布後）

1. 抓當月新發布的貼文 id（步驟一）
2. 對照內容矩陣的「廣告漏斗層」欄，決定它屬於 A／B／C
3. 在對應活動的廣告組合底下**新增一個 ad**（`object_story_id` 指該貼文），狀態 PAUSED
 —— 不要動既有的 ad，讓舊素材繼續累積互動
4. 檢查每個自訂受眾的 `delivery_status`：過門檻的回報「這個可以開了」
5. 素材疲勞時**暫停舊 ad，不要刪**（刪掉會失去那則貼文累積的社群證明）
6. 落地一行紀錄

**這樣做的好處**：早期跑起來的數據會告訴你哪個切角最會吸人，下個月的內容就能往那邊加碼——
不用等三個月才知道。

## 六段再行銷池什麼時候才完整

名單天數是自然長出來的：第 3 個月時最舊的名單只有 60 天，181–365 天那幾段要到第 7–12 個月
才有人。**但這不影響現在就開始跑**——池子淺就先跑淺的那幾段，深的自己會長出來。

---

# 護欄

- **一律建成 PAUSED**，永遠不要直接開跑。預算與投放時機是 你 的決定。
- 寫入操作要 `--yes`；唯讀查詢不用問。
- **不要重建 creative 來投既有貼文**——互動會被打散。
- **不要為了成效把 CTA 加到 TOF 素材上**。TOF 的任務是共鳴，加了 CTA 就變成 BOF，
 兩層都做不好。
- 客戶資產留在客戶自己的企業管理平台，不要分享到 你 的平台（風險隔離）。
- 台灣廣告主驗證未完成前，地區不能設台灣。

# 已知的坑

- **Generate 出來的權杖是短效的（1–2 小時）**，一定要按 ⓘ→延長存取權杖。
- **缺 `read_insights` 時 insights 端點回空資料而不是報錯**，數字會靜靜變成 0。
 任何吃 insights 的流程都要先查權限。
- **Meta 已下架貼文層級的觸及／曝光**（v25.0 實測），FB 也從不提供儲存數。
 自然貼文只能用分享、留言、心情、點擊衡量。
- 不要開測試工具的「除錯」按鈕，它會把完整權杖寫進網址列與瀏覽器歷史。
