# -*- coding: utf-8 -*-
"""一本正经的封面插画：生图网关 images/edits，参考 16_举着写满的试卷 原图，纯色浅蓝底（之后用素材库 抠图.py 抠透明）。
输出 assets/cover/原图/插画_横.png、插画_竖.png；已有的跳过。"""
import base64, json, os, subprocess, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent
GATEWAY = (os.environ.get("IMAGE_GATEWAY_BASE_URL") or os.environ.get("IMAGE_API_BASE", "").removesuffix("/v1")
           or "https://yunyihui.mystic.net.cn/image-api").rstrip("/")   # 域名入口，走代理即可；云端环境变量 IMAGE_API_BASE 带 /v1
REF = Path(__file__).resolve().parents[3] / "共用/小团子AI素材" / "动作/原图/16_举着写满的试卷.png"
OUT = D / "assets/cover/原图"; OUT.mkdir(parents=True, exist_ok=True)
KEY = os.environ.get("IMAGE_API_KEY") or (Path.home() / ".config/image-gateway/api-key").read_text().strip()   # 云端读环境变量，本机读文件
BASE = ("保持参考图里同一个角色的长相和画风：白色软糯的饭团状小团子，圆脸，黑豆眼，粉色腮红，橙色小嘴，粗白描边的贴纸风格，深色细轮廓线。"
        "画面：小团子双手举着一张写得满满的试卷（纸上只有密密麻麻的灰色横线，没有任何字），表情一本正经但有点心虚，额头一滴汗珠；"
        "旁边一个大大的白色对话气泡，气泡里只有几条灰色横线和一个大大的橙色感叹号；气泡旁飘着三张小卡片，每张上面只有一个大大的问号，"
        "周围几颗橙色和蓝色的小星星。{layout}"
        "只画角色、画板和这些小元素，不要任何文字、字母、数字、按钮或界面。背景：不透明、纯色浅蓝 #DCE8FA、无纹理无噪点。")
JOBS = {
    "插画_横": "横向构图，对话气泡在左上、小团子在右下，主体占满画面，四周少留空白。",
    "插画_竖": "竖向构图，对话气泡在上、小团子在下偏右，主体占满画面，四周少留空白。",
}
for name in sys.argv[1:] or JOBS:
    dst = OUT / f"{name}.png"
    if dst.exists():
        continue
    for attempt in range(2):
        r = subprocess.run(["curl", "-sS", "--max-time", "600", "-A", "xiaotuanzi-routine/1",
                            "-H", f"Authorization: Bearer {KEY}",
                            "-F", "model=gpt-image-2.5-sunburst", "-F", f"image=@{REF}", "-F", "prompt=" + BASE.format(layout=JOBS[name]),
                            "-F", "size=auto", "-F", "quality=auto", "-F", "n=1",
                            f"{GATEWAY}/v1/images/edits"], capture_output=True)
        try:
            dst.write_bytes(base64.b64decode(json.loads(r.stdout)["data"][0]["b64_json"]))
            print("ok", name, flush=True); break
        except Exception:
            print("fail", name, r.stdout[:200], r.stderr[:200], flush=True)
