"""建立三張純色假圖與座標，僅驗證產生器，不可作為真實教學素材。"""
import argparse
import json
import struct
import zlib
from common import load_config, project_path


def png(color):
 def chunk(kind, body):
 data = kind + body
 return struct.pack('>I', len(body)) + data + struct.pack('>I', zlib.crc32(data) & 0xffffffff)
 pixels = (b'\x00' + bytes(color)*2560)*1720
 return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 2560,1720,8,2,0,0,0)) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


def make(config):
 base, cfg = load_config(config)
 directory = project_path(base, cfg['imgdir'])
 directory.mkdir(parents=True, exist_ok=True)
 path = project_path(base, cfg['manifest'])
 images = [directory / f'fixture-{i}.png' for i in range(3)]
 if path.exists() or any(image.exists() for image in images):
 raise FileExistsError('只允許在尚無清單與假圖的測試專案建立，不覆蓋既有素材')
 for image, color in zip(images, [(220,230,220),(210,220,235),(230,220,210)]):
 image.write_bytes(png(color))
 manifest = {}
 for sc in cfg['scenarios']:
 steps = []
 for i in range(sc['count']):
 step = {'tt': f'測試步驟 {i+1}', 'dd': '純色假素材，僅供產生器測試。', 'click': True, 'z': 1.6, 'live': i == 1, 'fixture': True}
 for phase, image in zip(('pre','mid','post'),images):
 if phase == 'mid' and not step['live']:
 continue
 step[phase] = {'img': image.relative_to(base).as_posix(), 'r': {'x': 280+i*60, 'y': 230+i*70, 'w': 260, 'h': 80}}
 steps.append(step)
 manifest[sc['id']] = {'h': sc['title'], 'p': sc['description'], 'steps': steps, 'fixture': True}
 path.parent.mkdir(parents=True, exist_ok=True)
 path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('三張 2560×1720 假圖與清單已建立；不可作為正式素材')


if __name__ == '__main__':
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('config')
 make(parser.parse_args().config)
