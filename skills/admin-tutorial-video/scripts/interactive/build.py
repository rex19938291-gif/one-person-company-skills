"""以通用設定產生逐步教學；圖片各自存成 JPG，不嵌入頁面。"""
import argparse
import html
import json
from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import load_config, project_path, validate_manifest, display_rect, fitted_zoom


def build(config):
    base,cfg=load_config(config)
    manifest=json.loads(project_path(base,cfg['manifest']).read_text())
    validate_manifest(cfg,manifest)
    out=project_path(base,cfg['interactive']);(out/'img').mkdir(parents=True,exist_ok=True)
    scenes={};size=0
    for sc in cfg['scenarios']:
        rows=[]
        for i,step in enumerate(manifest[sc['id']]['steps']):
            ov=cfg['overrides'].get(f"{sc['id']},{i}",{})
            row={'tt':ov.get('tt',step['tt']),'dd':ov.get('dd',step['dd']),
                 'locp':ov.get('locp',cfg.get('locp','後台 ›')),'loc':ov.get('loc',cfg.get('loc',{}).get(sc['id'],sc['title'])),
                 'click':step['click'],'chips':ov.get('chips',[]),'dur':ov.get('dur',cfg['timing']['step'])}
            for phase in ('pre','mid','post'):
                if not step.get(phase):continue
                dest=out/'img'/f"{sc['id']}-{i:03d}-{phase}.jpg"
                with Image.open(project_path(base,step[phase]['img'])) as image:
                    image=image.convert('RGB');image.thumbnail((1600,1075));image.save(dest,quality=60,optimize=True)
                size+=dest.stat().st_size
                rect=display_rect(cfg,ov.get('menu_rect',cfg['overview']['menu_rect']) if i==0 else step[phase]['r'])
                row[phase]={'img':dest.relative_to(out).as_posix(),'r':rect}
            row['z']=fitted_zoom(cfg,step['z'],row['pre']['r'],i==0)
            row['spotZ']=fitted_zoom(cfg,step.get('spotZ') or step['z'],row['post']['r'],i==0)
            rows.append(row)
        scenes[sc['id']]={'h':sc['title'],'p':sc['description'],'must':sc.get('must',''),'steps':rows}
    data={'title':cfg['title'],'sub':cfg['sub'],'capW':1280,'capH':860,'scenes':scenes,'notes':cfg['outro']}
    theme=dict(cfg['theme']);theme.update(panel=theme['paper'],line=theme['grid'],soft=theme['bg'])
    css=';'.join(f'--{k}:{v}' for k,v in theme.items())
    page=(Path(__file__).with_name('player.html').read_text().replace('__TITLE__',html.escape(cfg['title']))
          .replace('__THEME__',css).replace('__BG__',theme['bg'])
          .replace('__MANIFEST__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')))
    if size+len(page.encode())>cfg.get('interactive_max_mb',6)*1_000_000:
        raise ValueError('互動版超過容量上限，請壓縮圖片或拆段')
    (out/'index.html').write_text(page)
    print('互動版完成，共',sum(len(s['steps']) for s in scenes.values()),'步')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');build(p.parse_args().config)
