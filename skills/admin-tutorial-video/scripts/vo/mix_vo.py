"""依 timing.json 排旁白並混音，保留影片編碼。可選 STEM=前綴 輸出分軌供量測。
用法：mix_vo.py vo/ silent.mp4 output.mp4 [速度=1.15] [音樂.wav]
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess


def mix(vodir, video, output, speed=1.15, music=None):
    vodir = Path(vodir)
    if Path(video).resolve() == Path(output).resolve():
        raise ValueError('輸出不可覆蓋輸入影片')
    if speed != 1.15:
        raise ValueError('須與產生器一致，旁白速度固定 1.15')
    tm = json.loads((vodir/'timing.json').read_text())
    total = tm['total']
    if not isinstance(total, (int, float)) or not math.isfinite(total) or total <= 0:
        raise ValueError('影片秒數不正確')
    lines_path, transcript_path = vodir/'lines.json', vodir/'transcripts.json'
    if lines_path.exists():
        transcripts = json.loads(transcript_path.read_text())
        for line in json.loads(lines_path.read_text()):
            if transcripts.get(line['id'], {}).get('text') != line['text']:
                raise ValueError('旁白稿與錄音不一致，請重錄：'+line['id'])
    items = sorted(tm['at'].items(), key=lambda x: x[1])
    if not items:
        raise ValueError('沒有旁白時間點')
    for key, at in items:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', key) or not isinstance(at, (int, float)) or not math.isfinite(at) or not 0 <= at < total:
            raise ValueError('旁白識別或時間點不正確')
        if not (vodir/(key+'.wav')).is_file():
            raise FileNotFoundError('缺少錄音：'+key)
        sec = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(vodir/(key+'.wav'))],capture_output=True,text=True,check=True).stdout)
        if at + sec / speed > total:
            raise ValueError('錄音超出影片，請重新產生秒數：'+key)
    args = ['ffmpeg','-hide_banner','-loglevel','error','-n','-i',str(video)]
    fc = []
    for n, (key, at) in enumerate(items, 1):
        args += ['-i',str(vodir/(key+'.wav'))]
        fc.append(f'[{n}:a]atempo={speed},aresample=48000,adelay={round(at*1000)}:all=1[a{n}]')
    inputs = ''.join(f'[a{i}]' for i in range(1,len(items)+1))
    fc.append(f'{inputs}amix=inputs={len(items)}:normalize=0,apad,atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[voice]')
    stem = os.environ.get('STEM')
    if music:
        args += ['-stream_loop','-1','-i',str(music)]
        fc.append('[voice]asplit=2[voiceMix][detector]')
        fc.append(f'[{len(items)+1}:a]aresample=48000,atrim=0:{total},loudnorm=I=-24.7:TP=-9:LRA=7,aresample=48000[bg0]')
        fc.append('[bg0][detector]sidechaincompress=threshold=0.03:ratio=3:attack=40:release=800[bg]')
        if stem:
            fc += ['[voiceMix]asplit=2[vstem][vsum]', '[bg]asplit=2[bstem][bsum]', '[vsum][bsum]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.9:level=0[final]']
        else:
            fc.append('[voiceMix][bg]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.9:level=0[final]')
    elif stem:
        fc.append('[voice]asplit=2[vstem][final]')
    else:
        fc.append('[voice]anull[final]')
    args += ['-filter_complex',';'.join(fc),'-map','0:v:0','-map','[final]','-c:v','copy','-c:a','aac','-b:a','128k','-ac','2','-t',str(total),'-movflags','+faststart',str(output)]
    if stem:
        args += ['-map','[vstem]','-c:a','pcm_s16le','-t',str(total),stem+'-vo.wav']
        if music:
            args += ['-map','[bstem]','-c:a','pcm_s16le','-t',str(total),stem+'-bg.wav']
    subprocess.run(args, check=True)
    print('混音完成，共',len(items),'句')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('vodir');p.add_argument('video');p.add_argument('output')
    p.add_argument('speed',type=float,nargs='?',default=1.15);p.add_argument('music',nargs='?')
    a = p.parse_args();mix(a.vodir,a.video,a.output,a.speed,a.music)
