"""把點擊、換章節等音效依 sfx.json 排進已完成的 MP4（影片不重壓，只重做音軌）。
用法：python3 add_sfx.py sfx.json in.mp4 out.mp4 [--sfx-dir 音效資料夾] [--volume 0.35]
sfx.json：{"total": 秒數, "cues": [{"t": 秒, "name": "click-soft"}, ...]}，由產生器自動輸出。
音效資料夾預設用 HyperFrames 的 hyperframes-media 內附音效庫（Pixabay 授權、免標註）；
可用 --sfx-dir 或環境變數 SFX_DIR 指定自己的資料夾，檔名＝cue 名稱＋.mp3。
原片有聲音（旁白／背景音樂）就疊在下面，沒有就只放音效。找不到的音效檔略過並列出，不中斷。"""
import argparse, json, os, subprocess, sys

DEFAULT_DIR = os.path.expanduser("~/.agents/skills/hyperframes-media/assets/sfx")
p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("cues"); p.add_argument("video"); p.add_argument("out")
p.add_argument("--sfx-dir", default=os.environ.get("SFX_DIR", DEFAULT_DIR))
p.add_argument("--volume", type=float, default=0.35)
a = p.parse_args()

spec = json.load(open(a.cues, encoding="utf-8"))
cues, missing = [], set()
for c in spec["cues"]:
    f = os.path.join(a.sfx_dir, c["name"] + ".mp3")
    if os.path.exists(f):
        cues.append((float(c["t"]), f, float(c.get("volume", a.volume))))
    else:
        missing.add(c["name"])
if missing:
    print("略過（找不到音效檔）：", " ".join(sorted(missing)), "於", a.sfx_dir)
if not cues:
    print("沒有可用的音效，未輸出"); sys.exit(1)

probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                        "-of", "csv=p=0", a.video], capture_output=True, text=True)
has_audio = bool(probe.stdout.strip())

files = sorted({f for _, f, _ in cues})
args = ["ffmpeg", "-loglevel", "error", "-y", "-i", a.video]
for f in files:
    args += ["-i", f]
idx = {f: n for n, f in enumerate(files, start=1)}
chains, labels = [], []
for n, (t, f, vol) in enumerate(cues):
    ms = int(round(t * 1000))
    chains.append(f"[{idx[f]}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{n}]")
    labels.append(f"[s{n}]")
fc = ";".join(chains) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0[sfx]"
if has_audio:
    fc += ";[0:a]aresample=48000,aformat=channel_layouts=stereo[base];[base][sfx]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]"
else:
    fc += ";[sfx]apad,alimiter=limit=0.95[a]"  # 補靜音到片尾，長度由 -t 截齊
args += ["-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-t", str(spec["total"]), "-movflags", "+faststart", a.out]
subprocess.run(args, check=True)
print("完成", a.out, len(cues), "個音效", "（疊在原音軌上）" if has_audio else "（原片無聲）")
