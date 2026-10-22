"""Offline tests for the workbench server: a synthetic AI 视频 root folder in a temp dir."""
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import studio  # noqa: E402

SCRIPT = """# 某剧

## 这一版想拍什么

不该显示的说明。

## 正式剧本

### 一、诊室 · 日

报告摊在桌中央。
医生低眼看着。

**林悦**
医生，我想问一下——

| 段 | 台词 |
|---|---|
| S1 | 你好 |

- [0–4 秒] 中景。她说：{还没怀呢。}<门外叫号>
- [4–8 秒] 医生抬头。

## 导演处理

- 不该显示的导演说明。
"""


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def work_json(p, info):
    write(p / "作品.json", json.dumps(info, ensure_ascii=False))


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = Path(self.tmp.name) / "AI视频"
        write(r / "工作台.json", json.dumps({"入行日期": "2026-10-17"}))
        write(r.parent / "外面.png", "png")                                                # 总文件夹外的文件
        drama = r / "短剧/某剧/第1集"
        work_json(drama, {"类别": "短剧", "标题": "某剧", "状态": "进行中", "日期": "2026-10-21",
                          "角色": [{"名字": "林悦", "照片": "2_素材/角色/林悦_三视图.png", "位置": "左"},
                                   {"名字": "医生"}, {"名字": "路人", "照片": "../../../../外面.png"}],
                          "剧本": {"文件": "1_文档/剧本.md", "章节": ["正式剧本"]},
                          "成片": ["6_成片/旧版.mp4"]})
        write(drama / "1_文档/剧本.md", SCRIPT)
        (drama / "2_素材/角色").mkdir(parents=True)
        (drama / "2_素材/角色/林悦_三视图.png").write_bytes(b"png")
        (drama / "6_成片").mkdir()
        (drama / "6_成片/旧版.mp4").write_bytes(b"old")
        work_json(r / "短剧/老剧/第1集", {"类别": "短剧", "标题": "老剧", "状态": "已完成（v6）", "日期": "2026-10-17"})
        work_json(r / "短剧/停剧/第1集", {"类别": "短剧", "标题": "停剧", "状态": "成片 v1 完成；暂停", "日期": "2026-10-20"})
        code = r / "技术解说/示例片"
        work_json(code, {"类别": "代码动画", "标题": "示例", "状态": "已完成", "日期": "2026-10-19",
                         "成片": ["缺失.mp4", "a.mp4"], "剧本": "voice/旁白.txt",
                         "角色": [{"名字": "团子", "照片": "../../共用/团子.png"}]})
        (code / "a.mp4").write_bytes(b"0123456789")
        write(code / "voice/旁白.txt", "第一句。\n\n第二句。\n")
        write(r / "共用/团子.png", "png")
        work_json(r / "短剧/某剧/归档/旧版", {"类别": "短剧", "标题": "不该出现"})          # 归档不扫
        write(code / "node_modules/x/作品.json", "{}")                                      # 依赖目录不扫

    def tearDown(self):
        self.tmp.cleanup()

    def test_home_groups_kinds_and_orders_by_status(self):
        h = studio.home(self.root)
        self.assertIsInstance(h["day"], int)
        self.assertEqual([g["类别"] for g in h["groups"]], ["短剧", "代码动画"])
        dramas = h["groups"][0]["作品"]
        self.assertEqual([(w["标题"], w["状态"]) for w in dramas],
                         [("某剧", "进行中"), ("停剧", "暂停"), ("老剧", "已完成")])
        self.assertEqual([w["标题"] for w in h["groups"][1]["作品"]], ["示例"])

    def test_short_drama_shows_cast_and_formal_script_only(self):
        w = studio.work(self.root, "短剧/某剧/第1集")
        self.assertIsNone(w["成片"])                                   # 没完成就不显示旧成片
        self.assertEqual(w["角色"], [
            {"名字": "林悦", "照片": "短剧/某剧/第1集/2_素材/角色/林悦_三视图.png", "位置": "left"},
            {"名字": "医生", "照片": None, "位置": "center"},
            {"名字": "路人", "照片": None, "位置": "center"}])             # 总文件夹外的照片不给
        s = w["剧本"]
        self.assertEqual(s["来源"], "1_文档/剧本.md · 正式剧本")
        self.assertEqual([b["t"] for b in s["blocks"]], ["h", "p", "say", "table", "list"])
        self.assertEqual(s["blocks"][1]["text"], "报告摊在桌中央。\n医生低眼看着。")
        self.assertEqual(s["blocks"][2], {"t": "say", "who": "林悦", "text": "医生，我想问一下——"})
        self.assertEqual(s["blocks"][3]["rows"], [["S1", "你好"]])
        self.assertEqual(len(s["blocks"][4]["items"]), 2)
        self.assertNotIn("不该显示", json.dumps(s, ensure_ascii=False))

    def test_finished_code_animation_shows_film_and_narration(self):
        w = studio.work(self.root, "技术解说/示例片")
        self.assertEqual(w["成片"], "技术解说/示例片/a.mp4")             # 跳过不存在的文件
        self.assertEqual(w["角色"][0]["照片"], "共用/团子.png")
        self.assertEqual(w["剧本"]["blocks"], [{"t": "say", "who": "旁白", "text": "第一句。"},
                                              {"t": "say", "who": "旁白", "text": "第二句。"}])

    def test_missing_script_and_bad_ids(self):
        w = studio.work(self.root, "短剧/老剧/第1集")
        self.assertIsNone(w["剧本"])
        for bad in ("../x", "/etc", ".hidden", "", "短剧"):
            with self.assertRaises(KeyError):
                studio.work(self.root, bad)

    def test_pick_sections_keeps_titles_for_several_and_stops(self):
        text = "# 题\n## 故事\n甲\n## 分段\n乙\n**制作要求**\n丙\n## 其他\n丁"
        self.assertEqual(studio.pick_sections(text, ["故事", "分段"], "**制作要求**"), "## 故事\n甲\n## 分段\n乙")
        self.assertEqual(studio.pick_sections(text, []), "## 故事\n甲\n## 分段\n乙\n**制作要求**\n丙\n## 其他\n丁")

    def test_bold_line_alone_is_not_a_speaker(self):
        self.assertEqual(studio.parse_script("**颜色规则**：先灰后彩"), [{"t": "p", "text": "**颜色规则**：先灰后彩"}])
        self.assertEqual(studio.parse_script("**制作要求**"), [{"t": "p", "text": "**制作要求**"}])

    def test_days_since(self):
        self.assertEqual(studio.days_since("2026-10-17", date(2026, 10, 22)), 6)
        self.assertIsNone(studio.days_since(None))

    def test_safe_path_and_range(self):
        self.assertIsNone(studio.safe_path(self.root, "../a"))
        self.assertIsNone(studio.safe_path(self.root, "x/.git/config"))
        self.assertEqual(studio.safe_path(self.root, "工作台.json"), (self.root / "工作台.json").resolve())
        self.assertEqual(studio.parse_range("bytes=2-4", 10), (2, 4))
        self.assertEqual(studio.parse_range("bytes=-3", 10), (7, 9))
        self.assertEqual(studio.parse_range("bytes=20-", 10), "bad")

    def test_server_serves_api_and_ranged_files(self):
        server = studio.make_server(self.root, port=0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with urllib.request.urlopen(base + "/api/home") as r:
                self.assertEqual(json.load(r)["groups"][0]["类别"], "短剧")
            film = urllib.parse.quote("技术解说/示例片/a.mp4")
            req = urllib.request.Request(f"{base}/f/{film}", headers={"Range": "bytes=2-4"})
            with urllib.request.urlopen(req) as r:
                self.assertEqual((r.status, r.read()), (206, b"234"))
            with self.assertRaises(urllib.error.HTTPError) as e:
                urllib.request.urlopen(base + "/api/work?id=" + urllib.parse.quote("../x"))
            self.assertEqual(e.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()

    def test_flows_are_valid(self):
        for f in (ROOT / "flows").glob("*.json"):
            d = json.loads(f.read_text(encoding="utf-8"))
            self.assertIn("card", d, f.name)
            for s in d["steps"]:
                for k in ("key", "name", "icon", "fg", "how", "alts"):
                    self.assertIn(k, s, f"{f.name}:{s.get('key')}")
                for src in [h["src"] for h in s["how"] if "src" in h] + [x for a in s["alts"] for x in a["src"]]:
                    self.assertIn(src["type"], d["srcTypes"], f"{f.name}:{s['key']}")


if __name__ == "__main__":
    unittest.main()
