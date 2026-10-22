"""AI 视频工作台：一个本地网页，打开就看到短剧和代码动画各做到哪，点进去看角色照片和剧本。

python3 studio.py [--root AI视频总文件夹] [--port 8765] [--lan] [--no-open]

总文件夹默认取环境变量 AI_VIDEO_ROOT，没有就是 ~/Downloads/AI视频。里面每个作品文件夹放一个 作品.json：
  {"类别": "短剧" 或 "代码动画", "标题": "...", "状态": "进行中" / "暂停" / "已完成", "日期": "2026-10-19",
   "角色": [{"名字": "林悦", "照片": "2_素材/角色/林悦_三视图.png", "位置": "左"}],
   "剧本": {"文件": "AI视频/短剧/能不能不切/剧本.md", "章节": ["正式剧本"], "截止": "**制作要求**"},
   "成片": ["6_成片/xx.mp4"]}
- 角色照片相对作品文件夹，可以指到总文件夹里的别处（如 ../../共用/…）；没有照片只写名字。
  "位置"是方形头像从哪边裁（左 / 中 / 右，默认中）：三视图的胸像在最左边，写"左"。
- 剧本文件以 AI视频/ 开头的从本仓库读，其余相对作品文件夹。.md 只取"章节"里列的二级标题（不写就整篇），
  遇到"截止"那一行就停；.txt 每行一句旁白。
- 只显示现行的东西：只有状态是"已完成"的作品才显示成片，其余不显示（旧成片往往落后于剧本）。

网页只读，不写任何文件。默认只给本机用；加 --lan 让同一局域网的电脑和手机也能打开。按 Ctrl+C 退出。
"""
import argparse
import hashlib
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

REPO = Path(__file__).resolve().parent
PAGE = REPO / "studio.html"
SETTINGS = "工作台.json"  # 总文件夹里的设置，例如 {"入行日期": "2026-10-17"}
WORK = "作品.json"
DEFAULT_ROOT = "~/Downloads/AI视频"
SKIP_DIRS = {"node_modules", "__pycache__", "归档"}
KIND_ORDER = ("短剧", "代码动画")
STATES = ("进行中", "暂停", "已完成")      # 也是作品在首页的排序
CROP = {"左": "left", "中": "center", "右": "right"}
TYPES = {".mp4": "video/mp4", ".m4v": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
         ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
         ".gif": "image/gif", ".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4"}
IMAGES = (".png", ".jpg", ".jpeg", ".webp", ".gif")
THUMBS = Path(tempfile.gettempdir()) / "ai-video-workbench-thumbs"
THUMB_PX = 640


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def walk_dirs(root, depth=4):
    """总文件夹下的非隐藏目录（不进 node_modules、归档 等），最多 depth 层。"""
    root = Path(root)
    for dirpath, dirnames, _ in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS)
        if len(rel.parts) >= depth:
            dirnames[:] = []
        yield Path(dirpath), rel


def inside(root, p):
    """p 在总文件夹里就返回相对路径（/ 分隔），否则 None。"""
    try:
        return Path(p).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return None


def status_of(info):
    s = str(info.get("状态") or "")
    if s in STATES:
        return s
    return "已完成" if s.startswith("已完成") else "暂停" if "暂停" in s else "进行中"


def characters(root, d, info):
    out = []
    for c in info.get("角色") or []:
        if not isinstance(c, dict) or not c.get("名字"):
            continue
        rel = None
        if c.get("照片"):
            p = d / c["照片"]
            rel = inside(root, p) if p.is_file() else None
        out.append({"名字": c["名字"], "照片": rel, "位置": CROP.get(c.get("位置"), "center")})
    return out


def summary(root, d, rel, info):
    return {"id": rel, "标题": info.get("标题") or d.name, "类别": info.get("类别") or "其他",
            "状态": status_of(info), "日期": info.get("日期", ""), "角色": characters(root, d, info)}


def find_works(root):
    root = Path(root)
    works = []
    for d, rel in walk_dirs(root):
        info = load_json(d / WORK)
        if isinstance(info, dict):
            works.append(summary(root, d, rel.as_posix(), info))
    # 进行中的排前面，同一状态里新的在前
    works.sort(key=lambda w: w["日期"], reverse=True)
    works.sort(key=lambda w: STATES.index(w["状态"]))
    return works


