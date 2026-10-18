"""孤字修正：依 WebKit 檢查結果，把句尾幾個字包成不斷行。只改元件設定裡的文字，不動樣板。
用法：python3 orphanfix.py <頁面代號> <輸入 n3.json> <輸出 n4.json>"""
import json, re, sys, glob, html
PAGE = {'home': '27575', 'story': '31152', 'career': '31155', 'terms-2': '27927', 'privacy-policy-2': '3', 'yuanlin': '31296', 'changhua': '31299', 'beitun': '31302'}
page, src, dst = sys.argv[1:4]
targets = {}
for line in open(f'wk/{page}.txt'):
    u, w, o, l = line.rstrip('\n').split('|', 3)
    try:
        for s in json.loads(o):
            full = s.replace(' ｜ ', ''); tail = s.split(' ｜ ')[-1]
            targets[full] = max(targets.get(full, 0), len(tail))
    except Exception:
        pass
NW = '<span style="white-space: nowrap;">'
def plain(h): return html.unescape(re.sub(r'<[^>]+>', '', h))
def wrap(h, k):
    # 從尾端往回數 k 個可見字；遇到標籤整個跳過（不算字數）
    i = len(h); n = 0
    while i > 0 and n < k:
        if h[i-1] == '>':
            i = h[:i].rfind('<'); continue
        if h[i-1] == ';' and re.search(r'&[#\w]+;$', h[:i]):
            i = h[:i].rfind('&'); n += 1; continue
        i -= 1; n += 1
    if n < k: return None
    # 起點若落在某個元素裡面（後面有它的結尾標籤），往前移到該元素的開頭標籤
    while True:
        depth = {}; moved = False
        for m in re.finditer(r'<(/?)([a-z0-9]+)\b[^>]*>', h[i:]):
            tag = m.group(2)
            if m.group(1): 
                if depth.get(tag, 0) > 0: depth[tag] -= 1
                else:
                    j = h[:i].rfind('<' + tag)
                    if j < 0: return None
                    i = j; moved = True; break
            elif not m.group(0).endswith('/>') and tag not in ('br', 'img', 'wbr'):
                depth[tag] = depth.get(tag, 0) + 1
        if not moved: break
    return h[:i] + NW + h[i:] + '</span>'
done, miss = [], []
els = json.load(open(src))
def fix_val(v):
    if v.count('<p') > 1:
        parts = re.split(r'(<p\b[^>]*>.*?</p>)', v, flags=re.S)
        return ''.join(fix_one(x) if x.startswith('<p') else x for x in parts)
    return fix_one(v)
def fix_one(v):
    t = re.sub(r'\s+', '', plain(v))
    for full, tl in list(targets.items()):
        if t == re.sub(r'\s+', '', full):
            core = v.rstrip()
            m = re.search(r'(</p>)\s*$', core)
            body, end = (core[:m.start()], core[m.start():]) if m else (core, '')
            nw = wrap(body, tl + 3)
            if nw:
                done.append(full[:24]); targets.pop(full); return nw + end
    return v
def walk(es):
    for e in es:
        s = e['settings']
        for k in ('title', 'editor', 'text'):
            if isinstance(s.get(k), str): s[k] = fix_val(s[k])
        for rep in ('tabs', 'icon_list'):
            for it in s.get(rep) or []:
                for k in ('tab_title', 'tab_content', 'text'):
                    if isinstance(it.get(k), str): it[k] = fix_val(it[k])
        walk(e.get('elements', []))
walk(els)
json.dump(els, open(dst, 'w'), ensure_ascii=False)
print(page, '已修', len(done), '未找到／未改', len(targets), [t[:24] for t in targets])
