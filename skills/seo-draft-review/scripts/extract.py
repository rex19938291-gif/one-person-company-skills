#!/usr/bin/env python3
"""抽出文章的標題結構、段落、表格與圖片序列，供初稿排查比對。

用法：
 python3 extract.py <輸出前綴> <網址> [<網址> ...]

產出（寫在目前目錄）：
 <前綴>_<n>.html 原始 HTML（不要讀進對話）
 txt_<前綴>_<n>.txt 依序的 [tag]\t內容
 img_<前綴>_<n>.txt 只含內文圖片，標註所在章節與 alt

之後：
 grep -E "^\\[(h1|h2|h3)\\]" txt_*.txt 看結構
 圖片逐張下載，先 sips -Z 1100 縮圖再看，一次一張。
"""
import html
import re
import subprocess
import sys

TAGS = r"h1|h2|h3|h4|p|li|td|th|blockquote|img"
SKIP_IMG = re.compile(r"150x150|768x576|1024x768|logo|gravatar|\.svg|data:image")


def strip(s: str) -> str:
 return html.unescape(re.sub(r"(?s)<[^>]+>", "", s)).strip()


def run(prefix: str, urls: list[str]) -> None:
 for i, url in enumerate(urls, 1):
 raw = f"{prefix}_{i}.html"
 subprocess.run(
 ["curl", "-sL", "-A", "Mozilla/5.0", url, "-o", raw], check=True
 )
 s = open(raw, encoding="utf-8", errors="ignore").read()
 s = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", s)

 # 兩次掃描再依位置合併：文字標籤的 (.*?)</tag> 會吞掉巢狀的 <img>，
 # 所以圖片必須單獨掃一遍，否則放在段落裡的圖會整批消失。
 found = []
 for m in re.finditer(rf"(?is)<({TAGS})\b([^>]*)>(?:(.*?)</\1>)?", s):
 found.append((m.start(), m.group(1).lower(), m.group(2) or "", m.group(3) or ""))
 for m in re.finditer(r"(?is)<img\b([^>]*)>", s):
 found.append((m.start(), "img", m.group(1), ""))

 seq, imgs, ctx, seen = [], [], "", set()
 for pos, tag, attrs, inner in sorted(found, key=lambda x: x[0]):
 if (pos, tag) in seen:
 continue
 seen.add((pos, tag))
 if tag == "img":
 src = re.search(r'(?is)\bsrc=["\']([^"\']+)', attrs)
 alt = re.search(r'(?is)\balt=["\']([^"\']*)', attrs)
 src = src.group(1) if src else ""
 if src.startswith("data:"):
 d = re.search(r'(?is)\bdata-src=["\']([^"\']+)', attrs)
 src = d.group(1) if d else src
 if src and not SKIP_IMG.search(src) and src not in {i[1] for i in imgs}:
 imgs.append((ctx, src, alt.group(1) if alt else ""))
 seq.append(f"[img]\t{src}")
 continue
 t = strip(inner)
 if not t:
 continue
 if tag in ("h1", "h2", "h3"):
 ctx = f"{tag}: {t}"
 seq.append(f"[{tag}]\t{t}")
 imgs = [f"[{c}]\t{u}\tALT={a}" for c, u, a in imgs]

 open(f"txt_{prefix}_{i}.txt", "w", encoding="utf-8").write("\n".join(seq))
 open(f"img_{prefix}_{i}.txt", "w", encoding="utf-8").write("\n".join(imgs))
 print(f"{raw}: {len(seq)} 個區塊, {len(imgs)} 張內文圖片")


if __name__ == "__main__":
 if len(sys.argv) < 3:
 sys.exit(__doc__)
 run(sys.argv[1], sys.argv[2:])
