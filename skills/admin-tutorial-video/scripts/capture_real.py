"""通用後台拍攝；各步失敗記錄後續拍，最後以非零結束碼提醒補拍。"""
import argparse
import html
import json
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse
from common import load_config, project_path, clip_rect


def command(cfg, profile):
 cap = cfg["capture"]
 browser = shutil.which(cap["browser"])
 if not browser:
 raise RuntimeError("找不到瀏覽器，請設定 capture.browser 為執行檔位置")
 return [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
 f"--user-data-dir={profile}", "--window-size=1280,860",
 "--force-device-scale-factor=2",
 f"--virtual-time-budget={cap['virtual_time_budget']}"]


def run_browser(cfg, args, output_file=None):
 # 每次使用獨立暫存設定檔，不使用個人的登入工作階段。
 with tempfile.TemporaryDirectory(prefix="tutorial-capture-") as profile:
 proc = subprocess.Popen(command(cfg, profile) + args,
 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
 try:
 out, err = proc.communicate(timeout=cfg["capture"]["timeout"])
 except subprocess.TimeoutExpired:
 proc.kill()
 out, err = proc.communicate()
 # 部分瀏覽器拍完仍不退出；只接受完整 PNG 或含明確結果的 DOM。
 if not (output_file and output_file.is_file()) and b'@@{' not in out:
 raise RuntimeError("瀏覽器超過等待時間")
 if proc.returncode not in (0, -9) or (proc.returncode == -9 and not output_file and b'@@{' not in out):
 raise RuntimeError(f"瀏覽器執行失敗，結束碼 {proc.returncode}")
 return out.decode("utf-8", errors="replace")


def dump(cfg, url):
 source = run_browser(cfg, ["--dump-dom", url])
 if "@@ERR" in source:
 raise RuntimeError("步驟頁回報錯誤，請檢查本機頁面")
 match = re.search(r"@@(\{.*?\})@@", html.unescape(source), re.S)
 if not match:
 raise RuntimeError("找不到步驟座標輸出")
 data = json.loads(match[1])
 clip_rect(data["r"])
 return data


def shot(cfg, url, destination):
 # 先拍到新檔再取代，失敗不覆蓋已存在的圖檔。
 with tempfile.TemporaryDirectory(prefix="tutorial-shot-") as temp:
 png = Path(temp) / "frame.png"
 run_browser(cfg, [f"--screenshot={png}", url], png)
 with png.open("rb") as file:
 header = file.read(24)
 if header[:8] != b"\x89PNG\r\n\x1a\n" or len(header) < 24 or struct.unpack(">II", header[16:24]) != (2560, 1720):
 raise RuntimeError("截圖不是完整的兩倍解析度 PNG")
 shutil.copyfile(png, destination)


def run(config):
 base, cfg = load_config(config)
 cap = cfg["capture"]
 parsed = urlparse(cap["base_url"])
 if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
 raise ValueError("只拍攝本機去個資頁面，base_url 必須為本機 HTTP 位址")
 imgdir = project_path(base, cfg["imgdir"])
 imgdir.mkdir(parents=True, exist_ok=True)
 errors, manifest = [], {}

 def url(page, sc, index, phase):
 rel = cap["pages"][page]
 if urlparse(rel).scheme or rel.startswith(("/", "//")) or ".." in rel.split("/"):
 raise ValueError("頁面對照表只接受本機相對路徑")
 return urljoin(cap["base_url"], rel) + "#r=" + quote(f"{sc},{index},{phase}", safe=",")

 for sc in cfg["scenarios"]:
 key = sc["id"]
 rows = manifest[key] = {"h": sc["title"], "p": sc["description"], "steps": []}
 page = sc.get("page", cap["default_page"])
 try:
 metadata = dump(cfg, url(page, key, 0, "pre"))["meta"]
 if len(metadata) != sc["count"]:
 raise ValueError("設定步數與頁面步數不符")
 except Exception as exc:
 errors.append({"scenario": key, "phase": "metadata", "reason": str(exc)})
 rows["steps"] = [{"error": "無法取得情境步驟"} for _ in range(sc["count"])]
 continue
 for i, meta in enumerate(metadata):
 row = dict(meta)
 rows["steps"].append(row)
 phases = ["pre"] + (["mid"] if meta.get("live") else []) + ["post"]
 for phase in phases:
 current = cap.get("phase_pages", {}).get(f"{key},{i},{phase}") or (
 meta.get("postPage") if phase == "post" else None) or meta.get("page") or page
 try:
 target = url(current, key, i, phase)
 data = dump(cfg, target)
 filename = imgdir / f"{key}-{i:03d}-{phase}.png"
 shot(cfg, target, filename)
 row[phase] = {"img": filename.relative_to(base).as_posix(), "r": data["r"]}
 except Exception as exc:
 row["error"] = "需要補拍"
 errors.append({"scenario": key, "step": i, "phase": phase, "reason": str(exc)})
 path = project_path(base, cfg["manifest"])
 path.parent.mkdir(parents=True, exist_ok=True)
 path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
 path.with_name(path.stem+"-errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
 print(f"拍攝完成，失敗 {len(errors)} 項；有失敗時不可繼續渲染")
 return 1 if errors else 0


if __name__ == "__main__":
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument("config")
 raise SystemExit(run(parser.parse_args().config))
