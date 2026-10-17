"""把已取得授權的音樂接成指定長度，接縫最多兩秒交叉淡化、片尾淡出。
用法：loop_bgm.py 音樂.mp3 秒數 輸出.wav；不會下載音樂。
"""
import argparse
import math
import subprocess


def loop(source, seconds, output):
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('目標秒數必須大於零')
    duration = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',source],capture_output=True,text=True,check=True).stdout)
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('來源音樂沒有有效長度')
    xf = min(2.0, duration / 4)
    copies = max(1, math.ceil((seconds-duration)/(duration-xf))+1)
    args = ['ffmpeg','-hide_banner','-loglevel','error','-n']
    for _ in range(copies):
        args += ['-i',source]
    fc, prev = [], '[0:a]'
    for i in range(1,copies):
        label = f'[join{i}]'
        fc.append(f'{prev}[{i}:a]acrossfade=d={xf}:c1=tri:c2=tri{label}')
        prev = label
    fade = min(4, seconds/2)
    fc.append(f'{prev}atrim=0:{seconds},afade=t=in:d={min(1.5,seconds/2)},afade=t=out:st={seconds-fade}:d={fade},aresample=48000[final]')
    subprocess.run(args+['-filter_complex',';'.join(fc),'-map','[final]','-t',str(seconds),'-ac','2',output],check=True)
    print('背景音軌完成',seconds,'秒')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('seconds',type=float);p.add_argument('output')
    a=p.parse_args();loop(a.source,a.seconds,a.output)
