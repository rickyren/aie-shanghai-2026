"""Regression checks for evidence validation and safe, reproducible site builds."""
import copy
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import build_site
from analysis_validation import validate
from check_site import check_site
from landscape import load_landscape, talk_positions
from review_clean import parse_md
from stage3_prepare import main as prepare_transcript
from stage4_prepare import main as prepare_analysis
from validate_data import validate_inputs


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / "data/04_analysis_v3/d1m05.json").read_text())
        self.schema = json.loads((ROOT / "pipeline/schemas/talk_analysis_v3.json").read_text())
        _, blocks = parse_md((ROOT / "data/03_clean/d1m05.md").read_text())
        self.paras = [b for b in blocks if b[0] == "p" and b[2]]

    def test_rejects_missing_fields_types_and_scores(self):
        for field, value in (("novelty", 999), ("novelty", True), ("pr_level", 0),
                             ("skeleton", "not a list"), ("core_message", "  "),
                             ("intent", "unknown"), ("signals", [{}]),
                             ("frameworks", self.doc["frameworks"] * 3)):
            with self.subTest(field=field, value=value):
                doc = copy.deepcopy(self.doc)
                doc[field] = value
                self.assertTrue(validate(doc, self.schema, self.paras))
        del self.doc["core_message"]
        self.assertTrue(validate(self.doc, self.schema, self.paras))

    def test_rejects_empty_quote_wrong_paragraph_and_reversed_range(self):
        for quote, span in (("", "974–980"), (self.doc["non_consensus"][0]["quote"], "875–883"),
                            (self.doc["non_consensus"][0]["quote"], "980–974")):
            with self.subTest(quote=quote, span=span):
                doc = copy.deepcopy(self.doc)
                doc["non_consensus"][0].update(quote=quote, seg=span)
                self.assertTrue(validate(doc, self.schema, self.paras))

    def test_rejects_range_in_gap_between_paragraphs(self):
        doc = copy.deepcopy(self.doc)
        doc["non_consensus"] = []
        doc["signals"] = [{"type": "launch", "signal": "example", "value_as_heard": "", "seg": "20–21"}]
        doc["frameworks"] = []
        self.assertTrue(validate(doc, self.schema, [("p", "one", (1, 10)), ("p", "two", (30, 40))]))

    def test_fixed_d2m01_quote_points_to_the_right_paragraph(self):
        doc = json.loads((ROOT / "data/04_analysis_v3/d2m01.json").read_text())
        _, blocks = parse_md((ROOT / "data/03_clean/d2m01.md").read_text())
        paras = [b for b in blocks if b[0] == "p" and b[2]]
        self.assertEqual([], validate(doc, self.schema, paras))
        doc["non_consensus"][1]["seg"] = "271–280"
        self.assertTrue(validate(doc, self.schema, paras))

    def test_shared_segment_range_attached_or_on_separate_line(self):
        for body in ("first\n\nsecond [seg 1–3]", "first\n\nsecond\n\n[seg 1–3]"):
            with self.subTest(body=body):
                _, blocks = parse_md(body)
                self.assertEqual([("p", "first", (1, 3)), ("p", "second", (1, 3))], blocks)
                html = build_site.render_transcript(body, [1, 2, 3])
                self.assertEqual(1, html.count('id="seg-1"'))
                self.assertIn("second", html)

    def test_schema_labels_and_codes_match(self):
        for name, labels in self.schema["enums"].items():
            self.assertEqual(set(labels), set(self.schema["$defs"][name]["enum"]))

    def test_repository_inputs_are_valid(self):
        self.assertEqual([], validate_inputs(ROOT))


