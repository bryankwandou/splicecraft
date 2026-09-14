"""Planner regression tests. Run: python -m unittest discover tests"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "splicecraft" / "scripts" / "splicecraft.py"
WORDS = ROOT / "examples" / "demo" / "out" / "words.json"
sys.path.insert(0, str(SCRIPT.parent))
import splicecraft as sc  # noqa: E402


def plan(level, style="studio"):
    out = Path(tempfile.mkdtemp()) / "edl.json"
    subprocess.run([sys.executable, str(SCRIPT), "plan", str(WORDS), "-o", str(out), "--level", str(level),
                    "--style", style, "--duration", "40.8"], check=True, capture_output=True)
    return json.loads(out.read_text(encoding="utf-8"))


class PlanTests(unittest.TestCase):
    def test_showrunner_finds_every_scripted_beat(self):
        types = [c["type"] for c in plan(85)["cards"]]
        for t in ("hook", "number", "quote", "ranking", "callback", "cta"):
            self.assertIn(t, types)

    def test_numbers_merge_and_callback_recalls_them(self):
        cards = plan(85)["cards"]
        num = next(c for c in cards if c["type"] == "number")
        self.assertEqual([i["value"] for i in num["items"]], ["3", "2", "0"])
        cb = next(c for c in cards if c["type"] == "callback")
        self.assertEqual([i["value"] for i in cb["items"]], ["3", "2", "0"])

    def test_cards_never_overlap_at_any_level(self):
        for level in (1, 25, 50, 75, 100):
            cards = sorted(plan(level)["cards"], key=lambda c: c["start"])
            for a, b in zip(cards, cards[1:]):
                self.assertLessEqual(a["end"], b["start"], f"level {level}: {a['type']} overlaps {b['type']}")

    def test_breathing_room_at_least_38_percent(self):
        for level in (50, 85, 100):
            e = plan(level)
            busy = sum(c["end"] - c["start"] for c in e["cards"])
            self.assertGreaterEqual(1 - busy / e["duration"], 0.38)

    def test_density_grows_with_level(self):
        self.assertLess(len(plan(10)["cards"]), len(plan(90)["cards"]))

    def test_clean_tier_has_no_music_or_sfx(self):
        e = plan(10)
        self.assertFalse(e["params"]["music"])
        self.assertEqual(e["sfx"], [])

    def test_every_style_loads(self):
        for style in json.loads((SCRIPT.parent.parent / "presets" / "styles.json").read_text()):
            self.assertIn("accent", plan(60, style)["theme"])

    def test_keep_ranges_are_ordered(self):
        keep = plan(100)["keep"]
        for (s0, e0), (s1, _) in zip(keep, keep[1:]):
            self.assertLess(e0, s1)

    def test_ass_colors_are_bgr(self):
        self.assertEqual(sc.ass_color("#FF5A1F"), "&H001F5AFF")


if __name__ == "__main__":
    unittest.main()
