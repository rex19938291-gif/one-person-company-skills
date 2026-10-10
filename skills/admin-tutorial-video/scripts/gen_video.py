"""以專案 video.config.json 與 manifest 產生 HyperFrames 教學影片。"""
import argparse
import html
import json
import math
import os
import re
import shutil
from pathlib import Path
from common import load_config, project_path, clip_rect, validate_manifest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("config", help="專案設定檔")
args = parser.parse_args()
BASE, CFG = load_config(args.config)
man = json.loads(project_path(BASE, CFG["manifest"]).read_text(encoding="utf-8"))
validate_manifest(CFG, man)
out = project_path(BASE, CFG["out"])
(out / "assets").mkdir(parents=True, exist_ok=True)
CFG["order"] = [(sc["id"], sc["mark"]) for sc in CFG["scenarios"]]
CFG["scen_name"] = {sc["id"]: sc["title"] for sc in CFG["scenarios"]}
CFG["scen_sub"] = {sc["id"]: sc["description"] for sc in CFG["scenarios"]}
CFG["must"] = {sc["id"]: sc.get("must", "") for sc in CFG["scenarios"]}
CFG["over"] = { (k.split(",")[0], int(k.split(",")[1])): v for k,v in CFG["overrides"].items() }
CFG["chips"] = {k:v.get("chips",[]) for k,v in CFG["over"].items()}
T_INTRO, T_SEC, T_STEP, T_OUTRO = (CFG["timing"][k] for k in ("intro", "section", "step", "outro"))
steps, secs, t = [], [], T_INTRO
for k, mark in CFG["order"]:
 sc = man[k]
 secs.append({"k": k, "mark": mark, "h": CFG["scen_name"][k], "p": CFG["scen_sub"][k], "must": CFG["must"].get(k, ""), "t": t}); t += T_SEC
 n = len(sc["steps"])
 for i, s in enumerate(sc["steps"]):
 ov = CFG["over"].get((k, i), {})
 st = {"k": k, "i": i, "n": n, "t": round(t, 3), "tt": ov.get("tt", html.unescape(s["tt"])), "dd": ov.get("dd", html.unescape(s["dd"])),
 "chips": CFG["chips"].get((k, i), []), "dur": ov.get("dur", T_STEP),
 "click": s["click"], "z": s["z"], "spotZ": s.get("spotZ"),
 "scen": str(mark) + "　" + CFG["scen_name"][k]}
 for ph in ("pre", "mid", "post"):
 if s.get(ph):
 src = project_path(BASE, s[ph]["img"])
 fn = f"{k}-{i:03d}-{ph}{src.suffix.lower()}"
 shutil.copy(src, os.path.join(out, "assets", fn))
 r = clip_rect(s[ph]["r"])
 st[ph] = {"img": "assets/" + fn, "r": r}
 steps.append(st); t += st["dur"]
T_OUT0 = round(t, 3); TOTAL = round(t + T_OUTRO, 3)

def vz(z): # 影片畫面較大，推鏡倍率收斂避免放大過度模糊
 return round(max(CFG["zoom"]["min"], min(CFG["zoom"]["max"], z * CFG["zoom"]["factor"])), 3)
for s in steps:
 s["vz"] = vz(s["z"]); s["vzPost"] = vz(s["spotZ"]) if s.get("spotZ") else s["vz"]

imgs = []
for si, s in enumerate(steps):
 for ph in ("pre", "mid", "post"):
 if s.get(ph):
 imgs.append(f'<img class="shot" id="im-{si}-{ph}" src="{s[ph]["img"]}" alt="">')

caps = []
for si, s in enumerate(steps):
 scene_steps = [(j, row) for j, row in enumerate(steps) if row["k"] == s["k"]]
 visible = [(j, row) for j, row in scene_steps if abs(row["i"] - s["i"]) <= 2]
 outline = "".join(f'<li class="{ "current" if row["i"] == s["i"] else "" }">{row["i"]+1:02d}　{html.escape(row["tt"])}</li>' for j, row in visible)
 caps.append(f'''<div class="cap" id="cap-{si}">
 <div class="scen">{html.escape(s["scen"])}</div>
 <div class="num"><span class="big">{s["i"]+1:02d}</span><span class="of">／{s["n"]:02d}</span></div>
 <h2 class="tt">{html.escape(s["tt"])}</h2>
 <p class="dd">{html.escape(s["dd"])}</p>
 {('<div class="chips">' + "".join(f'<div class="chip"><code>{html.escape(a)}</code><span>{html.escape(b)}</span></div>' for a, b in s["chips"]) + '</div>') if s["chips"] else ""}
 <ol class="outline">{outline}</ol>
</div>''')

