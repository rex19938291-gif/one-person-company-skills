import sys,json,re,difflib
d=json.load(open(sys.argv[1])); pairs=json.loads(sys.argv[2])
def norm(s,i):
    s=re.sub(r'<div id="wpadminbar".*?<!-- #wpadminbar -->|<div id="wpadminbar".*?</div>\s*</div>\s*(?=<)', '', s, flags=re.S)
    s=s.replace(str(i),'PID'); s=re.sub(r'(page-id-|postid-)\d+',r'\1N',s); s=re.sub(r'nrr(=|%3D)\d+','',s); s=re.sub(r'\b[0-9a-f]{10}\b','H',s)
    return re.sub(r'>\s*<','>\n<',s).split('\n')
for a,b in pairs:
    x,y=norm(d[str(a)]['a'],a),norm(d[str(a)]['b'],b)
    df=[l for l in difflib.unified_diff(x,y,lineterm='',n=0) if l[:1] in '+-' and l[:3] not in ('---','+++')]
    df=[l for l in df if not re.search(r"ab-|wp-admin-bar|wpadminbar|^[-+]</(li|ul|div|span)>$|^[-+]<(ul|div) role|^[-+]</span>標記|ab-submenu",l)]
    print(a,b,'剩餘差異',len(df))
    for l in df[:20]: print('   ',l[:240])
