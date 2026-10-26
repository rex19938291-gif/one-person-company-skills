#!/bin/zsh
# 範例：把本機做好的 OD 首頁打包成正式站匯入包（Elementor JSON＋頁面引用的本機資產＋匯入說明）。
# 輸出：dist/od-home-import-<日期>.zip。BASE／UP／資產資料夾名稱請換成自己的專案。
set -e
BASE=${BASE:?請設定 BASE＝本機範本工作資料夾}
UP=${UP:?請設定 UP＝本機 wp-content/uploads 路徑}
ASSET_DIR=${ASSET_DIR:-od-parity}          # uploads 底下放這個頁面資產的資料夾
STAMP=$(date +%Y%m%d)
PKG=$BASE/dist/od-home-import-$STAMP
rm -rf "$PKG"; mkdir -p "$PKG/templates" "$PKG/assets/$ASSET_DIR"

cp $BASE/json/*.json "$PKG/templates/"

# 頁面與範本引用到的資產（保留 uploads 之下的相對路徑）
cp -R "$UP/$ASSET_DIR/." "$PKG/assets/$ASSET_DIR/"

cat > "$PKG/IMPORT.md" <<'EOF'
# OD 首頁 正式站匯入指南

## 內容
- `templates/od-home.json` — 首頁（Elementor 頁面範本格式）
- `templates/od-global-header.json` / `-footer.json` — Theme Builder header/footer
- `assets/` — 頁面引用的所有圖片/SVG（保留 `wp-content/uploads/` 之下的相對路徑）

## 步驟
1. **先上傳資產**：把 `assets/` 底下的資料夾原樣放到正式站 `wp-content/uploads/`
   （路徑一致 = JSON 內相對 URL `/wp-content/uploads/...` 直接生效，不需改 JSON）。
2. **匯入範本**：Elementor → 範本 → 匯入範本，逐一上傳三個 JSON。
   - header/footer 匯入後在 Theme Builder 設定顯示條件（建議先只掛首頁測試）。
   - 首頁範本：建立新頁面 → 用 Elementor 開啟 → 從「我的範本」插入，或直接把範本套成頁面內容；頁面 Layout 選「Elementor 全寬（elementor_header_footer）」並隱藏標題。
3. **SVG 圖示**：icon widget 引用的 SVG 走媒體庫附件。若匯入後 icon 顯示空白，
   到 Elementor → 設定 → 進階 開啟「未過濾檔案上傳」，把 SVG 上傳到媒體庫後在 widget 重選（或用 wp media import 批次匯入）。
4. **選單**：Pro Nav Menu widget 需在正式站建立同結構的 WP 選單，並在 header 範本的 Nav Menu widget 選單欄位選它。
5. **彈窗**：CTA 若連到 Elementor 彈窗（`data-elementor-popup-id`），正式站的彈窗 ID 通常和本機不同，
   要在按鈕連結裡把 URL-encoded JSON 內的 `"id":"<彈窗ID>"` 換成正式站的值。

## 驗證清單
- 桌機/手機 hero 疊層與打字機動畫
- 品牌跑馬燈自動捲動＋拖曳
- 輪播、counter 數字動畫、FAQ 手風琴、捲動後導覽列狀態
- 無水平溢出（390/768/1440）
EOF

cd $BASE/dist && zip -qr "od-home-import-$STAMP.zip" "od-home-import-$STAMP"
echo "PACKAGE: $BASE/dist/od-home-import-$STAMP.zip ($(du -h $BASE/dist/od-home-import-$STAMP.zip | cut -f1))"
