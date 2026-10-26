import sys,json,re,difflib,subprocess
pairs=json.loads(sys.argv[1]); tag=sys.argv[2]
php=open('payloads/256-render-cmp.php').read()
php=re.sub(r'\$pairs=.*?;\n','$pairs='+ '['+','.join(f'[{a},{b}]' for a,b in pairs)+'];\n',php,count=1)
php=php.replace("preg_match('#<main\\b.*</main>#s',$h,$m); $out[$a][$k]=$m[0]??('NOMAIN '.substr($h,0,300));","preg_match('#<body\\b.*</body>#s',$h,$m); $out[$a][$k]=$m[0]??('NOBODY '.substr($h,0,300));")
open('payloads/259-render-cmp-body.php','w').write(php)
subprocess.run(['python3','nv-get.py','payloads/259-render-cmp-body.php',f'native/cmp/{tag}.json'],check=True)
d=json.load(open(f'native/cmp/{tag}.json'))
def norm(s,i): 
    s=s.replace(str(i),'PID'); s=re.sub(r'(page-id-|postid-)\d+',r'\1N',s); s=re.sub(r'nrr=\d+','',s); s=re.sub(r'\b[0-9a-f]{10}\b','H',s)
    return re.sub(r'>\s*<','>\n<',s).split('\n')
for a,b in pairs:
    x,y=norm(d[str(a)]['a'],a),norm(d[str(a)]['b'],b)
    df=[l for l in difflib.unified_diff(x,y,lineterm='',n=0) if l[:1] in '+-' and l[:3] not in ('---','+++')]
    print(a,b,'行數',len(x),len(y),'差異行',len(df))
    for l in df[:16]: print('   ',l[:220])
