"""產生可逐步操作的互動教學頁；使用同一份設定、清單與素材。"""
import argparse
import html
import json
import shutil
from common import load_config, project_path, validate_manifest


def build(config):
 base, cfg = load_config(config)
 manifest = json.loads(project_path(base, cfg['manifest']).read_text(encoding='utf-8'))
 validate_manifest(cfg, manifest)
 out = project_path(base, cfg['interactive'])
 (out / 'assets').mkdir(parents=True, exist_ok=True)
 rows, total_bytes = [], 0
 for sc in cfg['scenarios']:
 for i, step in enumerate(manifest[sc['id']]['steps']):
 override = cfg['overrides'].get(f"{sc['id']},{i}", {})
 row = {'title': override.get('tt', step['tt']), 'description': override.get('dd', step['dd']), 'scenario': sc['title']}
 for phase in ('pre', 'mid', 'post'):
 if not step.get(phase):
 continue
 source = project_path(base, step[phase]['img'])
 dest = out / 'assets' / f"{sc['id']}-{i:03d}-{phase}{source.suffix}"
 try:
 from PIL import Image
 except ImportError:
 shutil.copyfile(source, dest)
 else:
 dest = dest.with_suffix('.jpg')
 with Image.open(source) as image:
 image = image.convert('RGB')
 image.thumbnail((1024, 688))
 image.save(dest, quality=45)
 total_bytes += dest.stat().st_size
 row[phase] = {'img': dest.relative_to(out).as_posix(), 'r': step[phase]['r']}
 rows.append(row)
 data = json.dumps(rows, ensure_ascii=False).replace('<', '\\u003c')
 title = html.escape(cfg['title'])
 page = f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>{title}</title><style>body{{margin:0;padding:24px;background:#f6f7f3;color:#14201b;font:18px/1.6 sans-serif}}main{{max-width:1280px;margin:auto}}button,select{{font:inherit;padding:8px;max-width:100%}}.screen{{position:relative}}img{{display:block;width:100%}}#focus{{position:absolute;border:3px solid #d93a2b;box-sizing:border-box;pointer-events:none}}nav{{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}}</style>
<main><h1>{title}</h1><p>示意資料；此頁不會操作原網站。</p><select id="step" aria-label="選擇步驟"></select><h2 id="title"></h2><p id="description"></p><nav><button id="previous">上一步</button><button id="next">下一步</button><select id="phase" aria-label="拍攝階段"></select></nav><div class="screen"><img id="image" alt="後台操作畫面"><div id="focus"></div></div></main>
<script>const rows={data};let index=0;const el=id=>document.getElementById(id);rows.forEach((r,i)=>{{const o=document.createElement('option');o.value=i;o.textContent=r.scenario+'・'+(i+1)+'・'+r.title;el('step').append(o)}});function show(){{const r=rows[index];el('step').value=index;el('title').textContent=r.title;el('description').textContent=r.description;el('phase').replaceChildren();for(const p of ['pre','mid','post'])if(r[p]){{const o=document.createElement('option');o.value=p;o.textContent={{pre:'按下前',mid:'展開中',post:'按下後'}}[p];el('phase').append(o)}}el('previous').disabled=index===0;el('next').disabled=index===rows.length-1;draw()}}function draw(){{const p=rows[index][el('phase').value],r=p.r;el('image').src=p.img;Object.assign(el('focus').style,{{left:r.x/1280*100+'%',top:r.y/860*100+'%',width:r.w/1280*100+'%',height:r.h/860*100+'%'}})}}el('step').onchange=e=>{{index=Number(e.target.value);show()}};el('phase').onchange=draw;el('previous').onclick=()=>{{index=Math.max(0,index-1);show()}};el('next').onclick=()=>{{index=Math.min(rows.length-1,index+1);show()}};show();</script></html>'''
 size = total_bytes + len(page.encode('utf-8'))
 if size > cfg.get('interactive_max_mb', 6)*1_000_000:
 raise ValueError('互動版超過容量上限，請使用圖片壓縮或拆成多個情境；尚未產生頁面')
 (out / 'index.html').write_text(page, encoding='utf-8')
 print(f"互動版完成，共 {len(rows)} 步，含素材約 {size/1_000_000:.2f} MB")


if __name__ == '__main__':
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('config')
 build(parser.parse_args().config)
