# -*- coding: utf-8 -*-
"""雪花变画用的小团子新动作：生图网关 images/edits，参考 01_挥手打招呼 原图。输出到 /tmp/xtz_new/原图。"""
import base64, json, os, subprocess, sys
from pathlib import Path
GATEWAY = (os.environ.get("IMAGE_GATEWAY_BASE_URL") or os.environ.get("IMAGE_API_BASE", "").removesuffix("/v1")
           or "https://yunyihui.mystic.net.cn/image-api").rstrip("/")   # 域名入口，走代理即可；云端环境变量 IMAGE_API_BASE 带 /v1   # 域名入口，走代理即可
LIB = Path(__file__).resolve().parents[3] / "共用/小团子AI素材"   # AI视频/共用/…：Mac 的 ~/Downloads/AI视频 和仓库里的 AI视频 结构一样
REF = LIB / "动作/原图/01_挥手打招呼.png"
OUT = Path("/tmp/xtz_new/原图"); OUT.mkdir(parents=True, exist_ok=True)
KEY = os.environ.get("IMAGE_API_KEY") or (Path.home() / ".config/image-gateway/api-key").read_text().strip()   # 云端读环境变量，本机读文件
BASE = ("保持参考图里同一个角色的长相和画风：白色软糯的饭团状小团子，圆脸，黑豆眼，粉色腮红，橙色小嘴，"
        "整体有粗白描边的贴纸风格，深色细轮廓线，橙色点缀。换成新的姿势和表情：{a}。"
        "只画这一个角色和它手里的道具，完整全身居中，四周留出空白。不要键盘、不要回车键、不要胸前徽章、不要任何文字。"
        "背景：不透明、纯色浅蓝 #DCE8FA、无纹理无噪点。")
ACTS = {
    "11_拿抹布擦": "一只手拿着一块浅蓝色的抹布，正用力朝画面右侧来回擦一块看不见的玻璃，身体微微前倾，表情认真带点开心，抹布旁有几道橙色的擦拭动作线",
    "12_记笔记": "双手捧着一个小笔记本，一只手拿铅笔正在写，眼睛盯着本子，表情专注，头顶一个小小的橙色闪光",
    "13_拧旋钮": "双手握住身前一个大大的圆形旋钮（浅灰色，上面一道橙色指示线），正用力拧，表情认真，旋钮旁有一道弧形的橙色转动箭头",
    "14_按骰子": "一只手高高抬起，正往下拍身前一个大大的白色骰子（橙色圆点，像一个大按钮），表情兴奋期待，骰子旁有几道橙色的弹跳动作线",
    "15_举着抹布": "一只手把浅蓝色的抹布高高举过头顶，像举着奖杯，另一只手叉腰，表情得意开心，周围几颗橙色和蓝色的小星星",
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