def days_since(start, today=None):
    try:
        return ((today or date.today()) - date.fromisoformat(start)).days + 1
    except (TypeError, ValueError):
        return None


def home(root):
    root = Path(root)
    settings = load_json(root / SETTINGS) or {}
    works = find_works(root)
    kinds = list(KIND_ORDER) + sorted({w["类别"] for w in works} - set(KIND_ORDER))
    return {"day": days_since(settings.get("入行日期")),
            "groups": [{"类别": k, "作品": [w for w in works if w["类别"] == k]} for k in kinds]}


def pick_sections(text, wanted, stop=None):
    """只留二级标题在 wanted 里（按开头匹配）的几节；wanted 为空就整篇去掉一级标题。遇到 stop 开头的行就停。"""
    out, keep = [], not wanted
    for line in text.splitlines():
        m = re.match(r"##\s+(.+)", line)
        if m:
            keep = not wanted or any(m.group(1).strip().startswith(w) for w in wanted)
            if keep and len(wanted) != 1:
                out.append(line)            # 只取一节时节名不用再显示
            continue
        if re.match(r"#\s", line):
            continue
        if stop and line.strip().startswith(stop):
            keep = False
        if keep:
            out.append(line)
    return "\n".join(out)


LIST_ITEM = re.compile(r"\s*(?:[-*]|\d+[.、])\s+(.*)")
SPEAKER = re.compile(r"\*\*([^*]{1,12})\*\*")


def parse_script(text):
    """Markdown 剧本 → 排版用的块：节名 h2、场景 h、台词 say、动作 p、列表 list、表格 table、说明 note。"""
    blocks, para = [], []

    def flush():
        if not para:
            return
        m = SPEAKER.fullmatch(para[0].strip())
        if m and len(para) > 1:
            blocks.append({"t": "say", "who": m.group(1).strip(), "text": "\n".join(x.strip() for x in para[1:])})
        else:
            blocks.append({"t": "p", "text": "\n".join(x.strip() for x in para)})
        para.clear()

    rows = []

    def flush_table():
        if len(rows) >= 2:
            body = [r for r in rows[1:] if not all(re.fullmatch(r":?-{3,}:?", c) for c in r if c)]
            blocks.append({"t": "table", "head": rows[0], "rows": body})
        elif rows:
            blocks.append({"t": "p", "text": " | ".join(rows[0])})
        rows.clear()

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and len(s) > 1:
            flush()
            rows.append([c.strip() for c in s[1:-1].split("|")])
            continue
        flush_table()
        h = re.match(r"(#{2,6})\s+(.+)", s)
        item = LIST_ITEM.fullmatch(line)
        if not s or s.startswith("```") or re.fullmatch(r"-{3,}|\*{3,}", s):
            flush()
        elif h:
            flush()
            blocks.append({"t": "h2" if len(h.group(1)) == 2 else "h", "text": h.group(2).strip()})
        elif s.startswith(">"):
            flush()
            blocks.append({"t": "note", "text": s.lstrip("> ").strip()})
        elif item:
            flush()
            if blocks and blocks[-1]["t"] == "list":
                blocks[-1]["items"].append(item.group(1).strip())
            else:
                blocks.append({"t": "list", "items": [item.group(1).strip()]})
        else:
            para.append(line)
    flush()
    flush_table()
    return blocks


def script_of(d, spec):
    """作品.json 的"剧本" → {"来源": 显示用的路径, "blocks": [...]}；没配就 None。"""
    if isinstance(spec, str):
        spec = {"文件": spec}
    if not isinstance(spec, dict) or not spec.get("文件"):
        return None
    f = str(spec["文件"])
    p = REPO / f if f.startswith("AI视频/") else d / f
    wanted = [str(x) for x in spec.get("章节") or []]
    label = f + (f" · {'、'.join(wanted)}" if wanted else "")
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return {"来源": label, "blocks": [], "缺失": True}
    if p.suffix.lower() == ".txt":
        blocks = [{"t": "say", "who": spec.get("说话人") or "旁白", "text": x.strip()} for x in text.splitlines() if x.strip()]
    else:
        blocks = parse_script(pick_sections(text, wanted, spec.get("截止")))
    return {"来源": label, "blocks": blocks}


