# splicecraft

> Published 2026-09-15. Platform facts were researched that day; re-check them if you read this much later.

An open skill file that lets an AI agent turn a raw talking-head clip into a finished short video.

The agent asks how hard you want the edit (1 to 100), then removes pauses, writes word-synced captions, animates info cards on the words that earn them, zooms, grades color, keys green screens, mixes a music bed under the voice with ducking, adds sound effects, normalizes loudness, and checks its own render against nine quality gates.

- Site and tutorial: https://splicecraft.vercel.app (mirror: https://bryankwandou.github.io/splicecraft/)
- The skill: [`skills/splicecraft/SKILL.md`](skills/splicecraft/SKILL.md)
- Requirements: ffmpeg (with libass) and Python 3.9+. Transcription via a Groq API key or offline faster-whisper.

## Install

Claude Code and other agents that read `SKILL.md` folders:

```bash
npx skills add bryankwandou/splicecraft
```

Any agent (Codex, Gemini CLI, Cursor, a local model):

```bash
git clone https://github.com/bryankwandou/splicecraft .splicecraft
```

Then tell it: `Read .splicecraft/skills/splicecraft/SKILL.md and follow it to edit ./take.mp4.`

No agent at all:

```bash
export GROQ_API_KEY=...            # or: pip install faster-whisper
python skills/splicecraft/scripts/splicecraft.py auto take.mp4 -d work --level 60 --style auto --genre auto --size 1080x1920
```

## One-file version

[`MEGA-SKILL.md`](MEGA-SKILL.md) is every file below merged into one document, for chat tools that accept a single upload. Rebuild it with `python tools/build_mega.py`.

## What is in the repo

```
skills/splicecraft/
  SKILL.md                    step-by-step instructions any agent can follow
  scripts/splicecraft.py      probe, transcribe, detect, brief, script, library, music, options, plan, render, qa, sheet, compare, auto
  presets/levels.json         the five tiers behind the 1-100 dial
  presets/styles.json         six looks: studio, cinema, neon, editorial, noir, glass
  presets/audience.json       brief options: platform, market, age, stage, funnel, niche
  presets/content.json        100 content structures, 200 named hooks, beat guide
  presets/music.json          18,432 license-free music templates and the genre match table
  presets/genres.json         eight auto-detected genres (hackathon demo, tutorial, launch, ...) and 360 variants
  references/
    baseline-teardown.md      second-by-second study of the first reference video and its flaws
    design-secrets-glass.md   what makes frosted-glass edits look expensive, with recipes
    beat-library.md           every beat type: trigger, look, timing, sound, what not to do
    edit-levels.md            what each level changes
    captions.md               typography rules, fonts, non-Latin scripts, SRT export
    color-and-cinematic.md    grades, LUTs, cinematic checklist, chroma key tuning, reframing
    audio.md                  voice chain, music, ducking, loudness, sound effects
    edl-schema.md             the edit list format, for hand edits
    agent-prompts.md          prompts for Claude Code, ChatGPT, Codex, Fable 5.1, Gemini CLI, Cursor, small models
    script-and-marketing.md   scripts, hooks, titles, descriptions, hashtags, 2026 platform signals with sources
    audience-and-market.md    brief.json, demographics, TAM/SAM/SOM, revenue math, safe zones
    music-guide.md            background music: templates, matching, mixing, licensed sources
    genres-and-variants.md    genre detection, auto style, variant math, proof
    troubleshooting.md        errors and fixes
examples/briefs/             three example briefs (hackathon Web3, B2B SaaS LinkedIn, Gen Z beauty Reels)
examples/demo/                license-free demo: synthetic green-screen presenter + TTS voice, and its render
site/                         the tutorial site deployed to Vercel
tests/test_plan.py            planner regression tests
docs/evidence/                screenshots and QA output from the test runs
```

## Tests

```bash
python -m unittest discover tests
```

## Honest limits

- Beat detection is rule-based. It will not draw custom illustrations.
- No face tracking. Cards assume the speaker sits in the middle third of the frame.
- Background removal without a green screen, and text placed behind the speaker, need a segmentation model that is not bundled.
- Rendering 1080x1920 with per-frame zoom is CPU heavy: roughly real time to 3x real time on a laptop.

## Credits and footage

The two reference videos studied in `references/` belong to their creators (withPT.ai and softgirlnocode). They are described for study and are not included in this repository. The demo video is generated from scratch.

MIT licensed.
