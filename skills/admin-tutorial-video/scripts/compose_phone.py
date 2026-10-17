"""把 390×844、三倍拍攝的手機圖合成至 3200×2150 畫布。
用法：compose_phone.py video.config.json input.png output.png [--rect rect.json --rect-output rect-out.json]
輸入框為手機 CSS 座標，輸出為 1600×1075 CSS 座標；產生器再乘 0.8。
"""
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw
from common import load_config, clip_rect


def canvas_rect(rect):
    if any(type(rect.get(k)) not in (int,float) or not math.isfinite(rect[k]) for k in ('x','y','w','h')) or not (0 <= rect['x'] < 390 and 0 <= rect['y'] < 844 and 0 < rect['w'] <= 390-rect['x'] and 0 < rect['h'] <= 844-rect['y']):
        raise ValueError('手機框須在 390×844 範圍內')
    return {'x':(1171+rect['x']*2.2)/2,'y':(146+rect['y']*(1857/844))/2,
            'w':rect['w']*1.1,'h':rect['h']*(1857/844)/2}


def compose(config, source, output, rect=None, rect_output=None):
    _, cfg=load_config(config)
    if (cfg['capture']['width'],cfg['capture']['height']) != (1600,1075):
        raise ValueError('合成素材須設定 capture 為 1600×1075、scale 2')
    if Path(source).resolve()==Path(output).resolve():
        raise ValueError('輸出不可覆蓋來源圖片')
    with Image.open(source) as image:
        if image.size!=(1170,2532):
            raise ValueError('手機圖須為 390×844、scale 3，實際 1170×2532')
        screen=image.convert('RGB').resize((858,1857),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(3200,2150),cfg['theme']['bg']);draw=ImageDraw.Draw(canvas)
    x,y=1171,146
    draw.rounded_rectangle((x-24,y-24,x+858+24,y+1857+24),radius=74,fill=cfg['theme']['phone_body'])
    mask=Image.new('L',screen.size,0);ImageDraw.Draw(mask).rounded_rectangle((0,0,857,1856),radius=54,fill=255)
    canvas.paste(screen,(x,y),mask);canvas.save(output)
    if rect:
        if not rect_output:raise ValueError('提供框座標時須指定 --rect-output')
        Path(rect_output).write_text(json.dumps(canvas_rect(json.loads(Path(rect).read_text())),indent=2)+'\n')
    print('手機外框合成完成')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');p.add_argument('source');p.add_argument('output');p.add_argument('--rect');p.add_argument('--rect-output')
    a=p.parse_args();compose(a.config,a.source,a.output,a.rect,a.rect_output)
