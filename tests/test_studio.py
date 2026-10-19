"""Offline tests for the workbench server: a synthetic AI 视频 root folder in a temp dir."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import studio  # noqa: E402


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = Path(self.tmp.name)
        write(r / "工作台.json", json.dumps({"入行日期": "2026-10-17"}))
        w = r / "技术解说/示例片"
        write(w / "作品.json", json.dumps({"类别": "代码动画", "标题": "示例", "日期": "2026-10-19",
                                         "成片": ["a.mp4", "缺失.mp4"], "章节": ["第一章", "第二章"]}, ensure_ascii=False))
        (w / "a.mp4").write_bytes(b"0")
        write(w / "film/cues_base.json", json.dumps({"duration": 10, "ev": {"ch1_tag": 1.0, "ch2_tag": 5.0}}))
        write(w / "film/cues.json", json.dumps({"duration": 12, "ev": {"ch1_tag": 1.2, "ch2_tag": 6.0},
                                                "subs": [{"t": [0.5, 1.0], "text": "你好"}], "voice": []}))
        write(r / "短剧/某剧/第1集/作品.json", json.dumps({"类别": "短剧", "标题": "某剧", "日期": "2026-10-18"}, ensure_ascii=False))
        write(r / "技术解说/示例片/node_modules/x/作品.json", "{}")          # 依赖目录不扫
        lib = r / "共用/素材库"
        write(lib / "素材清单.md", "# 清单")
        (lib / "表情/透明").mkdir(parents=True)
        (lib / "表情/透明/01_开心.png").write_bytes(b"png")
        (lib / "表情/原图").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_home_lists_works_assets_and_start_date(self):
        h = studio.home(self.root)
        self.assertEqual(h["started"], "2026-10-17")
        self.assertEqual([w["path"] for w in h["works"]], ["短剧/某剧/第1集", "技术解说/示例片"])   # 按日期排
        self.assertEqual(h["works"][1]["成片"], ["a.mp4"])                                        # 不存在的成片不列
        self.assertEqual(h["assets"][0]["groups"], [{"name": "表情", "items": ["共用/素材库/表情/透明/01_开心.png"]}])
        self.assertIn("代码动画", h["kinds"])

    def test_codework_chapters_before_and_after_narration(self):
        c = studio.codework(self.root, "技术解说/示例片")
        self.assertEqual((c["duration"], c["duration0"]), (12, 10))
        self.assertEqual(c["chapters"], [{"name": "第一章", "t": 1.2, "t0": 1.0}, {"name": "第二章", "t": 6.0, "t0": 5.0}])
        self.assertEqual(c["info"]["成片"], ["技术解说/示例片/a.mp4"])
        self.assertEqual(len(c["subs"]), 1)

    def test_codework_rejects_paths_outside_root(self):
        for bad in ("../x", "/etc", ".hidden", ""):
            with self.assertRaises(KeyError):
                studio.codework(self.root, bad)

    def test_safe_path_blocks_hidden_and_escape(self):
        self.assertIsNone(studio.safe_path(self.root, "../a"))
        self.assertIsNone(studio.safe_path(self.root, "x/.git/config"))
        self.assertEqual(studio.safe_path(self.root, "工作台.json"), (self.root / "工作台.json").resolve())

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
