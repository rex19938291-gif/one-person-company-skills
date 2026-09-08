# Humanizer-zh: 繁中去 AI 化 Skill

這是 你 本機 Codex 使用的去 AI 化 Skill。

執行入口是 `SKILL.md`，本 README 只保留來源與維護說明。

## 目前版本

- 本機 skill 名稱保留為 `humanizer-zh`，避免既有觸發詞失效。
- 主流程已拆成精簡的 `SKILL.md`、按需讀取的 `references/`，以及 SF／SNF 誤殺回歸集。
- 內容採繁體中文、台灣用語優先，並加入事實保護、情境力度、長文防縮水與自動化模式。
- 你 的 FB/IG 社群貼文規則已獨立到 `social-post-codex`，不在本通用去 AI 化 skill 中預設套用。

## 來源

- `kevintsai1202/Humanizer-zh-TW`
- `op7418/Humanizer-zh`
- `blader/humanizer`
- `hardikpandya/stop-slop`
- `Raymondhou0917/speak-human-tw`
- Wikipedia `Signs of AI writing`

## 安全處理

這份本機版本沒有使用 upstream 的 `allowed-tools` 權限，也沒有安裝腳本、執行碼、背景網路呼叫或憑證處理。

詳細檢查紀錄見 `SECURITY_REVIEW.md`。
