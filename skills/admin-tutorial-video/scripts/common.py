"""共用設定、路徑與素材檢查；所有專案路徑以設定檔所在目錄為基準。"""
import json
import math
import re
from pathlib import Path


def project_path(base, value):
    path = (base / value).resolve()
    if path != base and base not in path.parents:
        raise ValueError(f"專案路徑不可超出設定檔目錄：{value}")
    return path


def load_config(filename):
    path = Path(filename).resolve()
    cfg = json.loads(path.read_text(encoding="utf-8"))
    base = path.parent
    ids = set()
    for sc in cfg["scenarios"]:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", sc["id"]) or sc["id"] in ids:
            raise ValueError("情境識別須唯一，限英文字母、數字、底線與連字號")
        ids.add(sc["id"])
        if type(sc["count"]) is not int or sc["count"] < 1:
            raise ValueError("步數須為正整數")
    if not ids:
        raise ValueError("至少需要一個情境")
    for key in ("manifest", "out", "imgdir", "interactive"):
        dest = project_path(base, cfg[key])
        if dest == base:
            raise ValueError(f"{key} 不可指向專案根目錄")
    if len({cfg[k] for k in ("manifest", "out", "imgdir", "interactive")}) != 4:
        raise ValueError("素材、影片、互動版與清單路徑不可相同")
    for key, value in cfg["timing"].items():
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 3:
            raise ValueError(f"時間須至少三秒：{key}")
    for key, ov in cfg.get("overrides", {}).items():
        match = re.fullmatch(r"([a-zA-Z0-9_-]+),(\d+)", key)
        if not match or match[1] not in ids:
            raise ValueError(f"未知步驟覆寫：{key}")
        sc = next(s for s in cfg["scenarios"] if s["id"] == match[1])
        if int(match[2]) >= sc["count"] or not math.isfinite(ov.get("dur", 4.8)) or ov.get("dur", 4.8) < 3.5:
            raise ValueError(f"步驟超出範圍或閱讀時間不足：{key}")
    for key, value in cfg["theme"].items():
        if not re.fullmatch(r"[a-z_]+", key):
            raise ValueError("色票鍵限小寫字母與底線")
        if not re.fullmatch(r"#[0-9a-fA-F]{3,8}|rgba?\([\d\s.,%]+\)", value):
            raise ValueError("色票限十六進位或 rgb／rgba 色值")
    zoom = cfg["zoom"]
    if any(not isinstance(zoom[k], (int, float)) or not math.isfinite(zoom[k]) or zoom[k] <= 0 for k in ("min", "max", "factor")) or zoom["min"] > zoom["max"]:
        raise ValueError("推鏡限制須為有效正數，最小值不可大於最大值")
    cap = cfg["capture"]
    if (cap["width"], cap["height"], cap["scale"]) not in ((1280, 860, 2), (1600, 1075, 2)):
        raise ValueError("支援 1280×860 或 1600×1075 CSS 像素、兩倍拍攝")
    cfg.setdefault("overrides", {})
    return base, cfg


def clip_rect(rect, width=1280, height=860):
    if not isinstance(rect, dict) or any(k not in rect for k in ("x", "y", "w", "h")):
        raise ValueError("缺少焦點座標")
    if any(not isinstance(rect[k], (int, float)) or not math.isfinite(rect[k]) for k in ("x", "y", "w", "h")):
        raise ValueError("焦點座標必須是有限數字")
    x, y = max(4, rect["x"]), max(36, rect["y"])
    x2, y2 = min(width-4, rect["x"] + rect["w"]), min(height-4, rect["y"] + rect["h"])
    if x2 <= x or y2 <= y:
        raise ValueError("焦點不在可見視窗內，請修正拍攝捲動")
    return {"x": x, "y": y, "w": x2-x, "h": y2-y}


def validate_manifest(cfg, manifest):
    for sc in cfg["scenarios"]:
        rows = manifest[sc["id"]]["steps"]
        if len(rows) != sc["count"]:
            raise ValueError(f"步數不符：{sc['id']}")
        for i, step in enumerate(rows):
            if step.get("error") or not step.get("pre") or not step.get("post"):
                raise ValueError(f"拍攝未完成：{sc['id']}，第 {i+1} 步")
            if step.get("live") and not step.get("mid"):
                raise ValueError("下拉步驟缺少展開中畫面")
            for phase in ("pre", "mid", "post"):
                if step.get(phase):
                    clip_rect(step[phase]["r"], cfg["capture"]["width"], cfg["capture"]["height"])
            for key in ("z", "spotZ"):
                z = step.get(key)
                if z is not None and (not isinstance(z, (int, float)) or not math.isfinite(z) or z <= 0):
                    raise ValueError("推鏡倍率須為正數")


def display_rect(cfg, rect):
    """拍攝 CSS 座標轉成 1280×860 監看座標；1600 寬時倍率為 0.8。"""
    cap = cfg['capture']
    clip_rect(rect, cap['width'], cap['height'])
    return clip_rect({k: v * 1280 / cap['width'] for k, v in rect.items()})


def fitted_zoom(cfg, suggested, rect, overview=False):
    if overview or suggested <= 1.05:
        return 1.0
    z = max(cfg['zoom']['min'], min(cfg['zoom']['max'], suggested * cfg['zoom']['factor']))
    return round(max(1, min(z, 1180 / rect['w'], 780 / rect['h'])), 3)