def snapshot(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob("*") if p.is_file()}


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aie-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        for directory in ("data", "pipeline"):
            shutil.copytree(ROOT / directory, self.root / directory,
                            ignore=shutil.ignore_patterns("_input", "__pycache__"))
        self.output = self.root / "docs"

    def build(self):
        with redirect_stdout(io.StringIO()):
            build_site.main(self.root, self.output)

    def test_build_has_working_evidence_links_and_is_reproducible(self):
        self.build()
        self.assertEqual([], check_site(self.output))
        self.assertEqual(55, len(list(self.output.rglob("*.html"))))
        index = (self.output / "index.html").read_text()
        self.assertIn("AIE Shanghai 2026 参会笔记", index)
        for old_text in ("从 53 场分享看 AI 行业", "全部分享与打标", "核心 message", "演讲骨架"):
            self.assertNotIn(old_text, "".join(p.read_text() for p in self.output.rglob("*.html")))
        page = (self.output / "talks/d2m01.html").read_text()
        self.assertIn('href="#seg-281"', page)
        self.assertIn('id="seg-281"', page)
        before = snapshot(self.output)
        self.build()
        self.assertEqual(before, snapshot(self.output))

    def test_failed_preflight_and_broken_link_preserve_existing_output(self):
        self.output.mkdir()
        (self.output / "index.html").write_text("old site")
        before = snapshot(self.output)
        path = self.root / "data/04_analysis_v3/d1m05.json"
        original = path.read_text()
        path.unlink()
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(before, snapshot(self.output))
        path.write_text(original)
        with patch.object(build_site, "build_report", return_value='<a href="talks/d1m05.html#missing">bad</a>'):
            with self.assertRaises(ValueError):
                self.build()
        self.assertEqual(before, snapshot(self.output))

    def test_failed_directory_swap_restores_existing_output(self):
        self.output.mkdir()
        (self.output / "index.html").write_text("old site")
        before = snapshot(self.output)
        rename = Path.rename

        def fail_new_site(path, target):
            if path.name == "site":
                raise OSError("simulated rename failure")
            return rename(path, target)

        with patch.object(Path, "rename", fail_new_site):
            with self.assertRaises(OSError):
                self.build()
        self.assertEqual(before, snapshot(self.output))

    def test_removes_stale_talk_pages_and_keeps_unrelated_assets(self):
        (self.output / "talks").mkdir(parents=True)
        (self.output / "talks/stale.html").write_text("old talk")
        (self.output / "custom.css").write_text("body{}")
        self.build()
        self.assertFalse((self.output / "talks/stale.html").exists())
        self.assertEqual("body{}", (self.output / "custom.css").read_text())

    def test_duplicate_labels_and_unknown_sessions_fail(self):
        path = self.root / "data/01_segment_labels.jsonl"
        original = path.read_text()
        path.write_text(original + original.splitlines()[0] + "\n")
        self.assertTrue(any("重复 label" in issue for issue in validate_inputs(self.root)))
        rows = original.splitlines()
        index = next(i for i, line in enumerate(rows) if json.loads(line)["type"] == "talk")
        row = json.loads(rows[index])
        row["session_id"] = "unknown"
        rows[index] = json.dumps(row)
        path.write_text("\n".join(rows) + "\n")
        self.assertTrue(any("场次不存在" in issue for issue in validate_inputs(self.root)))

    def test_stage4_prepares_v3_inputs(self):
        with redirect_stdout(io.StringIO()):
            prepare_transcript(self.root, ["d1m05"])
            prepare_analysis(self.root, ["d1m05"])
        prompt = (self.root / "data/04_analysis_v3/_input/d1m05.prompt.md").read_text()
        self.assertIn("data/04_analysis_v3/d1m05.json", prompt)
        self.assertIn("schemas/talk_analysis_v3.json", prompt)
        self.assertNotIn("{file_id}", prompt)
        self.assertNotIn("<project_root>", prompt)
        self.assertFalse((self.root / "data/04_analysis").exists())

    def test_validation_cli_returns_nonzero(self):
        path = self.root / "data/04_analysis_v3/d1m05.json"
        doc = json.loads(path.read_text())
        doc["novelty"] = 999
        path.write_text(json.dumps(doc))
        result = subprocess.run([sys.executable, str(ROOT / "pipeline/validate_data.py"), str(self.root),
                                 "--talk", "d1m05"], capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("novelty", result.stdout)
        for value in (None, "wrong type", {}):
            with self.subTest(non_consensus=value):
                doc["novelty"] = 3
                doc["non_consensus"] = value
                path.write_text(json.dumps(doc))
                self.assertTrue(validate_inputs(self.root, "d1m05"))

    def test_source_directories_cannot_be_build_targets(self):
        for output in (self.root, self.root.parent, self.root / "data/site", self.root / "pipeline"):
            with self.subTest(output=output), self.assertRaises(ValueError):
                build_site.main(self.root, output)


class SiteAndMapTests(unittest.TestCase):
    def test_link_checker_catches_missing_file_fragment_and_duplicate_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "index.html").write_text('<a href="missing.html">x</a><a href="#no">y</a><p id="a"></p><p id="a"></p>')
            self.assertEqual(3, len(check_site(path)))

    def test_map_categories_match_approved_figure(self):
        data = load_landscape(ROOT)
        self.assertEqual(53, len(talk_positions(data)))
        figure = ET.parse(ROOT / "data/05_synthesis/landscape.svg")
        groups = [group for layer in data["layers"] if layer.get("show_in_figure", True)
                  for row in layer["rows"] for group in row]
        self.assertEqual([group["name"] for group in groups],
                         [node.text for node in figure.findall('.//*[@class="ls-gt"]')])
        expected = [(e["name"], e.get("description", ""), bool(e.get("exhibitor")))
                    for group in groups for e in group["entities"]]
        actual = [(node.text, "".join(child.text for child in node), node.get("class") == "ls-xn")
                  for node in figure.iter() if node.get("class") in {"ls-n", "ls-xn"}]
        self.assertEqual(expected, actual)
        group = data["layers"][0]["rows"][0][0]
        group["name"] = "changed category"
        self.assertEqual("changed category", talk_positions(data)["d1m13"][1])
        group["entities"].append(copy.deepcopy(group["entities"][0]))
        with self.assertRaises(ValueError):
            talk_positions(data)


if __name__ == "__main__":
    unittest.main()