secs_html = []
for j, c in enumerate(secs):
 secs_html.append(f'''<section class="clip seccard" id="sec-{j}" data-start="{c["t"]}" data-duration="{T_SEC}" data-track-index="2">
 <div class="sec-panel" id="secp-{j}"></div>
 <div class="sec-inner">
 <div class="sec-mark" id="secm-{j}">{html.escape(str(c["mark"]))}</div>
 <div class="sec-copy">{('<div class="must" id="secmust-'+str(j)+'">'+html.escape(c["must"])+'</div>') if c["must"] else ""}<div class="sec-kicker">{html.escape(CFG["labels"]["section"].format(current=j+1,total=len(secs)))}</div><h2 class="sec-h" id="sech-{j}">{html.escape(c["h"])}</h2><p class="sec-p" id="secq-{j}">{html.escape(c["p"])}</p></div>
 </div>
</section>''')

tags = "".join(f'<span class="tag">{html.escape(x)}</span>' for x in CFG["tags"])
outro_li = "".join(f'<li class="oli" id="oli-{i}"><span class="ono">{i+1:02d}</span><span>{html.escape(x)}</span></li>' for i, x in enumerate(CFG["outro"]))
data = json.dumps({"steps": [{k: v for k, v in s.items() if k in ("t", "dur", "click", "vz", "vzPost", "pre", "mid", "post")} for s in steps],
 "secs": [c["t"] for c in secs], "T_STEP": T_STEP, "T_SEC": T_SEC, "T_OUT0": T_OUT0, "TOTAL": TOTAL}, ensure_ascii=False).replace("<", "\\u003c")

