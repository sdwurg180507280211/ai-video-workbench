# -*- coding: utf-8 -*-
"""雪花变画的封面插画：生图网关 images/edits，参考 11_拿抹布擦 原图，纯色浅蓝底（之后用素材库 抠图.py 抠透明）。
输出 assets/cover/原图/插画_横.png、插画_竖.png；已有的跳过。"""
import base64, json, os, subprocess, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent
GATEWAY = (os.environ.get("IMAGE_GATEWAY_BASE_URL") or os.environ.get("IMAGE_API_BASE", "").removesuffix("/v1")
           or "https://yunyihui.mystic.net.cn/image-api").rstrip("/")   # 域名入口，走代理即可；云端环境变量 IMAGE_API_BASE 带 /v1
REF = Path(__file__).resolve().parents[3] / "共用/小团子AI素材" / "动作/原图/11_拿抹布擦.png"
OUT = D / "assets/cover/原图"; OUT.mkdir(parents=True, exist_ok=True)
KEY = os.environ.get("IMAGE_API_KEY") or (Path.home() / ".config/image-gateway/api-key").read_text().strip()   # 云端读环境变量，本机读文件
BASE = ("保持参考图里同一个角色的长相和画风：白色软糯的饭团状小团子，圆脸，黑豆眼，粉色腮红，橙色小嘴，粗白描边的贴纸风格，深色细轮廓线。"
        "画面：小团子站在一块竖立的方形画板旁边，手拿浅蓝色抹布正在擦画板，表情开心认真。画板左半边还是黑白灰的电视雪花噪点，"
        "右半边已经被擦干净，露出一只可爱的灰色小猫，脖子上围着红围巾，暖米色背景；擦过的边界有几道橙色的擦拭动作线，"
        "周围飘着几颗小小的黑白灰方块雪花点和橙色、蓝色小星星。{layout}"
        "只画角色、画板和这些小元素，不要任何文字、字母、数字、按钮或界面。背景：不透明、纯色浅蓝 #DCE8FA、无纹理无噪点。")
JOBS = {
    "插画_横": "横向构图，画板在左、小团子在右，主体占满画面，四周少留空白。",
    "插画_竖": "竖向构图，画板在上偏左、小团子在右下，主体占满画面，四周少留空白。",
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
