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


def fake_words(text):
    words, t = [], 0.0
    for tok in text.split():
        words.append({"w": tok, "s": round(t, 2), "e": round(t + 0.3, 2)})
        t += 0.38 if not tok.endswith((".", "?", "!")) else 0.9
    return words


def plan_words(words, **kw):
    d = Path(tempfile.mkdtemp())
    (d / "w.json").write_text(json.dumps({"words": words}), encoding="utf-8")
    sc.plan(str(d / "w.json"), str(d / "e.json"), kw.get("level", 60), kw.get("style", "studio"), None, None,
            False, kw.get("genre", "none"), kw.get("variant"))
    return json.loads((d / "e.json").read_text(encoding="utf-8"))


FIX = json.loads((ROOT / "tests" / "fixtures" / "genre_scripts.json").read_text(encoding="utf-8"))


class GenreTests(unittest.TestCase):
    def test_detects_every_genre_in_english_and_indonesian(self):
        for genre, scripts in FIX.items():
            for text in scripts:
                self.assertEqual(sc.detect_genre(fake_words(text))["genre"], genre, text[:50])

    def test_same_edit_model_for_every_style(self):
        # without a genre, the look changes but cuts, cards, zooms and sfx are identical
        base = plan(70, "studio")
        for style in ("cinema", "neon", "editorial", "noir", "glass"):
            e = plan(70, style)
            for k in ("keep", "cards", "zooms", "sfx", "words"):
                self.assertEqual(e[k], base[k], f"{style}: {k} differs")
            self.assertNotEqual(e["theme"]["accent"] + e["theme"]["card_bg"],
                                base["theme"]["accent"] + base["theme"]["card_bg"])

    def test_auto_style_follows_genre(self):
        for genre, style in (("hackathon_demo", "neon"), ("tutorial_docs", "editorial"), ("product_launch", "glass")):
            e = plan_words(fake_words(FIX[genre][0]), style="auto", genre="auto")
            self.assertEqual(e["params"]["genre"], genre)
            self.assertEqual(e["theme"]["style"], style)

    def test_genre_changes_the_edit(self):
        w = fake_words(FIX["tutorial_docs"][0] + " " + FIX["education_explainer"][0])
        docs = plan_words(w, level=70, genre="tutorial_docs")
        edu = plan_words(w, level=70, genre="education_explainer")
        self.assertLess(docs["params"]["level"], edu["params"]["level"])
        self.assertLess(docs["params"]["zoom_amount"], edu["params"]["zoom_amount"])
        self.assertFalse(any(c["type"] in ("word", "versus") for c in docs["cards"]))

    def test_variants_are_deterministic_and_distinct(self):
        w = fake_words(FIX["hackathon_demo"][0])
        a = plan_words(w, genre="hackathon_demo", variant=5)
        b = plan_words(w, genre="hackathon_demo", variant=5)
        self.assertEqual(a["theme"], b["theme"])
        looks = {json.dumps(plan_words(w, genre="hackathon_demo", variant=v)["theme"], sort_keys=True)
                 for v in range(0, 360, 7)}
        self.assertGreater(len(looks), 40)

    def test_option_count_is_in_the_thousands(self):
        self.assertGreaterEqual(sc.option_count()["variants_per_genre_and_style"], 1000 // 3)
        self.assertGreater(sc.option_count()["total_combinations"], 1_000_000)


class MusicTests(unittest.TestCase):
    def test_thousands_of_templates_and_every_genre_has_a_set(self):
        self.assertEqual(len(sc.music_templates()), 18432)
        for g in json.loads((SCRIPT.parent.parent / "presets" / "genres.json").read_text())["genres"]:
            self.assertGreaterEqual(len(sc.music_templates(g)), 100, g)

    def test_pick_respects_genre_and_pace(self):
        m = json.loads((SCRIPT.parent.parent / "presets" / "music.json").read_text())
        slow = fake_words(FIX["tutorial_docs"][0])
        pick = sc.pick_music(slow, "tutorial_docs", "editorial", 3)
        mood, key, drums, timbre, energy = pick["template"].split(".")
        g = m["genre_match"]["tutorial_docs"]
        self.assertIn(mood, g["moods"]); self.assertIn(drums, g["drums"]); self.assertIn(energy, g["energy"])

    def test_plan_stores_template(self):
        e = plan_words(fake_words(FIX["hackathon_demo"][0]), genre="auto", style="auto")
        self.assertIn(e["theme"]["music_template"], sc.music_templates("hackathon_demo"))


BRIEFS = ROOT / "examples" / "briefs"


class BriefCaptionScriptTests(unittest.TestCase):
    def test_briefs_change_the_edit(self):
        w = fake_words(FIX["hackathon_demo"][0])
        out = {}
        for b in ("hackathon-web3", "b2b-saas-linkedin", "genz-beauty-reels"):
            d = Path(tempfile.mkdtemp())
            (d / "w.json").write_text(json.dumps({"words": w}), encoding="utf-8")
            sc.plan(str(d / "w.json"), str(d / "e.json"), 60, "auto", None, None, False, "auto", None, None,
                    str(BRIEFS / f"{b}.json"))
            out[b] = json.loads((d / "e.json").read_text(encoding="utf-8"))
        self.assertLess(out["b2b-saas-linkedin"]["params"]["level"], out["genz-beauty-reels"]["params"]["level"])
        self.assertEqual(out["b2b-saas-linkedin"]["theme"]["cta_text"], "Book a demo")
        self.assertEqual(out["hackathon-web3"]["theme"]["cta_text"], "Try the live demo")
        self.assertTrue(out["hackathon-web3"]["params"]["brief"]["compliance"])
        self.assertEqual(len({e["theme"]["style"] for e in out.values()}), 3)

    def test_revenue_math_and_market_checks(self):
        r = sc.brief_report({"tam": 100, "sam": 50, "som": 10, "price": 10, "revenue_target": 1000})
        self.assertIn("FAIL", " ".join(r["checks"]))  # 100 buyers > SOM 10
        self.assertEqual(r["revenue_math"]["buyers_needed"], 100)

    def test_every_caption_mode_builds(self):
        base = json.loads((ROOT / "examples" / "demo" / "out" / "edl.json").read_text(encoding="utf-8"))
        for m in sc.CAPTION_MODES:
            e = json.loads(json.dumps(base)); e["params"]["captions"] = m
            p = Path(tempfile.mkdtemp()) / "c.ass"
            sc.build_ass(e, 1080, 1920, str(p), "Arial", "Arial")
            self.assertIn("Dialogue:", p.read_text(encoding="utf-8"), m)

    def test_no_tier_defaults_to_plain_captions(self):
        tiers = json.loads((SCRIPT.parent.parent / "presets" / "levels.json").read_text())["tiers"]
        self.assertNotIn("plain", [t["params"]["captions"] for t in tiers])

    def test_cta_not_in_platform_ui_zone(self):
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("y = 1620", src)

    def test_library_sizes_and_script(self):
        c = json.loads((SCRIPT.parent.parent / "presets" / "content.json").read_text(encoding="utf-8"))
        self.assertEqual(len(c["frameworks"]), 100)
        self.assertEqual(len(c["hooks"]), 200)
        out = Path(tempfile.mkdtemp()) / "s.md"
        sc.script("refund bonds", "hackathon_demo", 60, None, None, "judges", "en", str(out),
                  str(BRIEFS / "hackathon-web3.json"))
        t = out.read_text(encoding="utf-8")
        for k in ("Hook options", "market_size", "Revenue math", "Compliance", "Title options"):
            self.assertIn(k, t)

    def test_voice_pitch_is_locked_by_default(self):
        self.assertEqual(sc.voice_pitch_filter({"params": {}}), "")
        with self.assertRaises(SystemExit):
            sc.voice_pitch_filter({"params": {"voice": {"pitch_semitones": 3}}})
        with self.assertRaises(SystemExit):
            sc.voice_pitch_filter({"params": {"voice": {"pitch_semitones": 4, "reason": "fix_wrong_sample_rate"}}})
        f = sc.voice_pitch_filter({"params": {"voice": {"pitch_semitones": -1.47, "reason": "fix_wrong_sample_rate"}}})
        self.assertIn("atempo", f)

    def test_every_doc_is_dated(self):
        for p in [SCRIPT.parent.parent / "SKILL.md", *(SCRIPT.parent.parent / "references").glob("*.md")]:
            self.assertIn("**Published:**", p.read_text(encoding="utf-8"), p.name)


if __name__ == "__main__":
    unittest.main()