page = f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="viewport" content="width=1920, height=1080">
<title>{html.escape(CFG["title"])}</title>
<link rel="stylesheet" href="{html.escape(CFG["runtime"]["fonts"], quote=True)}">
<script src="{html.escape(CFG["runtime"]["gsap"], quote=True)}"></script>
<style>
/* 色票由專案設定提供。 */
:root{{--bg:{CFG["theme"]["bg"]};--paper:{CFG["theme"]["paper"]};--ink:{CFG["theme"]["ink"]};--muted:{CFG["theme"]["muted"]};--accent:{CFG["theme"]["accent"]};--accent2:{CFG["theme"]["accent_dark"]};--hot:{CFG["theme"]["focus"]};--line:{CFG["theme"]["grid"]}}}
html,body{{margin:0;background:var(--bg)}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;font-family:"Noto Sans TC",sans-serif;color:var(--ink)}}
.clip{{position:absolute;inset:0}}
.fill{{position:absolute;inset:0;background:var(--bg)}}
.grid{{position:absolute;inset:-128px;background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:64px 64px;opacity:.45}}
.ghost{{position:absolute;left:-30px;bottom:-120px;font-size:520px;font-weight:900;color:var(--accent);opacity:.09;letter-spacing:-20px;line-height:1}}
.reg{{position:absolute;width:34px;height:34px;border-color:var(--ink);border-style:solid;opacity:.55}}
.reg.tl{{left:28px;top:28px;border-width:3px 0 0 3px}}.reg.tr{{right:28px;top:28px;border-width:3px 3px 0 0}}
.reg.bl{{left:28px;bottom:28px;border-width:0 0 3px 3px}}.reg.br{{right:28px;bottom:28px;border-width:0 3px 3px 0}}
.meta{{position:absolute;left:72px;top:58px;font-family:"IBM Plex Mono",monospace;font-size:20px;letter-spacing:.08em;color:var(--muted)}}
.meta b{{color:var(--accent);font-weight:700}}
.monitor{{position:absolute;left:592px;top:112px;width:1280px;height:860px;border-radius:18px;overflow:hidden;background:{CFG["theme"]["monitor"]};box-shadow:0 0 0 4px var(--ink),0 30px 60px -20px {CFG["theme"]["shadow"]}}}
.mon-label{{position:absolute;left:592px;top:62px;font-family:"IBM Plex Mono",monospace;font-size:20px;color:var(--muted);letter-spacing:.06em}}
.mon-label i{{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--hot);margin-right:10px;vertical-align:1px}}
.cam{{position:absolute;left:0;top:0;width:1280px;height:860px;transform-origin:0 0}}
.shot{{position:absolute;left:0;top:0;width:1280px;height:860px;opacity:0}}
.spot{{position:absolute;z-index:1000000;border-radius:10px;box-shadow:0 0 0 5000px {CFG["theme"]["spot_shadow"]};opacity:0}}
.spot .ring{{position:absolute;inset:-7px;border:4px solid var(--hot);border-radius:12px}}
.cursor{{position:absolute;z-index:1000002;left:0;top:0;width:34px;height:34px;transform-origin:4px 2px}}
.ripple{{position:absolute;z-index:1000001;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;border:5px solid var(--hot);opacity:0}}
.rail{{position:absolute;left:72px;top:112px;width:460px;height:860px}}
.cap{{position:absolute;left:0;top:0;width:460px;height:860px;opacity:0}}
.outline{{position:absolute;left:0;right:0;bottom:12px;list-style:none;padding:0;margin:0;font-size:20px;line-height:1.5;color:var(--muted)}}
.outline li{{padding:3px 12px}}.outline .current{{background:var(--accent);color:var(--paper);font-weight:700}}
.scen{{display:inline-block;background:var(--accent);color:{CFG["theme"]["paper"]};font-weight:700;font-size:26px;padding:10px 20px;border-radius:999px}}
.num{{margin-top:44px;font-family:"League Gothic",sans-serif;line-height:.85;color:var(--accent2)}}
.num .big{{font-size:190px}}.num .of{{font-family:"IBM Plex Mono",monospace;font-size:30px;color:var(--muted);margin-left:8px}}
.tt{{margin:26px 0 0;font-size:46px;font-weight:900;line-height:1.28;letter-spacing:.01em}}
.dd{{margin:22px 0 0;font-size:31px;font-weight:400;line-height:1.55;color:var(--muted)}}
.dd b{{color:var(--hot);font-weight:700}}
.bar{{position:absolute;left:72px;top:1000px;width:1800px;height:6px;background:var(--line)}}
.bar i{{position:absolute;left:0;top:0;width:1800px;height:6px;background:var(--accent);transform-origin:0 0;transform:scaleX(0);display:block}}
.tc{{position:absolute;right:48px;top:58px;font-family:"IBM Plex Mono",monospace;font-size:20px;color:var(--muted)}}
.chips{{margin-top:22px;display:grid;gap:9px}}
.chip{{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;font-size:24px;line-height:1.35;color:var(--ink)}}
.chip code{{font-family:"IBM Plex Mono",monospace;font-size:22px;background:var(--paper);border:2px solid var(--accent);color:var(--accent2);padding:2px 10px;border-radius:8px;font-weight:600}}
.must{{display:inline-block;background:var(--hot);color:{CFG["theme"]["white"]};font-weight:900;font-size:40px;padding:10px 26px;border-radius:12px;margin-bottom:22px}}
/* 片頭 */
.intro{{background:var(--ink)}}
.intro-in{{position:absolute;inset:0;padding:150px 140px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:flex-end;gap:30px}}
.intro .k{{font-family:"IBM Plex Mono",monospace;color:{CFG["theme"]["light_accent"]};font-size:24px;letter-spacing:.12em}}
.intro h1{{margin:0;color:{CFG["theme"]["paper"]};font-size:132px;font-weight:900;line-height:1.05;letter-spacing:.02em}}
.intro p{{margin:0;color:{CFG["theme"]["intro_text"]};font-size:40px;max-width:1300px;line-height:1.5}}
.tags{{display:flex;gap:16px;flex-wrap:wrap}}
.tag{{border:3px solid {CFG["theme"]["light_accent"]};color:{CFG["theme"]["tag_text"]};font-size:26px;padding:8px 20px;border-radius:999px}}
.intro-rule{{position:absolute;left:140px;top:120px;width:1640px;height:4px;background:{CFG["theme"]["intro_rule"]};transform-origin:0 0;display:block}}
.intro-big{{position:absolute;right:-40px;top:40px;font-size:420px;font-weight:900;color:{CFG["theme"]["accent"]};opacity:.35;line-height:1}}
/* 章節卡 */
.sec-panel{{position:absolute;inset:0;background:var(--accent2);transform-origin:0 50%}}
.sec-inner{{position:absolute;inset:0;padding:0 160px;box-sizing:border-box;display:flex;align-items:center;gap:80px}}
.sec-mark{{font-size:300px;font-weight:900;color:{CFG["theme"]["light_accent"]};line-height:1}}
.sec-copy{{max-width:1150px}}
.sec-kicker{{font-family:"IBM Plex Mono",monospace;font-size:26px;letter-spacing:.14em;color:{CFG["theme"]["light_accent"]}}}
.sec-h{{margin:18px 0 0;font-size:104px;font-weight:900;color:{CFG["theme"]["paper"]};line-height:1.1}}
.sec-p{{margin:26px 0 0;font-size:38px;color:{CFG["theme"]["section_text"]};line-height:1.5}}
/* 片尾 */
.outro{{background:var(--paper)}}
.outro-in{{position:absolute;inset:0;padding:130px 160px;box-sizing:border-box;display:flex;flex-direction:column;gap:46px}}
.outro h2{{margin:0;font-size:96px;font-weight:900;color:var(--accent2)}}
.outro ol{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:30px}}
.oli{{display:flex;gap:30px;align-items:baseline;font-size:44px;line-height:1.45;max-width:1120px}}
.ono{{font-family:"IBM Plex Mono",monospace;font-size:34px;color:var(--hot);flex:none}}
.outro-ghost{{position:absolute;right:-40px;bottom:-110px;font-size:560px;font-weight:900;color:var(--accent);opacity:.12;line-height:1}}
.outro-rule{{display:block;width:420px;height:8px;background:var(--hot);transform-origin:0 0}}
.outro-panel{{position:absolute;right:0;top:0;width:520px;height:1080px;background:var(--accent2);transform-origin:100% 0}}
.op-in{{position:absolute;left:60px;right:50px;top:300px;color:{CFG["theme"]["paper"]};display:flex;flex-direction:column;gap:22px}}
.op-in span{{font-size:38px;color:{CFG["theme"]["light_accent"]};font-weight:700}}
.op-in b{{font-size:96px;line-height:1.1;font-weight:900}}
.outro .foot{{margin-top:auto;font-family:"IBM Plex Mono",monospace;font-size:22px;color:var(--muted);letter-spacing:.08em}}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{TOTAL}">
 <section class="clip" id="bgclip" data-start="0" data-duration="{TOTAL}" data-track-index="0">
 <div class="fill"></div><div class="grid" id="grid"></div><div class="ghost" id="ghost">{html.escape(CFG["ghost"])}</div>
 <div class="reg tl"></div><div class="reg tr"></div><div class="reg bl"></div><div class="reg br"></div>
 </section>
 <section class="clip" id="mainclip" data-start="0" data-duration="{TOTAL}" data-track-index="1">
 <div class="meta">{html.escape(CFG["labels"]["meta"])}</div>
 <div class="tc" id="tc">{html.escape(CFG["labels"]["timecode"])}</div>
 <div class="mon-label"><i></i>{html.escape(CFG["labels"]["monitor"])}</div>
 <div class="monitor"><div class="cam" id="cam">
 {"".join(imgs)}
 <div class="spot" id="spot"><div class="ring"></div></div>
 <div class="ripple" id="ripple"></div>
 <svg class="cursor" id="cursor" viewBox="0 0 24 24"><path d="M4 2l15 9-6.5 1.5L16 20l-3 1.5-3.6-7.6L4 18z" fill="{CFG["theme"]["white"]}" stroke="{CFG["theme"]["cursor_stroke"]}" stroke-width="1.4" stroke-linejoin="round"/></svg>
 </div></div>
 <div class="rail">{"".join(caps)}</div>
 <div class="bar"><i id="barfill"></i></div>
 </section>
 <section class="clip intro" id="intro" data-start="0" data-duration="{T_INTRO}" data-track-index="2">
 <div class="intro-big" id="introbig">{html.escape(CFG["ghost"])}</div>
 <div class="intro-rule" id="introrule"></div>
 <div class="intro-in">
 <div class="k" id="introk">{html.escape(CFG["labels"]["intro"])}</div>
 <h1 id="introh">{html.escape(CFG["title"])}</h1>
 <p id="introp">{html.escape(CFG["sub"])}</p>
 <div class="tags" id="introtags">{tags}</div>
 </div>
 </section>
 {"".join(secs_html)}
 <section class="clip outro" id="outro" data-start="{T_OUT0}" data-duration="{T_OUTRO}" data-track-index="2">
 <div class="outro-panel" id="outropanel"><div class="op-in" id="opin"><span>{html.escape(CFG["outro_panel"]["top"])}</span><b>{html.escape(CFG["outro_panel"]["main"])}</b><span>{html.escape(CFG["outro_panel"]["bottom"])}</span></div></div>
 <div class="outro-ghost" id="outroghost">{html.escape(CFG["ghost"])}</div>
 <div class="outro-in">
 <h2 id="outroh">{html.escape(CFG["outro_h"])}</h2>
 <i class="outro-rule" id="outrorule"></i>
 <ol>{outro_li}</ol>
 <div class="foot">{html.escape(CFG["labels"]["footer"])}</div>
 </div>
 </section>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const D = {data};
