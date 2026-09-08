#!/bin/zsh
# Build the production import package for the Claude Fable 5 OD homepage:
# Elementor JSONs + all referenced local assets (kept at original relative
# uploads paths) + import runbook. Output: dist/claude-fable5-od-home-import-<date>.zip
set -e
BASE=<你的本機路徑>
UP=<你的本機路徑>
STAMP=$(date +%Y%m%d)
PKG=$BASE/dist/claude-fable5-od-home-import-$STAMP
rm -rf "$PKG"; mkdir -p "$PKG/templates" "$PKG/assets/電商型客戶站-od-parity/assets/brand-logos" "$PKG/assets/電商型客戶站-od-parity-claude/icons"

cp $BASE/json/*.json "$PKG/templates/"

# assets referenced by the page/templates (relative uploads paths preserved)
cp $UP/電商型客戶站-od-parity/assets/glow-hero-edit11.png \
 $UP/電商型客戶站-od-parity/assets/glow-team.jpg \
 $UP/電商型客戶站-od-parity/assets/電商型客戶站-logo.png \
 "$PKG/assets/電商型客戶站-od-parity/assets/"
cp $UP/電商型客戶站-od-parity/assets/brand-logos/*.svg "$PKG/assets/電商型客戶站-od-parity/assets/brand-logos/"
cp $UP/電商型客戶站-od-parity-claude/*.png "$PKG/assets/電商型客戶站-od-parity-claude/"
cp $UP/電商型客戶站-od-parity-claude/icons/*.svg "$PKG/assets/電商型客戶站-od-parity-claude/icons/"

cat > "$PKG/IMPORT.md" <<'EOF'
# Claude Fable 5 - OD 首頁 正式站匯入指南

## 內容
- `templates/claude-fable5-od-home.json` — 首頁（Elementor 頁面範本格式）
- `templates/claude-fable5-od-global-header.json` / `-footer.json` — Theme Builder header/footer
- `assets/` — 頁面引用的所有圖片/SVG（保留 `wp-content/uploads/` 之下的相對路徑）

## 步驟
1. **先上傳資產**：把 `assets/` 底下兩個資料夾原樣放到正式站
 `wp-content/uploads/電商型客戶站-od-parity/` 與 `wp-content/uploads/電商型客戶站-od-parity-claude/`
 （路徑一致 = JSON 內相對 URL `/wp-content/uploads/...` 直接生效，不需改 JSON）。
2. **匯入範本**：Elementor → 範本 → 匯入範本，逐一上傳三個 JSON。
 - header/footer 匯入後在 Theme Builder 設定顯示條件（建議先只掛首頁測試）。
 - 首頁範本：建立新頁面 → 用 Elementor 開啟 → 從「我的範本」插入，或直接把範本套成頁面內容；頁面 Layout 選「Elementor 全寬（elementor_header_footer）」並隱藏標題。
3. **SVG 圖示**：icon widget 引用的 lucide SVG 走媒體庫附件。若匯入後 icon 顯示空白，
 到 Elementor → 設定 → 進階 開啟「未過濾檔案上傳」，並將 `assets/電商型客戶站-od-parity-claude/icons/*.svg`
 上傳到媒體庫後在 widget 重選（或用 wp media import 批次匯入）。
4. **選單**：Pro Nav Menu widget 需在正式站建立同結構的 WP 選單
 （首頁/團購方案/商店/成功案例/智能知識+4 子項），並在 header 範本的 Nav Menu widget 選單欄位選它。
5. **LINE 彈窗**：兩處 CTA 連到 popup id 36105（`data-elementor-popup-id`）。正式站 popup ID 若不同，
 在按鈕連結中替換該 ID（URL-encoded JSON 內的 `"id":"36105"`）。

## 驗證清單
- 桌機/手機 hero 疊層與打字機動畫
- 品牌跑馬燈自動捲動＋拖曳
- 情境模式四圖 crossfade 自動輪播
- counter 數字動畫、FAQ 手風琴、捲動後白色導覽列與 LINE FAB
- 無水平溢出（390/768/1440）
EOF

cd $BASE/dist && zip -qr "claude-fable5-od-home-import-$STAMP.zip" "claude-fable5-od-home-import-$STAMP"
echo "PACKAGE: $BASE/dist/claude-fable5-od-home-import-$STAMP.zip ($(du -h $BASE/dist/claude-fable5-od-home-import-$STAMP.zip | cut -f1))"
