"""由轉換後的元素樹產生編輯預覽專用 CSS：每個容器／原生元件的原始行內樣式 → 以元素 id 為選擇器的規則。"""
import json, re, sys, base64, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dom import DomBuilder, Node
P = '.elementor-editor-active .elementor .elementor-element.elementor-element-'
def attrs(st):
    out = {}
    for line in (st.get('_attributes') or '').split('\n'):
        if '|' in line:
            k, v = line.split('|', 1); out[k.strip()] = v
    return out
def st_of(n):
    return (dict(n.attrs).get('style') or '').strip().rstrip(';').replace('{', '').replace('}', '')
def first(n, tag):
    for c in n.elements():
        if c.tag == tag: return c
        x = first(c, tag)
        if x is not None: return x
    return None
def parse(h):
    b = DomBuilder(); b.feed(re.sub(r'\{\{[^}]*\}\}', 'X', h)); return b.root
def rep_rules(i, wt, tpl):
    r = parse(tpl); S = P + i; out = []
    if wt == 'toggle':
        out.append(f"{S} .elementor-toggle-item{{margin:0;border:0}}")
        out.append(f"{S} .elementor-tab-title{{padding:0;border:0;font:inherit;color:inherit}}")
        out.append(f"{S} .elementor-tab-title .elementor-toggle-icon{{display:none}}")
        out.append(f"{S} .elementor-tab-content{{padding:0;border:0}}")
        d = first(r, 'details')
        if d is not None:
            sm, h3, p = first(d, 'summary'), first(d, 'h3'), first(d, 'p')
            out.append(f"{S} .elementor-toggle-item{{{st_of(d)}}}")
            if sm is not None: out.append(f"{S} .elementor-tab-title{{{st_of(sm)}}}")
            if h3 is not None: out.append(f"{S} .elementor-toggle-title{{{st_of(h3)};display:block}}")
            if p is not None: out.append(f"{S} .elementor-tab-content{{{st_of(p)}}}")
        dl = first(r, 'dl')
        if dl is not None:
            row, dt, dd = first(dl, 'div'), first(dl, 'dt'), first(dl, 'dd')
            out.append(f"{S} .elementor-toggle{{{st_of(dl)}}}")
            if row is not None: out.append(f"{S} .elementor-toggle-item{{{st_of(row)}}}")
            if dt is not None: out.append(f"{S} .elementor-tab-title{{{st_of(dt)};cursor:default}}")
            if dd is not None: out.append(f"{S} .elementor-tab-content{{{st_of(dd)};display:block!important}}")
    else:
        lst = first(r, 'ol') or first(r, 'ul'); li = first(r, 'li')
        if lst is not None: out.append(f"{S} .elementor-icon-list-items{{{st_of(lst)}}}")
        if li is not None:
            out.append(f"{S} .elementor-icon-list-item{{{st_of(li)};margin:0}}")
            sp = [c for c in li.elements() if c.tag == 'span']
            if sp: out.append(f"{S} .elementor-icon-list-text{{{st_of(sp[-1])};padding:0}}")
        out.append(f"{S} .elementor-icon-list-icon{{display:none}}")
    return out
def fig_rules(i, tpl):
    r = parse(tpl); S = P + i; out = []
    fc = first(r, 'figcaption'); img = first(r, 'img')
    out.append(f"{S} figure.wp-caption{{margin:0;display:flex;flex-direction:column;gap:14px}}")
    out.append(f"{S} img{{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover}}")
    if fc is not None: out.append(f"{S} figcaption{{{st_of(fc)};margin:0;text-align:inherit}}")
    return out

def gen(els):
    rules = []
    def walk(es):
        for e in es:
            s = e['settings']; a = attrs(s)
            sty = (a.get('style') or '').strip().rstrip(';')
            if sty and '{' not in sty and '}' not in sty:
                rules.append(f"{P}{e['id']}{{{sty}}}")
            wt = e.get('widgetType')
            if e['elType'] == 'widget' and wt in ('toggle', 'icon-list') and a.get('data-zbt'):
                rules.extend(rep_rules(e['id'], wt, base64.b64decode(a['data-zbt']).decode()))
            if e['elType'] == 'widget' and wt == 'image' and 'data-zbfig' in a:
                rules.extend(fig_rules(e['id'], base64.b64decode(a['data-zbt']).decode()))
            if e['elType'] == 'widget' and e.get('widgetType') == 'image':
                fill = 'data-zbfill' in a
                rules.append(f"{P}{e['id']} img{{display:block;{'width:100%;height:100%' if fill else 'height:100%;width:auto;max-width:none'};object-fit:inherit;object-position:inherit;border-radius:inherit}}")
            walk(e.get('elements', []))
    walk(els)
    return '\n'.join(rules)
if __name__ == '__main__':
    print(gen(json.load(open(sys.argv[1]))))