const tl = gsap.timeline({{ paused: true }});
const W = 1280, H = 860;
function camT(r, z) {{
 let tx = W/2 - (r.x + r.w/2)*z, ty = H*0.48 - (r.y + r.h/2)*z;
 tx = Math.min(0, Math.max(W - W*z, tx)); ty = Math.min(0, Math.max(H - H*z, ty));
 return {{ x: tx, y: ty, scale: z }};
}}
function spotT(r) {{ const p = 8; return {{ x: r.x - p, y: r.y - p, width: r.w + 2*p, height: r.h + 2*p }}; }}
function curPos(s, r) {{
 return s.click ? {{ x: r.x + Math.min(r.w*0.55, r.w - 10), y: r.y + r.h*0.6 }} : {{ x: Math.max(8, r.x - 46), y: r.y + Math.min(40, r.h/2) }};
}}
// 片頭
tl.from("#introrule", {{ scaleX: 0, duration: 0.8, ease: "expo.out" }}, 0.1);
tl.from("#introk", {{ x: -40, opacity: 0, duration: 0.5, ease: "power3.out" }}, 0.25);
tl.from("#introh", {{ y: 70, opacity: 0, duration: 0.7, ease: "back.out(1.4)" }}, 0.35);
tl.from("#introp", {{ y: 30, opacity: 0, duration: 0.6, ease: "power2.out" }}, 0.6);
tl.from("#introtags .tag", {{ y: 24, opacity: 0, duration: 0.4, stagger: 0.08, ease: "power3.out" }}, 0.8);
tl.from("#introbig", {{ x: 120, opacity: 0, duration: 1.4, ease: "power2.out" }}, 0);
// 背景緩慢漂移
tl.to("#ghost", {{ x: 60, duration: D.TOTAL, ease: "none" }}, 0);
tl.to("#grid", {{ x: 64, y: 32, duration: D.TOTAL, ease: "none" }}, 0);
// 章節卡
D.secs.forEach((t0, j) => {{
 tl.fromTo("#secp-"+j, {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.55, ease: "expo.inOut" }}, t0);
 tl.from("#secm-"+j, {{ scale: 0.6, opacity: 0, duration: 0.6, ease: "back.out(1.8)" }}, t0 + 0.35);
 tl.from("#sech-"+j, {{ y: 60, opacity: 0, duration: 0.55, ease: "power3.out" }}, t0 + 0.45);
 tl.from("#secq-"+j, {{ y: 24, opacity: 0, duration: 0.5, ease: "power2.out" }}, t0 + 0.65);
 tl.set("#cam", {{ x: 0, y: 0, scale: 1 }}, t0 + 0.6);
 tl.set("#spot", {{ opacity: 0 }}, t0 + 0.6);
 if (document.getElementById("secmust-"+j)) tl.from("#secmust-"+j, {{ scale: 1.6, opacity: 0, rotation: -4, duration: 0.5, ease: "back.out(2.2)" }}, t0 + 0.8);
 tl.to(["#secm-"+j, "#sech-"+j, "#secq-"+j], {{ opacity: 0, duration: 0.25 }}, t0 + D.T_SEC - 0.4);
 tl.to("#secp-"+j, {{ scaleX: 0, transformOrigin: "100% 50%", duration: 0.4, ease: "expo.in" }}, t0 + D.T_SEC - 0.45);
}});
// 步驟
let prevImg = null;
D.steps.forEach((s, i) => {{
 const t0 = s.t, r = s.pre.r, fin = s.post || s.pre, fr = fin.r || r;
 const pre = "#im-"+i+"-pre", mid = s.mid ? "#im-"+i+"-mid" : null, post = s.post ? "#im-"+i+"-post" : null;
 tl.set(pre, {{ opacity: 1, zIndex: 3*i+1 }}, t0);
 if (prevImg) tl.set(prevImg, {{ opacity: 0 }}, t0 + 0.05);
 if (i === 0) {{ tl.set("#cam", camT(r, 1), 0); tl.set("#cursor", {{ x: 900, y: 600 }}, 0); }}
 tl.to("#cam", {{ ...camT(r, s.vz), duration: 0.9, ease: "power3.inOut" }}, t0);
 tl.to("#spot", {{ ...spotT(r), opacity: 1, duration: 0.8, ease: "power3.inOut" }}, t0);
 const c = curPos(s, r);
 tl.to("#cursor", {{ x: c.x, y: c.y, duration: 0.8, ease: "power2.inOut" }}, t0 + 0.35);
 // 左側字卡
 tl.fromTo("#cap-"+i, {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, t0 + 0.15);
 tl.to("#cap-"+i, {{ opacity: 0, duration: 0.2 }}, t0 + s.dur - 0.2);
 tl.to("#barfill", {{ scaleX: (i+1)/D.steps.length, duration: 0.6, ease: "power2.out" }}, t0 + 0.2);
 let tPost = t0 + 1.5;
 if (s.click) {{
 tl.to("#cursor", {{ scale: 0.82, duration: 0.09, yoyo: true, repeat: 1 }}, t0 + 1.25);
 tl.fromTo("#ripple", {{ x: c.x + 4, y: c.y + 4, scale: 0.3, opacity: 1 }}, {{ scale: 1.6, opacity: 0, duration: 0.55, ease: "power2.out" }}, t0 + 1.3);
 }}
 if (mid) {{ tl.set(mid, {{ zIndex: 3*i+2 }}, t0); tl.to(mid, {{ opacity: 1, duration: 0.2 }}, t0 + 1.4); tPost = t0 + 2.45; }}
 if (post) {{
 tl.set(post, {{ zIndex: 3*i+3 }}, t0);
 tl.to(post, {{ opacity: 1, duration: 0.4, ease: "power1.inOut" }}, tPost);
 if (fr.x !== r.x || fr.y !== r.y || fr.w !== r.w) {{
 tl.to("#cam", {{ ...camT(fr, s.vzPost), duration: 0.8, ease: "power3.inOut" }}, tPost + 0.1);
 tl.to("#spot", {{ ...spotT(fr), duration: 0.7, ease: "power3.inOut" }}, tPost + 0.1);
 const c2 = {{ x: fr.x + Math.min(40, fr.w*0.3), y: fr.y + Math.min(36, fr.h*0.4) }};
 tl.to("#cursor", {{ x: c2.x, y: c2.y, duration: 0.6, ease: "power2.inOut" }}, tPost + 0.2);
 }}
 if (mid) tl.set(mid, {{ opacity: 0 }}, tPost + 0.45);
 tl.set(pre, {{ opacity: 0 }}, tPost + 0.45);
 prevImg = post;
 }} else {{ prevImg = mid || pre; if (mid) tl.set(pre, {{ opacity: 0 }}, t0 + 1.6); }}
}});
// 片尾
tl.from("#outroh", {{ x: -60, opacity: 0, duration: 0.6, ease: "power3.out" }}, D.T_OUT0 + 0.15);
tl.from("#outropanel", {{ scaleX: 0, duration: 0.7, ease: "expo.out" }}, D.T_OUT0);
tl.from("#opin", {{ y: 40, opacity: 0, duration: 0.6, ease: "power3.out" }}, D.T_OUT0 + 0.6);
tl.from("#outrorule", {{ scaleX: 0, duration: 0.6, ease: "power3.out" }}, D.T_OUT0 + 0.35);
tl.from("#outroghost", {{ y: 80, opacity: 0, duration: 1.2, ease: "power2.out" }}, D.T_OUT0 + 0.1);
tl.from(".oli", {{ y: 34, opacity: 0, duration: 0.5, stagger: 0.18, ease: "power3.out" }}, D.T_OUT0 + 0.45);
window.__timelines["main"] = tl;
</script>
</body>
</html>'''
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
print("產生完成", "steps", len(steps), "secs", len(secs), "duration", TOTAL, "imgs", len(imgs))
