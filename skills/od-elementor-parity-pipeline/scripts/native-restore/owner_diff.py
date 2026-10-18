"""會後部署前：抓 10 份正式內容，和切換時寫入的 n-*.json 逐元件比對，列出業主改過的地方。"""
import json, subprocess, sys
subprocess.run(['python3', 'nv-get.py', 'payloads/341-live-data.php', 'native/cmp/live-now.json'], check=True, capture_output=True)
live = json.load(open('native/cmp/live-now.json'))
def flat(els, o=None):
    o = {} if o is None else o
    for e in els: o[e['id']] = e; flat(e.get('elements', []), o)
    return o
SKIP = {'_attributes', '_css_classes'}
changed = {}
for pid, data in live.items():
    base = open(f'native/n-{pid}.json').read()
    if data == base:
        print(pid, '沒有修改'); continue
    a, b = flat(json.loads(base)), flat(json.loads(data))
    rows = []
    for i in sorted(set(a) | set(b)):
        if i not in b: rows.append((i, '被刪除', a[i]['settings'].get('_title', ''), '')); continue
        if i not in a: rows.append((i, '新增', b[i].get('widgetType', b[i]['elType']), json.dumps(b[i]['settings'], ensure_ascii=False)[:200])); continue
        sa, sb = a[i]['settings'], b[i]['settings']
        for k in sorted(set(sa) | set(sb)):
            if sa.get(k) != sb.get(k):
                rows.append((i, k, json.dumps(sa.get(k), ensure_ascii=False)[:160], json.dumps(sb.get(k), ensure_ascii=False)[:160]))
        if [c['id'] for c in a[i].get('elements', [])] != [c['id'] for c in b[i].get('elements', [])]:
            rows.append((i, '子元件順序', '', ''))
    changed[pid] = rows
    print(pid, '有修改', len(rows), '處')
    for r in rows[:30]: print('   ', ' | '.join(r))
json.dump(changed, open('native/cmp/owner-changes.json', 'w'), ensure_ascii=False, indent=1)
