#!/usr/bin/env python3
"""驗證年度內容矩陣是否守住比例硬規則與封閉集合。

用法:
 python3 validate_matrix.py matrix.csv

CSV 必要欄位（標題列）:
 月, 篇次, 類型, 受眾身分, 卡住的環節, 故事切角

硬規則（違反即報錯，不是警告）:
 每月合計 = 8
 共鳴 >= 3
 收網 <= 3
 同月的受眾身分 / 卡住的環節 / 故事切角 皆不得重複

封閉集合由 sets.json 提供（與 CSV 同目錄），格式:
 {"受眾身分": [...6個...], "卡住的環節": [...6個...], "故事切角": [...8個...]}
若檔案不存在則跳過集合檢查並提醒。
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

C, M, B = "共鳴故事", "方法拆解", "收網"
EXPECT_PER_MONTH = 8
MIN_C = 3
MAX_B = 3
UNIQUE_COLS = ["受眾身分", "卡住的環節", "故事切角"]
PLACEHOLDER = {"—", "-", "", "—　"}


def load_sets(csv_path):
 p = os.path.join(os.path.dirname(os.path.abspath(csv_path)), "sets.json")
 if not os.path.exists(p):
 return None
 with open(p, encoding="utf-8") as f:
 return json.load(f)


def main(path):
 with open(path, encoding="utf-8-sig") as f:
 rows = list(csv.DictReader(f))
 if not rows:
 sys.exit("錯誤：CSV 沒有資料列")

 sets = load_sets(path)
 errors, warnings = [], []

 if sets is None:
 warnings.append("找不到 sets.json，略過封閉集合檢查")
 else:
 for col, expected_n in (("受眾身分", 6), ("卡住的環節", 6), ("故事切角", 8)):
 vals = sets.get(col)
 if vals is None:
 errors.append(f"sets.json 缺少「{col}」")
 elif len(vals) != expected_n:
 errors.append(f"「{col}」應有 {expected_n} 個值，實際 {len(vals)} 個")

 by_month = defaultdict(list)
 for i, r in enumerate(rows, start=2):
 month = (r.get("月") or "").strip()
 if not month:
 errors.append(f"第 {i} 列：缺少「月」")
 continue
 by_month[month].append((i, r))

 if sets:
 for col in UNIQUE_COLS:
 v = (r.get(col) or "").strip()
 if v in PLACEHOLDER:
 continue
 if col in sets and v not in sets[col]:
 errors.append(f"第 {i} 列：「{col}」的值「{v}」不在封閉集合裡")

 for month in sorted(by_month, key=lambda x: (len(x), x)):
 entries = by_month[month]
 types = Counter((r.get("類型") or "").strip() for _, r in entries)
 total = len(entries)

 if total != EXPECT_PER_MONTH:
 errors.append(f"M{month}：合計 {total} 篇，應為 {EXPECT_PER_MONTH}")
 if types[C] < MIN_C:
 errors.append(f"M{month}：共鳴故事 {types[C]} 篇，硬規則要求 >= {MIN_C}")
 if types[B] > MAX_B:
 errors.append(f"M{month}：收網 {types[B]} 篇，硬規則要求 <= {MAX_B}")

 unknown = set(types) - {C, M, B}
 for u in unknown:
 errors.append(f"M{month}：出現未知類型「{u}」")

 for col in UNIQUE_COLS:
 vals = [(r.get(col) or "").strip() for _, r in entries]
 vals = [v for v in vals if v not in PLACEHOLDER]
 dup = [v for v, n in Counter(vals).items() if n > 1]
 if dup:
 warnings.append(f"M{month}：「{col}」同月重複 → {'、'.join(dup)}")

 print(f"{'月':>4} {'共鳴':>5} {'方法':>5} {'收網':>5} {'合計':>5}")
 q_totals = Counter()
 for month in sorted(by_month, key=lambda x: int(x) if x.isdigit() else 99):
 t = Counter((r.get("類型") or "").strip() for _, r in by_month[month])
 print(f"{month:>4} {t[C]:>5} {t[M]:>5} {t[B]:>5} {sum(t.values()):>5}")
 if month.isdigit():
 q = (int(month) - 1) // 3 + 1
 q_totals[q] += sum(t.values())
 for q in sorted(q_totals):
 flag = "" if q_totals[q] == 24 else " ← 應為 24"
 print(f"Q{q} 合計 {q_totals[q]} 支{flag}")

 if warnings:
 print("\n提醒：")
 for w in warnings:
 print(f" · {w}")

 if errors:
 print("\n違規（必須修正）：")
 for e in errors:
 print(f" ✗ {e}")
 sys.exit(1)

 print("\n✓ 比例與集合全部通過")


if __name__ == "__main__":
 if len(sys.argv) != 2:
 sys.exit(__doc__)
 main(sys.argv[1])
