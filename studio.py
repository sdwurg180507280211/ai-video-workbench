"""AI 视频工作台：一个本地网页，看清每类做法怎么做、每个作品做到哪、手里有哪些素材。

python3 studio.py [--root AI视频总文件夹] [--port 8765] [--no-open]

总文件夹默认取环境变量 AI_VIDEO_ROOT，没有就是 ~/Downloads/AI视频。里面每个作品文件夹放一个 作品.json：
  {"类别": "短剧" 或 "代码动画", "标题": "...", "简介": "...", "状态": "已完成", "成片": ["相对作品目录的 mp4"], ...}
短剧作品按 seedance-short-drama 的项目目录扫描；代码动画作品读 film/cues.json（节拍、字幕、旁白位置）。
有 素材清单.md 的文件夹当作素材库，下面带 透明/ 子文件夹的每组贴纸都会列出来。

页面只读文件。唯一会写的是短剧的看片标记：<作品>/5_审片/标记.json，截图存在 5_审片/标记/。
默认只监听本机 127.0.0.1。按 Ctrl+C 退出。
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

PAGE = Path(__file__).resolve().with_name("studio.html")
FLOWS = PAGE.with_name("flows")      # 每类做法一份流程数据：flows/<类别>.json
SETTINGS = "工作台.json"  # 总文件夹里的设置，例如 {"入行日期": "2026-10-17"}
WORK = "作品.json"
ASSET_LIST = "素材清单.md"
DEFAULT_ROOT = "~/Downloads/AI视频"
SKIP_DIRS = {"node_modules", "__pycache__"}
MARKS = "5_审片/标记.json"
MARK_DIR = "5_审片/标记"
MARK_STATES = ("待处理", "已处理", "已删除")
KINDS = {"video": (".mp4", ".mov", ".m4v", ".webm"), "image": (".png", ".jpg", ".jpeg", ".webp", ".gif"),
         "audio": (".wav", ".mp3", ".m4a", ".aac"), "doc": (".md",),
         "text": (".txt", ".json", ".log", ".sh", ".py", ".swift", ".csv")}
TYPES = {".mp4": "video/mp4", ".m4v": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
         ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
         ".gif": "image/gif", ".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".aac": "audio/aac"}
SEG_ID = re.compile(r"S\d+")
TAKE = re.compile(r"(S\d+)_t(\d+)_([^_]+)_(\d+p)")
FILM = re.compile(r"成片|粗剪|预览|整片|_v\d+")
# 制作流程 9 步：工作台按这里讲解每一步，再按项目里的文件判断做到哪了
STEPS = [
    {"key": "need", "title": "需求",
     "what": "开工前把剧本里看不出来的事定下来：用途和平台、画风、预算、画质，还有拍到哪几下你就满意。",
     "tool": "Claude 问你几个问题，写成需求文档。",
     "cost": "不花钱", "outputs": ["1_文档/需求.md"],
     "pitfalls": ["只问剧本里看不出来的事，问题越少越好。",
                  "画风拿不准时，先出两三张样图让你挑，不要只用文字描述。",
                  "预算写进需求；以后每次花钱前，先报金额，等你确认。"]},
    {"key": "script", "title": "剧本",
     "what": "故事和台词定稿。写什么由你决定，Claude 负责把它整理成能拍的样子。",
     "tool": "你给剧本或方向，Claude 整理成剧本定稿。",
     "cost": "不花钱", "outputs": ["1_文档/剧本定稿.md"],
     "pitfalls": ["剧本是改起来最便宜的环节；问题拖到成片才发现，就只能整段重抽。",
                  "改台词要你确认。",
                  "医疗、法律这类专业内容要核对事实，并注明“剧情纯属虚构”。"]},
    {"key": "split", "title": "切段和连戏",
     "what": "把剧本切成一段一段，每段 4～12 秒、放 2～4 个镜头，一段调一次视频模型。"
             "再用连戏表锁住容易穿帮的细节：长相、服装、站位、道具、画面文字。",
     "tool": "Claude 写分段表和连戏表。分段表同时当进度表，记下每段生成了几条、选了哪条。",
     "cost": "不花钱", "outputs": ["1_文档/分段表.md", "1_文档/连戏表.md"],
     "pitfalls": ["同一段里的几个镜头一次生成，人物和场景自然对得上；每多一次单独生成，就多一道接缝。",
                  "大动作单独成一段，给够时间，不然容易变形。",
                  "连戏表上没写的细节，模型就会随便发挥。"]},
    {"key": "assets", "title": "角色素材",
     "what": "给每个露脸的角色做一张三视图（胸像、正面全身、侧面全身），给每个说话的角色准备一段音色录音。"
             "生成视频时把它们当参考传给模型，人脸和声音才能前后一致。",
     "tool": "三视图用 Seedream 5.0 Pro 文生图；音色是一段 2～30 秒的 wav 录音。",
     "cost": "三视图约 ¥0.3 一张；音色录音不花钱", "outputs": ["2_素材/角色/", "2_素材/声音/", "3_提示词/角色/"],
     "pitfalls": ["Seedance 会拒绝写实人脸的参考图，只有本账号 Seedream 文生图生成的原图能用；原图不能裁剪、压缩、转格式。",
                  "三视图整张传，不拆成单张。",
                  "三视图里的表情会被带进每一段，所以用放松的中性表情，性格写进每段的提示词。",
                  "每个角色加一个辨识特征（痣、补丁），审片时拿它认人。"]},
    {"key": "prompts", "title": "提示词",
     "what": "每段写一份提示词：几个镜头、每个镜头从第几秒开始、人怎么演、说什么台词、有什么声音、哪些东西不能出现。",
     "tool": "Claude 按 Seedance 官方写法写：@图片1 指第一张参考图，@音频1 指第一段音色，台词放在 {} 里，音效放在 <> 里。",
     "cost": "不花钱", "outputs": ["3_提示词/"],
     "pitfalls": ["写什么出什么：通用结尾里的一个词，会落到每个角色身上。",
                  "形容表情的词会被放大，“坚定”会演成凶。要写清看着谁、想做什么、情绪怎么变。",
                  "不给人物安排具体动作，他就会立正站着念台词。",
                  "“不要 X”有时反而招来 X。"]},
    {"key": "generate", "title": "生成视频",
     "what": "每段调一次视频模型：把提示词、三视图、音色一起传过去，模型生成一段带台词和音效的视频。",
     "tool": "Seedance 2.5，通过火山方舟 API 调用：720p、竖屏 9:16、开声音。批量脚本同时最多跑 3 段。",
     "cost": "720p 每秒 ¥1.51，480p 每秒 ¥0.67；只有生成成功才收费", "outputs": ["4_生成片段/"],
     "pitfalls": ["每次花钱前，先报模型、秒数和金额，等你确认。",
                  "新写法先试跑一两段，过了再批量。",
                  "提交失败时先查任务列表：任务可能已经建成，盲目重提会重复扣费。",
                  "生成的视频地址只保存 24 小时，要及时下载。",
                  "测写法、测表演用 2.5 的 480p，不用 Mini：Mini 演不出细微表情。"]},
    {"key": "review", "title": "审片",
     "what": "每条片段都要查：脸像不像、画面里有没有字、手和身体有没有变形、台词全不全、音量合不合适，最后逐句看表演。",
     "tool": "审片脚本把片段抽帧拼成检查图，找切镜点、识别画面里的字、量音量；Claude 看检查图；你看片，只说看到的现象。",
     "cost": "不花钱", "outputs": ["5_审片/"],
     "pitfalls": ["脚本量不出表演，硬指标全过也不等于可以交片。",
                  "有动作的那几秒要抽得更密，不然变形会漏掉。",
                  "看片时只说现象，原因和改法交给 Claude。"]},
    {"key": "fix", "title": "修补",
     "what": "审片发现问题，先想能不能在剪辑里修；修不了再重新生成，而且只重抽有问题的那一段。",
     "tool": "剪辑里的修法：推近把字裁出画面、打码、只换画面保留原声、剪掉坏帧。重抽前先找到原因、改好提示词。",
     "cost": "剪辑修补不花钱；重抽一段按秒计费", "outputs": ["6_成片/剪辑表.json"],
     "pitfalls": ["硬边打码的方块很显眼，优先用推近把字裁掉。",
                  "不找原因就重抽，多半还是同样的问题。"]},
    {"key": "output", "title": "剪辑出片",
     "what": "按剪辑表把各段拼成成片：每段用哪一条、从第几秒到第几秒、音量统一、结尾定格淡出，最后接片尾卡。",
     "tool": "剪辑表（一个 json 文件）加剪辑脚本（调用 ffmpeg）。改了剪辑表，重新运行就能重新出片。",
     "cost": "不花钱", "outputs": ["6_成片/"],
     "pitfalls": ["每段的音量要统一，不然接缝处忽大忽小。",
                  "结尾别太急，给观众留一点回味的时间。",
                  "出片后写自审报告，再交给你看。"]},
]
_probe_cache = {}
_marks_lock = threading.Lock()


def kind_of(name):
    ext = Path(name).suffix.lower()
    return next((k for k, exts in KINDS.items() if ext in exts), "other")


def area_of(parts):
    if len(parts) == 1:
        return "根目录"
    if parts[0] == "归档" and len(parts) > 2:
        return f"归档/{parts[1]}"
    return parts[0]


def group_of(area):
    if area.startswith("归档"):
        return "归档"
    if area.startswith("实验"):
        return "实验"
    return area


def clean(text):
    return re.sub(r"[*`]", "", text).strip()


def take_no(stem):
    """S6_t1_2.5_720p、S6_t1_两张床 → "1"；不是这种命名返回 None。"""
    m = re.match(r"S\d+_t(\d+)(?:_|$)", stem)
    return m.group(1) if m else None


def list_files(project):
    out = []
    for dirpath, dirnames, filenames in os.walk(project):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d != "__pycache__")
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if name.startswith(".") or p.is_symlink():
                continue
            rel = p.relative_to(project)
            st = p.stat()
            out.append({"path": rel.as_posix(), "name": name, "kind": kind_of(name), "size": st.st_size,
                        "mtime": st.st_mtime, "area": area_of(rel.parts)})
    return out


def md_tables(text):
    """Markdown 表格 → [[{表头: 单元格}, ...], ...]；跳过代码块里的内容。"""
    tables, rows, in_code = [], [], False
    for line in text.splitlines() + [""]:
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
        if not in_code and s.startswith("|") and s.endswith("|") and len(s) > 1:
            rows.append([c.strip() for c in s[1:-1].split("|")])
            continue
        if len(rows) >= 2 and all(re.fullmatch(r":?-{3,}:?", c) for c in rows[1] if c):
            head = rows[0]
            body = [dict(zip(head, r + [""] * (len(head) - len(r)))) for r in rows[2:]]
            if body:
                tables.append(body)
        rows = []
    return tables


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def probe_media(path):
    """ffprobe 取时长和画面尺寸，按文件大小和修改时间缓存；失败返回空值，不抛错。"""
    try:
        st = path.stat()
    except OSError:
        return {"duration": None, "width": None, "height": None}
    key = (str(path), st.st_size, st.st_mtime)
    if key not in _probe_cache:
        info = {"duration": None, "width": None, "height": None}
        try:
            r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height:format=duration", "-of", "json", str(path)],
                               capture_output=True, text=True, timeout=20)
            d = json.loads(r.stdout or "{}")
            stream = (d.get("streams") or [{}])[0]
            dur = d.get("format", {}).get("duration")
            info = {"duration": round(float(dur), 3) if dur else None,
                    "width": stream.get("width"), "height": stream.get("height")}
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
        _probe_cache[key] = info
    return _probe_cache[key]


def timeline(project, edl, probe):
    """和 edit.py 同样的算法：每段长度 = 出点 - 入点 + 定格，最后接片尾卡。缺片段时返回 None。"""
    rows, t = [], 0.0
    for row in edl.get("段落", []):
        if not isinstance(row, dict) or not row.get("文件"):
            continue
        a0 = float(row.get("入点") or 0)
        a1 = row.get("出点")
        a1 = float(a1) if a1 is not None else probe(project / row["文件"]).get("duration")
        if a1 is None:
            return None
        d = a1 - a0 + float(row.get("定格") or 0)
        rows.append({"段": row.get("段", ""), "文件": row["文件"], "起": round(t, 3), "止": round(t + d, 3),
                     "入点": a0, "备注": row.get("备注", "")})
        t += d
    card = edl.get("片尾卡")
    if isinstance(card, dict) and card.get("时长"):
        d = float(card["时长"])
        rows.append({"段": "片尾", "文件": card.get("图片", ""), "起": round(t, 3), "止": round(t + d, 3),
                     "入点": 0, "备注": ""})
    return rows


def scan(project, probe=probe_media):
    project = Path(project)
    files = list_files(project)
    idx = {f["path"]: f for f in files}

    def read(rel):
        try:
            return (project / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    docs = [dict(f) for f in files if f["kind"] == "doc"]
    texts = {d["path"]: read(d["path"]) for d in docs}
    for d in docs:
        m = re.search(r"^#\s+(.+)$", texts[d["path"]], re.M)
        d["title"] = m.group(1).strip() if m else Path(d["path"]).stem

    segs, people = {}, {}

    def seg(sid):
        return segs.setdefault(sid, {"id": sid, "fields": {}, "takes": [], "refs": {}, "used": None,
                                     "prompt_path": None, "prompt": "", "dialogue": [], "cost": 0.0})

    # 1_文档 里的表：段 → 内容、台词、候选、过审……（分段表覆盖剧本）；人物 → 辨识特征、服装……
    table_docs = sorted((p for p in texts if p.startswith("1_文档/") and "/参考/" not in p),
                        key=lambda p: ("剧本" not in p, p))
    for rel in table_docs:
        for table in md_tables(texts[rel]):
            first = next(iter(table[0]))
            key = clean(first)
            for row in table:
                name = clean(row[first])
                if key == "段" and SEG_ID.fullmatch(name):
                    seg(name)["fields"].update({clean(k): v for k, v in row.items() if k != first and v})
                elif key in ("人物", "角色") and name:
                    info = people.setdefault(name, {})
                    for k, v in row.items():
                        if k != first and v:
                            info.setdefault(clean(k), v)

    for rel in idx:
        m = re.fullmatch(r"3_提示词/(S\d+)\.txt", rel)
        if m:
            s = seg(m.group(1))
            s["prompt_path"], s["prompt"] = rel, read(rel)
            s["dialogue"] = re.findall(r"\{([^{}]+)\}", s["prompt"])

    ref_path = next((p for p in ("3_提示词/分段.json", "3_提示词/素材.json") if p in idx), None)
    refs = load_json(project / ref_path) if ref_path else None
    for sid, cfg in (refs.items() if isinstance(refs, dict) else []):
        if SEG_ID.fullmatch(sid) and isinstance(cfg, dict):
            seg(sid)["refs"] = {"图片": cfg.get("图片") or cfg.get("images") or [],
                                "音频": cfg.get("音频") or cfg.get("audios") or [],
                                "时长": cfg.get("时长") or cfg.get("duration")}

    edls = {}
    for f in files:
        if f["path"].endswith(".json"):
            d = load_json(project / f["path"])
            if isinstance(d, dict) and isinstance(d.get("段落"), list) and isinstance(d.get("输出"), str):
                edls[f["path"]] = d
    main_edl = "6_成片/剪辑表.json" if "6_成片/剪辑表.json" in edls else next(
        (p for p in edls if not p.startswith("归档/")), None)
    used = {}
    for row in (edls[main_edl]["段落"] if main_edl else []):
        if isinstance(row, dict) and SEG_ID.fullmatch(str(row.get("段", ""))) and row.get("文件"):
            used[row["段"]] = row["文件"]
            seg(row["段"])["used"] = row["文件"]

    outputs = {}
    for p, d in edls.items():
        outputs.setdefault(d["输出"], p)
    films, others = [], []
    for f in files:
        if f["kind"] != "video":
            continue
        rel, stem, area = f["path"], Path(f["path"]).stem, f["area"]
        live = not area.startswith("归档")
        item = dict(f, **(probe(project / rel) if live else {}))
        m = SEG_ID.match(stem)
        sid = m.group(0) if m and stem[m.end():m.end() + 1] in ("", "_") else None
        if rel in outputs or area == "6_成片" or (not re.match(r"S\d+[A-Za-z]?(?:_|$)", stem) and FILM.search(stem)):
            item["group"] = "成片" if area == "6_成片" else ("预览" if live else "历史版本")
            item["edl"] = outputs.get(rel)
            item["timeline"] = timeline(project, edls[item["edl"]], probe) if item["edl"] and live else None
            films.append(item)
            continue
        item["group"] = "候选" if area == "4_生成片段" else group_of(area)
        # 归档里只认按 <段>_t<序号> 命名的废弃候选；旧版本的草稿和中间文件不算这一版的分段
        if not sid or not (live or take_no(stem)):
            item["label"] = stem
            others.append(item)
            continue
        take = TAKE.fullmatch(stem)
        item["label"] = (f"t{take.group(2)} · {take.group(3)} · {take.group(4)}" if take
                         else stem[len(sid) + 1:].replace("_", " · ") or stem)
        item["seg"], item["in_use"] = sid, used.get(sid) == rel
        seg(sid)["takes"].append(item)
    order = {"候选": 0, "实验": 1, "归档": 2}
    seg_list = [segs[k] for k in sorted(segs, key=lambda s: int(s[1:]))]
    for s in seg_list:
        s["takes"].sort(key=lambda t: (not t["in_use"], order.get(t["group"], 3), t["name"]))
        listed = s["fields"].get("候选", "")
        s["cost"] = round(sum(float(x) for x in re.findall(r"¥\s*(\d+(?:\.\d+)?)", listed)), 2)
        # 分段表"候选"一栏的写法：t1（¥15.18；…）
        prices = dict(re.findall(r"(t\d+)\s*[（(]\s*¥\s*(\d+(?:\.\d+)?)", listed))
        for t in s["takes"]:
            n = take_no(Path(t["name"]).stem)
            if n and t["group"] != "实验" and f"t{n}" in prices:
                t["cost"] = float(prices[f"t{n}"])
    films.sort(key=lambda f: ({"成片": 0, "预览": 1}.get(f["group"], 2), -f["mtime"]))

    names = []
    for f in files:
        if f["kind"] == "image" and f["path"].startswith("2_素材/角色/"):
            names.append(Path(f["name"]).stem.split("_")[0])
        elif f["kind"] == "audio" and f["path"].startswith("2_素材/声音/"):
            names.append(Path(f["name"]).stem)
    characters = []
    for name in dict.fromkeys(n for n in names + list(people) if n):
        variants = [dict(f, group="在用" if f["path"].startswith("2_素材/") else group_of(f["area"]))
                    for f in files if f["kind"] == "image" and name in Path(f["name"]).stem
                    and any(w in f["path"] for w in ("三视图", "定妆", "角色"))]
        characters.append({
            "name": name,
            "main": next((v for v in variants if v["path"].startswith("2_素材/角色/")), None),
            "variants": variants,
            "voices": [f for f in files if f["kind"] == "audio" and Path(f["name"]).stem == name],
            "prompts": [f["path"] for f in files if f["path"].startswith("3_提示词/角色/") and name in f["name"]],
            "segments": [s["id"] for s in seg_list
                         if name in s["refs"].get("图片", []) or name in s["refs"].get("音频", [])],
            "info": people.get(name) or {},
        })
    other_assets = [f for f in files if f["path"].startswith("2_素材/")
                    and not f["path"].startswith(("2_素材/角色/", "2_素材/声音/"))]

    marks = load_json(project / MARKS)
    marks = marks if isinstance(marks, list) else []
    handoff = max((d for d in docs if d["area"] == "根目录" and d["name"].startswith("交接")),
                  key=lambda d: d["mtime"], default=None)
    stage_desc = {}
    for table in (md_tables(texts[handoff["path"]]) if handoff else []):
        for row in table:
            cells = list(row.values())
            for i, c in enumerate(cells[:-1]):
                m = re.search(r"归档/([^/`\s]+)", c)
                if m:
                    stage_desc.setdefault(m.group(1), cells[i + 1])

    def summary(prefix):
        fs = [f for f in files if f["path"].startswith(prefix)]
        counts = {}
        for f in fs:
            counts[f["kind"]] = counts.get(f["kind"], 0) + 1
        return {"counts": counts, "first": min((f["mtime"] for f in fs), default=None),
                "last": max((f["mtime"] for f in fs), default=None), "total": len(fs)}

    stages = []
    archive = project / "归档"
    for d in sorted(p for p in (archive.iterdir() if archive.is_dir() else []) if p.is_dir()):
        if not d.name.startswith("."):
            stages.append(dict(summary(f"归档/{d.name}/"), name=d.name, path=f"归档/{d.name}",
                               desc=stage_desc.get(d.name, "")))
    experiments = []
    for d in sorted(p for p in project.iterdir() if p.is_dir() and p.name.startswith("实验")):
        record = next((x["path"] for x in docs if x["path"].startswith(f"{d.name}/")), None)
        experiments.append(dict(summary(f"{d.name}/"), name=d.name, path=d.name, record=record,
                                title=next((x["title"] for x in docs if x["path"] == record), d.name)))

    days = {}
    for f in files:
        day = days.setdefault(datetime.fromtimestamp(f["mtime"]).strftime("%Y-%m-%d"), {})
        counts = day.setdefault(f["area"], {})
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    activity = [{"date": k, "areas": [{"area": a, "counts": c} for a, c in sorted(days[k].items())]}
                for k in sorted(days, reverse=True)[:14]]

    edl = edls.get(main_edl) or {}
    steps = pipeline(idx, files, seg_list, characters, films, marks, edl, main_edl, ref_path)
    latest = max(files, key=lambda f: f["mtime"], default=None)
    settings = {}
    for d in (project, *list(project.parents)[:2]):   # 项目里没有就往上找：总文件夹放一份，各剧各集共用
        try:
            settings = json.loads((d / SETTINGS).read_text(encoding="utf-8"))
            break
        except (OSError, ValueError):
            continue
    return {
        "project": f"{project.parent.name} {project.name}" if re.fullmatch(r"第\d+集", project.name) else project.name,
        "scanned": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": files, "docs": docs, "segments": seg_list, "films": films, "other_videos": others,
        "characters": characters, "other_assets": other_assets, "pipeline": steps,
        "activity": activity, "stages": stages, "experiments": experiments,
        "handoff": handoff["path"] if handoff else None, "main_edl": main_edl, "marks": marks,
        "costs": {"segments": round(sum(s["cost"] for s in seg_list), 2)},
        "latest": {"area": latest["area"], "mtime": latest["mtime"]} if latest else None,
        "started": settings.get("入行日期"),
    }


def walk_dirs(root, depth=4):
    """总文件夹下的非隐藏目录（不进 node_modules 等），最多 depth 层。"""
    root = Path(root)
    for dirpath, dirnames, _ in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS)
        if len(rel.parts) >= depth:
            dirnames[:] = []
        yield Path(dirpath), rel


def find_works(root):
    works = []
    for d, rel in walk_dirs(root):
        info = load_json(d / WORK)
        if isinstance(info, dict):
            films = [f for f in info.get("成片", []) if (d / f).is_file()]
            works.append(dict(info, path=rel.as_posix(), 成片=films,
                              封面=[f for f in info.get("封面", []) if (d / f).is_file()]))
    return sorted(works, key=lambda w: (w.get("日期", ""), w["path"]))


def find_assets(root):
    libs = []
    for d, rel in walk_dirs(root):
        if not (d / ASSET_LIST).is_file():
            continue
        groups = []
        for g in sorted(p for p in d.iterdir() if p.is_dir() and (p / "透明").is_dir()):
            pngs = sorted(x.name for x in (g / "透明").glob("*.png"))
            groups.append({"name": g.name, "items": [f"{rel.as_posix()}/{g.name}/透明/{n}" for n in pngs]})
        libs.append({"name": d.name, "path": rel.as_posix(), "list": f"{rel.as_posix()}/{ASSET_LIST}", "groups": groups})
    return libs


def home(root):
    root = Path(root)
    settings = load_json(root / SETTINGS) or {}
    kinds = sorted(p.stem for p in FLOWS.glob("*.json"))
    return {"root": root.name, "started": settings.get("入行日期"), "kinds": kinds,
            "works": find_works(root), "assets": find_assets(root),
            "scanned": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


def codework(root, rel):
    """代码动画作品：作品.json + 节拍（章节、字幕、旁白）+ 试音、封面、音轨。路径都相对总文件夹。"""
    d = safe_path(root, rel)
    if not d or not d.is_dir():
        raise KeyError(rel)
    info = load_json(d / WORK) or {}
    cues = load_json(d / "film/cues.json") or {}
    base = load_json(d / "film/cues_base.json") or {}
    ev, ev0 = cues.get("ev", {}), base.get("ev", {})
    tags = sorted((k for k in ev if re.fullmatch(r"ch\d+_tag", k)), key=lambda k: int(re.findall(r"\d+", k)[0]))
    names = info.get("章节", [])
    chapters = [{"name": names[i] if i < len(names) else f"第 {i + 1} 章", "t": ev[k], "t0": ev0.get(k)} for i, k in enumerate(tags)]
    pre = rel.rstrip("/") + "/"
    rel_files = lambda pat: sorted(pre + p.relative_to(d).as_posix() for p in d.glob(pat))
    return {"path": rel, "info": dict(info, 成片=[pre + f for f in info.get("成片", []) if (d / f).is_file()],
                                      封面=[pre + f for f in info.get("封面", []) if (d / f).is_file()]),
            "duration": cues.get("duration"), "duration0": base.get("duration"), "chapters": chapters,
            "subs": cues.get("subs", []), "voice": cues.get("voice", []),
            "narration": pre + "voice/旁白.txt" if (d / "voice/旁白.txt").is_file() else None,
            "samples": rel_files("voice/试音/*.mp3"), "audio": pre + "film/out/audio.wav" if (d / "film/out/audio.wav").is_file() else None,
            "credits": pre + "CREDITS.md" if (d / "CREDITS.md").is_file() else None}


def pipeline(idx, files, segs, characters, films, marks, edl, main_edl, ref_path):
    """制作流程 9 步，按项目里有没有对应的文件判断做到哪了。"""
    n = len(segs)

    def doc(rel):
        return [{"label": Path(rel).name, "path": rel}] if rel in idx else []

    def ratio(k, done_text):
        return ("done" if n and k == n else "doing" if k else "todo"), done_text

    sheets = sum(1 for c in characters if c["main"])
    voices = sum(1 for f in files if f["path"].startswith("2_素材/声音/") and f["kind"] == "audio")
    cards = [f for f in files if f["path"].startswith("2_素材/片尾/")]
    prompts = sum(1 for s in segs if s["prompt_path"])
    gen = sum(1 for s in segs if any(t["group"] == "候选" for t in s["takes"]))
    cand = sum(1 for s in segs for t in s["takes"] if t["group"] == "候选")
    exp = sum(1 for s in segs for t in s["takes"] if t["group"] == "实验")
    retakes = sum(1 for s in segs if len({take_no(Path(t["name"]).stem) for t in s["takes"]
                                           if t["group"] != "实验"} - {None}) > 1)
    reviews = [f for f in files if f["path"].startswith("5_审片/") and not f["path"].startswith(MARK_DIR + "/")
               and f["path"] != MARKS]
    pending = sum(1 for m in marks if m.get("状态") == "待处理")
    fixes = sum(len(r.get(k) or []) if isinstance(r.get(k), list) else 1
                for r in edl.get("段落", []) if isinstance(r, dict) for k in ("推近", "打码", "画面替换") if r.get(k))
    final = [f for f in films if f["group"] == "成片"]
    tables = doc("1_文档/连戏表.md") + doc("1_文档/分段表.md")

    raw = [
        (("done" if doc("1_文档/需求.md") else "todo"), "需求.md" if doc("1_文档/需求.md") else "", doc("1_文档/需求.md")),
        (("done" if doc("1_文档/剧本定稿.md") else "todo"), "剧本定稿.md" if doc("1_文档/剧本定稿.md") else "",
         doc("1_文档/剧本定稿.md")),
        (("done" if len(tables) == 2 else "doing" if tables else "todo"), f"{len(tables)}/2 份", tables),
        (("done" if sheets else "doing" if voices else "todo"), f"三视图 {sheets} · 音色 {voices}",
         [{"label": f"三视图 {sheets} 张、音色 {voices} 段", "view": "assets"}]
         + [{"label": f["name"], "path": f["path"]} for f in cards]),
        (*ratio(prompts, f"{prompts}/{n} 段"),
         [{"label": f"{prompts}/{n} 段有提示词", "view": "segments"}] + doc(ref_path or "")),
        (*ratio(gen, f"{gen}/{n} 段"),
         [{"label": f"{gen}/{n} 段已生成，候选 {cand} 条" + (f"，实验 {exp} 条" if exp else ""), "view": "segments"}]),
        (("doing" if pending else "done" if reviews else "todo"),
         f"待处理标记 {pending}" if pending else f"{len(reviews)} 个文件",
         [{"label": f["name"], "path": f["path"]} for f in reviews if f["kind"] == "doc"]
         + [{"label": f"看片标记：待处理 {pending} 条", "view": "review"}]),
        (("done" if final else "todo"), f"修补 {fixes} 处 · 重抽 {retakes} 段",
         ([{"label": f"剪辑里修补 {fixes} 处", "path": main_edl}] if main_edl else [])
         + [{"label": f"重抽过 {retakes} 段", "view": "segments"}]),
        (("done" if final else "todo"), final[0]["name"] if final else "",
         [{"label": f["name"], "film": f["path"]} for f in final] + doc(main_edl or "")),
    ]
    return [dict(step, status=st, summary=sm, items=items) for step, (st, sm, items) in zip(STEPS, raw)]


def load_marks(project):
    p = Path(project) / MARKS
    if not p.exists():
        return []
    marks = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(marks, list):
        raise ValueError(f"{MARKS} 不是列表，先手动检查这个文件")
    return marks


def save_marks(project, marks):
    p = Path(project) / MARKS
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(marks, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(p)


def add_mark(project, body, now=None):
    project = Path(project)
    video = str(body.get("视频") or "")
    if not safe_path(project, video) or not (project / video).is_file():
        raise ValueError(f"找不到视频：{video}")
    sec = round(float(body.get("秒")), 2)
    with _marks_lock:
        marks = load_marks(project)
        now = now or datetime.now()
        base = mid = now.strftime("%Y%m%d-%H%M%S")
        n = 1
        while any(m.get("编号") == mid for m in marks):
            n += 1
            mid = f"{base}-{n}"
        rec = {"编号": mid, "创建": now.strftime("%Y-%m-%d %H:%M:%S"), "视频": video, "秒": sec}
        if body.get("段"):
            rec["段"] = str(body["段"])
        if body.get("段内秒") is not None:
            rec["段内秒"] = round(float(body["段内秒"]), 2)
        rec["说明"] = str(body.get("说明") or "").strip()
        img = str(body.get("截图数据") or "")
        if img.startswith("data:image/") and "," in img:
            head, data = img.split(",", 1)
            ext = ".jpg" if "jpeg" in head else ".png"
            (project / MARK_DIR).mkdir(parents=True, exist_ok=True)
            (project / MARK_DIR / f"{mid}{ext}").write_bytes(base64.b64decode(data))
            rec["截图"] = f"{MARK_DIR}/{mid}{ext}"
        rec["状态"] = "待处理"
        marks.append(rec)
        save_marks(project, marks)
    return rec


def update_mark(project, mid, body):
    with _marks_lock:
        marks = load_marks(project)
        rec = next((m for m in marks if m.get("编号") == mid), None)
        if rec is None:
            raise KeyError(mid)
        if "状态" in body:
            if body["状态"] not in MARK_STATES:
                raise ValueError(f"状态只能是 {'、'.join(MARK_STATES)}")
            rec["状态"] = body["状态"]
        if "说明" in body:
            rec["说明"] = str(body["说明"]).strip()
        save_marks(project, marks)
    return rec


def safe_path(project, rel):
    """只允许项目目录里的非隐藏文件。"""
    rel = unquote(rel or "")
    if not rel or rel.startswith(("/", "\\")) or "\\" in rel or any(p.startswith(".") for p in rel.split("/")):
        return None
    root = Path(project).resolve()
    p = (root / rel).resolve()
    return p if p.is_relative_to(root) and p != root else None


def parse_range(header, size):
    """Range 头 → (起, 止) 闭区间；没有 Range 返回 None，不合法返回 "bad"。"""
    if not header:
        return None
    m = re.fullmatch(r"bytes=(\d*)-(\d*)", header.strip())
    if not m or m.group(1) == m.group(2) == "":
        return "bad"
    if m.group(1) == "":
        n = int(m.group(2))
        if n == 0:
            return "bad"
        start, end = max(0, size - n), size - 1
    else:
        start = int(m.group(1))
        end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
    return (start, end) if start <= end and start < size else "bad"


class Handler(BaseHTTPRequestHandler):
    server_version = "AIVideoWorkbench/1"

    def log_message(self, fmt, *args):
        pass

    def send_body(self, code, body, ctype, extra=None, head=False):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def send_json(self, obj, code=200):
        self.send_body(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        self.route(head=False)

    def do_HEAD(self):
        self.route(head=True)

    def route(self, head):
        u = urlparse(self.path)
        path, q = u.path, parse_qs(u.query)
        work = (q.get("work") or [""])[0]
        try:
            if path in ("/", "/index.html"):
                self.send_body(200, PAGE.read_bytes(), "text/html; charset=utf-8", head=head)
            elif path == "/api/home":
                self.send_json(home(self.server.root))
            elif path == "/api/flow":
                f = safe_path(FLOWS, (q.get("kind") or [""])[0] + ".json")
                if not f or not f.is_file():
                    return self.send_json({"错误": "没有这类做法的流程数据"}, 404)
                self.send_body(200, f.read_bytes(), "application/json; charset=utf-8", head=head)
            elif path == "/api/project":
                d = safe_path(self.server.root, work)
                if not d or not d.is_dir():
                    return self.send_json({"错误": "找不到这个作品"}, 404)
                self.send_json(scan(d))
            elif path == "/api/codework":
                self.send_json(codework(self.server.root, work))
            elif path.startswith("/f/"):
                self.send_file(path[3:], head)
            else:
                self.send_json({"错误": "没有这个地址"}, 404)
        except KeyError:
            self.send_json({"错误": "找不到这个作品"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_file(self, rel, head):
        p = safe_path(self.server.root, rel)
        if not p or not p.is_file():
            return self.send_json({"错误": "找不到文件"}, 404)
        ext = p.suffix.lower()
        ctype = TYPES.get(ext) or ("text/plain; charset=utf-8" if kind_of(p.name) in ("doc", "text")
                                   else "application/octet-stream")
        size = p.stat().st_size
        rng = parse_range(self.headers.get("Range"), size)
        if rng == "bad":
            return self.send_body(416, b"", "text/plain", {"Content-Range": f"bytes */{size}"}, head)
        start, end = rng or (0, size - 1)
        self.send_response(206 if rng else 200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(max(0, end - start + 1)))
        self.send_header("Cache-Control", "no-cache")
        if rng:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        if head or size == 0:
            return
        with p.open("rb") as fh:
            fh.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = fh.read(min(256 * 1024, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > 30 * 1024 * 1024:
                return self.send_json({"错误": "内容太大"}, 413)
            body = json.loads(self.rfile.read(length) or b"{}")
            u = urlparse(self.path)
            project = safe_path(self.server.root, (parse_qs(u.query).get("work") or [""])[0])
            if not project or not project.is_dir():
                return self.send_json({"错误": "找不到这个作品"}, 404)
            path = u.path
            if path == "/api/marks":
                return self.send_json(add_mark(project, body))
            m = re.fullmatch(r"/api/marks/([\w-]+)", path)
            if m:
                return self.send_json(update_mark(project, m.group(1), body))
            self.send_json({"错误": "没有这个地址"}, 404)
        except KeyError:
            self.send_json({"错误": "找不到这条标记"}, 404)
        except (ValueError, TypeError) as e:
            self.send_json({"错误": str(e)}, 400)
        except (BrokenPipeError, ConnectionResetError):
            pass


def make_server(root, host="127.0.0.1", port=8765, tries=20):
    last = None
    for p in ([0] if port == 0 else range(port, port + tries)):
        try:
            server = ThreadingHTTPServer((host, p), Handler)
            server.daemon_threads = True
            server.root = Path(root).resolve()
            return server
        except OSError as e:
            last = e
    raise last


def main(argv=None):
    ap = argparse.ArgumentParser(description="AI 视频工作台：本地网页看各类做法、作品和素材")
    ap.add_argument("--root", default=os.environ.get("AI_VIDEO_ROOT", DEFAULT_ROOT), help="AI 视频总文件夹")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1", help="默认只给本机用")
    ap.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    a = ap.parse_args(argv)
    root = Path(a.root).expanduser().resolve()
    if not root.is_dir():
        print(f"找不到总文件夹：{root}（用 --root 指定，或设环境变量 AI_VIDEO_ROOT）", file=sys.stderr)
        return 1
    server = make_server(root, a.host, a.port)
    url = f"http://{a.host}:{server.server_address[1]}/"
    print(f"AI 视频工作台：{url}  （总文件夹：{root}；按 Ctrl+C 退出）", flush=True)
    if not a.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
