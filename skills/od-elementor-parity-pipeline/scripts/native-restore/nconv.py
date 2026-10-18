#!/usr/bin/env python3
"""zb-u 文字元件（整段網頁碼）→ 原生元件。前台由外掛 zb-native.php 依樣板 data-zbt 組回相同網頁碼。"""
import json, re, random, base64, sys, html as H
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dom import DomBuilder, Node, VOID

SVGV = {'path','circle','rect','line','polyline','polygon','use','stop','ellipse'}
def ea(v): return v.replace('&', '&amp;').replace('"', '&quot;')
def opentag(n, skip=()):
    return '<' + n.tag + ''.join((f' {k}' if v is None else f' {k}="{ea(v)}"') for k, v in n.attrs if k not in skip) + '>'
def ser(n):
    if isinstance(n, tuple): return n[1]
    s = opentag(n)
    if n.tag in VOID and not n.children:
        return s[:-1] + '></' + n.tag + '>' if n.tag in SVGV else s
    return s + inner(n) + f'</{n.tag}>'
def inner(n): return ''.join(ser(c) for c in n.children)
def close(n): return f'</{n.tag}>'
def text_of(n):
    if isinstance(n, tuple): return H.unescape(n[1])
    return ''.join(text_of(c) for c in n.children)

INLINE = {'span','br','strong','em','b','i','small','mark','sup','sub','wbr'}
def inline_only(n, a=False):
    return all(isinstance(c, tuple) or ((c.tag in INLINE or (a and c.tag == 'a')) and inline_only(c, a)) for c in n.children)
def has_text(n): return bool(text_of(n).strip())

HEX = '0123456789abcdef'
USED = set()
def eid():
    while True:
        x = ''.join(random.choice(HEX) for _ in range(7))
        if x not in USED:
            USED.add(x); return x
def b64(s): return base64.b64encode(s.encode()).decode()

ATT = {}
def att_id(src):
    m = re.search(r'/wp-content/uploads/([^"\s?]+)', src or '')  # 對應媒體庫 _wp_attached_file
    return ATT.get(m.group(1)) if m else None

STATS = {}
def stat(k): STATS[k] = STATS.get(k, 0) + 1

def title(s, prefix=''):
    t = re.sub(r'\s+', ' ', s).strip()
    return (prefix + t)[:24] or prefix.strip('：')

INL = {'span','a','button','img','strong','em','b','i','small','label'}
def edattrs(n):
    cls, eid_, lines = '', '', []
    if n is None: return cls, eid_, lines
    st = None
    for k, v in n.attrs:
        if k == 'class': cls = v or ''; continue
        if k == 'id': eid_ = v or ''; continue
        if k in ('href', 'src', 'srcset', 'sizes', 'alt', 'target', 'rel', 'loading', 'decoding', 'fetchpriority', 'width', 'height', 'data-zb-lazy'): continue
        if k == 'style': st = v or ''; continue
        if v is not None and ('\n' in v or '|' in v): continue
        lines.append(f'{k}|{"" if v is None else v}')
    st = st or ''
    if 'display' not in st:
        st = ('display: inline-block; ' if n.tag == 'img' else 'display: inline; ' if n.tag in INL else '') + st
    if st: lines.append('style|' + st)
    lines.append('data-zbtag|' + n.tag)
    return cls, eid_, lines

ZH = ['一','二','三','四','五','六','七','八','九','十','十一','十二']
def fill(tpl, st):
    def rows(m):
        out = ''
        parts = m.group(2).split('{{@rest}}', 1)
        for i, it in enumerate(st.get(m.group(1)) or []):
            body = parts[0] if i == 0 or len(parts) == 1 else parts[1]
            def r2(x):
                k = x.group(1)
                if k == '#zh': return ZH[i] if i < len(ZH) else str(i + 1)
                if k == '#n': return str(i + 1)
                v = it
                for kk in k.split('.'): v = v.get(kk, '') if isinstance(v, dict) else ''
                return ea(v.get('url', '')) if isinstance(v, dict) else str(v)
            out += re.sub(r'\{\{\.(#zh|#n|[a-z0-9_.]+)\}\}', r2, body)
        return out
    tpl = re.sub(r'\{\{@rows ([a-z0-9_]+)\}\}(.*?)\{\{/rows\}\}', rows, tpl, flags=re.S)
    def get(path):
        v = st
        for k in path.split('.'):
            v = v[int(k)] if isinstance(v, list) else v.get(k, '')
        return v
    def rep(m):
        v = get(m.group(1))
        return ea(v.get('url', '')) if isinstance(v, dict) else str(v)
    return re.sub(r'\{\{([a-z0-9_.]+)\}\}', rep, tpl)