def work(root, rel):
    root = Path(root)
    d = safe_path(root, rel)
    info = load_json(d / WORK) if d and d.is_dir() else None
    if not isinstance(info, dict):
        raise KeyError(rel)
    out = summary(root, d, rel, info)
    films = info.get("成片") or []
    films = [films] if isinstance(films, str) else films
    film = next((inside(root, d / f) for f in films if (d / f).is_file()), None)
    out["成片"] = film if out["状态"] == "已完成" else None
    out["剧本"] = script_of(d, info.get("剧本"))
    return out


def thumbnail(src):
    """用 macOS 自带的 sips 缩成小图，按路径、大小、修改时间缓存；没有 sips 或失败就返回 None，直接给原图。"""
    sips = shutil.which("sips")
    if not sips or src.suffix.lower() not in IMAGES:
        return None
    st = src.stat()
    key = hashlib.sha1(f"{src}|{st.st_size}|{st.st_mtime}|{THUMB_PX}".encode()).hexdigest()
    out = THUMBS / f"{key}.jpg"
    if not out.is_file():
        THUMBS.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".tmp.jpg")
        try:
            subprocess.run([sips, "-Z", str(THUMB_PX), "--setProperty", "format", "jpeg", str(src), "--out", str(tmp)],
                           capture_output=True, timeout=30, check=True)
            tmp.replace(out)
        except (OSError, subprocess.SubprocessError):
            return None
    return out


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
    server_version = "AIVideoWorkbench/2"

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
        try:
            if path in ("/", "/index.html"):
                self.send_body(200, PAGE.read_bytes(), "text/html; charset=utf-8", head=head)
            elif path == "/api/home":
                self.send_json(home(self.server.root))
            elif path == "/api/work":
                self.send_json(work(self.server.root, (q.get("id") or [""])[0]))
            elif path.startswith("/f/"):
                self.send_file(path[3:], head)
            elif path.startswith("/t/"):
                self.send_file(path[3:], head, thumb=True)
            else:
                self.send_json({"错误": "没有这个地址"}, 404)
        except KeyError:
            self.send_json({"错误": "找不到这个作品"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_file(self, rel, head, thumb=False):
        p = safe_path(self.server.root, rel)
        if not p or not p.is_file():
            return self.send_json({"错误": "找不到文件"}, 404)
        if thumb:
            p = thumbnail(p) or p
        ctype = TYPES.get(p.suffix.lower(), "application/octet-stream")
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


HOME_NETS = [ipaddress.ip_network(n) for n in ("192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12")]


def pick_lan(candidates):
    """从网卡地址里挑家用局域网那个；代理软件的虚拟网卡（如 198.18.x）不算。"""
    for ip in candidates:
        try:
            if any(ipaddress.ip_address(ip) in n for n in HOME_NETS):
                return ip
        except ValueError:
            continue
    return None


def lan_ip():
    """本机在局域网里的地址：先看 ifconfig 列出的网卡，再退回 UDP connect（不发包）选出口网卡。"""
    found = []
    try:
        out = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=5).stdout
        found += re.findall(r"inet (?:addr:)?(\d+\.\d+\.\d+\.\d+)", out)
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.168.0.1", 9))
            found.append(s.getsockname()[0])
    except OSError:
        pass
    return pick_lan(found)


def main(argv=None):
    ap = argparse.ArgumentParser(description="AI 视频工作台：看短剧和代码动画各做到哪、每部的角色和剧本")
    ap.add_argument("--root", default=os.environ.get("AI_VIDEO_ROOT", DEFAULT_ROOT), help="AI 视频总文件夹")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--lan", action="store_true", help="让同一局域网的电脑和手机也能打开（默认只给本机用）")
    ap.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    a = ap.parse_args(argv)
    root = Path(a.root).expanduser().resolve()
    if not root.is_dir():
        print(f"找不到总文件夹：{root}（用 --root 指定，或设环境变量 AI_VIDEO_ROOT）", file=sys.stderr)
        return 1
    server = make_server(root, "0.0.0.0" if a.lan else "127.0.0.1", a.port)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/"
    ip = lan_ip() if a.lan else None
    lan = f"http://{ip}:{port}/" if ip else None
    print(f"AI 视频工作台：{url}" + (f"  局域网：{lan}" if lan else "") + f"  （总文件夹：{root}；按 Ctrl+C 退出）", flush=True)
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
