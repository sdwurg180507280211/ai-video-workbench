# -*- coding: utf-8 -*-
"""一本正经用的小团子新动作：生图网关 images/edits，参考 01_挥手打招呼 原图。输出到 /tmp/xtz_new/原图。"""
import base64, json, os, subprocess, sys
from pathlib import Path
GATEWAY = (os.environ.get("IMAGE_GATEWAY_BASE_URL") or os.environ.get("IMAGE_API_BASE", "").removesuffix("/v1")
           or "https://yunyihui.mystic.net.cn/image-api").rstrip("/")   # 域名入口，走代理即可；云端环境变量 IMAGE_API_BASE 带 /v1   # 域名入口，走代理即可
LIB = Path(__file__).resolve().parents[3] / "共用/小团子AI素材"   # AI视频/共用/…：Mac 的 ~/Downloads/AI视频 和仓库里的 AI视频 结构一样
REF = LIB / "动作/原图/01_挥手打招呼.png"
OUT = Path(__file__).resolve().parent.parent / "assets/new_stickers/原图"; OUT.mkdir(parents=True, exist_ok=True)
KEY = os.environ.get("IMAGE_API_KEY") or (Path.home() / ".config/image-gateway/api-key").read_text().strip()   # 云端读环境变量，本机读文件
BASE = ("保持参考图里同一个角色的长相和画风：白色软糯的饭团状小团子，圆脸，黑豆眼，粉色腮红，橙色小嘴，"
        "整体有粗白描边的贴纸风格，深色细轮廓线，橙色点缀。换成新的姿势和表情：{a}。"
        "只画这一个角色和它手里的道具，完整全身居中，四周留出空白。不要键盘、不要回车键、不要胸前徽章、不要任何文字。"
        "背景：不透明、纯色浅蓝 #DCE8FA、无纹理无噪点。")
ACTS = {
    "16_举着写满的试卷": "双手把一张写得满满的试卷举在胸前给人看（白纸，上面密密麻麻的灰色横线代表字迹，右上角一个空白的分数框，纸上没有任何真实文字），表情有点心虚地笑，眼睛往旁边瞟，额头一滴小汗珠",
}
for name in sys.argv[1:] or ACTS:
    dst = OUT / f"{name}.png"
    if dst.exists():
        continue
    for attempt in range(2):
        r = subprocess.run(["curl", "-sS", "--max-time", "600", "-A", "xiaotuanzi-routine/1",
                            "-H", f"Authorization: Bearer {KEY}",
                            "-F", "model=gpt-image-2.5-sunburst", "-F", f"image=@{REF}", "-F", "prompt=" + BASE.format(a=ACTS[name]),
                            "-F", "size=auto", "-F", "quality=auto", "-F", "n=1",
                            f"{GATEWAY}/v1/images/edits"], capture_output=True)
        try:
            dst.write_bytes(base64.b64decode(json.loads(r.stdout)["data"][0]["b64_json"]))
            print("ok", name, flush=True); break
        except Exception:
            print("fail", name, r.stdout[:200], r.stderr[:200], flush=True)