def widget(wt, settings, tpl, extra_attrs=(), nav='', n=None):
    if n is not None:
        got = fill(tpl, settings)
        if got != ser(n): raise AssertionError('樣板還原不一致 ' + wt + ' ' + ser(n)[:160] + ' ≠ ' + got[:160])
    cls, eid_, el = edattrs(n)
    lines = ['data-zbt|' + b64(tpl)] + [f'{k}|{v}' for k, v in extra_attrs] + el
    st = {'_css_classes': ('zb-n ' + cls).strip(), '_attributes': '\n'.join(lines)}
    if eid_: st['_element_id'] = eid_
    if nav: st['_title'] = nav
    st.update(settings)
    stat(wt)
    return {'id': eid(), 'elType': 'widget', 'widgetType': wt, 'settings': st, 'elements': []}

def raw(h, nav):
    stat('raw')
    st = {'editor': h, '_css_classes': 'zb-u'}
    if nav: st['_title'] = nav
    return {'id': eid(), 'elType': 'widget', 'widgetType': 'text-editor', 'settings': st, 'elements': []}

def container(n, children, tag=None, link=None):
    st = {'content_width': 'full'}
    tag = tag or n.tag
    if tag != 'div': st['html_tag'] = tag
    lines = []
    for k, v in n.attrs:
        if k == 'class': st['css_classes'] = v; continue
        if k == 'id': st['_element_id'] = v; continue
        if tag == 'a' and k in ('href', 'target', 'rel'): continue
        if v is not None and ('\n' in v or '|' in v): raise ValueError(f'bad attr {k}')
        lines.append(f'{k}|{"" if v is None else v}')
    if lines: st['_attributes'] = '\n'.join(lines)
    if link: st['link'] = link
    stat('container')
    return {'id': eid(), 'elType': 'container', 'isInner': False, 'settings': st, 'elements': children}

def mklink(n):
    a = dict(n.attrs)
    return {'url': H.unescape(a.get('href') or ''), 'is_external': 'on' if a.get('target') == '_blank' else '', 'nofollow': '', 'custom_attributes': ''}

def href_tpl(n):
    # 原本的開頭標籤，href 換成 {{link}}
    return '<' + n.tag + ''.join(
        (f' {k}' if v is None else (f' {k}="{{{{link}}}}"' if k == 'href' else f' {k}="{ea(v)}"')) for k, v in n.attrs) + '>'

def walk_nodes(n):
    for c in n.elements():
        yield c
        yield from walk_nodes(c)

