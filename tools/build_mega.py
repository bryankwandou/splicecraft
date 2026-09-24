"""Merge SKILL.md, every reference, and the preset summaries into one MEGA-SKILL.md."""
import json
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SK = ROOT / "skills" / "splicecraft"
# Strategy layer first: these decide whether the script is any good, and a
# reader who stops early should have read them rather than the codec notes.
ORDER = ["anti-ai-ish.md", "academy-personal-branding.md", "academy-script-formulas.md", "academy-live-mentoring.md",
         "viral-edit-teardown.md", "content-memory.md",
         "script-and-marketing.md", "audience-and-market.md", "captions.md", "genres-and-variants.md", "music-guide.md", "beat-library.md", "edit-levels.md",
         "color-and-cinematic.md", "audio.md", "baseline-teardown.md", "design-secrets-glass.md",
         "edl-schema.md", "agent-prompts.md", "troubleshooting.md"]


def body(p):
    t = p.read_text(encoding="utf-8")
    if t.startswith("---"):
        t = t.split("---", 2)[2]
    return t.strip().replace("\n# ", "\n## ").replace("\n## ", "\n### ") if not t.lstrip().startswith("# ") \
        else "\n".join(("#" + l if l.startswith("#") else l) for l in t.strip().splitlines())


def main():
    refs = sorted(p.name for p in (SK / "references").glob("*.md"))
    missing = [r for r in refs if r not in ORDER]
    order = ORDER + missing
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        commit = "unknown"
    skill = (SK / "SKILL.md").read_text(encoding="utf-8")
    front, rest = skill.split("---", 2)[1], skill.split("---", 2)[2]
    out = ["---" + front + "---", "",
           f"> **MEGA-SKILL.md** · SKILL.md + {len(order)} references + presets in one file.",
           f"> **Published:** {date.today()} · built from commit `{commit}` · rebuild with `python tools/build_mega.py`, never edit by hand.",
           "> **Agent check:** compare the published date with today. If more than 6 months have passed, re-research "
           "platform algorithms, lengths, safe zones, demographics and model names on the web before relying on them, "
           "tell the user what changed, and update the source files.", "",
           "## Contents", "", "- Part 1. Main procedure (SKILL.md)"]
    out += [f"- Part {i + 2}. {n}" for i, n in enumerate(order)]
    out += [f"- Part {len(order) + 2}. Presets (levels, styles, genres, music)", "",
            "When this file says `references/<name>.md`, that section is included below under the same name.", "",
            "# Part 1. Main procedure", "", rest.strip().replace("\n# ", "\n## ", 1)]
    for i, n in enumerate(order):
        out += ["", "---", "", f"# Part {i + 2}. {n}", "", body(SK / "references" / n)]
    out += ["", "---", "", f"# Part {len(order) + 2}. Presets", ""]
    for n in ("levels.json", "styles.json", "genres.json", "audience.json", "music.json", "content.json"):
        out += [f"## presets/{n}", "", "```json", (SK / "presets" / n).read_text(encoding="utf-8").strip(), "```", ""]
    text = "\n".join(out) + "\n"
    for dest in (ROOT / "MEGA-SKILL.md", ROOT / "site" / "MEGA-SKILL.md"):
        dest.write_text(text, encoding="utf-8")
    print(f"MEGA-SKILL.md: {len(text.splitlines())} lines, {len(text) // 1024} KB, {len(order)} references, commit {commit}")


if __name__ == "__main__":
    main()