def conv(n):
    """回傳元件清單（可能 1 個或多個）"""
    if isinstance(n, tuple):
        m = re.fullmatch(r'(\s*)(\[zb_\w+[^\]]*\])(\s*)', n[1])
        if m:
            nm = {'zb_google_reviews': '自動：Google 評論', 'zb_ig_news': '自動：IG 最新消息', 'zb_ig_arrows': '自動：IG 左右箭頭', 'zb_store_rating': '自動：門市評分'}.get(re.match(r'\[(\w+)', m.group(2)).group(1), '自動區塊')
            w_ = widget('shortcode', {'shortcode': m.group(2)}, m.group(1) + '{{shortcode}}' + m.group(3), nav=nm)
            assert fill(m.group(1) + '{{shortcode}}' + m.group(3), w_['settings']) == n[1]
            return [w_]
        return [raw(n[1], '文字')] if n[1].strip() else []
    t = n.tag; a = dict(n.attrs)
    if t == 'img':
        src = a.get('src') or a.get('data-src') or ''
        i = att_id(src)
        if i is None: return [raw(ser(n), '照片（媒體庫外）')]
        return [widget('image', {'image': {'id': i, 'url': src, 'alt': a.get('alt', ''), 'source': 'library'}, 'image_size': 'full'},
                       ser(n), [('data-zbi', str(i))] + ([('data-zbfill', '1')] if re.search(r'(^|;)\s*width:\s*100%', a.get('style') or '') else []), title(a.get('alt', ''), '照片：'), n=n)]
    if not has_text(n) and not any(isinstance(c, Node) and c.tag in ('img',) for c in n.children) and not n.elements():
        return [raw(ser(n), '裝飾')]
    if t in ('h1','h2','h3','h4','h5','h6') or (t in ('span','div') and has_text(n) and inline_only(n)):
        return [widget('heading', {'title': inner(n), 'header_size': t}, opentag(n) + '{{title}}' + close(n), nav=title(text_of(n), '標題：' if t[0]=='h' else '文字：'), n=n)]
    if t == 'p' and inline_only(n, True):
        return [widget('text-editor', {'editor': inner(n)}, opentag(n) + '{{editor}}' + close(n), nav=title(text_of(n), '段落：'), n=n)]
    if t == 'button' and inline_only(n):
        return [widget('button', {'text': inner(n)}, opentag(n) + '{{text}}' + close(n), nav=title(text_of(n), '按鈕：'), n=n)]
    if t == 'a':
        if inline_only(n) or all(isinstance(c, tuple) or c.tag in INLINE or c.tag == 'svg' for c in n.children):
            kids = n.children
            svg_idx = [i for i, c in enumerate(kids) if isinstance(c, Node) and c.tag == 'svg']
            if svg_idx:
                before = ''.join(ser(c) for c in kids[:svg_idx[0]] if not (isinstance(c, Node) and c.tag == 'svg'))
                txt = ''.join(ser(c) for c in kids if not (isinstance(c, Node) and c.tag == 'svg'))
                svgs = ''.join(ser(kids[i]) for i in svg_idx)
                after = ''.join(ser(c) for c in kids[svg_idx[-1] + 1:])
                if before.strip() and after.strip():
                    return [raw(ser(n), '連結')]
                body = ('{{text}}' + svgs) if before.strip() else (svgs + '{{text}}')
                if len(svg_idx) > 1 and before.strip() and any(not (isinstance(c, Node) and c.tag == 'svg') and ser(c).strip() for c in kids[svg_idx[0]:]):
                    return [raw(ser(n), '連結')]
            else:
                txt, body = inner(n), '{{text}}'
            return [widget('button', {'text': txt, 'link': mklink(n)}, href_tpl(n) + body + close(n), nav=title(text_of(n), '按鈕：'), n=n)]
        # 卡片連結：容器（a 標籤）＋子元件
        return [container(n, sum((conv(c) for c in n.children), []), 'a', mklink(n))]
    if t == 'details':
        sm = [c for c in n.elements() if c.tag == 'summary']
        ps = [c for c in n.elements() if c.tag == 'p']
        if len(sm) == 1 and len(ps) == 1 and len(n.elements()) == 2:
            hs = [c for c in sm[0].elements() if c.tag in ('h3','h2','h4')]
            if len(hs) == 1 and len(sm[0].elements()) == 1 and inline_only(hs[0]) and inline_only(ps[0], True):
                h, p = hs[0], ps[0]
                tpl = '{{@rows tabs}}' + opentag(n) + opentag(sm[0]) + opentag(h) + '{{.tab_title}}' + close(h) + close(sm[0]) + opentag(p) + '{{.tab_content}}' + close(p) + close(n) + '{{/rows}}'
                ok = all(isinstance(c, Node) for c in n.children) and all(isinstance(c, Node) for c in sm[0].children)
                if ok:
                    return [widget('toggle', {'tabs': [{'_id': eid(), 'tab_title': inner(h), 'tab_content': inner(p)}]}, tpl, nav=title(text_of(h), '問答：'), n=n)]
        return [raw(ser(n), '問答')]
    if t == 'figure':
        imgs = [x for x in walk_nodes(n) if x.tag == 'img']
        caps = [c for c in n.elements() if c.tag == 'figcaption']
        if len(imgs) == 1 and len(caps) == 1 and inline_only(caps[0]):
            im = imgs[0]; a2 = dict(im.attrs); i = att_id(a2.get('src') or '')
            if i is not None:
                cap = caps[0]
                tpl = ser(n).replace(ser(cap), opentag(cap) + '{{caption}}' + close(cap), 1)
                return [widget('image', {'image': {'id': i, 'url': a2.get('src'), 'alt': a2.get('alt', ''), 'source': 'library'}, 'image_size': 'full',
                                         'caption_source': 'custom', 'caption': inner(cap)}, tpl, [('data-zbi', str(i)), ('data-zbfig', '1')], title(text_of(cap), '照片：'), n=n)]
        return [raw(ser(n), title(text_of(n), '網頁碼：'))]
    if t in ('ol', 'ul') and all(isinstance(c, Node) and c.tag == 'li' for c in n.children if not (isinstance(c, tuple) and not c[1].strip())):
        lis = n.elements()
        if lis and all(isinstance(c, Node) for c in n.children):
            k0 = lis[0].elements()
            if len(k0) == 2 and all(k.tag == 'span' for k in k0) and all(isinstance(c, Node) for c in lis[0].children):
                def rt(li):
                    k = li.elements()
                    if len(k) != 2 or not all(x.tag == 'span' for x in k) or not all(isinstance(c, Node) for c in li.children): return None
                    return opentag(li) + opentag(k[0]) + '{{.#zh}}' + close(k[0]) + opentag(k[1]) + '{{.text}}' + close(k[1]) + close(li)
                rts = [rt(li) for li in lis]
                rowtpl = None if None in rts else rts[0] if len(set(rts)) == 1 else (rts[0] + '{{@rest}}' + rts[1] if len(lis) > 1 and len(set(rts[1:])) == 1 else None)
                items = [{'_id': eid(), 'text': inner(li.elements()[1]) if len(li.elements()) == 2 else '', 'selected_icon': {'value': '', 'library': ''}} for li in lis]
            elif all(inline_only(li, True) for li in lis):
                rowtpl = opentag(lis[0]) + '{{.text}}' + close(lis[0])
                items = [{'_id': eid(), 'text': inner(li), 'selected_icon': {'value': '', 'library': ''}} for li in lis]
            else:
                rowtpl = None
            if rowtpl:
                tpl = opentag(n) + '{{@rows icon_list}}' + rowtpl + '{{/rows}}' + close(n)
                if fill(tpl, {'icon_list': items}) == ser(n):
                    return [widget('icon-list', {'icon_list': items}, tpl, nav=title(text_of(n), '清單：'), n=n)]
        if lis and all(inline_only(li, True) for li in lis):
            return [widget('text-editor', {'editor': ser(n)}, '{{editor}}', nav=title(text_of(n), '條列：'), n=n)]
        return [raw(ser(n), title(text_of(n), '網頁碼：'))]
    if t == 'dl':
        rws = n.elements()
        if rws and all(isinstance(c, Node) for c in n.children) and all(r.tag == 'div' and [c.tag for c in r.elements()] == ['dt', 'dd'] and all(isinstance(c, Node) for c in r.children) for r in rws):
            dt0, dd0 = rws[0].elements()
            rowtpl = opentag(rws[0]) + opentag(dt0) + '{{.tab_title}}' + close(dt0) + opentag(dd0) + '{{.tab_content}}' + close(dd0) + close(rws[0])
            items = [{'_id': eid(), 'tab_title': inner(r.elements()[0]), 'tab_content': inner(r.elements()[1])} for r in rws]
            tpl = opentag(n) + '{{@rows tabs}}' + rowtpl + '{{/rows}}' + close(n)
            if fill(tpl, {'tabs': items}) == ser(n):
                return [widget('toggle', {'tabs': items}, tpl, nav='門市資訊（欄位名稱／內容）', n=n)]
        return [raw(ser(n), '清單')]
    if t in ('div', 'section', 'figure') and t != 'figure' and all(isinstance(c, Node) or not c[1].strip() for c in n.children) and n.elements():
        return [container(n, sum((conv(c) for c in n.children), []))]
    return [raw(ser(n), title(text_of(n), '網頁碼：'))]

def conv_tree(els):
    out = []
    for e in els:
        if e['elType'] == 'widget' and e['widgetType'] == 'text-editor' and 'zb-u' in (e['settings'].get('_css_classes') or ''):
            h = e['settings']['editor']
            b = DomBuilder(); b.feed(h)
            assert inner(b.root) == h, 'roundtrip ' + h[:120]
            out += sum((conv(c) for c in b.root.children), [])
        elif e['elType'] == 'container':
            e = dict(e); e['elements'] = conv_tree(e['elements']); out.append(e)
        else:
            out.append(e)
    return out

if __name__ == '__main__':
    random.seed(20261017 * 100000 + int(sys.argv[3].lstrip("t") or 0))
    snap = json.load(open(sys.argv[1]))
    media = json.load(open(sys.argv[2]))
    for r in media['rows']: ATT[r['f']] = int(r['ID'])
    pid = sys.argv[3]
    src = json.loads(snap[pid]['data'])
    def _u(es):
        for e in es: USED.add(e['id']); _u(e.get('elements', []))
    _u(src)
    els = conv_tree(src)
    json.dump(els, open(sys.argv[4], 'w'), ensure_ascii=False)
    print(pid, STATS, len(json.dumps(els, ensure_ascii=False)))
