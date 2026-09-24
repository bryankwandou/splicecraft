---
name: splicecraft
description: Edit a raw talking-head or face-to-camera video into a finished short with word-synced captions, animated info cards, punch-in zooms, a color grade, chroma key, music with ducking, and sound effects — and write the script and personal-branding strategy behind it. Use when the user gives a video file and asks to "edit this video", "add subtitles/captions", "make it look professional", "add music", "make it cinematic", "remove the green screen", "turn this into a reel/short/TikTok", or wants an edit at a chosen intensity from 1 to 100. Also use when the user asks for a content script, a hook, a content plan, a niche, or personal branding strategy, or complains that a script or edit "feels AI" / "masih AI-ish". Keeps a local ledger of everything already made so it never repeats a theme. Runs locally with ffmpeg and Python; no paid editor needed.
license: MIT
---

> **MEGA-SKILL.md** · SKILL.md + 20 references + presets in one file.
> **Published:** 2026-09-24 · built from commit `ad2b9f3` · rebuild with `python tools/build_mega.py`, never edit by hand.
> **Agent check:** compare the published date with today. If more than 6 months have passed, re-research platform algorithms, lengths, safe zones, demographics and model names on the web before relying on them, tell the user what changed, and update the source files.

## Contents

- Part 1. Main procedure (SKILL.md)
- Part 2. anti-ai-ish.md
- Part 3. kadev-personal-branding.md
- Part 4. kadev-script-formulas.md
- Part 5. kadev-live-mentoring.md
- Part 6. viral-edit-teardown.md
- Part 7. content-memory.md
- Part 8. script-and-marketing.md
- Part 9. audience-and-market.md
- Part 10. captions.md
- Part 11. genres-and-variants.md
- Part 12. music-guide.md
- Part 13. beat-library.md
- Part 14. edit-levels.md
- Part 15. color-and-cinematic.md
- Part 16. audio.md
- Part 17. baseline-teardown.md
- Part 18. design-secrets-glass.md
- Part 19. edl-schema.md
- Part 20. agent-prompts.md
- Part 21. troubleshooting.md
- Part 22. Presets (levels, styles, genres, music)

When this file says `references/<name>.md`, that section is included below under the same name.

# Part 1. Main procedure

# splicecraft

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-23
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this skill.
> **Journal:** every design decision, measurement and known gap is recorded in `../../JOURNAL.md`. Read it before changing anything here.


You are the editor. The user hands you a raw clip. You hand back a finished MP4 plus proof that it passed quality checks.

This file is written so that any agent can follow it, including small or cheap models. Follow the steps in order. Do not skip a step. Do not invent flags that are not listed here. When a step says STOP, stop and talk to the user.

Everything heavy is done by one script: `scripts/splicecraft.py`. Your job is to (1) ask the right questions, (2) run the script with the right flags, (3) look at the result, (4) fix what the checks flag, (5) report.

---

## Step 0. Check the machine (do this once)

Run each command. Each must print a version, not an error.

```bash
ffmpeg -version
ffprobe -version
python --version
```

Rules:

- If `ffmpeg` is missing: tell the user to install it. Windows: `winget install Gyan.FFmpeg`. macOS: `brew install ffmpeg`. Debian/Ubuntu: `sudo apt install ffmpeg`. Then STOP until they confirm.
- Python must be 3.9 or newer. The script uses the standard library only.
- Check libass is present: `ffmpeg -hide_banner -filters | grep subtitles` (Windows PowerShell: `ffmpeg -hide_banner -filters | Select-String subtitles`). If nothing prints, the ffmpeg build cannot burn captions. Ask the user to install a full build.

Transcription needs one of these:

- `GROQ_API_KEY` in the environment (fast, free tier exists), or
- `pip install faster-whisper` (offline, slower, downloads a model the first time).

If neither is available, STOP and ask the user which one they want.

Set a variable for the script path so later commands are short. The skill folder is wherever this SKILL.md lives.

```bash
SC="python <skill-folder>/scripts/splicecraft.py"
LEDGER="python <skill-folder>/scripts/ledger.py"
```

Create the content ledger once per machine. It is the memory of everything this user has already made:

```bash
$LEDGER init
```

---

## Step 0.5. Strategy and script (when the video is not filmed yet, or the user wants strategy)

This step is where "AI-ish" is won or lost. A flat script cannot be rescued by editing.

**0.5a — Check the ledger first. Always.**

```bash
$LEDGER check "<the topic the user proposed>" --theme <tag> --theme <tag>
```

| Result | What you do |
|---|---|
| exit 0, under 45% | write it |
| exit 0, 45-61% | allowed, but **say out loud what is new about this one**. If you cannot name it, treat it as a repeat. |
| **exit 2**, 62%+ | **do not write it.** Change the angle, the pillar, or the audience segment, and check again. |

Two rules the table does not show, both learned from cold-agent tests on 2026-09-23:

- **Always pass `--theme` on `check`**, using the same tags you would log. Two agents phrasing the same subject differently must still collide; tags are what make that happen.
- **A blocked idea is still logged:** `$LEDGER add "<topic>" --status idea --theme ...`. A rejected idea is worth remembering, so it is not proposed again next week.

Run `$LEDGER stats` and `$LEDGER suggest` at the start of any strategy conversation. They tell you which pillar is overdue, which hook templates are burnt out, and whether the 80/15/5 ratio is holding. Full guide: `references/content-memory.md`.

**0.5b — Settle the foundation before writing a word.** Most AI-ish scripts are AI-ish because these were skipped:

| Must exist | Where it comes from |
|---|---|
| **Premis** — one paragraph turning a weakness into a message | `references/kadev-personal-branding.md` §2.4 |
| **Superniche** — named as a *who*, not a topic | §6.2. *"Niche bukan topik, tapi siapa secara spesifik."* |
| **4K** — Keresahan / Kebutuhan / Keinginan / Kebiasaan of that person | §6.6 |
| **Pillar** — Educate / Inspiration / Entertaining / Promotion | §8.2 |

| **Source of the idea** — a question someone asked, a repeated complaint, a misconception, something the user saw | `references/kadev-live-mentoring.md` §2.3. An idea with no source is an invented idea. |
| **Format** — one of the 15 named formats; if there is no winner yet, test several | `kadev-live-mentoring.md` §1, §5.3 |
| **Funnel stage** — TOFU (tahu) / MOFU (mau) / BOFU (beli) | §5.1. A small account starts at TOFU. |

If the user cannot answer these, walk them through the frameworks. Do not guess on their behalf.

**0.5c — Brief.** Write `brief.json` with the user: platform, market, age, stage, funnel, niche, and if relevant TAM/SAM/SOM, price, revenue target. Field list and effects: `references/audience-and-market.md`. Run `$SC brief brief.json` and show the checks and revenue math. Never present the placeholder conversion rates as facts.

**0.5d — Write.** Generate the skeleton: `$SC script "<topic>" --genre <genre> --seconds <n> --brief brief.json --language <en|id> -o script.md`. Then fill it using:

- **Hook** — one of the 20 templates, brackets filled from the real 4K answers: `references/kadev-script-formulas.md` §4
- **Elements** — all 6 Script Hack Elements present: §2
- **Beats** — 5-beat Storytelling Hack, where beat ⑤ reverses beat ①: §3
- **Length** — pick 20-30 s *or* 60-90 s deliberately, not 50 s by accident: §8
- **Selling?** Use Problem → Agitation → Solution with **one** benefit per video; agitation may not be skipped: `references/kadev-live-mentoring.md` §2
- **Opinion or education?** Write the thesis in one sentence and its 3-4 sourced arguments before any hook: `kadev-live-mentoring.md` §4.3

Fill the "Your line" column *with* the user. Use only facts the user confirms.

**0.5e — Gate.** Run the full checklist in `references/anti-ai-ish.md` §E before handing anything over.

**0.5f — Log it.**

```bash
$LEDGER add "<topic>" --niche "<superniche>" --pillar <pillar> \
  --hook-template <1-20> --angle "<what made THIS one different>" \
  --format <format> --funnel <tofu|mofu|bofu> --source "<where the idea came from>" \n  --theme <tag> --theme <tag> --status scripted --script-path script.md
```

Then the video gets filmed and you continue at Step 1 with `--brief brief.json` on every plan.

If the footage already exists, skip to Step 1 but still run 0.5a and ask for the brief fields in question 1c.

## Hard rules (apply to every step)

1. **Never change voice pitch.** No chipmunk, no robot. Only `references/audio.md` 'Voice pitch and speed' can allow it, and only for its listed reasons.
2. **Never invent facts** in scripts, cards, titles or descriptions. Numbers must come from the user or a cited source.
3. **Never invent a personal story.** The 6 Script Hack Elements require a Personal Opinion / Story, and it is the one element you cannot supply — it requires having lived something. If the user cannot give you a real story, a real number or a real opinion, **stop and ask**. A plausible invented anecdote is the worst failure this skill can produce: it is both AI-ish and dishonest. See `references/anti-ai-ish.md` §A.
4. **Never use music, fonts, or footage the user has no rights to.**
5. **Always check the ledger before writing and log after producing.** An agent that skips the log breaks the tool for every future session.
6. **Name production faults honestly.** Bad light, bad audio, wrong aspect ratio — say so and recommend a reshoot. Hiding them under heavy grading and zooms is itself an AI-ish move.
7. **Check dates.** If this skill's Published date is more than 6 months old, research platform facts again before advising on strategy.

## Step 1. Ask before you cut (intake)

Never start editing without answers to these. Ask them in one message, numbered, with the default in brackets so the user can reply "defaults".

1. **Edit level, 1 to 100** [60]. Show this table:

   | Level | Tier | What they get |
   |---|---|---|
   | 1-20 | Clean | Plain captions, pauses trimmed lightly, gentle grade. No music, no cards. |
   | 21-40 | Social | Bold 4-word captions, hook title, music bed, a few zooms, ranking cards. |
   | 41-60 | Creator | Word-highlight captions, number and quote cards, sound effects, callbacks. |
   | 61-80 | Pro | Pop-in captions, dense cards, progress bar, film grain on cinematic looks. |
   | 81-100 | Showrunner | Kinetic keyword captions, flash hits, tightest pause removal, maximum motion. |

1b. **What kind of video is it?** [auto]. Before asking, run `$SC detect work/words.json` (needs Step 3 first, so for this question alone you may transcribe early) and show the top genre with its keyword hits. Genres: hackathon_demo, tutorial_docs, product_launch, education_explainer, story_vlog, sales_pitch, podcast_talk, ai_comparison. The genre shifts the level, density, zoom, dropped beats, CTA and music. See `references/genres-and-variants.md`.
1c. **Who is it for?** [none]. Platform, market (b2c, b2b, investor, hackathon...), audience age, business stage, funnel goal, niche. Write them into `brief.json` and pass `--brief brief.json`. The brief changes level, caption style, look, grade, CTA, music, and adds compliance warnings.
2. **Look** [auto = chosen by genre, varied per video]. One of: `studio` (bright, orange accent), `cinema` (dark, gold, teal-orange grade), `neon` (black and lime, all caps), `editorial` (paper and blue, warm grade), `noir` (black and white, red accent), `glass` (frosted see-through cards over a blurred copy of the video, green accent, warm grade; best when the background has depth like a room or window, weak on a plain wall).
3. **Platform and shape** [9:16 vertical]. 9:16 for TikTok, Reels, Shorts. 16:9 for YouTube. 1:1 for feeds.
4. **Music** [auto template]. Options: auto (one of 18,432 license-free synthesized templates matched to genre and speaking pace; show the pick from `$SC music pick work/words.json` and offer `$SC music render <id> --seconds 20` as a preview), a template id they choose, their own file (they must own the rights), or none. See `references/music-guide.md`.
5. **Green or blue screen?** [no]. If yes, ask for a background image or video, or use the animated gradient.
6. **Brand colors or font?** [use the look]. If yes, collect hex codes and a font name.
7. **Language of speech** [auto-detect].
8. **Call to action text** for the end [Follow for part two].

If the user says "just do it", use every default and say so in your report.

Map the answers to flags:

| Answer | Flag |
|---|---|
| level N | `--level N` |
| look | `--style studio` (or cinema, neon, editorial, noir, glass, auto) |
| genre | `--genre auto` (or a genre name, or none) |
| audience / market | `--brief brief.json` |
| caption style | `--captions boxed` (clean_accent, chunk, highlight, pop, kinetic, sweep, boxed, bounce, stack, plain) |
| a different look, same genre | `--variant N` (0-359) |
| 9:16 | `--size 1080x1920` |
| 16:9 | `--size 1920x1080` |
| 1:1 | `--size 1080x1080` |
| own music | `--music path/to/song.mp3` |
| a specific template | set `theme.music_template` in `edl.json` to the id, then render |
| no music | pick level 1-20, or edit `edl.json` and set `params.music` to false |
| green screen | `--key green --bg path/to/background.jpg` |
| blue screen | `--key blue --bg ...` |
| brand colors | write `brand.json` (see below) and pass `--brand brand.json` |
| language | `--language en` (ISO code) |
| CTA text | put `"cta_text": "..."` in `brand.json` |

`brand.json` example. Every key is optional. Colors are `#RRGGBB`.

```json
{
  "accent": "#7C3AED",
  "on_accent": "#FFFFFF",
  "card_bg": "#FFFFFF",
  "card_text": "#111111",
  "muted": "#6B7280",
  "caption_text": "#FFFFFF",
  "caption_stroke": "#000000",
  "caption_size": 76,
  "caption_upper": false,
  "grade": "punchy",
  "cta_text": "Follow for part two"
}
```

---

## Step 2. Inspect the source

```bash
$SC probe input.mp4
```

Read the JSON. Write down: width, height, fps, duration, has_audio, orientation.

Decision rules:

- `has_audio` is false: captions and cards are impossible without speech. STOP and tell the user.
- duration over 15 minutes: warn that Groq accepts up to about 24 MB of audio. Offer `--engine local` or splitting.
- orientation is horizontal but the user wants 9:16: the script center-crops. Warn that a speaker who is not centered will be cut off. If the face is off center, ask the user or crop first with `ffmpeg -vf crop=...`.
- fps above 60: pass `--fps 60`. For faster test renders pass `--fps 30`.

---

## Step 3. Transcribe

```bash
$SC transcribe input.mp4 -o work/words.json
```

Optional: `--language id` to force Indonesian, `--engine local` to stay offline, `--key-file path` if the key is in a file. Key files saved on Windows often start with an invisible BOM; the script strips it.

Open `work/words.json` and read the `segments`. Check:

- Names and brand words are spelled right. If not, fix them in both `words[].w` and `segments[].text`. Do not change timestamps.
- Filler like "um", "uh" can stay; captions at level 61+ hide nothing, so remove fillers from `words` if the user wants a tight cut.

---

## Step 4. Plan the edit

**First, choose the cutting mode and commit to it.** This is the clearest finding from measuring 82 well-performing reference videos (`references/viral-edit-teardown.md`):

> Real edits are bimodal. AI-ish edits are uniform.

| Mode | Average shot length | Use when |
|---|---|---|
| **Cut-driven** | 0.5 - 2.5 s | voiceover over b-roll, a numbered list, a tutorial, documentation |
| **Single-take** | 8 s to *no cuts at all* | talking head, one location, a personal story |

28% of the reference videos sit in single-take mode and six of them have **zero** scene cuts across 18-46 seconds. They work. The failure mode is landing in the middle by default — a cut every 3-4 seconds regardless of what is being said — because that is the rhythm nobody chooses on purpose.

Pick one. Do not average them. For single-take mode, keep the level low enough that pause removal is the only cutting that happens.

**Then shape the opening and closing.** Also measured, and both are counterintuitive enough that the usual advice gets them backwards:

| Position | What the reference set does |
|---|---|
| **Opening shot** | **held**, ~1.58× a typical shot (median 2.22 s). The first 3 s cut at **0.75×** the video's own rate — *slower*, not faster. The hook is held, not chopped. |
| Middle | stays in the chosen mode (typical shot 1.32 s in cut-driven) |
| **Closing shot** | **held**, ~2.42× a typical shot (median 3.16 s), in **75%** of cut-driven videos. The last 3 s cut at **0.21×** — cutting essentially stops. |

> **Hold the open · chop the middle · hold the close.**

**These ratios are for cut-driven mode.** In single-take mode there is no shot to "hold" — the whole video is one held shot. Do not add cuts to a talking head to create an opening or closing shape; the only cuts are removed sentences and long pauses. What still applies in single-take: the hook is spoken *and* on screen from frame one, and the last ~3 s after the closing line are kept, not trimmed.

The held final shot is where the closing line lands — the one that reverses the opening (`references/kadev-script-formulas.md` §3). Do not trim it off as dead air; it is the beat that makes the video loop. Full numbers, method and limits: `references/viral-edit-teardown.md`.

```bash
$SC plan work/words.json -o work/edl.json --level 60 --style auto --genre auto --brief brief.json --duration <duration from probe>
```

The planner prints one line, for example:

```
level 85 (Showrunner): 10 cards, 18 zooms, 12 sfx, cut 6.5s of pauses -> 101.1s
```

What the planner decides, so you can explain it:

- **Cuts.** Pauses between words longer than a level-based gap are removed (0.9 s at level 1, 0.3 s at level 100). A small pad is kept so words are not clipped.
- **Beats.** Each sentence is classified. The full rules are in `references/beat-library.md`. Short version:
  - first sentence -> hook title
  - digits or number words -> number card with count-up; numbers in the next sentence join the same card
  - "first / second / third" -> ranking bars that grow one row at a time
  - "they say", "quote" -> quote card with typewriter reveal
  - "before and after", "vs", "compare" -> head-to-head card
  - a question under ten words -> question pill
  - a one to three word sentence -> giant word with punch zoom
  - "back to the number", "remember" -> callback card that brings earlier numbers back
  - "follow", "subscribe" near the end -> call-to-action pill
  - everything else -> nothing. Captions carry it. This is on purpose.
- **Breathing room.** There is a minimum gap between cards and a cards-per-minute ceiling, both set by the level. A video where every sentence has a graphic is worse, not better.

Open `work/edl.json` and read `cards`. Then check each card against the transcript:

- Does the card say something the speaker actually said? If not, delete it.
- Is a label a stop word (like "the")? Change it.
- Did an important moment get no card? Add one by copying an existing card object and changing `start`, `end`, and text. Schema: `references/edl-schema.md`.
- Keep `start` inside the sentence where the trigger word is spoken. Graphics that arrive late feel broken.

---

## Step 5. Render

```bash
$SC render input.mp4 work/edl.json -o work/edited.mp4 --size 1080x1920
```

Add the flags from Step 1: `--music`, `--key`, `--bg`, `--lut`, `--grade`, `--font-bold`, `--font-body`, `--fontsdir`.

Speed tips:

- First pass: `--fps 30 --preset veryfast`. Check it. Final pass: remove those flags.
- A 100 second 1080x1920 clip takes several minutes on a laptop. That is normal. Do not kill it early.
- If a render fails, the script keeps `graph.txt` in a temp folder and prints the path. Read the last lines of the error. The usual causes are in `references/troubleshooting.md`.

Or run everything in one command:

```bash
$SC auto input.mp4 -d work --level 60 --style studio --size 1080x1920
```

---

## Step 6. Check your work (mandatory)

```bash
$SC qa work/edited.mp4 --edl work/edl.json -o work/qa.json
$SC sheet work/edited.mp4 -o work/sheet.jpg
$SC compare input.mp4 work/edited.mp4 -o work/compare.mp4
```

`qa` exits with code 0 only if every gate passes:

| Gate | Pass condition |
|---|---|
| loudness | integrated loudness between -16.5 and -12.5 LUFS |
| true_peak | peak at or below -0.5 dBFS |
| no_black_gaps | no black stretch longer than 0.3 s |
| resolution | shortest side at least 720 px |
| duration_match | render length within 0.35 s of the plan |
| card_density | cards per minute at or below the level ceiling + 1 |
| no_card_overlap | no two cards on screen at the same time |
| breathing_room | at least 35% of runtime has no card |
| captions_present | the transcript produced captioned words |

If you can view images, open `sheet.jpg` and check by eye:

1. Captions never cover the mouth or eyes.
2. Cards sit in the top third and never cover the face.
3. Text is readable at phone size. If you have to squint at the sheet, it is too small.
4. No caption line runs off the edge.
5. Colors look natural on skin. Orange or green faces mean the grade is too strong: lower the level or pass `--grade clean`.

If any gate fails, fix and render again. Maximum three rounds. Fix table:

| Failure | Fix |
|---|---|
| loudness too low or high | your music file is very loud or quiet: change `--music-db` (default -20) |
| true_peak | lower `--music-db` by 3 |
| black gaps | the source has black frames; trim them first |
| duration_match | the source has variable frame rate: re-encode first with `ffmpeg -i in.mp4 -vf fps=30 -c:a copy fixed.mp4` |
| card_density or overlap | delete cards in `edl.json` or lower the level |
| breathing_room | delete the weakest cards |
| captions cover the face | raise `caption_y` in `brand.json` (bigger number = lower on screen, 1920 grid) |

---

## Step 7. Report

Send the user:

1. Path to `edited.mp4`.
2. The planner line (cards, zooms, cuts, final length).
3. The QA table with PASS or FAIL per gate.
4. The contact sheet image.
5. Any default you picked for them.
6. Anything you could not do and why.

Do not say "perfect" or "professional quality". Say what passed and what you checked.

**Then run the anti-AI-ish gate and log the result.** Both are mandatory and neither is optional bookkeeping.

Walk the checklist in `references/anti-ai-ish.md` §E. Report any ❌ plainly rather than quietly fixing or ignoring it — a production fault named honestly is worth more than a silently over-graded video.

```bash
$LEDGER add "<topic>" --niche "<superniche>" --pillar <pillar> \
  --hook-template <1-20> --angle "<what made THIS one different>" \
  --theme <tag> --theme <tag> \
  --platform <tiktok|reels|shorts> --format <talking_head|voiceover|...> \
  --seconds <final length> \
  --script-path work/script.md --video-path work/edited.mp4 \
  --status produced
```

If an entry already exists at `--status scripted` from Step 0.5f, update it instead of adding a second one:

```bash
$LEDGER edit <id> --set status=produced --set video_path=work/edited.mp4
```

An agent that skips the log breaks the tool for every future session. The ledger is the only memory that survives the end of this conversation.

---

## Rules that apply to every edit

1. Never cover the speaker's eyes or mouth with anything.
2. A graphic must appear within 0.15 s of the word that triggers it. Late graphics read as mistakes.
3. One idea on screen at a time. Two cards at once is a bug.
4. Leave sentences without graphics. At least 38% of the video should be just the person and captions; the planner drops the weakest cards (word, then question, versus, quote) until that holds.
5. Captions are for reading with the sound off. Every spoken word gets a caption, spelled right.
6. Music sits under the voice. If you can hear the music over a word, it is too loud.
7. Only use music the user owns or the generated bed. Never download songs.
8. Keep the original take. Write outputs to a new folder. Never overwrite the source.
9. No emoji in captions or cards unless the user asks.
10. Report failures honestly.

---

## Going further

**Strategy, script, and the anti-AI-ish gate** (the Kadev Academy body of work, Indonesian market):

- The full personal branding theory — Ikigai, Johari, SWOT → **Premis** → Personal Market Fit, Perception vs Persona, Circle of Control, Golden Circle, Opportunity Mapping, the **superniche ladder**, **80/15/5**, Perfect Niche, the **4K Method**, Sweet Spot, First Impression, the four **Brand Pillars**, Hirarki Konten, self-documentation, survival, evaluation, monetisation, PING, LinkedIn: `references/kadev-personal-branding.md`
- Writing the script — the **20 hooks**, the **6 Script Hack Elements**, the **5-beat Storytelling Hack**, Hook/Body/CTA, the Content Idea Framework, length budgets: `references/kadev-script-formulas.md`
- **The rejection list and the delivery gate** — what "AI-ish" actually means, rule by rule, with the evidence behind each: `references/anti-ai-ish.md`
- What 82 reference videos measurably do — cut rates, the bimodal finding, opening and closing shape, method and limits: `references/viral-edit-teardown.md`
- What the live mentoring recordings add — the **16 formats**, **PAS** selling scripts, the **Storytelling Arc**, attention economy and the six emotions, thesis + arguments, outer/inner circle, **TOFU/MOFU/BOFU**, test → win → replicate, **Trial Reels** and **Link Reels**, and a table of real account diagnoses: `references/kadev-live-mentoring.md`
- The content ledger — how the local memory works, what it stores, how the similarity check scores: `references/content-memory.md`
- Why every decision here is what it is, what was measured versus guessed, and what is still open: `../../JOURNAL.md`

**Craft and technique:**

- Cinematic looks, LUTs, relighting a flat shot, letterboxing, and chroma key tuning: `references/color-and-cinematic.md`
- Caption styles and the typography rules behind them: `references/captions.md`
- Music, ducking, loudness, sound effects: `references/audio.md`
- Every beat type with trigger words, timing, and what not to do: `references/beat-library.md`
- What each level changes, number by number: `references/edit-levels.md`
- Hand-editing the plan: `references/edl-schema.md`
- Copy-paste prompts for Claude Code, Codex, Gemini CLI, Cursor, and small models: `references/agent-prompts.md`
- The reference video this skill was built from, second by second, and its weak spots: `references/baseline-teardown.md`
- Writing the script: 100 structures, 200 hooks, titles, descriptions, hashtags, platform ranking signals (2026): `references/script-and-marketing.md`
- Target market, demographics, TAM/SAM/SOM, revenue math, safe zones: `references/audience-and-market.md`
- Voice pitch and speed: never change pitch unless an allowed reason applies; decision table and limits: `references/audio.md` (section 'Voice pitch and speed')
- Background music: template ids, genre match table, mood cheat sheet, mixing, beat sync, license-clear sources: `references/music-guide.md`
- How genre detection, auto style and the 360 per-video variants work, and the option count: `references/genres-and-variants.md`
- Why frosted-glass edits look expensive (glass cards, eyebrow labels, layout reflow, spatial captions, color pulses) and how to reproduce each: `references/design-secrets-glass.md`
- Errors and fixes: `references/troubleshooting.md`

---

# Part 2. anti-ai-ish.md

## Anti AI-ish: the rejection list

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Why this file exists:** community users complained that SpliceCraft's scripts and edits still *"berasa AI"*. This is the gate that catches it. Run it before delivering anything.
> **Editable:** every rule below carries its evidence. If you disagree with a rule, change it — but replace the evidence too. `<!-- journal -->` notes mark which rules are measured and which are judgement.

"AI-ish" is not a vibe. It is a short list of specific, nameable habits. Each one below is a habit, the reason it reads as machine-made, and the fix.

Two sources feed this file:
1. The course's own *"Contoh yang Salah"* and *"Yang Banyak Orang Lakukan"* slides (`kadev-personal-branding.md` §9.3, §8.1).
2. **Measurement of 82 real, well-performing reference videos** in `E:\Download\CONTOH INSPIRASI TEKNIK NGOTEN DAN EDITING VIDEO` — see `viral-edit-teardown.md` for the full numbers.

---

### A. The one that matters most

> **A script with no personal story is AI-ish, and no amount of editing fixes it.**

Element 5 of the 6 Script Hack Elements is *Personal Opinion / Story*. It is the only element a language model cannot supply, because it requires having lived something. Everything else in this file is secondary to it.

**The test:** point at the sentence in the script that could only have been written by this specific person. If you cannot find one, the script is AI-ish regardless of how good the hooks are.

**The rule for the agent:** if the user cannot give you a real story, a real number, or a real opinion — **stop and ask**. Do not write a plausible-sounding one. An invented anecdote is the worst possible failure here, because it is both AI-ish *and* dishonest.

---

### B. Script-level tells

#### B1. The opening sentence

| ❌ Reject | Why | ✅ Instead |
|---|---|---|
| *"Halo guys, balik lagi di channel aku"* | 2 seconds of nothing. The viewer gives you 8. | Start on the hook. No greeting at all. |
| *"Di video kali ini aku akan membahas tentang…"* | Announcing the video instead of starting it. The single most AI-ish sentence in Indonesian video. | The hook *is* the first sentence. |
| *"Pernahkah kamu bertanya-tanya…"* | Formal register nobody speaks in. | *"Pernah gak sih kamu…"* |
| *"Sebelum kita mulai, jangan lupa follow"* | CTA before value. Trains people to scroll. | CTA at the end, once. |

**Measured:** in the reference set the opening shot is **held** — median 2.22 s in cut-driven videos, which is 1.58× a typical shot in the same video. There is no greeting because the held shot is spending its time on the hook itself, not on a wind-up. See §C2.

#### B2. Vagueness where a number belongs

| ❌ | ✅ |
|---|---|
| "beberapa cara" | "3 cara" |
| "cukup lama" | "4 tahun" |
| "banyak orang" | "7 dari 10 orang" |
| "hasilnya lumayan" | "12 juta di bulan pertama" |

Vagueness is what a model produces when it does not know the fact. It is also what a person produces when they are hiding that they do not know. Both read the same. **If the number is not known, do not gesture at it — cut the claim.**

Every example in the source PDF uses **3, 4, or 5**. Odd, small, specific.

#### B3. Register drift into formal Indonesian

The source material is written in casual Indonesian and so is the market. Formal Indonesian in a TikTok script is a machine tell.

| ❌ Formal | ✅ Spoken |
|---|---|
| Anda | kamu / lu / kalian |
| tidak | gak / nggak |
| sangat penting | penting banget |
| melakukan | ngelakuin |
| memberikan | ngasih |
| oleh karena itu | makanya |
| dapat meningkatkan | bisa naikin |

Exception: a B2B or LinkedIn brief may legitimately want formal register. The brief decides. The *default* is spoken.

**"Kalian" → "kamu" / "kita".** Kadev's rule for spoken scripts (`kadev-live-mentoring.md` §8.2): *kalian* sounds like a teacher addressing a class, and a Gen Z viewer feels judged. Speak to one person. *Kalian* is acceptable only when an older speaker deliberately addresses a younger group.

#### B4. LLM sentence architecture

These are structural, not lexical, and they survive translation — which is why they are the hardest to spot.

- **Adjective triads.** *"efektif, efisien, dan optimal"*. Real speech uses one adjective, or none.
- **Balanced antithesis.** *"Bukan hanya X, tetapi juga Y."* Occasionally fine. Twice in one script is a tell.
- **The summarising close.** *"Jadi, itulah beberapa tips yang bisa kamu terapkan."* Nobody says this out loud. Real closes reverse the opening instead (see §C3).
- **Uniform sentence length.** Every sentence 12-18 words. Real speech alternates: a long one, then three words.
- **Hedging stacks.** *"mungkin bisa jadi salah satu cara yang cukup membantu"*. Four hedges, zero claims.
- **Listing without ranking.** Five items of equal weight and no opinion about which matters. The source material always says *"nomer 3 paling penting!"*

<!-- journal: B4 is judgement, not measurement — derived from reading the source scripts against typical LLM output, not from a corpus study. It is the least evidenced section here and the most likely to need revision. If someone later transcribes the 82 reference videos, this section should be rewritten against that data. -->

#### B5. The CTA

| ❌ | Why | ✅ |
|---|---|---|
| *"Semoga bermanfaat ya!"* | a sign-off, not a call to action | ask something answerable |
| *"Jangan lupa like, comment, share, save, dan follow!"* | five asks = zero asks | one ask |
| *"Follow untuk konten menarik lainnya"* | no reason given | *"Follow kalau kamu lagi bangun personal branding dari nol"* — names the tribe |

The course's own model CTA: *"Menurut kalian gimana? Kira-kira mic profesional bisa diganti sama AI ini? Beri tahu pendapat kalian di kolom komentar."* — a real question, with two defensible answers.

Element 6 is **Interactions**. A CTA that cannot be answered in a comment is not a CTA.

**Measured refinement (transcripts, `viral-edit-teardown.md` §9.3):** the reference corpus closes in two parts: **one** engagement move (a comment keyword → DM, or an answerable question), then a **fixed brand tagline** that is identical in every video (*"Repost kalau bermanfaat, dan follow untuk tips personal branding dan konten lainnya"*). The tagline is a signature, not a stack. What stays forbidden is several *different* asks written fresh for this video. 0 of 76 reference videos end on *"semoga bermanfaat"* or a summary.

---

### C. Edit-level tells

This section is measured. All numbers come from the 82-video reference set; method and full distribution in `viral-edit-teardown.md`.

#### C1. Uniform cutting is the giveaway

The single clearest finding from the measurement:

> **Real edits are bimodal. AI-ish edits are uniform.**

| Mode | Average shot length | Share of the 82 videos | What it is |
|---|---|---|---|
| **Cut-driven** | 0.5 - 2.5 s | 32 videos (39%) | b-roll, documentation, voiceover, jedag-jedug |
| *(the dead zone)* | 2.5 - 8 s | 27 videos (33%) | mixed / transitional |
| **Single-take** | 8 s - no cuts at all | 23 videos (28%) | talking head, straight to camera |

**Six of the 82 videos have zero scene cuts across 18-46 seconds.** They perform. They are not under-edited — they are a different grammar: one take, one person, captions and nothing else.

The AI-ish failure is landing in the middle by default: a cut every 3-4 seconds for the whole video, regardless of what is being said. That is the rhythm nobody chooses on purpose. It is the rhythm you get when a tool applies a uniform rule.

**The rule:** decide which mode the video is in *before* planning the edit, and commit.
- Talking head, one location, personal story → **single-take mode**. Cuts only where a sentence is removed. Possibly zero cuts.
- Voiceover over b-roll, a list, a tutorial → **cut-driven mode**. Median shot 1.5-2 s, and it stays there.

Never average the two.

<!-- journal: measured 2026-09-23 with ffmpeg scene detection (scale=160, select='gt(scene,0.3)') over all 82 files. Threshold 0.3 is conventional but not tuned; it will under-count cuts between visually similar shots (e.g. two angles of the same person against the same wall), so the single-take bucket may be slightly overstated. The bimodality is far too strong to be a threshold artifact. Raw per-file data in the session scratchpad, not committed. -->

#### C2. Openings

Measured on the reference set — and this one is **counterintuitive**, so read it before applying the usual advice:

- Median time to the **first cut** in cut-driven videos: **2.22 s** (p25 0.80 s, p75 4.00 s).
- Cuts landing in the first 3 s, against that video's own average rate: **0.75×**. The opening cuts **slower** than the video's baseline.
- The **first shot is 1.58× longer** than a typical shot in the same video. 56% of cut-driven videos hold it more than 1.2× as long.
- Median video length: **37.5 s**, bimodal — a cluster at **20-30 s** (24 videos) and a second at **60-90 s** (17 videos), with a dip between.

> **The hook is held, not chopped.**

This contradicts the common "chop the first three seconds to grab attention" instinct. The opening shot stays up long enough to read the on-screen hook and hear the spoken one, *then* the video starts moving.

**What this means for the opening:**
1. Give the hook shot about **1.5× your typical shot length**. Do not cut into it to seem energetic.
2. Something should still *change* early — a zoom, a card, a movement. Held is not the same as static.
3. The hook is *spoken* and *on screen* simultaneously. Many viewers start muted.
4. No logo animation. No "intro". The reference set has none.

#### C3. Closings

The course's Storytelling Hack beat ⑤ is *"Wrap It Up with a Relatable Message"* — and in the worked example, beat ⑤ **reverses** beat ①:

> ① *"Networking itu gila, bisa bikin kita sukses dan kaya raya"*
> ⑤ *"networking bukan seberapa banyak orang yang kamu kenal, tapi seberapa banyak orang yang pengen kenal kamu."*

That reversal is what makes a short loop: the viewer re-watches to check whether the opening already contained the ending. Rewatch and loop rate are ranking signals on every platform.

**Measured — and this is the most consistent single behaviour in the whole corpus:**

- Gap from the **last cut to the end**: median **3.16 s** in cut-driven videos.
- Cuts in the final 3 s against that video's own rate: **0.21×**. The closing cuts at about **one fifth** of normal.
- The **last shot is 2.42× longer** than a typical shot. **24 of 32 cut-driven videos (75%)** hold it more than 1.2× as long.

> **The ending is a landing, not a stop.**

The closing line gets its own held shot with the cutting switched off. That held shot is where beat ⑤ lands, and it needs room to be heard — it is what makes the video loop.

| ❌ AI-ish close | ✅ |
|---|---|
| summarises what was just said | reverses or reframes the opening claim |
| trails off | lands on a short sentence |
| stacks five CTAs | one question |
| keeps cutting over the CTA | stops cutting for the last ~3 s |
| hard-stops on the last syllable | holds the final shot ~2.4× a typical shot |

**Correction.** An earlier draft of this file said *"do not add a 2-second tail; the video ends on the last syllable."* The measurement says the opposite, and it has been corrected here. That advice is aimed at padded dead-air endings, which is a real fault — but in this style the held final shot is not dead air, it is the beat the closing line is delivered on. Cutting it off removes the loop. Full numbers and the correction record: `viral-edit-teardown.md` §5-6.

#### C4. Over-editing

Straight from the course's *"Contoh yang Salah"*:

> 🚫 **Editing Berlebihan / Minim Editing**
> - Terlalu banyak efek & transition, bikin pusing
> - Nggak ada subtitle, orang nggak ngerti kalau nonton tanpa suara
> - Musik terlalu kencang sampai nutupin suara

SpliceCraft's existing guards already encode this and they should not be relaxed:
- **breathing_room** gate: at least 35% of runtime with no card on screen.
- **no_card_overlap**: never two cards at once.
- **card_density** ceiling per level.
- Music sits under the voice; if you can hear music over a word, it is too loud.

Add one rule: **transitions are not decoration.** Use them at moments of *topic change*, not between every shot.

<!-- journal: the transition rule is INFERENCE, not measurement. Scene detection cannot see transitions, speed ramps or zooms - it only reports cuts. The rule is derived from the ASL distribution plus the course's own "terlalu banyak efek & transition, bikin pusing" slide. Do not present it to a user as measured. See viral-edit-teardown.md §7. -->

#### C5. Production faults that no edit repairs

From *"Contoh yang Salah"* — check these on the source file before planning anything:

| Fault | Check |
|---|---|
| **Cahaya buruk** — video gelap, wajah nggak kelihatan; backlight parah, muka jadi siluet | look at the contact sheet |
| **Suara nggak jelas** — noise (angin, kendaraan, orang ngobrol); ngomong terlalu pelan / jauh dari mic | listen; check the transcript's confidence |
| **Format salah** — horizontal footage for TikTok/Reels (terpotong); vertical for long YouTube | `$SC probe` reports orientation |
| **Mata nggak fokus** — ngeliatin layar HP, bukan kamera | visible on the sheet |
| **Kamera terlalu rendah** — double chin | visible on the sheet |

If one of these is present, **say so plainly and recommend a reshoot.** Silently "fixing" bad footage with heavy grading and zooms is itself an AI-ish move — it produces a video that looks processed rather than shot.

---

### D. Content-level tells

#### D1. Repetition across the account

This is why the content ledger exists (`content-memory.md`).

The failure: an AI asked for "content ideas about personal branding" produces the same twelve ideas every time. Over a month that becomes an account that says one thing twelve ways. The course names the symptom — *"orang gak inget dan gak percaya sama kamu"* — but blames inconsistency; the modern version of the problem is the opposite, **sameness**.

**Rule:** run `ledger check` before writing. Exit code 2 means do not write it.

#### D2. Writing to "everyone"

> **Niche bukan topik, tapi siapa secara spesifik.**

A script addressed to "content creators" is AI-ish. A script addressed to *"editor pemula yang baru pake CapCut dan videonya masih sepi"* is not. The 4K Method (`kadev-personal-branding.md` §6.6) exists to produce that sentence.

#### D3. Pillar monoculture

Four pillars: Educate, Inspiration, Entertaining, Promotion. An account that is 100% Educate reads like a knowledge base, not a person. `ledger stats` shows the balance; `ledger suggest` names what is due.

Same for the **80/15/5** ratio — superniche / adjacent / personal life. *"Bahas yang lain agar terlihat manusiawi."*

#### D4. Borrowed authority

*"Cuma bilang 'Saya bisa ini, saya jago itu' tanpa bukti nyata"* · *"Upload sertifikat doang tanpa konteks"* · *"Pamer doang tanpa value"*.

The fix from the same slide: **tunjukin proses kerja, bukan cuma hasil akhir.** Process footage is inherently un-fakeable, which is exactly why it reads as human.

---

### E. The gate

Run this before delivering. Any ❌ blocks delivery until fixed or explicitly waived by the user.

```
SCRIPT
  [ ] there is a sentence only this person could have written   (§A)
  [ ] no greeting, no "di video kali ini"                        (§B1)
  [ ] every vague quantity is either a real number or cut        (§B2)
  [ ] register is spoken Indonesian, unless the brief says else  (§B3)
  [ ] no adjective triads, no summarising close                  (§B4)
  [ ] exactly one CTA, and it is answerable                      (§B5)
  [ ] every factual claim confirmed by the user                  (§A)

EDIT
  [ ] mode chosen on purpose: cut-driven OR single-take          (§C1)
  [ ] shot rhythm stays in that mode, no drift to the middle     (§C1)
  [ ] opening shot HELD ~1.5x a typical shot                     (§C2)
  [ ] hook is spoken AND on screen                               (§C2)
  [ ] closing reverses the opening                               (§C3)
  [ ] final shot HELD ~2.4x a typical shot, cutting stops        (§C3)
  [ ] 9:16 vertical                                              (teardown §2)
  [ ] duration is 20-30 s OR 60-90 s on purpose                  (teardown §2)
  [ ] QA gates pass: breathing_room, no_card_overlap, density    (§C4)
  [ ] production faults named honestly, not hidden               (§C5)

CONTENT
  [ ] ledger check run, exit code 0                              (§D1)
  [ ] audience named as a specific WHO                           (§D2)
  [ ] pillar chosen, and not the same as the last three          (§D3)
  [ ] claims backed by process, not assertion                    (§D4)
```

---

### F. What this file does not claim

- These rules are tuned for **Indonesian short-form video** for a personal brand. A B2B English explainer wants different defaults; use `script-and-marketing.md`.
- The C-section numbers describe **82 videos from one reference folder**, most of them from a single creator. They are a strong signal about *this* style, not a universal law of short video. Treat them as "what good looks like in this lane."
- Nothing here guarantees reach. It removes the specific failure the community named. That is all.

---

# Part 3. kadev-personal-branding.md

## Personal branding: the full Kadev Academy body of theory

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Source material:** Kadev Academy by Kadafi Devayana — 37 lesson videos, 64 slide screens (6 chapters / 36+ learning materials), and 5 ebooks/PDFs. Extracted 2026-09-23.
> **Agent check:** compare this date with today. If more than 6 months have passed, re-check the platform claims here before relying on them. The *frameworks* below are the author's and do not expire; the *platform numbers* do.
> **Editable:** this file is meant to be edited. Every section carries a `<!-- journal -->` note explaining where it came from and what is still thin, so a future editor knows what is safe to change. See `../JOURNAL.md`.

This file is the theory. `kadev-script-formulas.md` is the execution layer (hooks, script structures, idea generation). `anti-ai-ish.md` is the quality gate. Read this one first: nearly every "AI-ish" script fails because the writer skipped straight to hooks without a premis, a niche, or a sweet spot.

---


> **Jump table** — for agents: grep the heading `## <n>.` and read only the section you need.
> - §0. The curriculum spine
> - §1. What personal branding actually is
> - §2. Chapter 1 — Know yourself (the foundation)
> - §3. Perception vs Persona
> - §4. "Ga Pede Personal Branding?" — the confidence block
> - §5. Chapter 2 — Vision Plan: start with WHY
> - §6. Niche, audience, and the algorithm
> - §7. First Impression
> - §8. Personal Brand Pillar
> - §9. Seni Dokumentasi Diri (documenting yourself)
> - §10. Chapter 4 — Survive Personal Branding
> - §11. Chapter 4 — Evaluation
> - §12. Chapter 5 — Expand & Monetize
> - §13. Networking, collaboration, and LinkedIn
> - §14. How SpliceCraft uses all of this
> - §15. Quote bank
> - §Provenance

### 0. The curriculum spine

Kadev Academy is ordered as 6 chapters, 36+ learning materials, and the order is load-bearing — the author explicitly says *"urut satu per satu, jangan skip kecuali udah paham."*

| # | Chapter | What it settles | Covered in |
|---|---|---|---|
| 0 | Onboarding + *Lebih dekat dengan Personal Branding* | definition, benefit, why it is not "just posting" | §1 |
| 1 | **Character Development** | who you are: Ikigai, Johari, SWOT, Premis, Selling Points | §2-§4 |
| 2 | **Vision Plan** | where you are going: Why/Golden Circle, Opportunity Mapping, niche | §5-§6 |
| 3 | **Execute & Show** | making it: algorithm, first impression, story, documentation, editing, design | §7-§9 + `kadev-script-formulas.md` |
| 4 | **Evaluate, Innovate & Growth** | surviving: consistency, crisis, trend, rebranding, evaluation | §10-§11 |
| 5 | **Expand & Monetize** | income: knowledge gap, digital product, networking, collaboration | §12-§13 |

**Why this matters to SpliceCraft.** A user who asks for a video edit usually arrives at chapter 3 with chapters 1 and 2 unanswered. That is the single largest cause of generic, AI-tasting scripts. Step 0.5 of `SKILL.md` exists to force chapters 1-2 to be answered before a word is written.

<!-- journal: spine taken verbatim from the slide "Struktur Belajar di Kadev Academy" (icons: Character Development → Vision Plan → Execute & Show → Evaluate, Innovate → Expand & Monetize) and cross-checked against the lesson-video filenames, which are numbered (0 x), (1 x) … (5 x) in the same order. High confidence. -->

---

### 1. What personal branding actually is

#### 1.1 The definition the author uses

> **Personal branding = "jual diri."** Not in the sleazy sense — it is how we package and market ourselves so other people are interested and get to know us better.

The slides sharpen this into a formula:

> **Jual Diri → Knowledge + Value + Experience → Kepercayaan, Kesempatan, Kekuatan.**

You are not selling a persona. You are selling *what you know*, *what you are worth*, and *what you have lived through*, and what you get back is trust, opportunity, and leverage.

#### 1.2 What it is NOT

Slide *"Personal Branding bukan sekedar…"* lists the things people mistake it for:

nama · logo · font · warna · tagline · konten · sosmed · followers · terkenal

All of those are *outputs*. None of them is the thing. Related slide: **"Followers banyak ≠ personal branding kuat."**

#### 1.3 The one word: OTENTIK

The author's conclusion after surveying every definition on Google and ChatGPT:

> Intinya ada satu kata yang mendefinisikan personal branding yaitu: **"OTENTIK"**.
> Menjadi otentik artinya menjadi versi terbaik dari diri kita sendiri, tapi tetap jujur dan nyata.

Supporting quotes he uses:
- *"Be yourself; everyone else is already taken."* — Oscar Wilde
- *"Menjadi diri sendiri adalah kunci untuk bisa berkarya dengan hati."* — Maudy Ayunda
- *"Personal branding itu jadi diri sendiri bukan jadi orang lain."* — Kadafi Devayana

The worked examples are Jerome Polin (made a hated subject, mathematics, feel easy and fun — by not hiding his struggle) and Najwa Shihab (never imitated anyone, so she became the most trusted).

#### 1.4 Why bother

Two framings appear across the material.

**The doors framing** — *Personal Branding is Your Access Card.* Five doors open:

| Door | What opens |
|---|---|
| **Bisnis** | people invest, buy, or partner more readily; the business is not only seen, it is *looked at* |
| **Karir** | recruiters now read your digital trail, not only your CV |
| **Relasi** | it forms a perception of who you are, so people with the same vision and energy find you |
| **Kolaborasi** | a professional identity makes you easy to invite into projects and communities |
| **Income** | paid jobs, freelance, speaking, partnership, affiliate, digital products |

**The stats framing** (slide *"Personal Branding adalah Masa Depan?"*): 74% / 63% / 62% figures are cited for *is the future*, *highly profitable*, *a trust accelerator*.

<!-- journal: the 74/63/62 percentages are printed on the slide but the slide does not name the study. Do NOT present them to a user as sourced fact — say "Kadev's slide cites" or drop them. Flagged as the weakest claim in this file. -->

#### 1.5 Personal branding is complex — but do not overcomplicate it

The author's own framing: *"Personal Branding itu Kompleks. Tapi jangan dibikin ribet, kamu akan menemukan jawaban seiring menyelesaikan materi demi materi dan coba untuk praktek."*

---

### 2. Chapter 1 — Know yourself (the foundation)

> Bagaimana kita bisa jual diri positif jika kita belum benar-benar mengenal siapa kita?

The metaphor used throughout: **Fondasi (Diri sendiri) → Istana (Proses Branding)**. When personal branding is not rooted in the actual self, four things happen, and the slides name them:

- **Ga Otentik** — it looks made-up, people can smell it
- **Gampang Goyah** — no anchor, so any criticism moves you
- **Bingung sendiri** — you do not know what to post
- **Sulit bertahan lama** — you burn out because you are performing

#### 2.1 Ikigai — and the key equation

**IKIGAI = NICHE.** This is the single most quotable line in chapter 1. Ikigai (生き甲斐, "iki" = hidup, "gai" = alasan) is four circles:

| Circle | Question | Kadev's phrasing |
|---|---|---|
| What You Love | Apa bidang yang kamu suka? | what you never get bored doing |
| What You Are Good At | Apa bidang yang kamu bisa? | what others often praise you for |
| What The World Needs | Apakah bidang itu dibutuhkan orang lain? | whose problem do you solve |
| What You Can Be Paid For | Apakah bidang itu bermanfaat untuk kamu? | how it becomes income |

The centre is **relate dan relevan**.

**The four questions to actually find it** (from the worksheet slide):
1. Apa yang membuat kamu senang & gak bosan melakukannya?
2. Skill apa yang sering dipuji orang lain dari kamu?
3. Masalah apa yang bisa kamu bantu selesaikan untuk orang lain?
4. Bagaimana caranya agar kamu bisa mendapatkan penghasilan dari ini?

**Why we need Ikigai** (slide *"Kenapa kita butuh cari IKIGAI?"*): because personal branding is a PROCESS; so you know your direction and focus; so you enjoy it and do it wholeheartedly; so what you do has impact and benefit; so it is relevant and pays; so your branding matches your actual self.

> *"Ikigai bikin kamu tahu nilai kamu, personal branding bikin nilai itu bersinar di depan dunia."* — Kadafi Devayana

#### 2.2 Johari Window

Developed by Joseph Luft and Harrington Ingham. In branding terms, "other people" = your audience.

|  | Kamu Pahami | Tidak Kamu Pahami |
|---|---|---|
| **Orang Lain Pahami** | **Open Area** — your visible behaviour, skills, experience | **Blind Spot** — habits others see that you do not |
| **Orang Lain Tidak Pahami** | **Hidden Area** — what you know but keep private | **Unknown** — latent potential neither side has seen |

Practical use: your **Open Area** is your safest early content. Your **Blind Spot** is found by asking people (see the Chapter-4 challenge in §11.1). Your **Hidden Area** is the reservoir for vulnerability content. **Unknown** is unlocked by trying new things and asking for feedback.

#### 2.3 SWOT for a person, and the "pesan diri"

> Personal branding bukan sekedar pencet tombol "post" doang. Harus punya **"pesan diri" yang konsisten**.

| SWOT | Pertanyaan untuk Diri Sendiri |
|---|---|
| **Strengths** (Kekuatan) | Apa yang kamu sudah kuasai? Apa yang membedakanmu dari orang lain? |
| **Weaknesses** (Kelemahan) | Apa yang sering kamu anggap sebagai kekurangan? |
| **Opportunities** (Peluang) | Tren atau peluang apa yang bisa kamu manfaatkan? Siapa yang bisa kamu jangkau? |
| **Threats** (Ancaman) | Hambatan eksternal apa yang bisa menghambat perkembangan personal branding-mu? |

> **Kunci utama: Kelemahan bisa jadi kekuatan dan pesan kalau kita tahu cara mengolahnya.**

This is the hinge of the whole method. The lesson is literally titled *"Ubah Kelemahan Jadi Kekuatan: Temukan Premis Diri Sendiri."*

#### 2.4 Premis and Personal Market Fit — the core original framework

This is the framework that does not appear in any of the PDFs and only exists in the slides. It is the most operationally useful thing in the entire course.

```
        SWOT (S W / O T)
               │
               ▼
           PREMIS         ← one paragraph: your weakness, turned, aimed at a group
               │
               ▼
   PERSONAL MARKET FIT (PMF = Premis)
               │
               ▼
      "Konten yang bakal dibikin"
```

**PMF = Premis.** Your market fit *is* your premise. If the premise is sharp, the content queue writes itself.

The slides give four worked examples. Reproduce their shape, not their words:

| S (strength) | W (weakness) | O (opportunity) | T (threat) | Premis |
|---|---|---|---|---|
| Praktisi dan ahli personal branding | Misterius, gengsi dan malu-malu | Buka kesempatan banyak dari personal branding | Pesaing banyak | *"Dari seorang misterius, gengsi dan malu buat mulai personal branding, akhirnya mencoba memulai dan mendapatkan banyak kesempatan baik dari Personal branding, mulai dari active income, nama dikenal, relasi dan kolaborasi."* |
| Inisiator WFA dan praktisi | Anak desa, ga bisa lanjut SMA | Banyak kesempatan kerja dimana aja, tapi banyak orang gatau | Pesaing banyak | *"Dari anak desa yang tidak bisa lanjut SMA menjadi inisiator Work From Anywhere (WFA), membantu ribuan orang mendapatkan penghasilan dari mana saja. Saya percaya bahwa peluang kerja digital sangat luas, tetapi banyak yang belum mengetahuinya. Melalui pengalaman dan praktik langsung, saya ingin membuka wawasan dan membimbing lebih banyak orang untuk memanfaatkan peluang ini."* |
| Punya pengalaman nyata dalam membangun bisnis | Pernah mengalami kegagalan bisnis | Banyak UMKM butuh mentor yang memahami tantangan mereka | Banyak pesaing di dunia bisnis dan mentor UMKM | *"Dari seseorang yang mengalami kegagalan bisnis berkali-kali, akhirnya belajar dari kesalahan dan sekarang membagikan strategi agar UMKM bisa bertahan dan berkembang."* |
| Punya pemahaman mendalam tentang komunikasi efektif | Dulu takut berbicara di depan umum | Banyak orang butuh dan ingin belajar public speaking | Sudah banyak pembicara di luar sana | *"Dari seorang yang pendiam dan takut berbicara di depan umum, akhirnya belajar mengatasi ketakutan dan sekarang menjadi pembicara yang membahas cara percaya diri saat berbicara di depan kamera dan audiens."* |

**The shape of a premis, extracted:**

> "Dari **[kelemahan / titik terendah yang spesifik]**, akhirnya **[apa yang kamu lakukan]**, dan sekarang **[posisi kamu hari ini]** untuk **[siapa yang kamu bantu]**."

**Action plan** (the slide closes chapter 1 with this):
1. ✅ Buat SWOT pribadi kamu
2. ✅ Tulis premis personal branding
3. ✅ Terapkan dalam konten dan komunikasi
> ➡ Kuncinya adalah **mengubah sudut pandang**.
> *"Personal branding bukan tentang pencitraan, tapi tentang bagaimana kamu bisa menyampaikan pesan yang berdampak!"*

<!-- journal: transcribed from six slide screens (Personal's Foundations ×4 + "Ubah Kelemahan Jadi Kekuatan" + ACTION PLAN). The premis paragraphs are quoted as printed, including their Indonesian phrasing. Two of the four examples had a blank/anonymous avatar, so the people are not identified — do not attribute them. This section is the highest-value part of the extraction and should NOT be shortened. -->

#### 2.5 Selling Points via STAR

Selling points = the unique, interesting aspects that make you stand out and — the author stresses — make you **remembered**, not merely seen.

> *"Personal branding bukan hanya tentang menjadi terlihat, tetapi juga tentang menjadi diingat."*

**STAR**, borrowed from interviews:

| Letter | Question |
|---|---|
| **S**ituation | Gambarkan situasi atau konteks yang relevan |
| **T**ask | Jelaskan tugas atau tantangan yang dihadapi |
| **A**ction | Ceritakan tindakan yang diambil untuk menyelesaikan tantangan |
| **R**esult | Sebutkan hasil yang diperoleh: pencapaian, pembelajaran, atau dampak |

The worked example (Kemal, food reviewer) yields the selling points: *cinematic video style, professional cinematography and editing skill, ability to reach an audience that wants premium culinary experiences.* Note how the selling point is a **capability + an audience**, never an adjective.

**Five rules for using selling points:** show them in profile and portfolio (easiest: make content about your work) · mention them when you speak or write about yourself · keep developing the skill behind them · stay honest, never inflate them · re-evaluate them periodically as the market and you change.

STAR is reused later as the LinkedIn caption structure (§13.3).

---

### 3. Perception vs Persona

Two concepts that decide whether branding stays honest.

| | **Perception** | **Persona** |
|---|---|---|
| Definition | What everybody else thinks about you | What you want everyone to think about you |
| Made of | opini · cara komunikasi · apa yang kita lakukan · penampilan | sukses · gagal · personal · nilai |
| Note on the slide | *"kita ga bisa hidup tanpa presepsi"* | shown as "Di sosmed" vs "Aslinya" |

**The two failure modes**, given as case studies:

- **Dina** lives entirely for *perception* — follows every trend, wears what friends approve of, signs up for a yoga class she has no interest in, and waits anxiously for likes. She loses her sense of self and is unhappy.
- **Rico** builds a false *persona* — borrows a sports car for photos, poses in front of a house that is not his, posts holidays he never took. He is financially struggling, exhausted from maintaining it, and people start to doubt him. Long-term reputation damage.

**The balance:** integrate the two honestly. The author cites Law 25 of Robert Greene's *The 48 Laws of Power* — *"Re-create Yourself: Do not accept the roles that society foists on you…"* — and reads it as *create something compelling, but keep it authentic.*

Closing slide: **"gak usah dibuat-buat · gak sesuai Ikigai · gak sesuai nilai diri"** → *hal yang menarik dari diri kita adalah "proses yang kita alami". Banyak orang yang menyerah personal branding karena ya capek ga jadi diri sendiri.*

#### 3.1 The Circle of Control

Answer to the DM: *"Bang, gimana sih kita tetap konsisten personal branding, tanpa dengerin omongan dan hujatan lingkungan sekitar?"*

> **Aku akan fokus kepada hal yang bisa aku kontrol dan kendalikan.**

| Bisa aku kendalikan | Tidak bisa aku kendalikan |
|---|---|
| Tindakanku — konten yang aku buat, cara aku berinteraksi | Perasaan orang lain tentang konten atau diriku |
| Perkataanku — bagaimana aku menyampaikan pesan | Perlakuan orang lain terhadap kontenku |
| Caraku memperlakukan orang lain — kolaborator, audiens, komunitas | Apa yang orang lain pikirkan / katakan |
| Caraku mengelola perasaanku — stres, kegagalan, kritik | Tren yang muncul, algoritma sosial media |
| Batasanku — waktu dan energi, agar tidak kelelahan | Keputusan orang lain, waktu & cuaca, hal-hal di masa lalu |
| Belajar personal branding, bikin konten yang punya value, skill & pengetahuan yang dikembangkan, evaluasi | Presepsi orang, hate orang lain, dikatain alay/pamer/sombong |

<!-- journal: two versions of this diagram exist in the material (one in the ebook, one in the slides, the slide version has more items and is the one tabulated here). Merged. -->

---

### 4. "Ga Pede Personal Branding?" — the confidence block

The exact fear, quoted on the slide:

> *"Aku udah mau mulai bangun personal branding, tapi takut di-hate, di-katain pamer, alay, haus validasi, sok-sok an, bla bla…."*

The answer is the Perception/Persona pair plus the Circle of Control above, and one reframe that recurs across the course: **kritik itu bahan bakar, bukan penghambat** (see §11.2).

---

### 5. Chapter 2 — Vision Plan: start with WHY

> **Tujuan Ga Jelas = Percuma Personal Branding.**
> **Karena beda tujuan, beda juga cara bikin kontennya.**

#### 5.1 The Golden Circle (Simon Sinek)

| Ring | Question | Kadev's Javanese gloss |
|---|---|---|
| **Why** — Your Purpose | What is your cause? What do you believe? | *lapo* — apa tujuan dan motivasi kamu? |
| **How** — Your Process | Specific actions taken to realise your Why | *yaopo* — gimana cara kamu mencapai "kenapa" kamu dengan aksi spesifik? |
| **What** — Your Result / Proof | What do you do? The result of Why. Proof. | *opo* — apa hasil yang pengen kamu dapetin? |

> *"Why" membantu kamu tetap konsisten dan fokus meski ada tantangan.*

**Two worked examples:**

| Why | How | What |
|---|---|---|
| Share portfolio dan skill biar dapet kerja | Bikin konten yang relevan dengan lowongan pekerjaan yang kamu cari | Dapet kerja yang sesuai |
| Dapetin penghasilan dan bisa hidup dari konten | Bikin konten yang sesuai dengan kebutuhan pasar dan audiens | Bisa hidup dan kerja jadi konten kreator |

**The author's own Why**, printed on a slide, as a template for how specific it should get:

| Tujuan untuk diri sendiri | Tujuan untuk orang lain |
|---|---|
| Ningkatin kredibilitas di industri | Memberikan edukasi dan inspirasi khususnya untuk anak muda |
| Memperluas peluang karir dan bisnis | Menjadi salah satu sumber perubahan sosial |
| Ningkatin daya tarik kolaborasi dan networking | Intinya sering bangun personal branding, pengen bermanfaat aja sih, sekecil apapun itu |
| Menjadi konten kreator dan monetisasi ilmu | |

> Dari "WHY" kita bisa nentuin: **Strategi dan Vision Plan personal branding** — dan which platform (IG / TikTok / LinkedIn) you belong on. **Beda Tujuan, Beda Caranya.**

#### 5.2 The menu of possible goals

From *"Kenapa kamu personal branding?"* — pick and be honest:

Share portfolio? · Jadi konten kreator? · Peluang kolaborasi? · Dipercaya orang? · Bangun networking? · Dapetin income? · Peluang karir dan pekerjaan? · Untuk validasi?

<!-- journal: "untuk validasi kah?" appears in the Content Strategy ebook's list but not on the slides. Kept — it is the honest option and users pick it more often than they admit. -->

#### 5.3 Opportunity Mapping

Two ways to turn a Why into a queue of moves.

**A. Based on Passion.** A tree: `Passion → Opportunity ×5 → Solution ×4 each`.
- *Passion* = the field you know from Ikigai
- *Opportunity* = the jobs/paths that come from that passion
- *Solution* = the concrete things you can do to support each opportunity
- The whole tree is bracketed as **PERSONAL BRANDING**

Worked example: `Marketing → Consulting & Market Research | Product Management & Growth | Sales & Business Development | Digital Marketing & Advertising | Entrepreneurship & Startup`, each with its own column of concrete moves.

**B. Based on Time Frame.** The same tree, but the spine is time: Tahun, Semester, Quarter, Bulan, or Minggu. Worked examples given for four different people:

| POV | Spine | Example cells |
|---|---|---|
| Mahasiswa | Semester 1-8 | Scholarship, Competition, Volunteership, Organization → Short Exchange → MBKM → Company Development Program → Thesis / MT |
| Entrepreneur F&B | 2026→2029 | akselerator F&B → daftar franchise/cloud kitchen → buka peluang investor → ekspansi ke kota tier 2 dan 3 |
| Author / Penulis | Q1-Q4 | festival & konferensi → menawarkan buku ke penerbit → self-publishing & crowdfunding → drive festival internasional |
| Graphic Design Freelancer | W1-W4 | update & kurasi portfolio → optimasi profil Upwork/Fiverr → buat konten Instagram/TikTok → evaluasi & sesuaikan pricing |

Framing quote used: **Eat That Frog!** (Brian Tracy) — *"If it's your job to eat a frog, it's best to do it first thing in the morning. And if it's your job to eat two frogs, it's best to eat the biggest one first."*

Also framed as answers to: *"Udah punya passion, tapi bingung mau jadi apa?"* and *"Punya banyak waktu kosong, tapi bingung mau ngapain?"*

---

### 6. Niche, audience, and the algorithm

#### 6.1 The reframe

> **Niche bukan topik, tapi SIAPA secara spesifik.**

This one line fixes more bad content plans than anything else in the course.

#### 6.2 The superniche ladder

| Level | Example |
|---|---|
| General | Industri kreatif |
| Niche | Video Editing |
| **Superniche** | **Video Editing pakai CapCut** |

> **Fokus satu superniche, jadi paling hebat dan top of mind.**

**Why superniche wins** (the slide's three reasons):
- Algoritma media sosial merekam siapa yang nonton & engage dengan konten terbaikmu
- Kalau topikmu terlalu luas atau sering berubah drastis, algoritma bingung → reach turun
- Akun dengan niche jelas tumbuh lebih cepat karena algoritma tahu siapa target audiensnya

#### 6.3 How the algorithm actually works (Kadev's model)

```
Bahas Video Editing di CapCut → Editor Pemula → Interaksi → Editor Pemula lain kena konten kamu
```
versus the broken version:
```
Bahas Video Editing di CapCut + Bahas Politik/Finance → Editor Pemula → Gak Suka Kontennya → Algoritma membaca kontenmu gak punya value
```

Analogy given: the **Snowball Effect.**

Second analogy, the food-stall one, which is the most memorable in the whole course:

> *Hari ini jualan soto, besok gak jualan, lusa jualan bubur ayam.* ❌
> *Lama-lama, aku jadi males beli karena gak tahu sebenarnya dia jualan apa.*
> Sama kayak personal branding. Kalau hari ini bahas keuangan, besok gaming, lusa motivasi, orang bakal bingung kamu ini siapa. **Akhirnya, orang gak inget dan gak percaya sama kamu.**

#### 6.4 The 80 / 15 / 5 content ratio

Even with a superniche you are allowed to talk about other things — in this proportion:

| % | Topic layer | Example (Kadev's own account) |
|---|---|---|
| **80%** | the superniche itself | Personal branding untuk anak muda usia 18-24 tahun |
| **15%** | the adjacent layer | Self Development untuk anak muda usia 18-24 tahun |
| **5%** | personal life | Kehidupan personal |

> **Bahas yang lain agar terlihat manusiawi. Usahakan membahas topik lain yang masih sedikit beririsan.**

This is the single most concrete anti-AI-ish rule in the course. A feed that is 100% niche reads like a content farm; a feed that is 40% personal reads like a diary. 80/15/5.

#### 6.5 Perfect Niche and Money Making Potential

**Perfect Niche** = the intersection of three circles: `Your Passion ∩ Your Skill ∩ Money Making Potential`.

**Money Making Potential** ("Ga akan pernah mati") is a triangle whose centre is **Human Happiness**:

| Vertex | Why it never dies |
|---|---|
| **Health** ❤️ | orang selalu mau hidup lebih sehat |
| **Wealth** 💰 | orang selalu ingin lebih aman secara finansial |
| **Relationship** 👨‍👩‍👧 | orang selalu ingin terhubung |

Why this is a good strategy, per the slide: selalu relevan (topik ini timeless, selalu ada marketnya) · banyak model monetisasi (konten, jasa, kursus, coaching) · bisa disesuaikan dengan personal branding-mu.

#### 6.6 The 4K Method — finding what the audience actually needs

The audience-side counterpart of Ikigai. Diagram: `Your Persona ∩ Audience Needs = Sweet Spot`.

| K | Meaning | What to look for |
|---|---|---|
| **Keresahan** | Pain Point | what frustrates them |
| **Kebutuhan** | Needs | what they must have |
| **Keinginan** | Wants | what they wish for |
| **Kebiasaan** | Habits | what they already do |

**Three worked examples, reproduced in full** because they are the best template in the material:

**Niche: Produktivitas & Time Management**
- Keresahan: *"Susah atur waktu, kerjaan numpuk, sering prokrastinasi."*
- Kebutuhan: *"Tips simpel dan efektif buat lebih disiplin dan produktif."*
- Keinginan: *"Mau bisa kerja lebih cepat, punya banyak waktu luang, dan tetap santai."*
- Kebiasaan: *"Sering scroll sosmed cari tips, suka nonton video motivasi, pakai to-do list tapi sering gak kepake."*
- 🎯 Sweet Spot: bikin konten time management simpel yang relatable buat orang yang sering menunda pekerjaan, misalnya *"Cara Stop Prokrastinasi dalam 5 Menit"* atau *"Trik Rahasia Biar Kerjaan Kelar Lebih Cepat"*.

**Niche: Personal Finance untuk Anak Muda**
- Keresahan: *"Gaji cepat habis, susah nabung, takut salah investasi."*
- Kebutuhan: *"Panduan keuangan yang gampang dipahami tanpa ribet."*
- Keinginan: *"Bisa nabung tanpa tersiksa, punya passive income, tetap bisa nongkrong."*
- Kebiasaan: *"Suka belanja impulsif, sering lihat konten tentang kaya cepat, tapi bingung mulai dari mana."*
- 🎯 Sweet Spot: konten tips keuangan santai & fun buat anak muda, misalnya *"Cara Nabung Tanpa Ngerasa Miskin"* atau *"Investasi Buat Pemula: Mulai dari 10 Ribu"*.

**Niche: Kesehatan & Fitness untuk Pemula**
- Keresahan: *"Mau mulai olahraga tapi males, bingung diet yang bener."*
- Kebutuhan: *"Program diet dan workout yang gak ribet buat pemula."*
- Keinginan: *"Bisa turun berat badan tanpa harus olahraga berat atau makan hambar."*
- Kebiasaan: *"Sering coba-coba diet, gampang nyerah, lebih suka lihat tips cepat di TikTok/Instagram."*
- 🎯 Sweet Spot: konten diet & olahraga simpel yang fun, misalnya *"5 Gerakan Pemalas Biar Berat Badan Turun"* atau *"Makan Enak Tapi Tetap Kurus, Gimana Caranya?"*.

#### 6.7 The Sweet Spot, and what happens when you miss it

| Only *Your Persona* | ✅ **Sweet Spot** | Only *Audience Needs* |
|---|---|---|
| gak relevan · low engagement · narsis · jangan cuma fokus ke persona · ga bermanfaat · ego · sulit ningkatin followers · kurang punya peluang · pamer | Konsisten tanpa paksaan · Relevan (untuk diri sendiri dan audience) · Audiens betah & engaged · Gak kehilangan jati diri · Bangun kredibilitas & bikin orang percaya · Gak cepat burnout atau bosan · Bangun komunitas yang loyal · Kesempatan karir dan bisnis · Lebih gampang monetisasi · Beda dari orang lain · Bikin Personal Brand kamu Sustainable | Kehilangan Identitas Diri · Ga punya karakter diri · Tidak Berkelanjutan (Cepat Bosan & Lelah) · Ga ada USP, susah bedain sama kompetitor · Ga punya kredibilitas · Orang cenderung mengikuti seseorang yang punya cerita dan pengalaman unik |

#### 6.8 Buyer Persona

From the ebook. Three steps: **Riset Audiensmu** (survey, interview, social analytics; easiest = IG Stories question box) → **Identifikasi Karakteristik Utama** (demografi: usia, gender, lokasi, pekerjaan, pendidikan; psikografi: minat, hobi, nilai, gaya hidup; perilaku: kebiasaan belanja, penggunaan sosmed, preferensi konten) → **Gunakan Persona untuk Strategi.**

Worked example (food creator): *18-24, tinggal di kota yang punya universitas, mahasiswa; tertarik eksplorasi kuliner dan gaya hidup anak kos; mencari tempat makan viral dengan pengalaman unik dan estetis; aktif membagikan pengalaman kuliner di sosmed.*

#### 6.9 Audience-Focused Content and the feedback loop

Five moves: pahami kebutuhan dan minat audiens · berikan nilai tambah · libatkan audiens · dengarkan feedback · bangun komunitas.

The author's own story is the proof: in 2023 his Instagram went quiet; a friend (Zaki) told him *"Aku suka banget kalau konten kreator yang aku follow itu membalas DM atau reply story aku."* He started replying to every DM and comment and running Stories Q&A. Engagement recovered.

> Personal branding bukan hanya tentang konten yang kita buat, tetapi juga tentang **bagaimana kita berinteraksi dan memperlakukan audiens.**

#### 6.10 Changing niche without wrecking the account

> *"Aku udah mulai nih… tapi gak cocok sama niche-nya, gimana ya cara ngubahnya?"*
> **Jangan TIBA-TIBA, Algoritma bakal kacau.** Contoh buruk: Health → Otomotif, Finance → Editing ❌

**Solusi = Buat jembatan pelan-pelan.** Find the overlapping topic and walk across it.

```
Mobile Video Editing  ──[ topik yang beririsan keduanya ]──►  Personal Branding
```
Bridge content = content that belongs to both: *"3 akun editing video yang personal brandingnya bagus"*, *"Cara biar personal branding melekat yaitu dengan editing yang bagus"*.

---

### 7. First Impression

#### 7.1 Human Attention Span

| 2000 | 2024 | Goldfish |
|---|---|---|
| 12 seconds | **8 seconds** | 9 seconds |

> *"Kamu cuma punya 8 detik buat bikin orang tertarik dengan profilmu! Kalau mereka nggak suka? Bye, langsung scroll lewat!"*

The slide poses it as: *Kenapa ada akun yang langsung bikin orang follow? Kenapa ada yang di-skip meski kontennya bagus?* → **Jawabannya ada di FIRST IMPRESSION.** The three surfaces are **Photo Profile, Bio, Feeds**.

#### 7.2 Why profile and first impression matter

- **Time Waktu Penilaian Cuma 3 Detik** — orang butuh kurang dari 3 detik buat menentukan apakah mereka tertarik dengan profil kamu atau nggak
- **Foto Profil = Kesan Pertama** — profil Instagram/TikTok itu kayak "pintu depan" kamu di dunia digital
- **Bio = Elevator Pitch** — bio yang kuat bisa langsung menjelaskan siapa kamu, apa yang kamu tawarkan, dan kenapa orang harus follow kamu
- **Feeds = Bukti Konsistensi** — orang nggak cuma lihat satu post, tapi juga feeds kamu secara keseluruhan
- **Ningkatkan Kredibilitas & Trust** — kalau profil kamu terlihat profesional, orang lebih gampang percaya

#### 7.3 The anatomy of a profile, annotated

From the slide dissecting `@kadafidevayana`:

| Element | Rule |
|---|---|
| **Username** | Nama asli (personalisasi) |
| **Profile Name** | `Nama kamu + niche atau industri yang sedang kamu bahas` — *for SEO* |
| **Bio line 1 (Misi)** | *"🎯 Misi Bantu 10.000 Orang Bangun Personal Branding"* → **Value:** nilai apa yang kamu tawarkan |
| **Bio line 2 (Build / Peers)** | `Build @… | Founder @…` / `Peers @…` → **You:** siapa kamu, spesialisasi kamu dan proof |
| **CP / link** | `lynk.id/…` → **Call to Action:** berupa link untuk tau lebih lanjut |

**Profile photo:** ✅ clear face, natural light, friendly · ✅ clean formal headshot · ❌ a photo shot from behind / from far away · ❌ default blank avatar.

#### 7.4 Feeds Tips

- **Konsisten visual** → pakai tone warna atau style yang seragam supaya orang langsung kenal identitasmu
- **Mix konten** → gabungkan edukasi, storytelling, viral content, dan promo supaya feed nggak monoton
- **Thumbnail/video cover catchy** → pakai judul yang bikin penasaran, misalnya *"Kenapa konten kamu nggak FYP? Ini alasannya!"*
- **Engagement tinggi** → posting dengan format yang memancing interaksi, seperti polling di story, carousel tips, atau video tanya-jawab

#### 7.5 Highlights = RAW Portfolio

Instagram/TikTok highlights are treated as a portfolio, grouped by proof type: `on stage` · `Astra 🔵` · `Bicara 🎤`. The point is that a highlight names the *kind of proof*, not the month.

---

### 8. Personal Brand Pillar

> Personal Branding **Tanpa** Personal Branding. / Personal Branding **Tanpa Teriak** Personal Branding.

The fear it answers: *banyak orang pengen bangun personal branding, tapi takut terlihat "jualan diri" atau terlalu memaksakan image tertentu.*

#### 8.1 The anti-pattern list (memorise this)

| 🚫 Yang Banyak Orang Lakukan | ✅ Yang Bener |
|---|---|
| Cuma bilang *"Saya bisa ini, saya jago itu"* tanpa bukti nyata | Tunjukin **proses kerja**, bukan cuma hasil akhir |
| Upload sertifikat doang tanpa konteks | Ceritakan pengalaman, tantangan, dan solusi yang dipakai |
| Share hasil kerja, tapi tanpa storytelling atau value tambahan | Gunakan format carousel, case study, atau before-after biar lebih engaging |
| Pamer doang tanpa value | Bikin konten harus ada tujuannya |
| Bikin konten sekedar bahas tips, trik, berita, hiburan | |

> Caraku ngakalinnya… pakai **Personal Brand Pillar**.

#### 8.2 The four pillars

| Pillar | Produces |
|---|---|
| **Educate** | Kredibilitas |
| **Inspiration / Story** | Diingat dan Disukai |
| **Entertaining / Interaction** | Lebih dekat dan manusiawi |
| **Promotion** | Penjualan |

**Premis + Pillar = Match Branding.** Take the premis from §2.4, run it through the four pillars, and you have four content streams that all say the same thing in different registers. That is what "consistent" actually means — not posting at the same time, but four pillars pointing at one premis.

#### 8.3 The content-type map (ebook version)

| Edukasi | Inspirasi | Koneksi | Hiburan | Informasi |
|---|---|---|---|---|
| Tips dan Trik | Cerita gagal dan berhasil | Cerita pribadi | Ikut tren | Berita (news) |
| Tutorial | Pelajaran yang diambil | Insight pribadi | Relatable | Mitos dan Fakta |
| Nasihat | | Perjuangan pribadi | Aktivitas · Memes · Challenge | Pro dan Kontra |

Simplified four-type version also used: **Edukasi · Hiburan · Inspirasi/Emosi · Promosi.**

#### 8.4 Hirarki Konten (Mark Schaefer)

Four levels, bottom to top. Climb them.

| Level | Name | What you do |
|---|---|---|
| 1 | **Menjawab Pertanyaan** | answer the actual questions in your comments and DMs |
| 2 | **Edukasi** | teach your niche |
| 3 | **Emosional** | tell the struggle behind what you built |
| 4 | **Inspirasi** | make people act |

> Kalau konten kamu sudah sampai ada di titik menginspirasi, selamat… artinya **kamu sudah dikenal orang**.

---

### 9. Seni Dokumentasi Diri (documenting yourself)

The bridge between strategy and the camera — and the chapter that hands off directly to SpliceCraft.

#### 9.1 The format map

```
                       Content
        ┌──────────┬──────────┬──────────┬───────────┐
      Video      Writing    Stories   Live Stream
   ┌────┴────┐  ┌───┴────┐
Short-form  Long-form  Single/Carousel  Threads
```

| Kategori Konten | ✅ Plus | ❌ Minus | 🎯 Goals |
|---|---|---|---|
| **Short-form Video** | Gampang viral, nggak perlu lama bikin, interaksi tinggi | Umur konten pendek, harus sering upload | Biar lebih dikenal & menarik followers baru |
| **Long-form Video** | Bisa jelasin lebih detail, bangun loyal audience | Bikin lama, butuh effort lebih | Bangun kredibilitas & bikin audiens loyal |
| **Single Post / Carousel** | Cerita, edukasi atau inspirasi bisa simpel & padat | Harus bisa belajar nulis dan kreatif biar nggak tenggelam di algoritma | Share insight, edukasi, & bangun kredibilitas |
| **Threads** | Bisa storytelling lebih panjang, enak buat diskusi | Harus pinter bikin hook biar orang lanjut baca | Bikin diskusi, share opini & ningkatin kredibilitas |
| **Stories** | Lebih personal, enak buat storytelling | Cuma bertahan 24 jam, reach kadang nggak stabil | Bangun koneksi lebih dekat dengan audiens |
| **Live Streaming** | Interaksi langsung, lebih otentik | Harus siapin materi, kalau kelamaan bisa bikin bosan | Naikin trust & bikin engagement real-time |

Tips per format from the tree: Short-form → *Talking Head (video ngobrol langsung ke kamera)*, *Voice Over & Documentation (rekam aktivitas, narasi dibelakang)*, *Jedag-jedug / Trendy Edits (pengikut tren musik & transisi)*. Long-form → *Dokumenter perjalanan*, *Podcast video*, *Tutorial dan edukasi panjang*. Writing → *Kapan Pakai Single Post?* (kalau pesannya simpel & to the point; contoh: quotes, micro-blogging) vs *Kapan Pakai Carousel?* (untuk konten storytelling atau edukasi mendalam; contoh: studi kasus, step-by-step guides).

#### 9.2 Roll & Action — the production checklist

> ✅ Cahaya cukup, kalau bisa natural light atau ring light (Golden Hour)
> ✅ Suara jelas, pakai mic eksternal kalau perlu
> ✅ Teleprompter tips CapCut
> ✅ Bisa dimana aja kapan aja
> ✅ Gunakan format vertikal (9:16) buat Reels/TikTok, horizontal (16:9) buat YouTube
> ✅ Edit simpel, tambahin subtitle & musik biar engaging
>
> **Next Materi, Editing!**

#### 9.3 Contoh yang Salah — the production error list

This is the checklist SpliceCraft should run against any footage a user hands over.

| 🚫 Cahaya Buruk | 🚫 Suara Nggak Jelas | 🚫 Format Video Salah |
|---|---|---|
| Video gelap, wajah nggak kelihatan jelas | Banyak noise (suara angin, kendaraan, atau orang ngobrol) | Rekam horizontal buat TikTok/Reels (terpotong pas upload) |
| Backlight parah, muka jadi siluet | Ngomong terlalu pelan atau terlalu jauh dari mic | Video vertikal buat YouTube panjang (nggak full screen) |

| 🚫 Editing Berlebihan / Minim Editing | 🚫 Badan & Mata Nggak Fokus |
|---|---|
| Terlalu banyak efek & transition, bikin pusing | Ngeliatin layar HP, bukan kamera (kesannya nggak engage) |
| Nggak ada subtitle, orang nggak ngerti kalau nonton tanpa suara | Posisi kamera terlalu rendah (double chin alert 😅) |
| Musik terlalu kencang sampai nutupin suara | |

<!-- journal: this table is the direct ancestor of anti-ai-ish.md §"Production". Keep them in sync — if you edit one, edit the other. -->

---

### 10. Chapter 4 — Survive Personal Branding

#### 10.1 The number that frames the chapter

> Kebanyakan orang cuma pengen **viral**. Berhasil viral. Tapi, **gak bisa bertahan.**
> **7/10 orang gagal personal branding 6 bulan pertama.**

The author includes himself: *"Aku termasuk dari 7/10 itu."* (Shown with a screenshot of his abandoned 2017 YouTube uploads.) *"Terus gimana caraku untuk menghidupkan kembali?"*

**Ngejar Viral: cepat naiknya, cepat juga turunnya.**

#### 10.2 The five survival levers

The chapter's own diagram — a hand reaching out of sand — with five icons:

| Lever | Core idea |
|---|---|
| **Trend Adaptation** | ride trends *your way* |
| **Signature Content** | be instantly recognisable |
| **Loyal Audience** | community over follower count |
| **Personal Brand Crisis** | handle criticism without collapsing |
| **Unrelevan = Rebranding** | evolve on purpose, not by accident |

**Trend Adaptation — Rahasianya:**
- **Pilih tren yang relevan** → jangan asal ikut, pilih yang bisa dikaitkan dengan niche-mu
- **Gunakan tren sebagai kendaraan, bukan tujuan** → tren hanya alat untuk meningkatkan exposure
- **Twist tren dengan gaya sendiri** → ambil tren, lalu ubah sesuai style atau sudut pandang khasmu
- 🚫 Kesalahan banyak orang: ikut semua tren tanpa relevansi (branding jadi tidak jelas) · mengubah identitas hanya demi tren (malah bikin audiens bingung)

**Signature Content** — *gaya khas dalam menyampaikan konten yang bikin kamu mudah dikenali. Bisa berupa format visual, tone, atau cara penyampaian konten.*
- ✅ Eksplorasi berbagai format → coba carousel, thread, short-form video, atau podcast
- ✅ Pilih format yang paling nyaman & cocok → harus sustain dalam jangka panjang
- ✅ Buat template atau pola khas → misalnya, selalu mulai dengan storytelling atau pakai font/style tertentu
- Warna sebagai signature: `Kadafi → Hitam Putih`, `Uirofi → Orange`, `Kasisolusi → Biru`
- 🚀 Biar gampang dikenali! Orang langsung ngeh, *"Oh ini kontennya si …"* tanpa harus lihat username dulu.
- 🚀 Nggak pusing mikirin format baru tiap kali bikin konten. Udah ada pakemnya, tinggal eksekusi!
- 🚀 Engagement naik! Karena audiens udah familiar dan tahu apa yang bakal mereka dapetin dari kontenmu.

**Loyal Audience** — *Followers banyak ≠ personal branding kuat. Yang lebih penting adalah membangun komunitas loyal yang engaged dengan kontenmu.*
- ✅ Engage dengan audiens → balas komentar, DM, atau ajak diskusi
- ✅ Kasih value secara konsisten → orang akan terus follow kalau merasa mendapat manfaat
- ✅ Buat komunitas kecil → bisa lewat grup Telegram, Discord, atau membership
- 🚫 Kesalahan yang harus dihindari: fokus ke angka followers tapi engagement rendah · gak bikin komunitas
- Extra tips: **1. Jadi "Temen" Buat Audiens · 2. Autentik, Jangan Jadi "Karakter" · 3. Share kehidupan non branding · 4. Pahami Mereka, Jangan Asal Konten**

**Personal Brand Crisis** — *Di dunia digital, kesalahan atau kritik bisa muncul kapan aja. Cara menanganinya akan menentukan apakah personal branding-mu akan tetap bertahan atau malah runtuh.*
- ✅ Jangan defensif atau kabur → kalau ada kesalahan, akui dan tunjukkan solusi
- ✅ Tanggapi dengan profesional → jangan emosional dalam menanggapi kritik
- ✅ Gunakan kritik sebagai evaluasi → kalau bisa, jadikan bahan refleksi untuk memperkuat branding-mu

**Unrelevan = Rebranding dengan Strategi** — *Kadang, personal branding perlu berkembang atau berubah arah. Tapi kalau dilakukan tanpa strategi, bisa bikin audiens bingung atau bahkan kehilangan engagement.*
- ✅ Sisipin topik baru pelan-pelan → awalnya masih bahas editing, tapi mulai masuk ke personal branding
- ✅ Manfaatin skill lama → masih pakai editing buat bikin konten personal branding yang powerful
- ✅ Bangun kredibilitas di bidang baru → aktif sharing insight lewat konten, webinar, dan komunitas
- ✅ Konsisten & kuatkan narasi → semua platform disesuaikan dengan branding baru tanpa kehilangan audiens lama
- Contoh: *dulu fokus di self-development, sekarang mau masuk ke bisnis coaching* → bisa mulai dengan konten *"Self-development dalam Bisnis."* / *dulu bikin konten meme, sekarang mau lebih edukatif* → bisa mulai dengan *"Belajar dari Meme."*
- 🚫 Kesalahan yang harus dihindari: berubah terlalu drastis tanpa persiapan (audiens kaget dan mungkin unfollow) · menghapus branding lama secara tiba-tiba (bisa kehilangan trust dari komunitas yang sudah ada)

> **Conclusion: Survive personal branding bukan soal viral doang, tapi soal relevan, adaptif, dan tetap kasih value ke audiens.**

#### 10.3 Why people are not consistent

> **Kamu Gagal, karena kamu gak konsisten dan gak fokus.**
> - Konsistensi = Kredibilitas → orang percaya karena kita terus muncul dengan pesan yang sama
> - Algoritma juga suka yang konsisten → semakin sering muncul, semakin dikenal
> - Tanpa konsistensi, kita jadi "random" → orang gak tahu kita sebenarnya siapa dan apa yang kita tawarkan

**Faktor Kenapa Orang Gak Konsisten:**
- **Niru Orang Lain** → akhirnya kehilangan identitas sendiri, jadi capek dan bosen sendiri
- **Overclaim & Overpromising** → janji besar tapi gak bisa deliver, akhirnya malu sendiri
- **Perfeksionisme** → pengen konten sempurna terus, malah jadi gak pernah posting
- **Gak Punya Nilai yang Jelas** → branding-nya abu-abu, gak ada benang merah
- **Kemakan Motivasi** → semangat di awal tanpa komitmen buat berjuang

**Motivasi VS Konsistensi** — drawn as two graphs: motivation is tall spikes decaying to zero; consistency is a flat row of small even bumps that never stops.
> *Motivasi bagus untuk triggering dan mulai, tapi jangan ke makan motivasi terus, harus bisa komit.*

**Konsisten Personal Branding** splits into two halves:

| Mindset & Value | Content & Technical |
|---|---|
| Punya Ikigai — *"Si Paling public speaking"*, *"Si Paling Matematika"* | Tentukan format konten yang bisa kamu jalani (long form vs short form, tulisan vs video) |
| Punya SWOT - Premis | Buat sistem biar gak burnout → misal, jadwal posting yang realistis |
| Punya komitmen | |

Two more failure reasons the author confesses to from his own 4 lost years:
- **niru orang lain** — *yang ditiru ✅ / Peniru ❌*
- **alat harus proper dan hasil bagus** — *kalau jelek gak di-post. Padahal bagus itu subjektif.* (Illustrated with Avengers vs Barbie posters.) *Gas aja terus berproses, pelan-pelan dari jelek jadi ketemu titik bagusnya.*

#### 10.4 Kritik, and Grit

> **JANGAN SOK PINTER, terima kritik!** *Alasan 4 tahun aku gak growth, aku anti kritik.*
> **Kritik itu bahan bakar, bukan penghambat.** Ada 3 jenis kritik:
> - **Kritik membangun** → bisa jadi insight buat improve
> - **Kritik asal-asalan** → gak relevan, bisa di-skip
> - **Hate comment** → tanda bahwa kamu mulai dikenal (good sign!)
>
> **Cara mental kuat: Fokus ke yang bisa dikontrol.**

> **Grit: Kunci Kuat Naik Turunnya Personal Branding.**
> - **Grit = passion + komitmen action** → branding yang sukses butuh waktu
> - Bukan yang paling berbakat yang menang, **tapi yang paling tahan banting**
> - **Evaluasi terus** → lihat progress dalam **6 bulan**, bukan cuma dalam **1 minggu**

#### 10.5 Marathon, not Sprint

The chapter's closing metaphor, drawn as marathon runner vs sprinter:

| Marathon ✅ | Sprint ❌ |
|---|---|
| Butuh napas panjang | Ga bertahan lama |
| Strategi jangka panjang | Ga termotivasi |
| Konsisten | Cari viral aja |
| Sabar | Stamina cepat habis |
| Pelan tapi pasti | Proses instant |
| Percaya proses | Capek |
| Bukan sekali hajar kemudian selesai | Sekali hajar |

> - Hasil ga langsung kelihatan, butuh perjalanan panjang
> - Konsisten adalah kunci terus berjalan dan maju
> - Adaptasi adalah cara untuk ga cepat capek dan selalu termotivasi
> - **Investasi waktu dan ilmu. Ga bisa instant, nikmatin prosesnya. Jadikan perjalanan untuk semakin kuat, berkembang dan relevan.**
> - **Personal branding it's a process not a destination.**

The mountain-photo slide makes it personal: *ngerasa paling jago · awalnya ada di barisan paling depan malah tertinggal paling belakang · lari pengen cepat puncak · ngga nikmatin perjalanan · capek dan akhirnya diem ditempat · di dahuluin sama temen yang santai jalan nikmatin prosesnya.*

#### 10.6 Capek bikin konten / burnout

From the ebook. **Jadwal kerja yang seimbang** (tentukan jam kerja, pakai Pomodoro) · **Delegasi dan kolaborasi** (the author now has an editor and a social team) · **Self-care dan relaksasi** · **Cari dukungan** (mentor, komunitas kreator).

> *"Konsistensi adalah bentuk kesetiaan kita kepada diri kita sendiri dan tujuan kita."* — Kadafi Devayana

---

### 11. Chapter 4 — Evaluation

Three questions, asked in this order:

> **001 — Bagaimana orang lain mengenal kita?**
> **002 — Apakah personal branding kita sudah sesuai dengan tujuan?**
> **003 — Apa penyebab personal branding kita belum optimal?**

#### 11.1 Bagaimana Orang Lain Mengenal Kamu?

**Langkah Evaluasi:** tanyakan kepada orang-orang di sekitar kamu → *"Apa yang paling melekat dari diri saya?"*

> **Konsistensi** dalam menyampaikan pesan adalah kunci agar orang lain mengenali kamu sesuai dengan branding yang kamu inginkan.

💡 **Tantangan buat kamu:** *Coba tanyakan ke 5 orang di sekitar kamu, apa yang paling melekat dari diri kamu? Apakah jawaban mereka sesuai dengan branding yang ingin kamu bangun?*

The salt-and-sugar illustration makes the point: sugar and salt look identical in a pile. What you *intend* to be and what people *taste* are different things until you check.

#### 11.2 Apakah Sesuai dengan Tujuan?

**Case study:** seorang desainer UI/UX ingin membangun branding sebagai expert di bidangnya. Namun, setelah 6 bulan aktif di media sosial, ia lebih dikenal sebagai motivator karena sering berbagi tips mindset.
**Solusi:** ia perlu lebih banyak berbagi case study, pengalaman profesional, dan tips UI/UX agar brandingnya lebih sesuai dengan target.

#### 11.3 Apa Penyebab Belum Optimal?

| Penyebab | Diagnostic questions | Solusi |
|---|---|---|
| **WHY-nya tidak kuat** | Apakah kamu benar-benar tahu alasan di balik personal branding yang sedang dibangun? Jika kamu tidak yakin dengan "WHY" kamu, maka branding yang kamu bangun bisa terasa kosong dan kurang autentik. | kembali ke §5 |
| **Pesan yang kamu sampaikan tidak konsisten** | Apakah topik yang kamu bahas sering berubah-ubah? Apakah tone dan gaya komunikasi kamu seragam di semua platform? | **Pastikan ada benang merah dalam setiap konten yang kamu buat. Fokus pada 1-3 tema utama agar audiens mudah mengingat branding kamu.** |
| **Opportunity Mapping kurang optimal** | Apakah kamu sudah memanfaatkan semua peluang yang tersedia? Apakah kamu sudah aktif networking dan membangun koneksi dengan orang-orang di industri yang relevan? | **Buat daftar komunitas, event, dan platform yang bisa membantu kamu mendapatkan lebih banyak exposure dan kesempatan berkolaborasi.** |

---

### 12. Chapter 5 — Expand & Monetize

#### 12.1 Knowledge Gap / Information Gap

Two names for the same idea, both used in the material.

> **Knowledge Gap: apa yang KAMU TAU tapi ORANG LAIN GAK TAU.**
> Drawn as a chasm: `Orang gak tau` ——[ **Ilmu kamu** = the bridge ]—— `🏆`

Ebook version: *Information Gap adalah ketidakcocokan antara apa yang seseorang tahu dan apa yang mereka ingin tahu. Sebagai konten kreator, tugas kita adalah mengisi celah ini.*

**Why it matters:** Menarik Perhatian · Menjaga Ketertarikan · Membangun Kepercayaan. And: memberikan nilai tambah · membangun kepercayaan dan kredibilitas · menghasilkan pendapatan sesuai Ikigai.

**Cari Knowledge Gap Kamu — gimana caranya?** Four methods:

| Method | How |
|---|---|
| **Data analytics** | Google Trends. Pakai data dari insights media sosial, Google Trends, atau survei. Cari topik yang sering dicari tapi minim jawaban yang jelas. |
| **People Problem** | Dengerin pertanyaan dan masalah yang sering dihadapi orang-orang di industri kamu. Cek komentar, DM, atau forum diskusi terkait niche kamu. |
| **Competitor Benchmark** | Analisis kompetitor: Apa yang mereka bahas dan apa yang belum mereka bahas? Cari celah yang bisa kamu isi dengan perspektif unikmu. |
| **Self Experience** | Curahkan pengalaman pribadi sebagai insight. Apa yang dulu kamu bingungin dan akhirnya kamu berhasil pecahkan? |

**Worked case:** *"Aku jago ngedit, tapi banyak orang ga bisa ngedit dan pengen jago editing. Itu knowledge gap! Aku bisa isi gap itu dengan:* ✅ Ngajarin editing lewat konten gratis (kuncinya aja, orang penasaran) ✅ Bikin workshop atau kelas berbayar ✅ Jual preset, template, atau jasa editing (freelance).*
> ✨ **Intinya: Carilah kebutuhan pasar yang bisa kita isi dengan keahlian kita!**

**Ebook case studies:** the author's own *"Modal kopi 30 ribu jadi 12 Juta"* (Content Creator Blueprint, written in 2 hours, Rp12 juta in month one, settling to Rp4-8 juta/month after; 100% margin) and Timothy Ronald / Akademi Crypto (150+ modules, premium subscription up to Rp17 juta).

#### 12.2 The five monetisation doors

`Monetize → Product (Physical/Digital) · Speaker · Partnership/Collaboration · Mentorship · Affiliate`

| Door | How to Start |
|---|---|
| **Speaker** | ✅ Bangun Kredibilitas (Ngonten + Post foto lagi speaker) ✅ Buat Portofolio Speaker (Gratis dulu aja!) ✅ Benchmark orang lain buat tau rate kamu.<br>*Rate cited: 1× jadi public speaker = 1-2× UMR Jakarta / 3-6× UMR Jogja, 45-90 menit, 4-8 kali per bulan.* |
| **Partnership / Collaboration** | ✅ Bangun kredibilitas & engagement audiens ✅ Buat media kit & rate card ✅ Terima dan pitching ke brand yang relevan ✅ Tampilkan hasil kerja sama di portofolio |
| **Digital Product** | ✅ Personal Branding ✅ Pilih produk (ebook, template, course) ✅ Buat produk menarik (Design, Editing dll) ✅ Pakai platform ✅ Digital marketing.<br>*Lifetime sales shown: IDR 78,401,429* |
| **Mentorship** | ✅ Bangun kredibilitas dengan personal branding ✅ Tentuin spesialisasi & target mentee ✅ Benchmark rate mentoring ✅ Gunakan testimoni buat bangun kepercayaan ✅ Pakai platform yang pas (Zoom, Google Meet) |
| **Affiliate** | ✅ Pilih program afiliasi yang sesuai ✅ Daftar & dapatkan link afiliasi ✅ Buat konten review atau tutorial ✅ Gunakan CTA biar ada yang beli |

The Entrepreneur tree gives a second cut of the same thing: `Monetisasi (Community Building, Mentoring & Consulting, Speaker/Praktisi, Menjual produk F&B/fashion) · Digital Product (e-book, kelas online/webinar, template & framework businessplan) · Kolaborasi (collab bareng brand/influencer/sesama entrepreneur, joint venture/proyek bersama) · Networking (Komunitas Bisnis, Relasi ke Investor)`.

#### 12.3 Digital Products — the 4-step build

> **Karena Digital Product = Easy Money.** Cek portfolio Dafi · Belum lama coba tapi hasilnya lumayan · Side income, low effort maintenance.

```
   1. Idea  →  2. Create the Product   |   3. Funnel  →  4. Scale Up!
   └──── Creating ────┘                    └──── Selling ────┘
```

**Digital vs Physical** (the slide's comparison table): Modal Awal (murah, cukup skill & laptop / mahal, perlu bahan baku, stok, gudang) · Biaya Produksi (sekali bikin, bisa dijual terus / tiap unit harus diproduksi lagi) · Penyimpanan (cukup cloud / harus ada gudang) · Pengiriman (instan, cuma butuh link download / perlu ongkir, packing, bisa kena delay) · Skalabilitas (bisa dijual ke ribuan orang tanpa ribet / terbatas stok & kapasitas produksi) · Keuntungan (100% masuk kantong setelah modal tertutup / harus hitung biaya produksi per unit) · Maintenance (bisa update kapan aja / harus siap retur, garansi, barang rusak) · Keunikan (bisa custom banget, lebih fleksibel / harus bersaing sama banyak produk serupa) · Risiko (minim, nggak ada stok mati / bisa rugi kalau barang nggak laku atau rusak).

**1. Idea & Research**
1. **Fokus ke Ikigai Diri Sendiri** → manfaatin skill kamu: kalau jago copywriting, bisa bikin e-book atau kursus online
2. **Cari Masalah yang Sering Dihadapi Orang** → produk digital yang laris biasanya solusi dari masalah nyata. Contoh: banyak orang pengen jago desain tapi nggak bisa pakai Photoshop? Solusinya: jual template Canva!
3. **Lihat Tren di Pasar** → cek media sosial, forum, atau marketplace buat lihat apa yang lagi tren. Misalnya, AI tools lagi booming, mungkin bisa bikin panduan atau template terkait AI
4. **Kompetitor Benchmarking** → coba buat lebih baik sesuai dengan persona, ilmu dan pengalaman kamu. **(GAK BOLEH PLAGIAT!)**
5. **Refleksi dari Pengalaman Pribadi** → kadang pengalaman sendiri bisa jadi ide. Contoh: pernah sukses dapat klien dari LinkedIn, bisa bikin panduan cara optimasi LinkedIn buat freelance
> **Notes:** Jangan pernah plagiat apalagi mencuri, coba buat dari 0, kepercayaan dan kredibilitas harganya lebih mahal dari apapun.
> Tools shown: Google Trends · Threads · Etsy · Lynk · Amazon · Tribeversity

**2. Create the Product** (formats: Sheets · Canva · PDF · MP4)

| Contoh Ide | Step-step |
|---|---|
| eBook Content Creating | 1. Apa aja yang bakal dibahas dicatet di docs (buat outline-nya) 2. Isi sesuai teori, ilmu dan pengalaman kita (bisa minta bantu AI untuk brainstorming bareng) 3. Finalisasi desain di Canva |
| Template Personal Branding Builder | 1. Buat outline 2. Buat sheets dan rumusnya 3. Publikasi lewat platform |
| Template Media kit & Rate Card | 1. Buat outline 2. Buat design-nya 3. Share template link |
| Kelas Personal Branding | 1. Bikin webinar (Poster, Content Marketing, Grup WA) 2. Jual Recordnya (buat yang belum ikutan) |

**3. Funnel** — ToFu / MoFu / BoFu
- **Awareness** (ToFu): *Wildest audience, most general, least ready to convert* → Personal branding, Konten, Bikin/oleh community, dll
- **Consideration stage** (MoFu): *Targeted audience, may already be a lead* → Free sample, Free Webinar, Testimoni, Product Knowledge
- **Decision stage** (BoFu): *Narrow audience, interested or ready to buy* → Garansi, Diskon terbatas, Limited Edition
- Flow: `TikTok/LinkedIn/Threads/YouTube/Instagram/WhatsApp → Bikin konten, cari pasar dan audiencenya → Masuk ke platform (Amazon/Lynk/Etsy/m·caas) → Kasih Call to Action!`

**4. Scale Up!**
- 🚀 **Optimasi yang sudah ada** – perbaiki yang bisa ditingkatkan
- 🚀 **Tambah produk/bundling** – bikin pelanggan beli lebih banyak
- 🚀 **Ekspansi ke platform & market baru** – jangkau audiens lebih luas
- 🚀 **Automasi, Affiliate & delegasi** – supaya bisa fokus ke strategi besar
- 🚀 **Bangun brand yang kuat** – supaya bisnis sustainable jangka panjang

---

### 13. Networking, collaboration, and LinkedIn

#### 13.1 PING Framework

> **Personal Branding = Akar Networking.**

```
        ┌── 1. Personal Branding        ← the root
PING ───┼── 2. Interpersonal Communication
        ├── 3. Networking
        └── 4. Generating Value
```

**1. Personal Branding** is the root — the POV slides prove it: the same DM lands differently depending on whether the sender's profile shows `1 post / 181 followers` or a built profile. *POV Business Owner: "bro, kantor gue butuh orang, ngopi yok."* / *POV Organization Management: "mas, aku butuh kamu ngisi salah satu divisi di organisasiku, aku liat kamu capable."* The Before/After slide pairs a long formal cold WhatsApp application against an unsolicited LinkedIn recommendation from a recruiter.

**2. Interpersonal Communication = Memasak** 🍳

| Cooking | Communication |
|---|---|
| **Bahan** = Pesan yang Akan Disampaikan | sebelum memasak, kita harus memilih bahan yang tepat agar makanan enak → kita harus memilih kata-kata, nada, dan ekspresi yang sesuai agar pesan tersampaikan dengan baik |
| **Resep** = Struktur & Cara Menyampaikan Pesan | resep membantu kita mengolah bahan dengan urutan yang benar → struktur pesan harus jelas, pembukaan, isi, dan kesimpulan, agar mudah dipahami lawan bicara |
| **Teknik Memasak** = Gaya Komunikasi | menggoreng, merebus, atau memanggang? → nada suara, bahasa tubuh, dan ekspresi memengaruhi makna pesan yang diterima |
| **Rasa & Bumbu** = Emosi & Empati | kurang garam? terlalu pedas? → perlu keseimbangan agar makanan enak. Dalam komunikasi, kita harus memahami emosi lawan bicara dan menyesuaikan pendekatan agar percakapan berjalan baik |
| **Penyajian** = Cara Menyampaikan Pesan | makanan yang enak tapi disajikan asal-asalan bisa membuat orang enggan mencobanya → bahasa tubuh, dan konteks memengaruhi bagaimana pesan diterima |
| **Umpan Balik** = Respon dari Lawan Bicara | jika orang yang makan memberi respons, kita tahu apakah masakan itu enak atau perlu diperbaiki → kita harus mendengarkan tanggapan lawan bicara dan menyesuaikan pendekatan agar lebih efektif |

**3. Networking — Strategic Networking Framework**, a triangle:
- **Analyze (Analisis)** — mengidentifikasi kebutuhan ("Needs") dan sumber daya yang dimiliki ("Haves")
- **Plan (Perencanaan)** — menyusun portofolio hubungan yang berharga dan menentukan strategi dalam membangun jaringan. Fokus pada hubungan yang bernilai tinggi memungkinkan efektivitas dalam mencapai tujuan jangka panjang. *(Relationship Portfolio)*
- **Network (Jaringan)** — mencari dan bertukar informasi, melakukan analisis kontak serta hubungan yang ada. Proses ini memungkinkan seseorang atau organisasi untuk memperluas akses ke informasi dan sumber daya yang relevan. *(Search & exchange, Contact & relationship analytics)*

**4. Generating Value** 💯 — *bukan hanya sekadar membangun jaringan dan memperkenalkan brand, tetapi juga memberikan manfaat nyata kepada orang lain:*
- **Sharing Sumber Daya** (informasi, ilmu, koneksi)
- **Improve Diri** (membangun keterampilan agar dapat memberikan kontribusi lebih besar)
- **Giving Back** (gak cuma nerima manfaat dari orang, tetapi juga memberikan sesuatu kembali)
- **Pahami Kebutuhan dan Solusi** (tanya lebih dalam tentang tantangan bisnis rekan kerja, dan menawarkan solusi yang relevan)

#### 13.2 Kolaborasi = Supply & Demand matching

> Setiap orang punya **"supply"** (keahlian, skill, atau sumber daya) dan **"demand"** (kebutuhan, masalah yang ingin diselesaikan).

- **Kolaborasi** — A's Supply meets B's Demand, and back
- **Matching** — the two sides line up
- **Menaikkan Visibilitas** — *Personal Branding* raises your Supply above everyone else's identical Supply
> 🚀 **Jadi, personal branding meningkatkan visibilitas "supply" kita, sehingga lebih mudah ditemukan oleh orang yang memiliki "demand" yang cocok!**

#### 13.3 LinkedIn specifics

Included for completeness; only §13.3's STAR caption rule matters for video scripts.

**Follow vs Connect**

| | Connect | Follow |
|---|---|---|
| Hubungan | Terhubung dua arah | Satu arah (cuma yang follow) |
| Konten | Saling melihat postingan | Hanya melihat postingan yang difollow |
| Interaksi | Bisa DM langsung | Tidak bisa DM (kecuali lewat InMail) |
| Tujuan | Membangun koneksi | Mengonsumsi konten tanpa terhubung |

**Networking Circle** — three rings:
- **Inner Circle – "Orang Terdekat"**: teman kuliah atau kerja, dosen pembimbing, rekan organisasi, koneksi dari acara networking. *Connect langsung karena mereka adalah jaringan awal kita. Bisa mulai membangun engagement seperti berbagi insight atau mendiskusikan topik yang relevan.*
- **Middle Circle – "Jembatan Karier"**: alumni kampus yang bekerja di industri yang kita incar, rekruter atau HR dari perusahaan target, mentor atau senior dari komunitas profesional, orang yang pernah berbagi pengalaman terkait bidang yang kita minati. *Connect jika memungkinkan, atau Follow jika belum ada interaksi. Berikan engagement dengan komentar atau reaksi pada postingan mereka untuk membangun koneksi. Bisa DM mereka jika ada ketertarikan atau pertanyaan terkait karier.*
- **Outer Circle – "Sumber Inspirasi & Insight"**: thought leaders di industri tertentu, C-level executives dari perusahaan yang kita minati, influencer LinkedIn yang sering berbagi insight bermanfaat, profesional yang sering membagikan pengalaman atau tips di bidangnya. *Follow mereka untuk mendapatkan insight berharga. Terlibat di kolom komentar untuk meningkatkan visibility di komunitas mereka. Jika ada kesempatan, DM dengan pendekatan profesional untuk membangun hubungan lebih lanjut.*

**Funnel 3C** — `Connect (Bangun Koneksi yang Tepat) → Converse (Mulai & Jaga Interaksi) → Cultivate (Jaga & Perkuat Relasi)`

- **Connect:** follow & connect dengan orang yang relevan (sesuai bidang, industri, atau interest) · kirim personalized connection request, jangan hanya klik "Connect" · gunakan Networking Circle Model
- **Converse:** aktif berkomentar di postingan orang lain dengan opini yang bernilai · kirim pesan follow-up setelah connect, jangan hanya diam · gunakan metode **"Give First"** → berikan insight atau bantuan sebelum meminta sesuatu
- **Cultivate:** bangun hubungan jangka panjang dengan check-in berkala (tanya kabar, diskusi ringan) · berikan dukungan dalam bentuk engagement (like, comment, share postingan mereka) · undang ke diskusi atau ajak kolaborasi kecil

> **Kunci DM LinkedIn yang Efektif:** Jangan terkesan template & formal banget. Singkat, relevan, dan kasih alasan jelas kenapa mau connect. Lebih baik kasih nilai dulu (apresiasi, insight) sebelum minta sesuatu. **Ajak ngobrol, bukan wawancara!**

**LinkedIn algorithm:** `Posting Konten/Berinteraksi → Engagement Awal (Like, Comment, Repost) → Algoritma Menilai Kualitas Interaksi → Jika Engagement Tinggi → Muncul di Second-Degree Connection → Semakin Banyak Interaksi → Semakin Luas Jangkauan`
- ✅ **Engagement Awal itu Kunci!** Dalam 1-2 jam pertama setelah posting, usahakan ada like dan komentar. Balas setiap komentar untuk memperpanjang umur post di feed orang lain.
- ✅ **Jadilah Aktif, Bukan Pasif**
- ✅ **Ajak Audience Berdiskusi** — post yang mengajukan pertanyaan atau meminta pendapat lebih banyak mendapatkan engagement. LinkedIn memprioritaskan konten yang menciptakan diskusi dibanding sekadar informasi satu arah.

**Profile mechanics:** Headline = 220 characters (crosscheck: Background Pendidikan/Pekerjaan · Pengalaman Magang · Aspirasi Karir/Tujuan Karir · Highlight Prestasi/skill dan sertifikasi). Summary = 2600 characters (crosscheck: Field of Interest · Key highlight · Call to Action · Top Skills). URL: shorten it — `linkedin.com/in/m-arif-maliki123/` ❌ → `linkedin.com/in/arifmaliki/` ✅. Banner: use one. Enable **Top Skills**, collect **Endorsements**, ask for and give **Recommendations**, fill **Featured** with achievements. **Caption = STAR Methods** (§2.5). Experience description = Definition + Key highlight + Skills and Documentation.

<!-- journal: LinkedIn section is included because the user asked for complete coverage of the folder, but it is out of scope for a video-editing skill. If this file ever needs trimming, cut §13.3 first and move it to its own reference. The STAR caption rule and the PING framework should stay. -->

---

### 14. How SpliceCraft uses all of this

A mapping so the agent knows which framework to reach for at which moment.

| When the user says | Reach for | Why |
|---|---|---|
| "bikinin script" and cannot say who it is for | §6.1-6.2 superniche, §6.6 4K Method | a script without a specific *siapa* is the #1 source of AI-ish copy |
| "kontenku sepi" | §6.3 algorithm, §10.3 consistency, §6.4 80/15/5 | usually a focus problem, not an editing problem |
| "aku gak pede" / "takut dibilang pamer" | §3 Perception/Persona, §3.1 Circle of Control, §4 | the block is emotional; do not answer it with editing tips |
| "gak tau mau bikin konten apa" | §2.4 Premis → §8.2 Pillar → `kadev-script-formulas.md` Unlimited Idea | premis + pillar generates the queue |
| "mau jualan / monetisasi" | §12.1 Knowledge Gap, §12.2 five doors, §12.3 funnel | pick the door first, then write to that funnel stage |
| "hasilnya masih AI banget" | §2.4 premis missing, §9.3 production errors, `anti-ai-ish.md` | almost always: no premis, no personal story, over-editing |
| "mau ganti niche" | §6.10 bridge | never cut over abruptly |
| "udah 2 minggu gak ada hasil" | §10.4 Grit (evaluate at 6 months), §10.5 Marathon | reset the time horizon |

---

### 15. Quote bank

For CTA lines, closing cards, and callbacks. All by Kadafi Devayana unless noted. **Attribute them** if you put them on screen.

- *"Konsistensi adalah bentuk kesetiaan kita kepada diri kita sendiri dan tujuan kita."*
- *"Jadi dirimu sendiri, karena tidak ada orang lain yang bisa melakukannya lebih baik darimu."*
- *"Kisah hidupmu adalah seni yang tak ternilai. Lukislah dengan bangga, dan biarkan dunia menikmati keindahannya."*
- *"Mimpi ga bisa jadi kenyataan kalau kerjaan kamu cuma rebahan doang. Bangun, Planning dan Action!"*
- *"Kegagalan adalah guru terbaik untuk kita belajar."*
- *"Aku tidak menyesal sudah gagal di langkah atau percobaan pertamaku, karena kalau tidak dari langkah pertama itu, aku tidak akan ada di titik sekarang."*
- *"Ikigai bikin kamu tahu nilai kamu, personal branding bikin nilai itu bersinar di depan dunia."*
- *"Personal branding itu jadi diri sendiri bukan jadi orang lain."*
- *"Personal branding bukan hanya tentang menjadi terlihat, tetapi juga tentang menjadi diingat."*
- *"Belajar bukan tentang siapa yang paling cepat, tapi siapa yang paling konsisten!"*
- *"Personal branding it's a process not a destination."*
- *"Done is better than perfect."*
- *"Peluang dan kesempatan akan datang kepada orang yang siap dan terlihat siap."*
- *"Be yourself; everyone else is already taken."* — Oscar Wilde
- *"Menjadi diri sendiri adalah kunci untuk bisa berkarya dengan hati."* — Maudy Ayunda

---

### Provenance

| Source | What came from it |
|---|---|
| 64 slide screens, `E:\Download\SLIDE PPT KADEV` | §0, §2.4 (Premis/PMF), §6.2-6.7 (superniche, 80/15/5, Perfect Niche, 4K, Sweet Spot), §7, §8, §9, §10, §11, §12, §13 — the majority of this file |
| `02 - Personal Branding Mengubahmu eBook.pdf` (100 pp) | §1.3, §2.1-2.2, §2.5, §3, §6.8-6.9, §8.3, §10.6 |
| `04 - Content Creator Strategy.pdf` (53 pp) | §5.1-5.2, §6.8, §8.4 (Hirarki Konten), Idea Framework (in `kadev-script-formulas.md`) |
| `06 - Content Creator Blueprint.pdf` (8 pp) | §6.8, §10.6, audience/competitor analysis |
| `03 - Content Cheat (Hook Writing).pdf` (9 pp) | all 20 hooks → `kadev-script-formulas.md` |
| 37 lesson video filenames | §0 chapter ordering and topic list |

**Not extracted:** the lesson videos' spoken content. No transcription backend was available in this session (`GROQ_API_KEY` unset, `faster-whisper` not installed), so the videos contributed their titles and ordering only. The slides and PDFs are the author's own written version of the same lessons, and the slide deck is the more complete of the two — but **if a future session gets a transcription key, re-run over `E:\Download\kadev academy\*.mp4` and reconcile.** Two live-mentoring recordings in that folder (`22 Juli 2026 — Topik Format Winning`, `27 Agustus 2026 — Formula Script Viral & Jualan`) are the highest-value un-mined assets.

---

# Part 4. kadev-script-formulas.md

## Script formulas: hooks, structure, and idea generation (Kadev method)

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Source:** `03 - Content Cheat (Hook Writing).pdf`, `04 - Content Creator Strategy.pdf`, `02 - Personal Branding Mengubahmu eBook.pdf`, and the *Viral-Writing* / *Content-Writing* / *Bikin Orang Gak Bisa Move On* slide chapters. Extracted 2026-09-23.
> **Editable:** `<!-- journal -->` comments mark provenance and known gaps. See `../JOURNAL.md`.

This is the execution layer. The theory it depends on is in `kadev-personal-branding.md` — especially **Premis** (§2.4), **superniche** (§6.2), and the **4K Method** (§6.6). The quality gate that rejects the output is `anti-ai-ish.md`.

Language note: everything here is written for **Indonesian-language scripts**. The phrasing is deliberately casual-Indonesian (*gue/aku*, *banget*, *nih*, *deh*) because that is the register of the source material and of the market. Do not translate the templates into formal Indonesian — that alone makes a script read as machine-written. For English scripts use `script-and-marketing.md` instead.

---

### 1. The structure question, settled

The slides are explicit about this, and it is the single most important correction in the whole file:

> **"Masih ada yang nulis konten pake struktur ini?"**
> Hook → Body → Call to Action (CTA) ❌
> **"Jangan gunakan ini doang, tapi…"**

Hook/Body/CTA is not *wrong*. It is not *enough*. It is a skeleton with no meat, and a skeleton is exactly what an LLM produces when you ask it for a script. The Kadev method layers two things on top:

```
        ┌─────────────────────────────────────────┐
        │  Hook  →  Body  →  CTA                  │   the skeleton (necessary)
        └─────────────────────────────────────────┘
                          +
        ┌─────────────────────────────────────────┐
        │  6 Script Hack Elements                 │   what must be PRESENT
        └─────────────────────────────────────────┘
                          +
        ┌─────────────────────────────────────────┐
        │  Storytelling Hack (5 beats)            │   what ORDER it moves in
        └─────────────────────────────────────────┘
```

A script that has all three is hard to tell from a human's. A script with only the first is the thing the community has been complaining about.

---

### 2. The 6 Script Hack Elements

From the *Viral-Writing* slide. These are **elements**, not steps — they can appear in any order, but a viral-shaped script has all six.

| # | Element | What it is | Kadev's own example line |
|---|---|---|---|
| 1 | **Pain Point** | the specific frustration of a specific person | *"Anak desa tanpa privilege tapi pengen sukses"* |
| 2 | **Spesific Number** | a real, odd, countable number — not "beberapa" | *"3 Cara untuk melawan keterbatasan"* |
| 3 | **Promise of transformation** | who they become, not what they learn | *"Aku yakin kamu juga bisa berubah!"* |
| 4 | **Urgency Action** | the thing to do now | *"Kamu juga harus lakukan…"* |
| 5 | **Personal Opinion / Story** | your take or your scar — the uncopyable part | *(cerita pribadi)* |
| 6 | **Interactions** | a reason to type something | *"Komen 'siap' buat kamu yang siap untuk berubah!"* |

#### 2.1 Why these six, specifically

Each one blocks a distinct failure:

| Element | Failure it prevents |
|---|---|
| Pain Point | writing to "everyone" — see superniche, `kadev-personal-branding.md` §6.2 |
| Spesific Number | vagueness; also gives the SpliceCraft planner a count-up card to animate |
| Promise of transformation | a video that informs but does not move anyone |
| Urgency Action | a video people enjoy and then do nothing about |
| **Personal Opinion / Story** | **AI-ish flatness — this is the element LLMs cannot fake, because they have no scar** |
| Interactions | dead comments, which the algorithm reads as low value |

Element 5 is the load-bearing one. **A script missing element 5 is the definition of AI-ish.** If the user cannot supply a real story, do not invent one — stop and ask. That is a hard rule in `SKILL.md`.

<!-- journal: the six elements are transcribed exactly as the slide labels them, including the spelling "Spesific Number" (sic — the slide misspells "Specific"). I kept the slide's spelling in the table header for traceability but use correct English in prose. The example lines come from the companion slide "Bikin Konten Tulisan!" which maps each icon to a sample line. -->

---

### 3. The Storytelling Hack (5 beats)

From the slide *"Bikin Orang Gak Bisa Move On karena Ceritamu!"*. The stated purpose:

> **Ceritakan kisah hidupmu yang kamu rasa biasa aja, jadi suatu hal menarik dan menginspirasi.**

That sentence is the whole thesis. The user does not need a dramatic life. They need a structure.

```
  ①────────►②────────►③────────►④────────►⑤
Set the   Highlight   The       Success    Wrap It Up
Scene     the        Lesson    Follow-Up   with a Relatable
(Bangun   Struggle   (Pelajaran (Pencapaian Message
Konteks)  (Tunjukkan  dari      Setelah    (Motivasi dan
          Kegagalan)  Gagal)    Gagal)     pertanyaan)
```

| Beat | Job | Test |
|---|---|---|
| **1. Set the Scene** | build the context: where you were, who you were | Can a stranger picture it in one sentence? |
| **2. Highlight the Struggle** | show the failure, plainly | Is there an actual bad thing, or just "it was hard"? |
| **3. The Lesson** | what the failure taught — this is the value payload | Would this help someone who has not failed yet? |
| **4. Success Follow-Up** | what happened after | Is it proportionate? Not "and now I'm a millionaire" |
| **5. Wrap It Up** | a relatable message + a question | Does the last line loop back to beat 1? |

#### 3.1 A complete worked example

From the slides, a networking-topic script built on the 5 beats. This is the shape to imitate:

| Beat | Line |
|---|---|
| ① Set the Scene | *"Networking itu gila, bisa bikin kita sukses dan kaya raya"* |
| ② Highlight the Struggle | *"kadang orang bingung gimana cara networking, ini dia 5 cara kita bisa kenal sama orang sukses biar kita juga ikut sukses."* |
| ③ The Lesson | *1. Personal branding · 2. Interpersonal communication skill · 3. … · 4. … · 5. …* |
| ④ Success Follow-Up | *"dari networking akhirnya bisa sukses dan punya kesempatan"* |
| ⑤ Wrap It Up | *"networking bukan seberapa banyak orang yang kamu kenal, tapi seberapa banyak orang yang pengen kenal kamu."* |

Note what beat ⑤ does: it is a **reversal of beat ①**. Beat 1 said networking makes you rich; beat 5 redefines what networking even is. That reversal is why the video loops.

#### 3.2 Merging the two frameworks

The elements map onto the beats naturally. This is the template to actually write against:

| Beat | Elements that live here | Typical seconds (45 s video) |
|---|---|---|
| ① Set the Scene | **Pain Point** | 0-5 |
| ② Highlight the Struggle | **Personal Story**, **Spesific Number** (announce the count) | 5-14 |
| ③ The Lesson | the numbered list itself, **Personal Opinion** | 14-32 |
| ④ Success Follow-Up | **Promise of transformation** | 32-38 |
| ⑤ Wrap It Up | **Urgency Action** + **Interactions** | 38-45 |

<!-- journal: the beat→element mapping and the second-column timings are MY synthesis, not printed on any slide. The two frameworks appear on adjacent slides and are clearly meant to be used together (one slide, "Bikin Konten Tulisan!", literally shows both diagrams stacked), but the explicit mapping is mine. Flagged so a future editor knows this table is inference, not source. -->

---

### 4. The 20 hooks

From `03 - Content Cheat (Hook Writing).pdf`. The author's framing:

> Yes, kuncinya adalah **HOOK** alias kata-kata pancingan **3 detik pertama** video kamu.
> Aku udah analisis ratusan kreator viral dan ribuan video rame. Ini 20 daftar HOOK yang sering mereka pakai.

Reproduce these as **templates with the brackets filled from the 4K Method** (`kadev-personal-branding.md` §6.6). The bracket names below tell you which 4K bucket to draw from.

| # | Template | Contoh |
|---|---|---|
| 1 | Cara …**(mudah)**… tanpa …**(susah)**… | *"Cara dapetin duit tanpa harus keluar rumah"* · *"Cara matching outfit keren tanpa beli barang branded"* |
| 2 | Kalau kamu ngerasa sulit untuk …**(keresahan audience)**…, tonton ini… | *"Kalau kamu ngerasa sulit ngomong depan kamera, coba tonton video ini…"* |
| 3 | Lakukan …**(ini)**… agar …**(ini)**… | *"Lakukan 3 langkah ini, agar dapetin 10K followers dalam 10 hari"* · *"Lakukan ini setelah cuci muka, agar wajah kamu seger seharian"* |
| 4 | Stop melakukan **(kebiasaan umum audiens)** kaya gini, tapi… | *"Stop bikin konten kaya gini!, tapi coba lakuin yang seperti ini"* |
| 5 | Ciri-ciri kamu…**(ciri yang merepresentasikan audience)** | *"3 ciri-ciri kamu jago ngomong depan kamera, ciri nomer 3 paling penting!"* |
| 6 | **(Solusi)**…ini bisa mengubah hidup kamu… | *"3 Habits ini bisa mengubah hidup kamu jadi produktif lagi!"* |
| 7 | Kalau kamu pengen **(keinginan)**, tapi kamu **(keresahan)**, ini solusinya… | *"Kalau kamu pengen jadi konten kreator, tapi bingung caranya gimana, ini dia solusinya!"* |
| 8 | Perbedaan antara **(dua hal yang sering ketuker)** | *"Perbedaan hoodie yang punya kualitas bagus dengan kualitas jelek, kamu harus tau biar gaketipu seller curang!"* |
| 9 | 99% orang gamungkin dapetin **(keinginan)**, karena ini… | *"99% orang gamungkin bisa public speaking, karena hal ini.."* |
| 10 | Rahasia **(yang audience pengen tau)**, agar **(keinginan)** | *"Rahasia bikin konten viral, agar dapetin 10K dalam 10 hari!"* |
| 11 | Ini adalah **(x)** langkah untuk **(keinginan)** | *"Ini adalah 3 langkah untuk dapetin 10K Followers pertama di TikTok!"* |
| 12 | Ini langkah pertama dan penting untuk **(keinginan)** | *"Ini langkah pertama dan penting untuk pede ngomong depan kamera"* |
| 13 | Kalau kamu bosen dengan **(kebiasaan audiens)**, kamu perlu mencoba ini… | *"Kalau kamu bosen dengan belajar yang gitu-gitu aja, cobain metode ini deh biar belajar kamu gabosenin!"* |
| 14 | Cara **(keinginan)**, dalam **(waktu singkat)**, dengan **(solusimu)** | *"Cara pede ngomong depan kamera dalam 1 jam dengan metode ini"* |
| 15 | Ini fakta yang harus kamu tau tentang **(hal menarik)** | *"3 Fakta yang harus kamu tau tentang roket Elon Musk"* |
| 16 | Kamu perlu hack rahasia ini untuk… | *"kamu perlu hack rahasia ini untuk sukses di umur 20an"* |
| 17 | Cara ngga **(kesalahan umum audiens)** dengan **(x)** langkah mudah… | *"Cara ngga grogi public speaking dengan 3 langkah mudah ini"* |
| 18 | Ternyata **(sekelompok orang)** berbohong ke kamu! | *"Ternyata banyak konten kreator berbohong ke kamu, ini rahasia mereka bisa viral!"* |
| 19 | Ini **(keinginan)** yang gapernah dibahas oleh siapa pun… | *"Ini adalah rahasia bikin script konten yang gapernah dibahas oleh siapapun"* |
| 20 | Kamu gaboleh **(kebiasaan audiens)**, sebelum mengetahui **(X)** hal ini | *"Kamu gaboleh mulai bikin konten, sebelum tau 3 hal ini.."* |

#### 4.1 Rules for using them

1. **Fill the brackets from the user's real 4K answers.** A hook template filled with a guess is worse than no hook. `#2` with *"sulit ngomong depan kamera"* works because that is a real Keresahan; `#2` with *"sulit mencapai potensi maksimal"* is machine filler.
2. **Hooks 9, 18, and 19 are risky** in the sense defined in `script-and-marketing.md` §"Risky hooks". `#18` ("ternyata X berbohong ke kamu") and `#9` ("99% orang gamungkin") make claims. Use them only when the video actually proves the claim. Never aim `#18` at a named real person.
3. **Hook 20 and hook 4 are pattern-interrupts.** They work by telling the viewer to stop. They burn out if every video uses them.
4. **Odd numbers beat round numbers.** *3 langkah* and *5 cara* outperform *10 tips* in this material's own examples — every single numbered example in the PDF uses 3, 4, or 5.
5. **No greeting before the hook.** "Halo guys, balik lagi di channel aku" is 2 wasted seconds. See `anti-ai-ish.md`.

#### 4.2 Hook + first frame

The hook is spoken *and* written. `kadev-personal-branding.md` §7.1: the viewer gives you **8 seconds**, and the slide on Feeds says the cover must be *catchy — pakai judul yang bikin penasaran*. SpliceCraft renders the hook as an on-screen title card at level 21+; make sure the card text is the hook, not a summary of the video.

---

### 5. The classic Hook / Body / CTA layer

Still needed — it is the skeleton the six elements hang on. From the Content Strategy ebook:

**HOOK** — *Tujuan: Menarik perhatian audiens dalam beberapa detik pertama.*
1. **Tanya Pertanyaan** — mulailah dengan pertanyaan yang memicu rasa ingin tahu
2. **Gunakan Cliffhangers** — tinggalkan audiens dengan sesuatu yang membuat mereka ingin tahu lebih lanjut
3. **Jaga Singkat dan Padat** — sampaikan pesan utama dengan cepat dan tepat

**BODY** — *Tujuan: Menyampaikan informasi utama secara mendetail.*
1. **Elaborasi Hook** — kembangkan pertanyaan atau cliffhanger yang telah diajukan di hook
2. **Tambahkan Nilai Lewat Konten** — berikan informasi yang berguna dan relevan
3. **Libatkan Audiens** — buat konten yang menarik sehingga audiens merasa terlibat

**CTA** — *Tujuan: Mengajak audiens melakukan tindakan spesifik.*
1. **Buat Interaktif** — ajak audiens berpartisipasi, misalnya tanya apakah mereka relate dan minta berbagi pengalaman di komentar
2. **Jaga Tetap Sederhana** — instruksi yang mudah dimengerti. Misalnya *"coba komen dibawah deh guys!"*

**The author's own worked example** (Adobe Podcast video), quoted because it shows the register:
- *Hook:* "Audio yang kalian dengar direkam dari jarak 1 meter tanpa mic, apasih rahasianya?"
- *Body:* "Di video ini, aku akan membahas singkat tentang Adobe Podcast dan bagaimana cara menggunakan fitur-fitur canggihnya untuk meningkatkan kualitas audio. Dengan Adobe Podcast, kamu bisa merekam audio berkualitas tinggi tanpa perlu peralatan mahal…"
- *CTA:* "Menurut kalian gimana? Kira-kira mic profesional bisa diganti sama AI ini? Beri tahu pendapat kalian di kolom komentar dan jangan lupa like serta share video ini kalau kalian merasa bermanfaat!"

Notice: the hook is a **demonstration** ("the audio you are hearing right now"), and the CTA is a **real question with two sides**, not "follow for more". Both are copyable patterns.

---

### 6. Generating ideas that are not generic

#### 6.1 Content Idea Framework

From the Content Strategy ebook. A three-level tree:

```
                 General Topic
        ┌──────────────┼──────────────┐
    Problem        Problem        Problem
     Topic          Topic          Topic
        │              │              │
     ┌──┴──┐        ┌──┴──┐        ┌──┴──┐
     Do              Do              Do
     Don't           Don't           Don't
     Rekomendasi     Rekomendasi     Rekomendasi
     QNA             QNA             QNA
     Tips & Trik     Tips & Trik     Tips & Trik
     Penyebab        Penyebab        Penyebab
     Informasi       Informasi       Informasi
```

7 angles × 3 problems × N topics. The slides call the same structure **Unlimited Idea**.

**Worked example (Skincare):**

| | Kulit berminyak | Kulit berjerawat | Kulit kusam |
|---|---|---|---|
| Do / Don't / Rekomendasi / QNA / Tips & Trik / Penyebab / Informasi | ✓ | ✓ | ✓ |

*Contoh studi kasus:* Skincare → Kulit berminyak → **QNA** → (read from a comment) *"kak gimana sih biar kulit ngga berminyak meskipun seharian berkegiatan diluar ruangan?"*

**How to use it:**
1. **Identifikasi Masalah Utama** — tentukan kategori mana yang paling relevan dengan audiens kamu
2. **Pilih Sub-topik** — yang menarik dan menjawab permasalahan audiens
3. **Kembangkan Konten** — informatif, menarik, solusi nyata
4. **Diversifikasi** — variasikan format: Reels, TikTok, Carousel dll
5. **Interaksi** — ajak audiens ke Q&A atau minta feedback

#### 6.2 The AI prompt the course itself gives

The slide *"Unlimited Idea with AI"* hands out this prompt. It is included verbatim because the users of this skill will use it, and it is better that SpliceCraft knows what they used:

```
"Saya sedang membangun personal branding dan ingin menemukan 100 ide konten
untuk [topik/niche kamu]. Ide-ide ini harus berfokus pada permasalahan utama
audiens saya, yaitu [masalah audiens kamu], serta memberikan solusi yang
relevan dan bermanfaat.

Kelompokkan ide menjadi beberapa kategori:
  1. Edukasi     – Memberikan wawasan, strategi, atau informasi penting terkait topik saya.
  2. Motivasi    – Menginspirasi audiens dengan kutipan, kisah sukses, atau pengalaman pribadi.
  3. Tips Praktis– Berisi langkah-langkah atau strategi yang mudah diterapkan.
  4. Interaktif  – Mengajak audiens berpartisipasi melalui polling, Q&A, challenge, atau diskusi.
  5. Storytelling– Berbagi pengalaman atau kisah yang relatable dengan audiens.

Buat daftar 100 ide konten yang jelas, actionable, dan mudah dipahami."
```

**⚠ SpliceCraft's obligation here.** This prompt produces a list of *topics*, which is fine. It does **not** produce a script, and the list will overlap heavily with what every other user of the same prompt got. Two consequences:

1. Treat its output as **input to §6.1**, not as a content plan.
2. **Run every idea through the content ledger** (`content-memory.md`) before writing. The whole reason the ledger exists is that this prompt hands 100 people the same 100 ideas.

#### 6.3 Other idea sources (ebook)

**Riset Tren dan Topik Populer** · **Analisis Kompetitor** (*ambil inspirasi, ciptakan konten yang lebih baik atau sudut pandang berbeda*) · **Feedback dari Audiens** (polling, Q&A, komentar) · **Gunakan Kalender Konten** · **Personal Experience** (*audiens cenderung lebih tertarik dengan cerita nyata yang otentik*).

And the four Knowledge Gap methods from `kadev-personal-branding.md` §12.1 — Data analytics / People Problem / Competitor Benchmark / Self Experience — are idea sources too, and better ones, because they start from a gap rather than from a topic.

---

### 7. Content Pillar → script type

Pick the pillar first; it determines the register before you touch a hook.

| Pillar | Produces | Script leans on | Natural hooks |
|---|---|---|---|
| **Educate** | Kredibilitas | numbered list, Lesson beat | #3, #11, #12, #14, #17 |
| **Inspiration / Story** | Diingat dan Disukai | full 5-beat Storytelling Hack | #2, #6, #7, #13 |
| **Entertaining / Interaction** | Lebih dekat dan manusiawi | short, one idea, question CTA | #5, #8, #15 |
| **Promotion** | Penjualan | problem → proof → offer | #1, #9, #10, #16, #20 |

Ratio reminder: **80 / 15 / 5** (superniche / adjacent / personal life) — `kadev-personal-branding.md` §6.4. The ledger tracks pillar balance so the agent can tell a user *"the last nine scripts were all Educate; you are due a Story."*

---

### 8. Length and word budget

Measured against the 82 reference videos in `E:\Download\CONTOH INSPIRASI TEKNIK NGOTEN DAN EDITING VIDEO` (see `viral-edit-teardown.md` for the full measurement):

| Target | Seconds | Words (Indonesian, ~2.3 wps) | Use for |
|---|---|---|---|
| Short | 15-25 | 35-60 | one idea, entertaining, trend |
| **Standard** | **25-40** | **60-90** | the default; the measured median was 37.5 s |
| Long | 60-90 | 140-200 | full 5-beat story, tutorial |

Measured distribution of the 82 reference videos: 10-20 s (14), **20-30 s (24)**, 30-45 s (10), 45-60 s (9), 60-90 s (17), >90 s (8). Median 37.5 s, p25 22.2 s, p75 66.0 s.

Note the shape: it is **bimodal** — a big cluster at 20-30 s and a second cluster at 60-90 s, with a dip in between. Those are two different jobs (a quick hit vs. a full story), not one distribution. Pick which one you are making; do not land at 50 s by accident.

---

### 9. The writing pass

Once the beats are filled, run these before handing the script over. Each line here traces to something in the source material.

**Keep**
- Short sentences. One idea each. A 1-3 word sentence becomes a giant word card in the edit.
- Real numbers, spoken aloud. "Tiga langkah" → count-up card.
- Ordinals: *pertama… kedua… ketiga…* → ranking card.
- *"Dulu aku…"* — the Personal Story element, in the user's own words.
- Casual particles: *nih, deh, sih, banget, kan, yaudah*. The source material is full of them.
- Direct address: *kamu*, not *Anda* (unless the brief says B2B/formal).
- A question in the CTA that has two possible answers.

**Cut**
- Greetings before the hook.
- *"Di video kali ini aku akan membahas tentang…"* — the single most AI-ish sentence in Indonesian video.
- Any claim the user has not confirmed. Numbers especially.
- Words the user would not say out loud. Read it aloud; if it trips, rewrite it.
- Triads of adjectives (*efektif, efisien, dan optimal*).
- *"Semoga bermanfaat ya!"* as the whole CTA. That is a sign-off, not a call to action.

The full rejection list, with the reasoning and the measurements behind it, is `anti-ai-ish.md`.

---

### 10. Checklist before the camera rolls

```
PREMIS       [ ] there is a premis, written down, from SWOT      (§2.4 theory)
NICHE        [ ] superniche named as a WHO, not a topic          (§6.2 theory)
4K           [ ] Keresahan / Kebutuhan / Keinginan / Kebiasaan filled from real input
PILLAR       [ ] one of Educate / Inspiration / Entertaining / Promotion chosen
LEDGER       [ ] checked against past scripts — not a repeat     (content-memory.md)
HOOK         [ ] one of the 20, brackets filled with real 4K answers
ELEMENTS     [ ] all 6 present — especially #5 Personal Story
BEATS        [ ] 5 beats in order, beat ⑤ reverses beat ①
LENGTH       [ ] target picked deliberately: 20-30 s OR 60-90 s
FACTS        [ ] every number confirmed by the user
LEDGER WRITE [ ] logged after production                         (content-memory.md)
```

If **ELEMENTS #5** or **FACTS** cannot be ticked, stop and talk to the user. Do not fill them in yourself.

---

# Part 5. kadev-live-mentoring.md

## Live mentoring: what the recordings add to the slides

> **Published:** 2026-09-24 · **Last reviewed:** 2026-09-24
> **Source:** Kadev Academy VIP live-mentoring recordings, transcribed 2026-09-23/24 (see Provenance).
> **Editable:** `<!-- journal -->` comments mark provenance and known gaps. See `../JOURNAL.md`.

The slides (`kadev-personal-branding.md`, `kadev-script-formulas.md`) give the frameworks. The live VIP mentoring recordings show the mentors **using** those frameworks on real member accounts, and they add material that is not on any slide: the 16 formats, PAS with a worked sales script, the Storytelling Arc, and a series of account diagnoses.

Load this file when:
- the user asks "what format should I use", or has no winning content yet
- the script has to sell something (product, service, program) without feeling like an ad
- the user's account is stuck and they want a diagnosis
- the user is nervous or stiff on camera
- the user runs a business, or wants income from personal branding

**Jump table:** §1 16 formats · §2 PAS & Storytelling Arc · §3 account diagnoses · §4 attention economy, emotions, thesis+arguments, outer/inner circle · §5 TOFU/MOFU/BOFU, test→win→replicate · §6 Trial Reels & Link Reels · §7 "the niche is you", six income streams · §8 yapping on camera · §9 lesson-only additions (success vs failure, LinkedIn, CapCut order) · §10 Rich's 10k experiment · §11 business branding, archetypes · §12 networking · §13 anatomy of a viral format, editing elements, SFX map · §14 agent rules

Sources are listed at the bottom. Quotes are cleaned only where Whisper misheard a word. The meaning and the register are kept as spoken.

---

### 1. The 16 formats (mentoring "Topik Format Winning", 22 Juli 2026)

The problem this solves: *"salah pilih format bisa jadi effortnya kebuang"*. But a wrong format still gives you data. The rule is **try formats until one wins, then replicate it.** Nadif needed five tries before one format won.

The recording names 15 formats explicitly. The 16th is the ordinary long talking head, which the mentor counts separately from #1.

| # | Format | What it looks like | Effort | Best for | Mentor's note |
|---|---|---|---|---|---|
| 1 | **Talking head + green screen** | You talk; the visual (image, headline, clip) sits *behind* you instead of cutting away as B-roll | High | Education, commentary | Hit 118k views. It exists because a plain talking head with a B-roll every 3 seconds is getting stale |
| 2 | **Single post** | One image, one block of text, no carousel | Very low | People who write better than they speak | Very shareable. Keeps you posting on days you can't shoot: *"jangan sampai absen 7 hari"*. Put your name on it |
| 3 | **Dialog / percakapan** | Two characters (you playing both), A vs B, e.g. *kreator pro vs kreator pemula* | Medium | Education niches | *"Sejatinya manusia suka melabelkan dirinya"*: viewers comment which one they are |
| 4 | **Tunjuk-tunjuk** | You point at on-screen items: *sehari sekali / seminggu sekali / sebulan sekali* | Very low | Any niche; days you can't write | No long script needed and engagement is still OK |
| 5 | **Jangan X, tapi Y** | *"Jangan bangun followers, tapi bangun trust. Jangan kejar viral, tapi kejar value."* | Low | Any niche | Comparison again. Example for a student niche: *"Maba jangan chat dosen malam hari, tapi pagi hari"* |
| 6 | **Carousel** | Multi-slide text post | Medium | Long topic, not comfortable on camera | Slides 1–3 decide everything. Use **bridging** (see §1.1) and put proof on slide 1 |
| 7 | **10×10** | "10×10 [identity]": ten numbered one-liners over Pinterest/meme images | Low | Identity niches | Uses number psychology: people watch to #10. Nadif's account went up within a month on this |
| 8 | **Talking head (long)** | Plain explanation to camera with B-roll and text | High | Educators | *"Kredibilitas tidak pernah meragukan talking head."* Alternate it with the low-effort formats |
| 9 | **Music + text** | Text over a clip with music, no voice | Very low | People not yet confident on camera, storytelling | Show your face if you can: *"people trust people"*. This is mandatory if you sell anything |
| 10 | **Yapping** | Unscripted or semi-scripted talk, raw edit, subtitles only | Low edit / high skill | People who talk well naturally | Feels closest to the audience. Kadev admits that when he yaps his points wander and a 1-minute video becomes 2, so he writes bullet points first |
| 11 | **Comparison** | *"Ini fokus orang biasa. Ini fokus orang kaya. Ini fokus konglomerat."* | Low | Any niche with levels (pemula / pro / advanced) | Viewers self-classify |
| 12 | **7-second storytelling (text + music)** | Under 10–15s, one intriguing visual, text says *"baca caption"* | Very low | Reach | Full watch plus replays while people read the caption means a huge completion rate. That's why these get big views |
| 13 | **Motivational** | Deep lines over a song or beat | Low | Self-development niches only | |
| 14 | **Day in my life** | Vlog of a real day | Medium | Building **credibility** (guest lecture, corporate training) | Personal-centric, so expect **fewer views**. That's fine when the goal is proof. Make more of them only if the audience likes *you* more than your topic |
| 15 | **Carousel storytelling** | A timeline carousel: *"2016 ngonten di luar rumah karena malu… 2026 punya kantor 3 lantai"* | Medium | Strengthening the personal side | Makes people like the person, not only the content |

#### 1.1 Carousel bridging, and the CTA that doesn't feel like a CTA

- **Bridging** is a sentence *before* the content that builds curiosity: *"Aku ada satu metode yang powerful banget buat nulis carousel. Ini jarang dibahas orang lain…"*
- The save CTA is phrased as a choice the viewer will lose: *"jadi kamu perlu **catat atau save aja** biar gak lupa."* Nobody takes notes while scrolling, so they save. Compare *"save biar nggak lupa"*, which reads as *"konten kreator banget nyuruh nge-save"*.
- Put **proof** in the first slides (a screenshot of your results). *"Sejatinya manusia percaya kalau ada buktinya."*

#### 1.2 How the agent picks a format

1. If the user has **no winning content yet**, don't pick one format. Propose 3–5 different formats for the same topic and record each in the ledger with a `format` tag.
2. When one wins (views above the follower count and saves or shares above the account's usual), **replicate it** with new topics. Don't change the format and the topic at the same time.
3. When a winning format starts to decay (*"masih works tapi udah nggak prime"*), start a replacement topic or format **before** it dies. Nadif moved from *10×10 cowok* to *game × self-development* while 10×10 was still working.
4. The low-effort formats (2, 4, 5, 9, 12) exist to protect **consistency**. They are not a lesser tier. Suggest one when the user says they have no time this week.
5. To adapt any format to a niche, the mentor's shortcut is: screenshot the reference video, give it to an AI, and ask for ideas in this format for niche X. *"Tinggal bagaimana mengemasnya lagi."* The agent may do this, but the output still goes through `anti-ai-ish.md` and the ledger.

---

### 2. PAS for selling without sounding like selling (mentoring "Formula Script Viral & Jualan", 27 Agustus 2026)

Premise of the session: people don't reject products, they reject **how the story is told**. The three failure modes named:

1. The story is **self-centred** (*"terlalu sentris ke diri kita"*).
2. It sells **features and aesthetics**, not what changes for the buyer.
3. It never **attaches the product to the audience's own story or problem**. This is the hardest one.

#### 2.1 Problem → Agitation → Solution

| Beat | Do | Don't |
|---|---|---|
| **Problem** | Start from the audience's pain in their own life: *"Karena satu produk ini, aku bisa diterima cewek setelah 3 kali ditolak."* | Lead with the benefit: *"produk cuci muka ini bikin kamu tambah ganteng"*. The mentor calls that *"cuma announcement"*. |
| **Agitation** | **Validate** the problem with small specific details that make people say *"iya bener juga"*: *"beli baju mahal biar diterima doi, tapi muka nggak dirawat, sama aja bohong."* | Scare people: *"awas nanti nyesel kalau nggak beli"*. Too narrow, and it creates no urgency. |
| **Solution** | **One** benefit, short and dense. Keep price for a separate push. | Put every feature, benefit and the price into one video. |

> Agitation is the step that **cannot be skipped**. *"Kita nggak bisa langsung dari problem ke solusi."* Platforms reward retention. A strong hook with a weak body still loses.

Full 30-second example as spoken (face-wash product):
> *"5 kali PDKT, endingnya ditolak terus. Padahal dia wangi, bajunya bagus. Tapi satu hal ini yang bikin temanku ditolak terus. Minggu lalu temanku curhat, katanya abis nembak doi tapi ditolak karena muka kusam. Makanya aku langsung kasih satu produk ini. Sini aku ceritain satu produk yang bantu temanku dapet cewek."*

#### 2.2 Write for one fictional person

The mentor invents **Pak Andi** (15 years in marketing, great offline, too blunt online) and **Bu Nining** (a home tailor who is paid per piece). He writes every script as if he were talking to that one person. Answer four questions for the persona:

1. **Siapa dan kerjanya apa?**
2. **Masalahnya apa?**
3. **Kenapa harus sekarang?** This is the urgency, so they can't find a reason to put it off.
4. **Dia peduli sama apa?** The pain can be in their **circle**, not themselves: family, business, reputation. Insurance example: *"kalau tiba-tiba harus ke rumah sakit, anak di rumah makan apa?"*

Narrow beats broad. *"Pekerja"* is too broad. *"Pemilik laundry kecil, karyawan di bawah 10, belum kepikiran kalau ada kecelakaan"* is right. *"Makin sempit orangnya, makin gampang kontennya."*

#### 2.3 Where problems come from ("belanja masalah")

Take problems from observation, never invent them:

1. **Threads / X complaints** that repeat. *"Capek ini pasti ada yang berulang."*
2. **Common misconceptions**, e.g. the *standar-standar TikTok yang agak ngawur*.
3. **Things you saw yourself** at school, work, or among colleagues.
4. **Questions people ask you.** Write every one down. Each is an idea, and a natural **stitch or comment-reply** format (*"kalau followers kecil bisa ikut gak kak?"*).

> *"Ini benar-benar harus ditulis berdasarkan orang nanya, jadi nggak dihalusinasi."*

For the agent: when the user has no ideas, ask for these four sources before generating any. An idea with no source is marked `source: none` in the ledger and flagged.

#### 2.4 Storytelling Arc: Origin → Challenge → Turning point → Lesson

Worked example (Bu Nining → health insurance):

| Beat | Content |
|---|---|
| **Origin** | Sews at home, has regular customers, paid per piece |
| **Challenge** | Income depends entirely on her own hands. If she's sick, no money comes in |
| **Turning point** | Her finger gets caught in the machine. She can't sew for two weeks, and the treatment is expensive |
| **Lesson** | The danger was never losing customers. It was losing the ability to work |

The lesson is where the product can sit. This is the same arc as the 5-beat Storytelling Hack in `kadev-script-formulas.md` §3, compressed to four beats.

#### 2.5 The six elements used together in one script (insurance)

| Element | Line |
|---|---|
| Pain point | *"Punya usaha sendiri, kalau bapaknya jatuh sakit siapa yang nanggung?"* |
| Specific number | *"Dari semua klien yang aku temui bulan ini, 7 belum pernah dengar soal ini."* |
| Promise | *"Satu langganan ini bisa nyelametin kamu dari boncos."* |
| Opinion | *"Menurut aku asuransi itu penting, tapi banyak orang anggap nggak penting. Ini alasannya."* |
| Urgency | *"Orang baru nyesel pas udah kejadian, dan itu udah telat."* |
| Interaction | *"Ada yang pernah ngalamin? Tulis di komen."* |

Hook upgrade shown: *"Sosialisasi program perlindungan pekerja"* (nobody stops scrolling) became ***"5 hal yang sering disepelein bisnis owner"***. That's a specific number plus a call-out to an identity.

#### 2.6 CTA by goal

| Goal | CTA |
|---|---|
| Grow followers | *"Follow biar nggak ketinggalan konten selanjutnya."* |
| Get prospects / sell | Call the person out and move to DM: ***"Punya usaha kecil dan masih pusing soal pekerjanya? Coba ngobrol di DM ya."*** *"People trust people"*: the sale happens in the conversation, not in the video. |

#### 2.7 The recap chain

**Masalah → Cerita → Manfaat → Kepercayaan → Obrolan → Prospek.**
Trust comes from **consistency**, never from one video. Reveal **one benefit per video** on purpose so people ask. *"Bertanya itu potensi untuk dikonversi."*

---

### 3. Account diagnoses from the Q&A: patterns that repeat

Each row is a real member question with the mentors' answer, reduced to the rule.

| Symptom | Diagnosis | Rule |
|---|---|---|
| Views high but retention about 1 second | Hook doesn't open a loop | Open with a question that contradicts a common belief (*"Kenapa main game selalu dibilang buruk buat otak?"*). On Instagram watch the **skip rate**: under ~40–50% and the video starts to roll |
| Views stuck, 2 years, no winning content | Format never varied | Try all the formats (§1). For a Gen-Z audience (18–24), avoid heavy talking head. Use tunjuk-tunjuk, list or interview formats |
| Two topics on one account (property sales + team recruiting) | No overlap found | Find the **irisan** between them: *"kemarin tim saya yang baru seminggu closing rumah harga sekian M"* sells the property **and** the recruiting |
| Future niche differs from current stage (wants "living in China", not there yet) | Stage vs long-term brand | Start with the general topic that attracts the future audience (fun facts about China, learning the language) plus your journey. Shift later |
| "Realita kehidupan manusia" media account, slow growth | Positioning too broad | Answer: known as what, for whom (18–35 Gen Z/Millennials), why they should care, how. The USP gets discovered from audience feedback after posting. Don't wait for it before starting |
| Filmmaker student wants clients | Visuals without story | Good visuals are wasted without storytelling. Origin (still learning, studying abroad) → what you learned → showcase 1–2 projects as social proof |
| Leads come but don't convert this month | **High-involvement product** (education, 15–30 juta) | Content can't shorten a family decision. List and nurture leads and message them 3–4 months before intake. For speed use Threads, LinkedIn or Meta ads. Personal branding is the long game |
| Creative studio gets editors following, not clients | Goal not defined | Decide: is social media for clients or for audience? Content for the target market brings fewer followers but more sales |
| Carousel underperforms Reels | Platform is designed for Reels | Carousels have fewer variables, so the **copywriting** carries everything |
| Wants to post whole daily life (student + athlete + founder) | No hook on a new account | Nobody cares about a stranger's daily life. Pick USPs to highlight first |
| AI-cinematic account dropped from ~10k to 400 followers after 15 juta/month ads | Ads bought views with no engagement. Visuals look "masih AI banget". No story | Fix the storytelling and visuals before spending on ads. Short drama series win on story despite weak visuals. Ride topical moments |
| Changed niche after 30 posts | Too early | Fix the hook (a question hook instead of an information hook) before changing topic. Prefer a niche you control yourself. Documenting a sick parent risks looking *aji mumpung* |
| 7 days in, views equal to followers | Fine: that's a good start | Add a **text hook on the cover** that stays on screen the whole video. Lower the music. Call out an identity (*"10×10 cowok…"*) |
| Property vlog stuck under 1k while a peer gets 3.3M | Different market (foreigners, English) and the video was shot in the dark | Shoot property in **daylight**. Pick a language per market. Sell land with a story: *"pernah kepikiran punya villa di Bali?"* |
| Want to talk about someone else's product (MSI) | Endorsement | Start with a story about your own work, and let the product appear as the thing that made the productivity possible |

---

### 4. Attention economy, algorithm and emotion (mentoring "Attention Economy", 21 Okt 2025)

Speaker: Nadif, who also writes for Malaka Project. The Q&A is answered by Kadev, Rich and Kiki.

#### 4.1 The model
- Attention is the scarcest commodity. The average Indonesian attention span quoted is **8–10 seconds**. That's why every tip about hooks exists.
- Hooks alone don't win. *"Memenangkan atensi ekonomi itu melahirkan konten yang punya value."*
- The algorithm ranks on **three signals: retention** (how long, by how many), **interaction** in the video, and **shares**.
- Trend content spreads in three steps: **incendiary** (lots of fuel posts on one issue) → **controversial** (it becomes a fire) → **polarizing** (the algorithm pushes content that splits people into camps). Conflict spreads because audiences pass it on easily.
- Big creators use **clippers** (100–1,000 clip posts a day per creator) to flood feeds. Micro creators can't compete that way, and they don't need to: personal branding, self-improvement, fashion and product creators mostly don't use clippers.
- *"The new social currency hari ini adalah menjadi unik."* Don't copy your role model's delivery.

#### 4.2 The six emotions, and which ones hit
Happy · Fear · Surprise · Peaceful · Sad · Anger. **Fear and anger hit hardest** (e.g. fear of staying poor, public anger at a national coach). Sad works as relatable text-only posts. Surprise works when it rides a moment, e.g. new students who can't believe they got in.

**Sad without selling your sadness** (answer to a member worried about exploiting vulnerability):
1. **A shared, real problem, then the survival step.** *"19 juta lapangan pekerjaan… ternyata 19 juta pengangguran"* is the hook. Then show how to survive it, so the viewer isn't left stuck in the sadness.
2. **Ride the wave from another angle.** Borrow a trending phrase (*"sisakan ruang di kelas"*) and point it at your own topic.
3. **The issue's direct impact on the viewer**, as environmental creators do.

Direct charity-style sad content (going to poor people and filming the help) now reads as **opportunistic**. Avoid it.

#### 4.3 Thesis + arguments (Malaka's scriptwriting method)
- **Thesis**: a statement that needs explanation before anyone can judge it true. Example: *"RUU Penyiaran sangat berbahaya bagi kreator konten dan pekerja seni."*
- **Arguments**: 3–4 statements, each backed by data or theory, that make the thesis true.
- **About 70% of writing time goes to the thesis and arguments.** Storytelling is arranged last. Sources are books and Google Scholar.
- The thesis targets the audience the speaker has standing with. The presenter is a musician with a law background, so the target is the creative industry plus law.

For the agent: for educational or opinion scripts, write the thesis in one sentence and list the arguments **before** drafting any hook. If the user can't give a source for an argument, drop it. Don't invent one.

#### 4.4 Outer circle / inner circle (Kadev, whiteboard)
- **Outer circle** (general): gets you known by many people. Kadev's is *self-development*.
- **Inner circle** (specific): tells people what you are. Kadev's is *personal branding*.
- Kadev's split is **50/50**. Creator friends run 70/30 or 40/60.
- Example: an anime illustrator. Anime is the inner circle. Drawing and creativity in general is the outer circle.

> Tension with the slide ratio **80/15/5** (`kadev-personal-branding.md` §6.4). They measure different things: 80/15/5 splits **superniche / adjacent / personal** posts, while outer/inner is **reach vs. specialisation** inside the niche side. Use 80/15/5 for the calendar. Use outer/inner to decide how wide each niche post's hook is. Kadev also mentions a **70/20/10** rule in a dialog-format example (§1 #3). That line comes from a character in a sketch and isn't taught as a rule.

#### 4.5 Smaller rulings from the Q&A
- **Posting time:** use Instagram *Professional dashboard → Followers → Active times* (TikTok has the same). Kadev's audience peaks at **18:00**, after work. *"Harus upload jam 1 malam"* is **hoax**: no algorithm theory says so.
- **Agency accounts:** "good content" is subjective. Define the client (e.g. UMKM or startups that want cheap web development), then post what that client needs (cheap tips for UMKM). Research what works for that client, not for Kadev.
- **Winning content, again:** a member's business account had most videos in the tens of thousands and a few at 800k–1M. That came from replicating one winner. *"Quality is subjective. What we can control is consistency until we find the winner, then replicate until it's no longer fun."*
- **Teaching tools to others (UMKM mothers):** check their intent first. Sell the outcome (*"kalau bisa Canva, kamu bisa menghasilkan"*), not the tool (*"kamu harus bisa Canva"*).

---

### 5. Content & marketing funnel (mentoring, 17 Maret 2026)

Speaker: Kadev, with Rich. **A funnel is the audience's journey from not knowing you, to trusting you, to buying or becoming loyal.** Kadev's principle: *"Mending punya 10 audiens loyal daripada 1.000 yang cuma follow."* The contrast drawn: Willy Salim has a bigger following, but Ferry Irwandi's audience buys.

#### 5.1 The three stages
| Stage | Viewer goes from → to | Content | Question it answers | Expected numbers |
|---|---|---|---|---|
| **TOFU** (top) | nggak tahu → **tahu** | Light, general, relatable. Doesn't need to teach a framework. Kadev's example: *"dari YouTuber jadi musisi… dari videografer jadi personal branding"*. It rides famous names so people ask "who's this?" | **Why** should I care? | Highest views |
| **MOFU** (middle) | tahu → **mau** | Show your expertise (a law graduate breaks down a case) or the product in use | **What / how** | Mid, e.g. 30k |
| **BOFU** (bottom) | mau → **follow / beli** | Offer, testimonial, *"klik nomor di bawah"*, ebook, bootcamp | **Action** | Low views, e.g. 3k, but that's not bad |

- **Start with TOFU** when the account is small. *"Kalau tofu kita cuma 100 orang, ke bawah makin kecil."* Get views from 500 to 1,000 to 10,000 before you go further down the funnel.
- **Search content is BOFU.** Rich's example: *"rekomendasi resto di Malang"*. Low views, high conversion, because the viewer is already looking. TikTok works as a search engine.

#### 5.2 Four funnel mistakes
1. Selling from the first post. Nobody knows you yet, so nobody wants it.
2. Educating forever and never asking for action. *"Skill kamu mahal itu bukan berarti nggak ikhlas."*
3. Making every post the same when each one has a different job.
4. Chasing views and forgetting conversion. That's fine early on, but monetising means giving up some views.

Also: sell the product as **the solution to a problem**, not as something to sell. Testimonials and word of mouth can't be faked.

#### 5.3 Test → Win → Replicate (the answer to "what's my best format?")
1. **Test**: mix formats in one week, e.g. 2 carousels and 2 videos.
2. **Win**: when one goes up, make **3–5 more** in the same format. One hit could be luck.
3. **Replicate**: keep going with about **80% the winning format and 20% testing** others. Start testing again before the trend drops.
Rich's caution: a flop isn't always the format's fault. Writing and design are variables too. Test–win–replicate is the simplest workable evaluation.

#### 5.4 Cross-platform
- **Don't mirror posts unchanged.** Each platform has its own nature (LinkedIn is text-first). Turn a winning LinkedIn text post into a script or a carousel with the hook alone on slide 1.
- A low-effort bridge: screenshot your Threads or LinkedIn post into a carousel and **also paste the text in the caption**.
- An audience over 40 is mostly on **Facebook** in Indonesia, so the platform choice comes first.
- Don't run an affiliate-style spam strategy outside TikTok. *"Kalau kenalan, yang ditanya Instagram, bukan TikTok."*

For the agent: every ledger entry gets a `funnel` field (`tofu`, `mofu` or `bofu`). If the last 10 posts contain no TOFU, or the account is under ~1k followers and the draft is BOFU, the gate warns.

---

### 6. Trial Reels and Link Reels (mentoring "Trial Reels & Link a Reel", Jan 2026)

Speakers: Nadif (ran the test on his own account for about 30 days) and Kadev. **Both say plainly that the pattern isn't final.** Treat it as a working method, not a law.

#### 6.1 Trial Reels: a lab that only non-followers see
- Instagram shows a Trial Reel **only to non-followers**, and it doesn't appear on your grid. In Nadif's test, **82% of the reach came from non-followers**, and one faceless text reel reached 1.5M views.
- So it's where you test hooks, formats, and new topics without cluttering your main feed. It also suits people who are shy about friends seeing their content.
- It works on an old account **as long as you never bought followers or likes**.

**The pattern (Kadev's whiteboard):**
1. **Pick a format you can make fast.** Trial Reels need volume, so a talking head that takes hours to produce doesn't fit. The usual pick is a **7-second, multi-scene reel where only the text changes**, or an X/Twitter-style text card.
2. **Post volume.** **3–5 a day.** The platform allows up to 20, but Nadif stays at 5 or fewer because heavy volume might be read as spam, and Instagram's ban rules are unclear.
3. **Find the winner by probability.** Out of 15 uploads, maybe 2 win.
4. **Replicate the winning format and change only the context** (the same 7-second text format about hooks, then niche, then lighting…).
5. **Convert views into follows.** Trial viewers don't follow you yet, so use **comment-keyword → DM automation** with a freebie that requires a follow. Nadif's CTA: *"Kalau video ini muncul, artinya kamu belum follow akun ini."*
6. **Share the winner to the main feed** with the *share to everyone* button, done by hand. Auto-share after 72 hours exists, but **data settles after about 8 hours**.

**Rules from the Q&A:**
- **Don't reupload the same reel as a trial.** Change the hook text, the copy, the music, or the caption so the algorithm treats it as new.
- Editing a caption after posting doesn't change how the reel is ranked. Make a new one.
- Archive the trials that flop (Nadif: post 5, keep 2, archive 3).
- **The main profile has to match what the trial promised.** If a new follower lands on a grid about something else, the conversion is wasted. Keep posting on the main feed too.
- A trial can take a new angle on the niche. For a Canva niche, *"lunas utang gara-gara konten pakai Canva"* is fine because it's still Canva. A niche sets what you're known for. It isn't a cage.
- Faceless trials got views but few follows. Nadif's next experiment is showing his face.
- Instagram rolls features out unevenly, so some accounts don't have Trial Reels yet.

#### 6.2 Link Reels: a playlist, and why it snowballs
- Link Reels chains one reel to the next (*"Part 2"*), like a TikTok or YouTube playlist. A viewer who wants more taps through without opening your profile, and each episode feeds the others.
- **The link can only be set at upload time.** Post episode 1, then attach it while uploading episode 2.
- It needs **planned series writing**. Examples: a Canva series (layout, then fonts, then …) or a Ramadan series (bukber designs, amplop designs).
- Kadev hadn't measured results yet when this was recorded.

For the agent: when the user plans a series, log every episode with the same `--theme series:<name>` and put the previous episode's id in `notes`. `ledger check` **will** flag part 2 as close to part 1, because it has no series exemption. That warning is expected. Confirm with the user that it's a planned episode, and check that the new episode's angle really is different (fonts, not layout again).

---

### 7. "The niche is you" and the six income streams (mentoring "2026 Algorithm & Strategy", 13 Des 2025)

Speakers: Kadev (niche), Rich (monetisation). This is Kadev's most recent position on niche. He calls it forecast plus pattern-reading, *"nggak bisa bilang 100% benar"*.

#### 7.1 Niche isn't the most important thing. You are.
*"Niche itu gak penting"* is shorthand for *niche matters, but it isn't the most important thing.* Two dangers of a niche-only account:
1. **People follow the topic, not the person.** If you ever shift topics (Kadev went from videography to personal branding), a topic-loyal audience leaves. Kadev survived his shift only because he had always told his own story, in posts and in Stories.
2. **It limits authenticity.** You leave out the unique things that don't fit the niche label, and those are exactly what set you apart. Plenty of people talk about agencies, but not many run one at 17. That member's post reached 2M views. Timothy Ronald stands out in finance for his **personal opinions and experiences**, not his tips.

> *"Kita bukan creator lifestyle, gaming, bisnis… Kita adalah niche-nya."*

**Reconciling with the slides.** `kadev-personal-branding.md` §6.2 says *"niche bukan topik, tapi siapa secara spesifik"* and teaches the superniche ladder. Both hold: keep an **umbrella** (a message plus 1–2 pillars) and a specific audience, but define yourself by a **message**, not a topic label, and always include a **story pillar**. The agent should never refuse an idea just because it's outside the topic label, as long as it serves the message.

#### 7.2 Step 1: write your message (pesan)
Replace *"I'm a gaming creator"* with *"I help people earn extra income from their hobby"*. Then *"I made two digits from Mobile Legends jockeying"* becomes on-message. Four questions:
1. Do I hold a **different or contrarian view**? (It rises faster, but it must not harm anyone and must rest on data or patterns.)
2. What **change** do I want my audience to feel? (e.g. from *nggak pede* to *pede* in public speaking)
3. What **values** do I live by?
4. What do people **already ask me for help with**? Check DMs and friends.

Kadev's own: *help people who, like him, had potential but were too shy to show it, learn to make content and earn from it, so they get opportunities.* His pillars are **personal-branding education + self-development + story in almost everything.** *"Percuma bangun personal branding kalau pilarnya edukasi terus — orang peduli sama kontennya, bukan sama kita."*

#### 7.3 Three mistakes (Rich)
1. **Copying exactly** (*plek ketiplek*). It may work, but the identity belongs to someone else. ATM (amati, tiru, modifikasi) means modify.
2. **Chasing trends and news.** It's exhausting and the person disappears behind the news.
3. **Looking too far.** Benchmarking the biggest or foreign creators when the material is in your own story.

#### 7.4 The six income streams (validated by Kadev's team)
| # | Stream | What it is | Rule |
|---|---|---|---|
| 1 | **Digital / info products** | Ebook, mini ebook, templates, Notion systems, mini course, LMS (Kadev Academy itself) | About 99% margin. The only cost is marketing. Pick whatever fits your brand best |
| 2 | **Services / freelance / consulting** | Editing, AI automation (n8n, Telegram bots), social media management, copywriting | Easiest start: needs skill, not capital. **Sell your core hard skill**, not the trending one you don't have |
| 3 | **Sponsored content / ads** | Endorsements, placement | Brands now put more budget into small **KOL/UGC** creators than into ads, because unknown faces feel more trustworthy. Make your format **brand-friendly**: leave a natural slot for a product (a *"POV beli sarapan di McD"* style) |
| 4 | **Subscription / membership** | Paid live chat, memberships (the BigMo live-streaming model) | Live-first |
| 5 | **Affiliate / resell** | Mostly TikTok (Instagram's yellow basket hasn't taken off in Indonesia) | **Only products in your own field**, where your view is credible. Check the commission percentage before you commit |
| 6 | **Leverage an offline business** | Your personal account carries your own brand's campaigns | Cheaper than a brand ambassador, which can cost hundreds of millions. Example: a "New Year, New Me" resolution story in which your speaker brand solves your focus problem |

This extends the five doors on the slides (`kadev-personal-branding.md` §12.2: product, speaker, partnership, mentorship, affiliate). Speaker and mentorship fall under *services*. Subscription and offline leverage are new.

---

### 8. The Art of Yapping: sounding like a person on camera (mentoring, 27 Mei 2026)

Speaker: Kadev (10 years on camera), with Nadif on editing. This is the delivery half of anti-AI-ish. A clean script read badly still sounds AI-made. *"Audience itu paham: ini baca script doang, ini dari AI."*

#### 8.1 Why people go stiff on camera
1. **Reading the script word for word.** Fluent, but obviously memorised. Fix: read and understand it, then **say it your way**. Swap words that aren't yours. Kadev's scripted *"90% personal branding di Indonesia salah arah"* comes out as *"90% orang yang bangun personal branding di Indonesia itu salah arah. Kenapa? Yuk kita bahas."* Same meaning, his wording.
2. **A fake "content creator voice"**: *"Hai guys, welcome back to my channel."* Ten years out of date.
3. **Asking permission to start**: *"Halo guys, izinin aku share sedikit hari ini."* If it's there at all, it must sound spoken, not read.

#### 8.2 The five delivery rules
| Rule | Detail |
|---|---|
| **The first 3 seconds are the hook, not an introduction** | No name, no small talk. Even an unscripted idea recorded while driving opens on the claim, not on *"aku lagi nyetir, nama aku…"* |
| **Talk to one person** | Picture one friend behind the camera and use their name in your head. Use **"kamu" or "kita", never "kalian"**, especially for Gen Z: *"kalian" terasa dihakimi, terasa diajarin.* Gen Z prefers being told a story and related to over being taught. *"Kalian"* only fits an older speaker addressing a younger audience |
| **Eyes on the lens, not the preview** | Tape over the preview if you have to. Looking at your own face reads as unfocused eyes |
| **Three takes at most** | Take 1 is practice, and take 2 or 3 is better. Take 4 and beyond just drains energy and the video never gets posted. Cut small slips in the edit |
| **Consistency beats polish** | Home lighting, a phone, the car are all fine. *"Kualitas ditentukan oleh data engagement, bukan oleh lighting."* Good by your standard isn't necessarily good by the audience's |

**Teleprompter workflow:** paste the script into Instagram's **Edits** app (built-in teleprompter), read it through once, rewrite any line that isn't how you talk, raise the scroll speed until it matches your pace, record, and cut the retakes in the edit. Practise in front of the phone camera, not a mirror.

Talking formats build **closer audiences** than text-only formats, even when text gets more views: *"manusia itu makhluk sosial — diajak ngobrol, mereka lebih dekat."*

#### 8.3 Length, and where storytelling sits
- Short-form ideal: **up to about 1.5 minutes.** At 2 minutes attention drops and editing takes longer. *"Kenapa gak bikin dua video 1 menit?"*
- **Storytelling is a pillar, not a step** before the education. In a 7-post week, for example: 2 storytelling, 3 education, 2 entertainment. The story posts explain the person behind the education. That's why audiences follow the person and not just the topic.

#### 8.4 Editing notes (Nadif)
- **B-roll**: screenshots and images that match each script line. Stock footage from YouTube works for personal-branding topics.
- **Sound design is what holds attention.** A voice alone sounds monotone and gets skipped. Layer a **backsound** under it, then **SFX**: clicks, minor hits, **whoosh** on transitions, **riser** into the key line. Mute everything and play it back to hear the difference.
- **Curate an asset library**: music by category, collected from viral FYP content. The edit goes fast once the library exists. Kadev Academy ships its own music and SFX packs (`ASSET MUSIC…zip`, `ASSET SOUND FX VIRAL…zip` in the course folder).
- Several timelines per project file are fine.

For the agent: when writing a script meant to be spoken, **use kamu/kita**. Mark lines the user should re-say in their own words rather than read. Never write *"hai guys / welcome back / izinin aku"* openers. When planning the edit, include a backsound bed plus whoosh/riser/click SFX cues (`references/audio.md`, `music-guide.md`).

---

### 9. Lesson videos: what the spoken lessons add to the slides

The 36+ lesson videos mostly narrate the slides already in `kadev-personal-branding.md` and `kadev-script-formulas.md`. The storytelling hack, the four pillars and the idea template are repeated almost word for word. This section keeps only what the spoken lessons **add**.

#### 9.1 Success or failure: which to show? (lesson 1.3)
**Both, naturally.** Personal branding is a process, not a destination, and the process is what makes you authentic.
| Show success for | Show failure for |
|---|---|
| **Credibility**: competence, ability, value | **Authenticity**: you're a person who failed |
| **Proof of work** | **Inspiration**: "I failed too, here's what changed" |
| **Motivation** for others to try | **Human touch**: nobody relates to a god |

Only successes and the audience feels *"ini orang terlalu dewa, aku nggak bisa menjangkau dia"*. Only failures and they conclude there's no competence. Package failure as **a lesson or a growth step**, using the 5-beat Storytelling Hack (set the scene → the struggle → the lesson → success follow-up → a relatable message). Kadev's own worked example: *"dari desa kecil di Madura, tanpa koneksi…"* leads to *"170 ribu lebih pengikut"*.

#### 9.2 Personal branding without shouting "personal branding" (lesson 3.1.2)
**Four wrong ways:** claiming *"aku jago ini"* with no proof · posting certificates or achievements **without context** · sharing results with no story or added value · making only tips and entertainment with no purpose.
**Four right ways:** show the **process**, not only the result · tell the challenge and the solution you used · use **case-study or before/after carousels** · give every piece a **purpose**, which is the pillar:

| Pillar | Purpose |
|---|---|
| Education | credibility |
| Inspiration | being remembered and liked |
| Entertaining | closeness, feeling human |
| Promotion | sales |

**Premis × pillar = your "match branding".** Kadev's premis (*"from a mysterious Gen Z to earning from personal branding"*) becomes: education on how to start · inspiration from his mysterious past · entertainment about his old zero-post profile · promotion of a webinar for people who are still "mysterious".

#### 9.3 LinkedIn, effortlessly (lesson 3.2.6, Arif "Kiki" Maliki)
- LinkedIn distributes to **home feeds**, not an explore page. Early engagement in the **first 1–2 hours** decides whether a post reaches **second-degree connections** and keeps spreading.
- **Be active, not passive.** Your likes, comments and reposts show up in other people's feeds. Engaging consistently on **one kind of content** (Kiki always engages with consulting and business-case-competition posts) *is* personal branding. People start to associate you with the topic.
- Invite discussion: a curious or contrarian first line, and a closing question.
- **Connect → Converse → Cultivate** is a funnel of relationships that narrows as it goes:
  - *Connect*: a DM with a genuine compliment about their insight and a clear reason to connect.
  - *Converse*: days or weeks later, share an insight they'd find useful.
  - *Cultivate*: check in every 2–4 weeks (*"lagi sibuk project apa?"*), follow up on an old topic, invite them to events.
  - Rules: don't sound like a template · keep it short and relevant · **give value before asking** · make it a chat, not an interview.

#### 9.4 Kadev's CapCut order (lesson 3.1.6)
1. **Cut**: remove everything that isn't a point.
2. **Auto-caption** (Text → Auto captions → language **Indonesian**), then apply one simple, tidy caption template.
3. **Colour**: an Adjustment layer over everything. He mostly lowers *brilliance*, pulls back yellow and adds a little blue. No full grading for social content.
4. **Transitions only where the angle changes.** Not everywhere.
5. **An SFX on each transition** (search CapCut's own library, e.g. a "paper" whoosh).
6. **Backsound, turned down.** *"Banyak kesalahan orang: musiknya keras banget."* Lower it until the voice sits clearly on top.
7. Effects last, and sparingly.
*"Trend sekarang: konten yang basic-basic aja, yang simpel-simpel aja."*

This matches SpliceCraft's own pipeline order (`SKILL.md` Steps 1–6) and its ducking rule (`audio.md`). The agent may cite this lesson when a user asks why the voice must sit above the music.

---

### 10. 10,000 followers in 3 weeks: Rich's own experiment (mentoring, 18 April 2026)

Rich (a mentor who runs an AI company) grew a dormant personal account from **~1,400 to ~16,900 Instagram followers in about a month** using the Kadev framework, posting the same short videos to TikTok (~11.8k), Facebook (~7k), YouTube Shorts and Threads. His disclaimer: *"sesuaikan dengan kondisi, kapasitas dan kapabilitas masing-masing."*

#### 10.1 The ideal customer comes before any content
- **ICP (ideal customer profile)**: business people and finance people (investors, traders), **not** people who want to learn AI. His goal is selling AI services to companies, so AI tutorials would attract the wrong crowd.
- *"Viral doang tapi nargetin orang yang salah, nggak guna. Susah di-monetize."* Within three weeks the DMs came from the right people: a housewife who trades stocks and helps her husband's business, a company making industrial washing machines for the MBG program, requests for classes.
- That's why the course runs **Character Development + Vision Plan before Execute & Show**. A wrong foundation means confusion later (clippers and faceless footage accounts get views but can't monetise).

#### 10.2 What the tests showed
| Tested | Result |
|---|---|
| Heavy edit (overlays, logos) vs simple "tempel" edit | **No difference. Substance decides.** |
| Same script: proper office set-up vs phone + clip mic | The phone version did **slightly better** |
| Storytelling hook vs direct-headline hook | **Both worked** |
| Posting count before a winner | Under 5, because the foundation was already clear. Early posts hit 66k–100k |

#### 10.3 Angle, source, and judging a winner
- **Don't open on the news. Find the plain-language angle.** Anthropic's report said the safest job is *construction*, but *"konstruksi"* isn't everyday speech, so the hook became ***"Tukang jadi pekerjaan paling aman dari AI."***
- **Read primary sources** (Bloomberg, Yahoo Finance newsletters, company reports). Most creators copy other creators, which is ATM of ATM of ATM. Going to the source puts you a step ahead.
- **Test by watching your own video as an audience member.** Would you watch to the end? Creators are biased toward their own work.
- **A winner has balanced engagement**: views **and** comments **and** shares **and** saves. High views with no comments, or high likes with no shares, doesn't count.
- **Short vertical video** is the one format that posts to every platform.
- Explain your expertise in lay terms. Rich can talk papers, maths and code, but chooses the angle a non-expert wants.

#### 10.4 Three strategies
1. **Positioning**: most AI creators do news (exhausting, always racing) or tool tutorials (easy to copy). Rich positioned himself as *an AI practitioner explaining impact and use cases*, an angle few can cover.
2. **Leverage existing credibility**: mention the real credential in every video (his robotics and AI company).
3. **Smart funnel**: don't go viral with no purpose. Brand accounts that only chase trends get views, but the comments show nobody knows the brand or product. One brand account was taken for a talent's personal account until the talent resigned.

---

### 11. Business branding: face, story, archetype, font, colour (mentoring, 21 Feb 2026)

Speaker: Rich, with Nadif. For members who own a business, or plan to monetise personal branding by building one.

#### 11.1 Why a good product isn't enough
- Claimed statistic: *"75% UMKM berhenti di tahun ketiga — bukan karena produknya jelek, tapi karena branding dan cerita."* It's attributed to Kadev's own team research, with **no public source given. Don't repeat it as fact.**
- Branding isn't logo, tagline, font and colour. It's **trust**, which does four jobs: **assurance** (it's reliable) · **safety** (a known brand over an unknown one) · **difference** (Apple's clean design against LED gimmicks) · **value** (premium, affordable…).
- **Mispositioning kills sales.** A Rp15k ramen dressed as premium (gold logo, English-only copy, luxury storefront) scares off exactly the people who can afford Rp15k.
- **Storytelling matters most for high-involvement products** (cars, holidays, iPhones). Nobody buys a car from one post. Apple sells the story while the iPhone 14 and 16 look alike. The product decides whether people **buy again**. Branding decides whether they **try it the first time**.

#### 11.2 The founder is the face
- Examples: Iben for Sambal Bakar · Hermanto Tanoko (Cleo, Avian) with his own podcast · Elon Musk as the face of X (Jack Dorsey founded it but built less of a personal brand) · Agni, a Kadev member who is the face of her own risol business.
- **Hired talent is a risk.** The face leaves, or appears in other brands' content. *"People trust people, not logos."* People ask friends for recommendations before they trust brands.

#### 11.3 From story to brand: three steps and three questions
**Steps:** framework story → frame it as the brand (the founder as the face) → marketing.
**Three questions:**
1. What is the **core value**? (Kadev: spreading personal-branding knowledge.)
2. What **problem** do you solve for customers? (People start without direction and learn better with guidance.)
3. What **feeling** should every interaction leave?

**HMNS perfume example:** perfume brands describe scent notes most buyers can't tell apart. HMNS sells emotion and story instead. When a customer complained that a product photo was off-centre, HMNS replied that it was deliberate: *humans are imperfect*. A complaint became a brand moment.

#### 11.4 Persona: archetype, font, colour
- **12 brand archetypes** in four groups (connection, stability, legacy, spirituality): Everyman (IKEA: rooms set up so anyone can picture living there) · Caregiver · Ruler · **Creator** (Lego) · Innocent · Sage · Explorer · **Rebel** (Liquid Death: water in a menacing can) · Magician · Hero · Lover · Jester. Pandawara Group is used as a personal example (a steady clean-rivers message). Pick one and keep the message consistent for years.
- **Font** signals character: serif = tradition, respectable · display = friendly, expressive (Lego) · script = elegant, luxury (Hermès, LV) · modern sans = bold, strong. For personal branding this shows up in **caption and on-screen text fonts**. Change CapCut's default.
- **Colour psychology**: black = sophisticated, powerful, luxurious · white = pure, clean · red = passion, danger (Ferrari) · pink = feminine, romantic · brown = natural, genuine, trustworthy · Rich uses **orange = enthusiasm**. Apply it through shooting set-up and grading.
- **Rich's caveat:** font and colour are a *"condiment"*, a minor finishing touch. *"By the end of the day kita yang bikin narasinya."* Any colour works if you give it a narrative. Ideally keep **one** identity colour across your personal account and community.
- Q&A: an ADHD creator's deliberately busy edits drew *"berisik banget"* complaints from non-target viewers. The mentors' answer was to keep the style that serves the target audience.

---

### 12. Networking in practice (mentoring "Networking Strategy", 21 Okt 2025)

Speaker: Kiki (Arif Maliki), a student when he started. PING itself is on the slides (`kadev-personal-branding.md` §13.1). This section keeps only what the talk adds.

- **For a student, personal branding means *pamer*: showing experience, value and insight.** Kiki's LinkedIn in 2022 was empty. By 2024 it brought HR outreach, multinational projects, and organisations inviting him straight in without selection.
- **Post rejections as positive content.** He was rejected from **60+ internships** (*"rejection is a routine"*) and posted about it. Connections who saw it offered feedback and referrals.
- **Referral beats a perfect CV.** Most people stop at "learn CV, learn interview". The missing steps are personal branding and then a referral. Claimed: *"7 dari 10 HR melakukan background check"* on social media, citing *"a paper"* without naming it, so don't present it as a sourced number. Recruiters and anyone who might refer you check your LinkedIn, Instagram and TikTok first.
- **Interpersonal communication, as cooking:**
  1. **Ingredients**: prepare what you'll talk about, so the online impression survives meeting you in person.
  2. **Recipe**: STAR structure (situation, action, result).
  3. **Technique**: body language, expression, word choice fitted to the listener.
  4. **Seasoning**: emotion and empathy. **Research them first** (their background, their business), open with a **specific compliment** that proves you did the homework, and talk about what they care about right now. You've *clicked* when they start asking about you. **Don't be a *conversation killer***: always have a follow-up question.
- **Network strategy**: list your **needs** and your **haves**. Plan with two lists (people you know who match, and people you need to meet). Then grow the network outward.
- **Give value, raise the level**: keep sharing useful info and events. Move the relationship up (swapping info → competing together → building something together). **Give back** later, and don't show up only when you need something (*kacang lupa kulit*).
- **Generalists**: pick one sub-field for the long term. Find one mentor who is a generalist and one who is broad but has deep expertise in your chosen sub-field. Use Ikigai's questions to choose.
- **Following up with a VP after an event**: ask a question during the Q&A so the MC says your name. Research their education, past roles and achievements beforehand. Afterwards **skip the self-introduction**: open with a specific point from their talk and a compliment, find shared background, then make a specific ask. If you only pass in the hallway, use a sub-1-minute **elevator pitch**.

---

### 13. Anatomy of a viral format (mentoring, 30 Juni 2026)

Speakers: Nadif and Iqbal (the person behind Kadev's own content and modules).

- *"There's no new editing hack."* Everyone already posts consistently, learns editing and follows trends. What separates accounts now is a **distinctive format**: a way of presenting that is recognisably yours.
- Nadif's own before/after: an idealistic, self-centred cinematic edit flopped. A simple, relatable **10×10** with memes and a daily-life topic got saved and reposted.
- **Formats trending now** (mostly from creators outside Indonesia, which makes them an advantage here): *What's the difference* · green screen · game format · psychological test · reflection text · the Kumar format (1M followers in under 3 months) · picture storytelling · real-life analogy.
- **A distinctive format only works with strong storytelling.** Copy the format, never the script. Change the context and topic to fit your audience.

#### 13.1 Editing elements that help delivery, not decoration (Iqbal)
Complex edits take long and still don't guarantee a hit, so they're a bad fit for people who work or study all day. Pick from these:
1. **Subtitles that are accurate and easy to read**: placed **near the middle, not at the bottom edge**, so the eyes don't jump between face and text. Bold, larger (around size 14), with a shadow, one word at a time if you like. Spell foreign terms correctly.
2. **Lock the first 3 seconds** with a **large headline text** at the top in a contrasting colour: *"3 alasan kenapa kamu gak boleh jadi people pleaser."*
3. **Zoom in and out** to add depth and pull focus onto the key line.
4. **Cut pauses, errors and long breaths.** In a 3-minute video it adds up, and it makes you sound connected to your script.
5. **B-roll, SFX and assets that clarify**: when you say *bingung*, show someone confused.
6. **SFX map:** **whoosh** = zoom in/out · **pop / click** = pop-up overlay · **camera shutter** = transition · **magic refill** = revealing something · **"fsh"** = punchline.
Not every video needs every element. An eye-to-eye talking head may need no B-roll, and a text + music piece needs no subtitles.

#### 13.2 From the Q&A
- **Instagram vs TikTok behave differently.** Instagram favours education, inspiration and news. TikTok favours storytelling and easy entertainment. The same video can win on one and flop on the other.
- A design-tutorial creator's views dropped: the low performers opened on a **dark B-roll**, while the winners opened **bright and high-contrast with the bullet points on screen**. Nadif's fix is **anchoring with a number** (10×10 and the like) up front.
- **Keep deep ("daging") content to about 20%.** Beginners always outnumber experts, so basic content reaches more people. *"Kalau kamu merasa kontennya terlalu dasar, berarti bukan kamu target marketnya."* Advanced material belongs in your own class, down the funnel.

---

### 14. What the agent must do with this file

- **Format is a ledger field.** When logging a script, store `format` as one of the 15 names in §1. `ledger.py suggest` should prefer an untried format when the account has no winner.
- **For selling scripts, PAS is the default spine.** An agitation beat is required. A script that goes straight from problem to solution fails the gate.
- **Every idea needs a source** from §2.3. No source means the idea is invented, which is the definition of AI-ish content.
- **Diagnose before rewriting.** If the user shares stats, use the §3 table first. Most "bad script" complaints turn out to be format, lighting, market or goal problems.
- **Log the funnel stage** (`--funnel tofu|mofu|bofu`, §5). A small account starts at TOFU. `ledger.py suggest` warns when no recent piece is TOFU.
- **Spoken scripts use *kamu* or *kita*, never *kalian*.** Never open with *hai guys / welcome back / izinin aku*. Mark lines the user should re-say in their own words (§8).
- **Opinion and education scripts:** write the thesis and 3–4 sourced arguments before the hook (§4.3). Prefer **primary sources** over other creators' takes (§10.3).
- **Find the plain-language angle** of a news item instead of restating it (*konstruksi* → *tukang*, §10.3).
- **Define the ICP before content** (§10.1). A viral idea aimed at the wrong audience is a failure, not a win.
- **Judge winners on balanced engagement** (views + comments + shares + saves), not views alone (§10.3). Then test → win → replicate at 80/20 (§5.3).
- **Series are allowed repeats.** Log episodes with a shared `series:<name>` theme and expect the similarity warning (§6.2).
- **The niche is the person** (§7). Don't reject an idea just because it's outside the topic label if it serves the user's message. Always keep a story pillar.
- **Unsourced statistics in this file** (the 75% UMKM claim in §11.1, "7 of 10 HR" in §12) must not be repeated to a user as fact.

---

### Provenance

| Section | Source | Speaker |
|---|---|---|
| §1 | `22 Juli 2026 - Live Mentoring VIP Member Kadev Academy - Topik Format Winning` (7,687 s) | Kadafi Devayana |
| §2 | `27 Agustus 2026 - Live Mentoring VIP Member Kadev Academy - Formula Script Viral & Jualan` (7,233 s) | Nadif (mentor), hosted by Kadafi Devayana |
| §3 | Q&A sections of both recordings | Kadev, Nadif, Rich |
| §5 | `[17 Maret 2026] Kadev Academy - Mentoring VIP - Content & Marketing Funnel` (7,177 s, Groq whisper-large-v3) | Kadev, Rich |
| §6 | `[16 Jan 2065] Mentoring - Trial Reels & Link a Reel` (6,765 s, Groq; the year in the filename is a typo for 2026) | Nadif, Kadev |
| §7 | `[13 Des 2025] Mentoring - 2026 Algorthm & Strategt (1)` (8,135 s, Groq) | Kadev, Rich |
| §8 | `[27 Mei 2026] Kadev Academy - Mentoring VIP - The Art of Yapping` (6,685 s, Groq) | Kadev, Nadif, Rich |
| §9 | Lesson videos `(1 3)`, `(3.1 2)`, `(3.1 6)`, `(3.2 6)` (faster-whisper local) | Kadev, Arif Maliki |
| §10 | `[18 April 2026] Kadev Academy - Mentoring VIP - Dapetin 10K Followers dalam 3 Minggu` (7,522 s, Groq) | Rich, Kadev |
| §11 | `Kadev Academy - VIP Mentoring - February 21, 2026` (6,194 s, Groq) | Rich, Nadif |
| §12 | `[21 Okt 2025] Mentoring - Networking Strategy` (5,804 s, local) | Kiki (Arif Maliki), Hardy |
| §13 | `[30 Juni 2026] Kadev Academy - Mentoring VIP - Anatomi Format Viral` (7,284 s, Groq) | Nadif, Iqbal, Kadev |
| §4 | `[21 Okt 2025] Mentoring - Attention Economy` (4,312 s) | Nadif, Kadev, Rich, Kiki |

Transcribed locally with faster-whisper `small` (int8). Transcripts are in `transcripts/kadev/`. Whisper mishears names (*"Bruno Nadif"* = *"Bro Nadif"*, *"persemblending"* = *"personal branding"*). Numbers were checked against context. The 118k views figure and the 3.3M reference are spoken claims shown on screen, not verified.

<!-- journal 2026-09-24: first file built from transcripts rather than slides. The six-element order spoken by Nadif is pain / number / promise / opinion / urgency / interaction; the slide order puts urgency 4th and opinion/story 5th. Same six, different order — the slide says order doesn't matter, so no change to kadev-script-formulas.md. Edit freely; keep the provenance table in sync. -->

---

# Part 6. viral-edit-teardown.md

## Viral edit teardown: what 82 reference videos actually do

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Corpus:** all 82 `.mp4` files in `E:\Download\CONTOH INSPIRASI TEKNIK NGOTEN DAN EDITING VIDEO` — reference videos the user collected as examples of viral, well-made Indonesian short-form content. Creators: `bahasvideo`, `fitrisitisalma`, and `kadafidevayana` (the bulk).
> **Editable:** every number here is reproducible with the commands in §1. If you re-measure, update the numbers *and* the date.

### Why this file exists, and an honest note on method

The user asked SpliceCraft to learn editing, opening and closing technique from these videos so community users stop reporting that edits feel AI-ish.

Claude cannot watch video. So rather than guess at "technique" and dress the guess up as analysis, every file was **measured** with `ffprobe` and `ffmpeg` scene detection. What follows is what the measurements support, and nothing more. Where a claim is inference rather than measurement, it says so.

This turned out to matter: the measurements **contradicted** two things that seemed obviously true before the data came in. Both are documented in §6 rather than quietly dropped.

---

### 1. Method, so you can reproduce or challenge it

```bash
## per-file: dimensions, fps, duration
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate \
  -show_entries format=duration -of csv=p=0 "$f"

## per-file: scene-cut timestamps
ffmpeg -hide_banner -nostats -i "$f" \
  -vf "scale=160:-2,select='gt(scene,0.3)',showinfo" -f null - 2>&1 \
  | grep -o "pts_time:[0-9.]*" | cut -d: -f2
```

Downscaling to 160 px wide before scene detection makes the pass fast and does not meaningfully change cut detection.

**Known limits of this method, stated up front:**

- **Threshold 0.3 is conventional but untuned.** It under-counts cuts between visually similar shots — two angles of the same person against the same wall read as one continuous shot. So the "single-take" bucket in §3 may be slightly overstated. The bimodality is far too strong to be a threshold artifact, but the exact bucket sizes are soft.
- **A scene cut is not the only kind of edit.** Speed ramps, zooms, caption changes, and overlay animations are all editing and none of them register here. A video with zero scene cuts is not necessarily an unedited video.
- **53 of 82 files are 540×960** — re-compressed downloads, not masters. Fine for cut detection; useless for any conclusion about grading, grain, or colour.
- **No audio or transcript analysis.** No transcription backend was available this session. Music, loudness, ducking, and anything about what is *said* are unmeasured.

<!-- journal: raw per-file data lived in the session scratchpad and was not committed - it is ~82 lines of timestamps and regenerating it takes about 12 minutes. If you need it, re-run the commands above. -->

---

### 2. The corpus at a glance

| | |
|---|---|
| Files | 82 |
| Resolution | 540×960 (53), 1080×1920 (27), 360×640 (2) — **all 9:16 vertical, no exceptions** |
| Frame rate | 30 fps (80), 60 fps (2) |
| Duration | min 12.7 s · p25 22.2 s · **median 37.5 s** · p75 66.0 s · max 132.8 s |

**Duration is bimodal.** This is the first of three bimodal findings and they all point the same way.

| Bucket | Count |
|---|---|
| 10-20 s | 14 |
| **20-30 s** | **24** ← cluster |
| 30-45 s | 10 |
| 45-60 s | 9 |
| **60-90 s** | **17** ← cluster |
| > 90 s | 8 |

Two clusters — a quick hit at 20-30 s and a full story at 60-90 s — with a visible dip at 30-60 s between them.

**What follows:** pick which of the two jobs you are doing before you write. Landing at 50 s is usually what happens when nobody decided. See `kadev-script-formulas.md` §8 for the matching word budgets.

---

### 3. The headline finding: real edits are bimodal, AI-ish edits are uniform

Average shot length (ASL = duration ÷ number of shots) across all 82:

| | ASL |
|---|---|
| min | 0.54 s |
| p25 | 1.87 s |
| median | 3.23 s |
| p75 | 11.63 s |
| max | 46.35 s |

That p25-to-p75 spread — 1.87 s to 11.63 s — is not a distribution around a centre. It is two populations:

| Mode | ASL | Videos | Share | What it is |
|---|---|---|---|---|
| **Cut-driven** | 0.5 - 2.5 s | 32 | 39% | b-roll, voiceover, documentation, list content, jedag-jedug |
| *(dead zone)* | 2.5 - 8 s | 27 | 33% | mixed or transitional |
| **Single-take** | 8 s to no cuts | 23 | 28% | talking head, straight to camera |

Full ASL histogram: `<1 s` (3), `1-1.5 s` (5), `1.5-2.5 s` (24), `2.5-4 s` (10), `4-8 s` (17), `>8 s` (23).

**Six videos have zero scene cuts at all**, running 18.7 s, 29.5 s, 43.6 s and 46.3 s among others. They are in a folder the user collected as examples of good work. They are not under-edited — they are a different grammar: one take, one person, captions, nothing else.

Length correlates with mode, and not in the direction most people assume:

| | Median ASL |
|---|---|
| Videos under 30 s | 3.97 s |
| Videos 60 s and over | **2.00 s** |

**Longer videos cut faster.** A 90-second video earns its length by moving; a 20-second video can hold a single shot because it is over before attention runs out.

#### Why this is the anti-AI-ish rule

The failure is not "too many cuts" or "too few". It is **landing in the middle by default** — a cut every 3-4 seconds for the whole runtime regardless of what is being said. Nobody chooses that rhythm. It is what you get when a tool applies a uniform rule to non-uniform material.

**The rule:** choose the mode before planning the edit, and commit to it.

- Talking head, one location, personal story → **single-take mode**. Cuts only where a sentence is removed. Zero cuts is a legitimate outcome.
- Voiceover over b-roll, a numbered list, a tutorial → **cut-driven mode**. Typical shot 1.3-2 s, and it *stays* there.

Never average the two.

---

### 4. Openings — measured

Restricting to the 32 cut-driven videos, since a single-take video has no opening cut by definition:

| | Time to first cut |
|---|---|
| p25 | 0.80 s |
| **median** | **2.22 s** |
| p75 | 4.00 s |

Across all 76 videos that have any cuts at all, the median is 4.33 s — pulled up by the single-take group.

#### The counterintuitive part

Cuts falling in the first 3 seconds, compared against what that video's own average cut rate would predict:

> **median 0.75×** — the opening cuts **slower** than the video's own baseline.

And the first shot compared to a typical shot in the same video:

> **first shot = 1.58× the median shot length.** In 56% of cut-driven videos the opening shot is more than 1.2× a typical one.

In absolute terms: first shot **2.22 s** median, against a typical shot of **1.32 s**.

**The hook is held, not chopped.** This is the opposite of the "chop the first three seconds to grab attention" instinct. The opening shot stays on screen long enough for a person to read the on-screen hook and hear the spoken one — and *then* the video starts moving.

**What follows for the edit:**
1. Give the hook shot roughly **1.5× your typical shot length**. Do not cut into it to seem energetic.
2. Something should still *change* early — a zoom, a card, a movement. Held is not the same as static.
3. The hook is spoken **and** on screen simultaneously. Many viewers start muted, and 8 seconds is the whole budget (`kadev-personal-branding.md` §7.1).
4. No logo animation, no intro card. The corpus has none.

---

### 5. Closings — measured, and the strongest finding in the file

Gap from the last scene cut to the end of the video:

| | All 76 with cuts | Cut-driven 32 |
|---|---|---|
| p25 | 2.21 s | 1.15 s |
| **median** | **3.56 s** | **3.16 s** |
| p75 | 4.33 s | 4.09 s |

Cuts in the final 3 seconds versus the video's own baseline rate:

> **median 0.21×** — the closing cuts at roughly **one fifth** of the video's normal rate.

Last shot versus a typical shot in the same video:

> **last shot = 2.42× the median shot length.**
> **24 of 32 cut-driven videos (75%)** hold their final shot more than 1.2× longer than a typical one.

In absolute terms: last shot **3.16 s** median, against a typical shot of **1.32 s**.

**The ending is a landing, not a stop.** The final line is delivered on one held shot, with the cutting essentially switched off. This is consistent across three quarters of the corpus — the most consistent single behaviour measured.

**What follows for the edit:**
1. Give the closing line its own shot and **hold it ~2.4× your typical shot length** — around 3 seconds in a fast edit.
2. Stop cutting entirely for the last ~3 s. No flourish, no rapid montage over the CTA.
3. That held shot is where the Storytelling Hack's beat ⑤ lands — the line that reverses the opening (`kadev-script-formulas.md` §3). It needs room to be heard, because it is what makes the video loop.

#### The shape, in one line

> **Hold the open · chop the middle · hold the close.**
> 1.58× — 1.0× — 2.42×

That is the measured grammar of this corpus. It is also, usefully, the exact shape a uniform automatic cutter will never produce.

---

### 6. Two things I got wrong, corrected

Both of these were written into `anti-ai-ish.md` before the timestamp measurement finished, on the strength of general short-form convention. Both were wrong for this corpus and have been corrected there. Recording them here because the wrong versions are widely believed.

**Wrong: "the first cut lands a median of 1.2 s in."**
That figure was the **p25**, misread as the median. The actual median is **2.22 s** for cut-driven videos and 4.33 s across the corpus. More importantly, the direction was wrong — openings cut *slower* than baseline (0.75×), not faster.

**Wrong: "ends on the last word, no tail — do not add a 2-second tail."**
The opposite is true here. The median final shot runs **3.16 s** and is **2.42× longer** than a typical shot, in 75% of cut-driven videos. The "tail" is not dead air; it is the held landing the closing line is delivered on. Cutting it off truncates the beat that makes the video loop.

The general advice these came from is not nonsense — it is aimed at padded, dead-air endings. But applied to this style it removes the single most consistent thing the corpus does.

---

### 7. What is *not* measured, and must not be asserted

Be honest with users about the boundary. The following were **not** measured and any claim about them is opinion:

- **Music** — presence, genre, loudness, ducking behaviour. No audio analysis was run.
- **Captions** — style, position, karaoke timing, font. Not detectable from scene cuts.
- **Zooms, speed ramps, transitions** — invisible to scene detection. The claim in `anti-ai-ish.md` §C4 that "cuts are hard cuts and flashy transitions appear at topic changes" is **inference from the ASL distribution, not measurement.** Flagged as such there.
- **Colour, grading, lighting** — most files are re-compressed 540×960; no valid conclusions available.
- **What is actually said** — no transcripts. Everything about script content comes from the Kadev course material, not from these videos.
- **Whether these videos actually performed well.** They are in a folder the user labelled as inspiring and viral. No view counts, no engagement data. Treat the corpus as "what this creator considers good", which is a real signal, not as verified top performers.

---

### 8. Applying it

| Decision | Setting |
|---|---|
| Aspect ratio | 9:16, always. 100% of the corpus. |
| Duration | 20-30 s **or** 60-90 s. Decide which. |
| Mode | cut-driven (ASL 1.3-2 s) **or** single-take (few cuts to none). Decide which. Never average. |
| Opening shot | ~1.5× your typical shot. Hold the hook. |
| Middle | stay in your chosen mode |
| Closing shot | ~2.4× your typical shot, ~3 s. Stop cutting. |
| Tail | keep it — it is the landing, not dead air |
| Longer video | cut *faster*, not slower |

Wired into `SKILL.md` Step 4 (mode choice) and `anti-ai-ish.md` §C (the gate).

### 9. What they *say*: openings and closings from the transcripts

§§2–8 measure the cutting. This section measures the words. All 80 reference videos were transcribed (faster-whisper `small`, `transcripts/reference/`). **76** have enough speech to count, i.e. 15+ words. Almost all are Kadafi Devayana's own shorts, so this describes **one successful creator's spoken grammar**, not Indonesian short-form in general. Median script length is **112 words** (p25 61, p75 200).

#### 9.1 Counts

| Pattern | Videos | Share |
|---|---|---|
| Opens with a greeting (*halo, hai, balik lagi*) in the first 5 words | **0** | **0%** |
| Opens by announcing the video (*"di video ini…"*) | 2 | 3%. Both are tutorials, one of them by a different creator |
| First sentence addresses the viewer (*kamu / lu*) | 27 | 36% |
| A number in the first 20 words | 18 | 24% |
| Opens with *Ini… / Kalau… / Pakai…* (a demonstrative or conditional frame) | 27 | 36% |
| Closes by summarising (*jadi itulah, semoga bermanfaat, demikian*) | **0** | **0%** |
| Closes with a comment keyword → DM (*"ketik X, nanti aku kirim lewat DM"*) | 20 | 26% |
| Closes with an answerable question (*sepakat gak?, komen di bawah*) | 17 | 22% |
| Asks for a follow | 35 | 46% |
| Asks for a repost or share | 28 | 37% |

Counted with keyword regexes over the plain transcripts. Whisper mangles the sign-off (*"lipos kalau bermanfaat"* = *"repost kalau bermanfaat"*), so the regex accepts the common mishearings. Treat the counts as ±2.

#### 9.2 The opening shapes that recur

Verbatim, lightly cleaned of transcription errors. Each is a **template**. Reusing the wording word-for-word is the fastest way to sound like a copy.

| Shape | Example |
|---|---|
| **Ini X, dan ini Y. Apa bedanya, dan kamu yang mana?** | *"Ini pencitraan, dan ini personal branding. Apa bedanya, dan kamu yang mana?"* (also: konten vs personal branding, bakat vs skill, hiburan vs edukasi, cringe vs yang ngatain cringe) |
| **The ladder**: *Kalau kamu A → B. Kalau A + C → D. …* | *"Kalau kamu ngonten, orang bakal notice kamu. Kalau ditambah niche, orang bakal kenal kamu. Kalau ada formula dan scripting, orang bakal follow kamu…"* |
| **Chant / repetition** (7–15 s shorts) | *"Sehari sekali. Seminggu sekali. Sebulan sekali."* Or one line said four times with rising energy |
| **Tunjuk list** | *"Pakai sound ini kalau konten kamu emotional. Pakai sound ini kalau edukasi…"* |
| **"Aku mau kamu nonton ini."** | Show a clip first, then *"Menurut kamu ada yang aneh? Ada."* |
| **A contrarian claim** | *"Jangan bangun followers, tapi bangun trust."* / *"Kalau aku lebih pilih bangun trust daripada sekadar viral."* |
| **A stranger's result** | *"Ada penjual kambing di Jawa Timur, followersnya tembus 100.000 cuma dalam 3 hari."* |
| **A famous-brand anomaly** | *"Ada brand yang logonya nempel di ketiak pemain World Cup 2026."* / *"Marvel dibangun dari nol banget."* |
| **Before → after** | *"Dulu kontenku sering sepi kayak gini. Sekarang bisa viral kayak gini."* |
| **The objection, in the viewer's voice** | *"Aku gak punya penghasilan karena susah cari kerja. Aku gak bisa investasi karena gajiku kecil."* |
| **A quiz with a wrong answer** | *"Juara 3 Piala Dunia 2018? Nggak inget kan? Aku nyebut Inggris juga kamu pasti percaya."* |

What's absent is as useful as what's there: no greeting, no *"pernahkah kamu"*, no *"di video kali ini aku akan…"*, and no statement of what the video is about.

#### 9.3 The closing is two parts

The corpus shows a stable two-part close:

1. **One engagement move**, which is the real CTA. Either a comment keyword that triggers a DM freebie (*"Ketik SOUND, nanti aku kirim list lengkapnya lewat DM"*) or a question with two defensible answers (*"Viral dulu atau cuan dulu? Yuk diskusi di komen."*, *"Sepakat gak?"*).
2. **A fixed brand tagline**, the same words in every video: *"Repost kalau bermanfaat, dan follow untuk tips personal branding dan konten lainnya."* Sometimes it's an identity line instead: *"Aku Kadafi Devayana, teman kamu buat upgrade konten dan personal branding tiap hari."*

Part 2 has two asks (repost and follow), but it doesn't work as a stack of CTAs. It's a **signature**, recognisable because it never changes, and it tells the viewer the topic to follow for. The fault `anti-ai-ish.md` §B5 names (*"like, comment, share, save, dan follow!"*) is different: five **new** asks invented for this video, none of them tied to a topic.

**For the agent:** write exactly one engagement move per script. If the user has a fixed tagline, append it unchanged. If they don't, help them write one **once** and store it in the ledger's `notes` of their first entry. Never generate a fresh multi-ask sign-off per video.

#### 9.4 What this adds to the gate
- Greeting in the first sentence: **reject**. 0 of 76 do it.
- Summary close: **reject**. 0 of 76 do it.
- Two or more *different* engagement moves (a keyword **and** a question **and** "save"): **reject**.
- No number, no *kamu*, no contrast frame and no named stranger in the first sentence: **warn**. The hook has none of the recurring shapes.

<!-- journal 2026-09-24: §9 added from transcripts. Before this, the skill knew how the corpus cuts but not what it says. The two-part close contradicted the site checker, which flagged any script with 2+ CTA words; the checker was changed to count *engagement moves*, not words. Caveat kept in the text: this is essentially one creator's style. -->

---

### Reproducing

Re-run §1 over the folder. Roughly 12 minutes for 82 files on the machine this was measured on. If you change the scene threshold, say so here and re-state every number that moves.

---

# Part 7. content-memory.md

## Content memory: the ledger

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Tool:** `scripts/ledger.py` (standard library only, Python 3.9+)
> **Store:** `~/.splicecraft/ledger.json` on the user's own machine. Nothing is uploaded anywhere.

### Why this exists

An AI asked for "ide konten personal branding" produces roughly the same twelve ideas every time it is asked. One user, over one month, ends up with an account that says one thing twelve ways. The course diagnoses inconsistency as the killer; the modern failure is the opposite — **sameness**.

The ledger is the fix: a local, permanent, user-owned record of every script, niche, hook and theme already produced, which the agent is required to consult *before* writing and required to update *after* producing.

It also solves a second problem. A user comes back three weeks later in a fresh conversation. The agent has no memory of the previous session. The ledger is that memory, and it lives on the user's disk rather than in a chat log.

---

### The contract

Two obligations, both mandatory, both wired into `SKILL.md`:

1. **Before writing any script or idea list** → `ledger check`. Exit code 2 means do not write it.
2. **After producing anything** → `ledger add`. Idea, script, or finished video — log it with its angle.

An agent that skips step 2 breaks the tool for every future session. Logging is not optional bookkeeping; it is the product.

---

### Setup

```bash
LEDGER="python <skill-folder>/scripts/ledger.py"
$LEDGER init
```

Prints the store path. Run once per machine. If it already exists, it says so and does nothing.

To keep the ledger somewhere else (a synced folder, a project directory):

```bash
$LEDGER --store "D:/brand/ledger.json" init
## or, for the whole session:
export SPLICECRAFT_LEDGER="D:/brand/ledger.json"
```

---

### Checking before you write

```bash
$LEDGER check "3 cara stop prokrastinasi buat mahasiswa" --theme prokrastinasi
```

```
checking: "3 cara stop prokrastinasi buat mahasiswa prokrastinasi"
against 14 entries

  BLOCK   71%  478aac15  2026-08-02  3 langkah biar gak prokrastinasi lagi
              angle: pakai timer fisik bukan app
  warn    48%  1dd93368  2026-07-19  kenapa to-do list kamu gak kepake
           9%  9f10ac22  2026-07-05  cerita gue gagal 4 tahun bikin konten

VERDICT: too close. Do not write this.
```

| Exit code | Meaning | What the agent does |
|---|---|---|
| 0, score < 45% | clear | write it |
| 0, score 45-61% | adjacent | allowed, but the agent must **say out loud what is new about it**. If it cannot, treat as a repeat. |
| **2**, score ≥ 62% | collision | **do not write it.** Change the angle, the pillar, or the audience segment. |

Useful flags: `--niche` restricts the comparison to one superniche first (falls back to everything if that niche is empty); `--json` for machine-readable output; `--hook` and `--angle` sharpen the probe.

#### How the score works

Two scores are computed and **the stronger wins**:

- **Topic-level** — topic + themes only, scaled to 0.92. Catches "you already covered this subject" even when the hook and angle differ. Because it is capped below 1.0, a pure subject repeat lands in WARN, not BLOCK: reusing a subject with a genuinely new angle is allowed, it just has to be declared.
- **Full-text** — topic, themes, hook, angle and premise together. Catches an actual rewrite, which blocks.

Each score blends unigram **overlap** (`|A∩B| / min(|A|,|B|)`) at 65% with bigram **Jaccard** at 35%. Overlap rather than Jaccard on unigrams because Jaccard punishes the short side — a five-word topic compared against a fully-filled entry scored low purely because the union was large, which let real repeats read as "clear". Bigrams stay Jaccard because they measure shared *phrasing*, where union size is meaningful, and phrasing is what separates "same subject, new angle" from "same script, reworded".

Indonesian and English stopwords are removed, plus words that appear in nearly every content brief (`konten`, `video`, `tiktok`, `script`, `tips`) and therefore carry no signal. A light Indonesian stemmer collapses `mengedit` / `editing` / `edit`.

<!-- journal: thresholds WARN_AT=0.45 / BLOCK_AT=0.62 were set by hand against a small set of constructed cases (a near-duplicate, a verbatim rewrite, an unrelated topic) and verified to give warn/block/clear respectively. They are not tuned against real user data because none exists yet. Expect to revisit once a real ledger has ~50 entries. Both constants are at the top of ledger.py and are meant to be edited. -->

---

### Logging after you produce

```bash
$LEDGER add "3 cara stop prokrastinasi buat mahasiswa" \
  --niche "produktivitas mahasiswa" \
  --pillar educate \
  --hook-template 11 \
  --hook "Ini adalah 3 langkah untuk stop prokrastinasi" \
  --angle "pakai timer fisik, bukan aplikasi" \
  --theme prokrastinasi --theme mahasiswa \
  --premise "dari mahasiswa yang selalu telat jadi yang selesai duluan" \
  --platform tiktok --format talking_head --seconds 32 \
  --script-path work/script.md --video-path work/edited.mp4 \
  --status published
```

Every field except the topic is optional, but the ones that matter most for future de-duplication are **`--angle`** and **`--theme`**. The angle is the sentence that answers *"what made this one different?"* — without it, the ledger can tell you that you covered a subject but not how.

`add` always reports the nearest existing entry. Logging a near-duplicate is permitted — the user may have decided it is fine — but it is never silent.

#### Fields

| Field | What goes in it |
|---|---|
| `topic` | what it was about, in the user's own words |
| `niche` | the superniche it serves |
| `pillar` | `educate` / `inspiration` / `entertaining` / `promotion` |
| `hook` | the actual hook line used |
| `hook_template` | which of the 20 templates (`kadev-script-formulas.md` §4) |
| `angle` | **what made this one different** |
| `themes` | repeatable tags |
| `premise` | the premis this serves (`kadev-personal-branding.md` §2.4) |
| `platform`, `format`, `seconds` | production facts |
| `script_path`, `video_path` | where the artifacts live |
| `status` | `idea` / `scripted` / `filmed` / `produced` / `published` |
| `performance` | reserved; fill later by hand with views, saves, comments |
| `notes` | anything |

Log at `--status idea` too. A rejected idea is worth remembering — it stops the agent proposing it again next month.

---

### Reading the ledger back

```bash
$LEDGER list --limit 20              # recent, newest first
$LEDGER list --pillar educate        # filter
$LEDGER stats                        # pillar balance, niche mix, hook fatigue, cadence
$LEDGER themes                       # everything covered, ranked
$LEDGER suggest                      # what is under-used and due next
$LEDGER show <id>                    # one entry in full
$LEDGER export --format md --out ledger.md
$LEDGER export --format csv --out ledger.csv
```

`stats` is the one to run at the start of a strategy conversation:

```
PILLAR BALANCE
  educate          9    64%  ###############
  inspiration      3    21%  #####
  entertaining     1     7%  ##
  promotion        1     7%  ##

NICHE MIX  (target 80 / 15 / 5 - superniche / adjacent / personal)
  personal branding             11    79%
  self development               2    14%
  kehidupan personal             1     7%

HOOK TEMPLATES USED
  #11       4  <- leaning on this
  #2        3
  #7        2

CADENCE  2026-07-05 -> 2026-09-14  (71 days)
  1.4 pieces per week
  last entry was 9 days ago
```

That readout answers, with evidence: is the 80/15/5 ratio holding? Is the account a pillar monoculture? Is the same hook template being reused until it burns out? Has the user actually stopped posting?

`suggest` turns the same data into a recommendation — which pillar is due, which hook templates are fatigued, and the last five topics so the agent does not circle back.

---

### Editing and correcting

The store is plain JSON, indented, UTF-8. The user can open it in any editor. From the CLI:

```bash
$LEDGER edit 478aac15 --set status=published --set "notes=did 40k views"
$LEDGER edit 478aac15 --set "themes=prokrastinasi,mahasiswa,produktivitas"
$LEDGER remove 478aac15
```

IDs are matched by prefix — the first 8 characters shown in `list` are enough.

If the file is hand-edited into invalid JSON, every command fails with a message naming the file and the parse error rather than silently starting over. Writes go to a temp file and are then moved into place, so an interrupted write cannot truncate an existing ledger.

---

### Privacy

- The ledger never leaves the machine. There is no network code in `ledger.py`.
- It is a plain file the user owns, can read, can back up, can delete.
- It records what the user made. If a topic is sensitive, they can `remove` it or edit the file directly.
- Do not copy ledger contents into anything that gets published.

---

### Limits

- Similarity is lexical, not semantic. *"cara berhenti menunda pekerjaan"* and *"stop prokrastinasi"* mean the same thing but share no tokens, and the ledger will not catch it. The `--theme` tags exist to bridge this — **tag consistently and the gap mostly closes.**
- One ledger per machine by default. A user running several brands should use `--store` per brand, or `SPLICECRAFT_LEDGER` per session.
- Performance data is not collected automatically. The `performance` field is there to be filled in by hand.
- The thresholds are hand-set, not learned. See the journal note above.

<!-- journal: the lexical-vs-semantic limit is the known weak point. An embedding-based check would fix it but would need either a model download or a network call, and this skill is deliberately offline and stdlib-only. If that constraint is ever relaxed, this is the first thing to upgrade. Until then, the --theme discipline is what carries it, which is why SKILL.md tells the agent to always pass themes. -->

---

# Part 8. script-and-marketing.md

## Script, hooks, and platform strategy

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Before the camera rolls, the script decides most of the edit. The planner can only animate what the speaker says: a number becomes a count-up, "first, second, third" becomes a ranking, a one-word sentence becomes a word hit. A flat script gives a flat edit at any level.

### The generator

```bash
$SC script "refund bond for online sellers" --genre hackathon_demo --seconds 60 --brief brief.json -o script.md
$SC script "cara pakai AI untuk edit video" --genre tutorial_docs --seconds 40 --language id
$SC library frameworks                       # all 100 structures
$SC library hooks --category curiosity       # 200 named hooks, risky ones flagged
```

`script` writes a timed skeleton: three hook options, every beat with its time window and word budget (2.6 words per second in English, 2.3 in Indonesian), retention rules, six titles, a description template, hashtags, and the exact render command. Your agent (or you) fills the "Your line" column. The generator does not invent facts; lines stay blank until someone who knows the project writes them.

### The anatomy every short needs

| Part | Seconds (45 s video) | Job | Test |
|---|---|---|---|
| Hook | 0-3 | stop the scroll | Would a stranger need the next sentence? |
| Context / why | 3-8 | tell them why they should care | Does it name who this is for? |
| Relatable | 5-12 | "that's me" moment | Is it a moment, not a category? |
| Tension | 8-20 | stakes, conflict, or an open loop | What happens if nothing changes? |
| Value / fact / demo | 12-35 | the payoff, with a number or a visual every 3-5 s | Is there proof? |
| Twist or verdict | 30-38 | answer the hook | Did you actually answer it? |
| Closing | 38-42 | callback to the hook, so the replay loops | Does the last line echo the first? |
| CTA | 42-45 | one action | Is there only one? |

### How to write a line the planner can edit well

- **Numbers out loud.** "Three minutes, two mistakes, zero edits" gives three count-ups. "A few minutes" gives nothing.
- **Ordinals for lists.** "First... second... third..." builds a ranking card.
- **Short sentences.** One idea per sentence. A 1-3 word sentence ("Rhythm.") becomes a giant word hit.
- **Say "before and after" or "versus"** when comparing: a head-to-head card appears.
- **Quote a line.** "They say..." gives a typewriter quote card.
- **Callbacks.** "Remember those numbers from the start?" brings the number card back.
- **Name the viewer.** "If you sell online..." is a tribe callout and raises completion for that group.
- **No greeting.** "Hi guys, welcome back" is 2 seconds of scroll bait. Start on the hook.

### 100 content structures (grouped)

Full list with steps: `$SC library frameworks` (source of truth: `presets/content.json`).

| Group | Count | Use when | Examples |
|---|---|---|---|
| conversion | 15 | selling, launches, sign-ups | AIDA, PAS, BAB, FAB, 4P, 4U, ACCA, PASTOR, QUEST, SLAP |
| story | 15 | founders, vlogs, nonprofits, brand | Hero's Journey, Pixar Pitch, Sparkline, Three-Act, SOAR, Mystery Box, Underdog, Inverted Pyramid |
| short | 15 | TikTok, Reels, Shorts | HVC, Pattern Disrupt, Contrarian-Proof-Twist, POV, Stop and Show, Open Loop, Mistake-Fix, Myth vs Fact, Endless Loop |
| education | 15 | tutorials, docs, explainers | What-Why-How, Rule of 3, Jargon-Buster, STAR, 5W1H, Checklist, Comparison Breakdown, Case Study |
| psychology | 15 | growth and reach | FOMO, Social Proof Stack, Us vs Them, Identity Shift, Curiosity Gap, Expectation vs Reality, Trojan Horse |
| community | 10 | comments and repeat viewers | Poll, Build in Public, Tier List, Stitch/Duet, Quiz, Resource Swap |
| ai | 15 | AI, SaaS, data | Prompt-to-Result, Automation Workflow, Micro-SaaS Teardown, Data Narrative, One-Prompt Solution |

### 200 hooks (grouped)

`$SC library hooks` lists all 200 by name. Ten groups of twenty: emotion, curiosity, value, visual_audio, social, story_format, interactive, data_ai, sales, meta. Twenty-four have fill-in templates the script generator uses.

#### Risky hooks: rules

Sixteen hooks are flagged `risky` (rage bait, outrage, paranoia bait, guilt, insecurity, data-leak framing, replacement threat, price shock, fake-out, accidental reveal, competitor flaw, tea spilling, common enemy, peer pressure, freebie bait, discontinuation warning). They work by pushing an emotion, and they backfire when the claim is not true.

An agent using this skill must:

1. Use a risky hook only when the claim is true and the video proves it.
2. Never invent scarcity, deadlines, leaks, or quotes.
3. Never target a real private person, a protected group, or health or money fears with false claims.
4. Prefer a curiosity or value hook with the same payoff when unsure. They hold up better over time.

Platforms penalize misleading content and engagement bait in their community guidelines, and a fooled viewer does not follow.

### Titles, descriptions, hashtags, on-screen text

- **Title / first caption line:** the searchable phrase people type, plus the payoff. "Edit a video with AI in 60 seconds" beats "My new workflow!!".
- **Say the keyword in the first sentence** too. Short-video platforms use captions, on-screen text, and the spoken transcript for search.
- **Description:** line 1 is the hook and payoff (it shows before "more"), line 2 a concrete detail, line 3 the CTA, line 4 hashtags.
- **Hashtags:** 3 to 5. One broad, two niche, one branded. Walls of tags do not help.
- **On-screen hook text** in the first frame, because many people start muted. The hook card does this automatically at level 21+.
- **Cover frame:** the frame with the hook card and a clear face. `sheet.jpg` shows candidates.

### Platform strategy (researched 2026-09-15; re-check before relying on it)

| Signal | TikTok | Instagram Reels | YouTube Shorts |
|---|---|---|---|
| Strongest ranking signal | watch time and completion | completion; shares and saves above likes; skip rate added | watch time per impression (not swipe rate) |
| Completion bar people cite | around 70% | completion is the most weighted metric | ~65% average view duration under 30 s, ~50% for longer |
| Sweet spot length | 15-30 s for highest completion | under 3 min for non-follower reach (max 20 min) | 30-45 s |
| Discovery | small test audience (hundreds), then wider pools; search is a major channel | shares to DMs | watch-time driven feed |

What follows from that, and what the planner does about it:

- **Cut dead air.** Pause removal is the cheapest completion gain. Every level removes pauses; higher levels remove more.
- **Loop the ending.** A closing line that calls back to the hook invites a replay (rewatch and loop rate are ranking signals).
- **Captions always.** Captioned videos are reported to get more watch time and completion. The exact "85% watch muted" figure is widely repeated but traces to a 2016 publisher claim; do not quote it as fact.
- **Earn shares and saves.** Checklists, numbers, and "save this" CTAs in consideration content. `funnel: consideration` in the brief sets this.
- **Post natively per platform.** Size and safe zones differ; see `references/audience-and-market.md`.

Nothing guarantees the For You page. The algorithm tests every video on a small audience first; the edit's job is to win that test.

### Sources

Checked 2026-09-15. Treat blog summaries as second-hand; platform pages change without notice.

- Hootsuite, How the TikTok algorithm works in 2026: https://blog.hootsuite.com/tiktok-algorithm/
- Darkroom, TikTok Algorithm 2026: https://www.darkroomagency.com/observatory/tiktok-algorithm-guide-2026-everything-we-know-about-how-videos-are-ranked
- Betterview, TikTok's 70% completion rate: https://betterview.nl/en/blog/tiktok-completion-rate-70-procent-2026
- Socialync, YouTube Shorts algorithm 2026: https://www.socialync.io/blog/youtube-shorts-algorithm-2026
- InstantDM, Instagram Reels reach 20 minutes: https://instantdm.com/blog/instagram-reels-reach-20-minutes-the-2026-limit-explained
- Fastlane, The Instagram Reels algorithm in 2026: https://www.usefastlane.ai/blog/instagram-reels-algorithm-2026
- Kapwing, Short-form video statistics 2026: https://www.kapwing.com/resources/short-form-video-statistics-tiktok-reels-and-shorts-by-the-numbers-in-2026/
- Vidico, 60+ short-form video statistics (notes the origin of the 85% muted claim): https://vidico.com/news/short-form-video-statistics/

---

# Part 9. audience-and-market.md

## Audience, market, and the project brief

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

The same transcript should not be edited the same way for Gen Z shoppers on Reels and for CFOs on LinkedIn. A brief file tells the planner who the video is for, and every edit decision follows from it.

### brief.json

Every field is optional. Unknown values stop with a list of valid ones.

```json
{
  "project": "Refund bond for online sellers",
  "platform": "tiktok",
  "market": "hackathon",
  "age": "millennial",
  "stage": "pre_revenue",
  "funnel": "awareness",
  "niche": "web3_crypto",
  "country": "ID",
  "seconds": 90,
  "tam": 64000000,
  "sam": 9000000,
  "som": 45000,
  "market_unit": "online sellers in Indonesia",
  "price": 5,
  "revenue_target": 20000,
  "view_to_profile": 0.01,
  "profile_to_click": 0.15,
  "click_to_buy": 0.02
}
```

Three worked examples are in `examples/briefs/`.

```bash
$SC brief brief.json                                   # what the brief changes, checks, revenue math
$SC plan work/words.json -o work/edl.json --level 60 --style auto --genre auto --brief brief.json
$SC script "your topic" --genre hackathon_demo --brief brief.json
```

### What each field changes

| Field | Options | Changes |
|---|---|---|
| platform | tiktok, reels, shorts, linkedin, youtube_long, x_twitter | level, card density, caption styles, output size, ideal length check |
| market | b2c, b2b, b2g, investor, creator, nonprofit, hackathon | level, density, caption styles, style, CTA |
| age | gen_z, millennial, gen_x, boomer, mixed | level (pace), caption size, caption styles, music energy, flashes off for older viewers |
| stage | idea, pre_revenue, growth, scale, enterprise | level, color grade (scrappy punchy vs polished cinematic vs safe clean) |
| funnel | awareness, consideration, conversion, retention | recommended frameworks, CTA |
| niche | tech_ai, saas_b2b, web3_crypto, finance, health_fitness, beauty_fashion, food, travel, education, gaming, real_estate, parenting, religion, local_business, automotive, career, entertainment | style, music moods, compliance warnings |
| tam / sam / som | numbers | sanity check (SOM <= SAM <= TAM), adds a market-size beat to investor, hackathon and B2B scripts |
| price, revenue_target | numbers | revenue math: buyers needed and views needed |
| view_to_profile, profile_to_click, click_to_buy | rates | replace the placeholder funnel rates with real analytics |

Effects stack in the order platform, market, age, stage, funnel, niche. `edl.json` stores the reasons under `params.brief.why`, so an agent can explain every choice.

Proof from the demo transcript at `--level 60` (same words, three briefs):

| Brief | Level | Captions | Style | Cards/min | CTA | Music |
|---|---|---|---|---|---|---|
| hackathon-web3 (TikTok, millennial) | 70 | highlight | neon | 8.5 | Try the live demo | tech_pulse, mid |
| b2b-saas-linkedin (Gen X, consideration) | 35 | highlight | editorial | 2.6 | Book a demo | corporate_clean, mid |
| genz-beauty-reels (conversion) | 90 | bounce | glass | 10.9 | Link in bio | bright_pop, high |

Generated by `tests/test_plan.py` (`test_briefs_change_the_edit`) and by planning `examples/demo/out/words.json` with each brief on 2026-09-15.

### TAM, SAM, SOM in a video

- **TAM**: everyone who could ever use this. **SAM**: the part you can reach with this product and channel. **SOM**: what you can realistically win in the next 1-3 years.
- In an investor or hackathon video, say them as three numbers in one sentence. The planner merges them into one count-up card.
- Source every number (report name and year) in the description. Judges and investors check.
- A revenue target that needs more buyers than the SOM is flagged as FAIL by `brief`.

### Revenue math

`views_needed = revenue_target / price / (view_to_profile x profile_to_click x click_to_buy)`

The default rates in `presets/audience.json` are placeholders so the formula runs. They are not benchmarks. Replace them with the user's own analytics before making plans with the output.

### Demographic notes (researched 2026-09-15; re-check)

- TikTok globally: 25-34 is the largest age group, 18-24 close behind.
- Indonesia is TikTok's largest market (reported over 180 million users), and around 40% of Indonesian TikTok users are reported to be 35 or older, so "TikTok means teenagers" is outdated there.
- Instagram in Indonesia: about 123.8 million users in August 2026, 54.7% women, 25-34 the largest group.
- B2B buyers: long cycles (60-180+ days) with several stakeholders; short proof-led clips under 60 s on LinkedIn and Shorts work for awareness, and the first 5 seconds decide retention.

Numbers differ between sources. Quote ranges, not decimals, in a video.

### Safe zones (researched 2026-09-15)

On 1080x1920: platform UI covers roughly the bottom 400 px (captions, audio line, buttons) and a strip on the right (about 140-180 px) for like and share icons; TikTok's overlay changes with caption length. A universal safe area is about 900x1400 centered.

What splicecraft does: captions at y 1390, cards in the top third starting at y 230, the CTA pill in the card zone at the top (moved out of the bottom zone in this version). Keep your own text inside x 60-900, y 140-1500.

### Sources

- NapoleonCat, Social media users in Indonesia 2026: https://stats.napoleoncat.com/social-media-users-in-indonesia/
- IDN Research Institute, Indonesia TikTok demographics: https://www.idnresearchinstitute.com/english/indonesia-social-media-demographics-platform-00-vnqjp-6nty80
- Useful Social Media, TikTok user demographics 2026: https://usefulsocialmedia.com/tiktok-user-demographics/
- PostEverywhere, Social media demographics 2026: https://posteverywhere.ai/blog/social-media-demographics-2026
- Whitehat SEO, B2B video marketing strategy 2026: https://whitehat-seo.co.uk/blog/video-marketing
- Koanthic, B2B short-form video guide 2026: https://koanthic.com/en/b2b-short-form-video-complete-guide-for-2026/
- PostPlanify, Social media safe zones 2026: https://postplanify.com/blog/social-media-safe-zones-2026-complete-guide
- Kreatli, Safe zone hub 2026: https://kreatli.com/guides/safe-zone-guide
- CreaMate, TikTok safe zone 2026: https://creamate.ai/en/blog/tiktok-safe-zone-guide

---

# Part 10. captions.md

## Captions

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Captions are rendered as an Advanced SubStation Alpha (`.ass`) file and burned in with libass. The `.ass` file is saved next to the output (`edited.ass`) so it can be inspected or edited and re-burned.

### Typography rules

1. **Size:** 66 to 80 px on a 1920 px tall frame. That is 3.4% to 4.2% of height. Smaller is unreadable on a phone; larger covers the face.
2. **Weight:** heavy. Default fonts are Segoe UI Black (Windows), Helvetica Neue (macOS), DejaVu Sans (Linux). Override with `--font-bold "Montserrat ExtraBold" --fontsdir ./fonts`.
3. **Contrast:** light text, 7 px dark stroke, 3 px shadow. Readable over white walls and dark rooms alike.
4. **Length:** three words at level 41+, four at 21-40, seven at 1-20. Break early at commas and sentence ends.
5. **Position:** centered at y 1390. Clear of the face above and of the platform caption and button zone below (about the bottom 400 px and the right 140-180 px on 1080x1920, per 2026 safe-zone guides).
6. **Timing:** a caption appears on its first word's start and leaves 0.25 s after its last word, or when the next one starts.
7. **Accent:** one accent color for the spoken word and keywords. Never more than two colors in a caption.
8. **Case:** sentence case by default. All caps only in the `neon` look, where the font is set wide.

### Creative caption styles (never flat)

Plain white text under a talking head is the most common reason an edit looks cheap. Every tier above level 20 uses an animated style, and even the calm styles put the accent color on keywords. `plain` exists only when someone asks for it with `--captions plain`.

| Style | What the viewer sees | Best for | Picked automatically by |
|---|---|---|---|
| clean_accent | whole phrase fades in, keywords in the accent color | tutorials, B2G, older audiences, level 1-20 | tutorial_docs, story_vlog, podcast_talk, linkedin, boomer |
| chunk | 4-word phrases that pop from 88% to 100% | clean social posts | level 21-40 without a genre |
| highlight | the spoken word turns accent, the phrase stays | education, B2B, consideration | education_explainer, b2b, gen_x |
| pop | words appear as spoken, the current word pops larger | creators, explainers | level 61-80 |
| kinetic | pop plus a spaced small-caps echo of long keywords above the line | AI, sales, Gen Z | ai_comparison, sales_pitch, gen_z |
| sweep | karaoke fill: accent sweeps through each word in time | stories, podcasts, music-led | story_vlog, podcast_talk, nonprofit |
| boxed | an accent pill slides under the active word | hackathon demos, launches, screen recordings | hackathon_demo, product_launch, hackathon market |
| bounce | each word drops in with a small tilt and overshoot | beauty, lifestyle, Gen Z | product_launch, gen_z |
| stack | small lead-in line, keyword huge underneath | sales tips, stats, investor | sales_pitch, education_explainer, investor |
| plain | no animation | accessibility exports only | never automatic |

Choose by hand with `--captions boxed` (plan or auto). Priority: `--captions` flag > brief > genre > level tier.

#### Rules that make captions look designed

1. **One accent, one base.** Accent on keywords (6+ letters or numbers) and the spoken word. Never a rainbow.
2. **Three words per line is the default.** A line should be read in under a second.
3. **Motion under 200 ms.** Captions follow speech; a slow animation lags behind the voice.
4. **Keywords decide emphasis, not position.** The planner highlights numbers and long content words, the words people remember.
5. **Match the style to the audience.** Kinetic and bounce for Gen Z; highlight and clean_accent for Gen X and B2B. The brief does this.
6. **Stay in the safe zone.** Captions sit at y 1390, above the platform UI in the bottom ~400 px.
7. **Pair with cards, don't compete.** When a card is on screen, captions stay; the card lives in the top third.
8. **Say what the caption should show.** Spoken numbers, names and short punchy sentences give captions something to emphasize. See `references/script-and-marketing.md`.

#### Known limits

- `boxed` estimates word width from the character count (0.5 x font size per character). Very wide or very narrow fonts shift the pill slightly; pass a font close to the default or check `sheet.jpg`.
- `sweep` relies on libass karaoke (`\kf`); some very old ffmpeg builds ignore it and show the fill color at once.
- Word-level styles need spaces between words. For Chinese and Japanese use `clean_accent` or `chunk`.

### Fonts on other machines

libass looks up fonts by family name. If the name is not installed, it falls back silently and the look changes. To make renders identical everywhere:

1. Put the `.ttf` or `.otf` files in a folder.
2. Pass `--fontsdir that/folder --font-bold "Exact Family Name"`.
3. Find the family name with `fc-list : family` (Linux/macOS) or by opening the font file on Windows.

Use fonts with a license that allows video embedding (for example anything on Google Fonts under OFL).

### Right-to-left and non-Latin scripts

libass shapes Arabic, Hebrew, Devanagari, Thai, and CJK when a font covering the script is available. Pass a suitable font, for example `--font-bold "Noto Sans Arabic"`. Word-pop styles assume spaces between words; for Chinese and Japanese use level 21-40 (chunk style).

### Editing a caption by hand

1. Open `edited.ass`.
2. Find the `Dialogue:` line with the wrong text. Fix the text only, not the `{...}` tags.
3. Re-burn without re-planning:

```bash
ffmpeg -i input_after_cuts.mp4 -vf "subtitles=edited.ass" -c:a copy fixed.mp4
```

Easier: fix the word in `edl.json` under `words` and run `render` again.

### Exporting an SRT for platforms that take sidecar captions

```bash
ffmpeg -i edited.ass edited.srt
```

---

# Part 11. genres-and-variants.md

## Genres, auto style, and variants

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

The same editing model runs for every look. What changes per video is decided from the transcript.

### Three layers

| Layer | Decides | Where |
|---|---|---|
| Edit model | cuts, beat detection, card timing, zooms, sound effects, breathing room, QA | `plan` in `scripts/splicecraft.py` (identical for every style) |
| Genre | level shift, card density, zoom strength, which beat types are dropped, default style, CTA text, music tempo | `presets/genres.json` |
| Look | colors, grade, caption size, card height, caption style | `presets/styles.json` plus the per-video variant |

The test `test_same_edit_model_for_every_style` proves layer one: for the same transcript and level, all six styles produce byte-identical `keep`, `cards`, `zooms`, `sfx`, and `words`. Only `theme` differs.

### Genre detection

```bash
$SC detect work/words.json
```

Each genre has English and Indonesian keywords. Every hit counts once; multi-word or long keywords (7+ letters) count twice. Numbers push toward education, questions push toward podcast. Scores are hits per 100 words. Below 1.0 the planner falls back to `education_explainer`.

| Genre | Default style | Level shift | Density | Zoom | Dropped beats | CTA |
|---|---|---|---|---|---|---|
| hackathon_demo | neon | +5 | x1.1 | full | none, no flash | Try the live demo |
| tutorial_docs | editorial | -15 | x0.8 | half | word, versus | Full guide in the description |
| product_launch | glass | +10 | x1.0 | full | callback | Link in bio |
| education_explainer | studio | 0 | x1.0 | full | none | Follow for part two |
| story_vlog | cinema | -5 | x0.6 | full | ranking, versus, no flash | Follow for the rest of the story |
| sales_pitch | noir | +10 | x1.15 | full | none | Comment GUIDE |
| podcast_talk | cinema | -20 | x0.5 | 60% | word, no flash | Full episode on the channel |
| ai_comparison | studio | +5 | x1.1 | full | none | Which one wins? Comment below |

Why these choices:

- **Hackathon demos** are judged in under two minutes. Dense number cards and a loud accent help the judge remember the claim. No flashes: judges often watch screen recordings where a white flash hides the UI.
- **Tutorials and documentation** need the viewer to read the screen. Fewer cards, half zoom (zooming a screen recording blurs text), no giant word hits.
- **Stories** lose intimacy with ranking bars. Warm cinema grade, fewer cards.
- **Podcasts** are long; a card every few seconds becomes noise.

Checked on real transcripts: the withpt.ai reference (Astra 6 vs Fable 5.1) detects as `ai_comparison`, and the synthetic demo also detects as `ai_comparison`. The softgirlnocode transcript was not saved, so its genre is untested.

### Using it

```bash
## detect genre, pick style from genre, vary the look per video
$SC plan work/words.json -o work/edl.json --level 60 --style auto --genre auto

## force a genre but keep your own style
$SC plan work/words.json -o work/edl.json --level 60 --style cinema --genre hackathon_demo

## pick a specific look (0-359); same number always gives the same look
$SC plan work/words.json -o work/edl.json --genre auto --style auto --variant 42
```

Without `--variant`, the variant is a hash of the transcript, so the same video always gets the same look and different videos get different ones.

`--genre none` (the default) keeps the old behavior: exact level, exact style colors.

### How many options

```bash
$SC options
```

Computed from the preset files, not typed in:

- 8 accent palettes x 3 caption sizes x 3 card heights x 5 grades = **360 variants** per genre and style
- 8 genres x 6 styles x 360 variants x 100 levels x 3 aspect ratios = **5,184,000 combinations**

Honest note: many neighboring combinations look alike (level 61 vs 62). The meaningful distinct looks are the 8 x 6 x 360 = 17,280 genre/style/variant setups.

### Adding a genre

1. Copy a block in `presets/genres.json` and rename it.
2. Add 15 or more keywords a speaker in that genre actually says, in each language you support.
3. Add two sample scripts to `tests/fixtures/genre_scripts.json`.
4. Run `python -m unittest discover tests`. The detection test must still pass for every genre.

### Proof

- `tests/test_plan.py`: `test_detects_every_genre_in_english_and_indonesian` (16 scripts, 8 genres, 2 languages), `test_same_edit_model_for_every_style`, `test_genre_changes_the_edit`, `test_variants_are_deterministic_and_distinct`.
- A per-genre rendered image matrix was attempted and failed on this machine (ffmpeg `drawtext` crashed without a fontconfig file); it is not included rather than faked.

---

# Part 12. music-guide.md

## Background music guide

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Music is picked automatically, but you can override every part. Three routes, in order of safety:

1. **Built-in templates** (default): 18,432 license-free beds synthesized by ffmpeg on the user's machine. No copyright claims possible.
2. **A library track the user owns or licensed**: `--music song.mp3`.
3. **A track the user found online**: only from the license-clear sources listed below, and only after reading that track's license.

Never download music from YouTube videos, TikTok sounds, or Spotify for a published edit. Platforms mute or claim it.

### Template ids

A template id is `mood.key.drums.timbre.energy`, for example `tech_pulse.D.driving.pluck.high`.

| Part | Options | Count |
|---|---|---|
| mood | uplifting, bright_pop, hopeful, confident, corporate_clean, playful, calm_ambient, chill_lofi, emotional, tech_pulse, cinematic_epic, dark_tension, mysterious, sunny_acoustic, motivational, news_neutral | 16 |
| key | C to B | 12 |
| drums | none, soft_pulse, four_floor, half_time, lofi, trap, driving, broken | 8 |
| timbre | sine, warm, organ, pluck | 4 |
| energy | low (x0.85 tempo), mid, high (x1.15 tempo) | 3 |

16 x 12 x 8 x 4 x 3 = **18,432 templates**. Check with `$SC music count`.

Honest limit: these are simple synth beds (pad, bass, drums). They sit well under a voice. They are not produced songs with melodies and vocals. For a music-led edit with no voice, use route 2.

### Commands

```bash
$SC music count                                   # how many templates, total and per genre
$SC music list --genre hackathon_demo --limit 30  # sample the ids that fit a genre
$SC music pick work/words.json                    # detect genre + speech pace, return one id and the reason
$SC music render tech_pulse.D.driving.pluck.high --seconds 30 -o preview.wav   # listen before rendering video
```

`plan` stores the pick in `edl.json` under `theme.music_template` and `params.music_pick`. `render` synthesizes it. To change it, edit `theme.music_template` in `edl.json` and render again.

### How the match is made

1. **Genre** (from `detect`) limits moods, drums, timbres and energy to ones that suit it (table below).
2. **Speaking pace**: words per minute. Under 130 = low energy, 130 to 170 = mid, above 170 = high. A fast talker over a slow bed feels sluggish; a calm talker over a fast bed feels anxious.
3. **Variant seed** (the same `--variant` as the look) picks inside the allowed set, so the same video always gets the same track and different videos get different ones.

| Genre | Moods | Drums | Timbres | Energy | Templates |
|---|---|---|---|---|---|
| hackathon_demo | tech_pulse, confident, uplifting, motivational | driving, four_floor, broken | pluck, warm | mid, high | 576 |
| tutorial_docs | calm_ambient, chill_lofi, corporate_clean | none, soft_pulse, lofi | sine, warm | low | 216 |
| product_launch | bright_pop, uplifting, sunny_acoustic, playful | four_floor, driving, half_time | pluck, warm, organ | mid, high | 864 |
| education_explainer | corporate_clean, hopeful, news_neutral, mysterious | soft_pulse, lofi, half_time | warm, sine, pluck | low, mid | 864 |
| story_vlog | emotional, hopeful, chill_lofi, sunny_acoustic | none, soft_pulse, lofi | warm, sine, pluck | low, mid | 864 |
| sales_pitch | confident, motivational, dark_tension, cinematic_epic | trap, driving, half_time | pluck, organ, warm | mid, high | 864 |
| podcast_talk | calm_ambient, chill_lofi, news_neutral | none, soft_pulse | sine, warm | low | 144 |
| ai_comparison | tech_pulse, mysterious, confident, playful | broken, driving, trap, half_time | pluck, warm | mid, high | 768 |

"100% match" is not something any rule can promise; taste is involved. What the rules do guarantee: the tempo family fits the pace, the mood fits the genre, and the ducking keeps the voice on top. Always listen to the preview.

### Mood cheat sheet (when choosing by hand)

| If the video says... | Mood | Why |
|---|---|---|
| "we built", "it works", results | tech_pulse, confident | minor drive sounds like momentum without being cheesy |
| "step one", "click", "open" | calm_ambient, chill_lofi | nothing competes with instructions |
| "introducing", "today we launch" | bright_pop, uplifting | major, four-on-the-floor lifts the reveal |
| "why", "research", "the reason" | corporate_clean, mysterious | neutral, or curious for reveals |
| "I felt", "my family", "honestly" | emotional, hopeful | iv minor chord gives the bittersweet turn |
| "the mistake", "the secret", money | dark_tension, confident | tension sells the problem, confidence sells the fix |
| comparisons, "which is better" | tech_pulse, playful | playful keeps a versus light; tech for AI |
| travel, food, day in the life | sunny_acoustic | bright, simple I-V-IV |

### Mixing rules (already applied by render)

- Music sits at `--music-db` (default -20 dB) under the voice and is ducked by sidechain compression whenever the voice speaks.
- Final mix normalized to -14 LUFS, true peak under -1 dBFS.
- 1.2 s fade in, 1.5 s fade out.
- Tutorials and podcasts: consider `--music-db -26`. Launches and hackathon demos: `-18`.
- No music under a quote card with a sad or serious line: set `params.music` to false in `edl.json` if the whole video is serious.

### Syncing cuts to the beat

The template tempo is in the render log (`133 bpm`). One beat = 60 / bpm seconds. Cards and zooms feel intentional when their `start` lands within 80 ms of a beat. To snap by hand in `edl.json`: `start = round(start / beat) * beat`. Do not snap captions; they follow speech.

### License-clear sources for real tracks (route 3)

Read each track's license page before use. Terms change.

| Source | Typical license | Watch out for |
|---|---|---|
| YouTube Audio Library (Studio > Audio Library) | free for YouTube; many need attribution | some tracks say "attribution required"; use outside YouTube may not be covered |
| Pixabay Music | Pixabay Content License, no attribution | a few tracks are Content ID registered; keep the license certificate |
| Uppbeat | free tier with credit, paid without | free tier needs the credit line in the description |
| Free Music Archive | varies per track (CC BY, CC BY-NC, ...) | NC means no commercial use: no ads, no sponsored posts |
| Incompetech (Kevin MacLeod) | CC BY 4.0 | attribution required in the exact format given |
| Artlist, Epidemic Sound, Musicbed | paid subscription | license covers the subscriber's channels only, while subscribed at publish time |

Search phrases that find beds that work under speech: `<mood> background no vocals`, `<mood> corporate underscore`, `lofi instrumental loop`, `minimal tech pulse`. Pick tracks without vocals and without a busy melody in the 1 to 4 kHz range, where speech lives.

---

# Part 13. beat-library.md

## Beat library

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

A beat is one sentence and the treatment it gets. The planner (`plan` in `scripts/splicecraft.py`) checks beats in the order listed. The first match wins. A sentence that matches nothing gets captions only.

All positions use a 1080 x 1920 design grid and are scaled to the output size. Cards live in the top third (y 230 to about 600). Captions live at y 1390. The face is assumed to sit between y 600 and y 1300.

Card timing rule for every type: `start` = the first word of the trigger, `end` = sentence end + 0.6 s, clamped to between 1.6 s and 4.2 s after start.

---

### 1. hook

- **Trigger:** the first sentence of the video. Level 21 and up.
- **Look:** panel across the top, sentence split into up to three lines, words fade in 70 ms apart, keywords (6+ letters or numbers) in the accent color.
- **Motion:** panel rises 40 px with a 92% to 100% scale. Video eases in to the level's zoom amount over the first 2 s.
- **Sound:** pop.
- **Why:** the first second decides whether the viewer stays. A title that builds word by word gives the eye something to track while the voice starts.
- **Do not:** use the hook card for a greeting ("Hi guys"). If the first sentence is a greeting, delete the hook card in `edl.json` and make the second sentence the hook by changing its start and text.

### 2. cta

- **Trigger:** a sentence in the last 40% of the video containing follow, subscribe, or ikuti. Used once.
- **Look:** accent pill in the card zone at the top (y card_y + 40); the bottom ~400 px is covered by platform buttons and captions with `cta_text` from the theme.
- **Variant:** "comment WORD" becomes a question pill reading `Comment WORD`.
- **Do not:** show two CTAs back to back. The planner keeps only the first follow sentence.

### 3. quote

- **Trigger:** "they say", "quote", "said", "kata orang", "pepatah". If the trigger sentence has four words or fewer ("Here's a quote."), the next sentence becomes the quote.
- **Look:** panel with a large accent opening quote mark and the sentence revealed character by character (ASS `\kf` karaoke with transparent secondary color).
- **Timing:** reveal takes about 30 ms per character, never longer than the sentence.
- **Do not:** quote a sentence longer than about 90 characters; it becomes a wall of text. Shorten the text field in `edl.json` and keep the meaning.

### 4. versus (before and after)

- **Trigger:** the phrase "before and after" (or "sebelum dan sesudah").
- **Look:** two panels, BEFORE and AFTER, with a round accent VS badge that scales from 0 to 115% to 100%.
- **Sound:** whoosh.

### 5. ranking

- **Trigger:** ordinal words: first, second, third, fourth, fifth (pertama, kedua, ketiga...). A ranking starts at "first". Each next ordinal within 6 s appends a row to the same card.
- **Look:** numbered rows; each bar wipes in from the left over 420 ms. Bars get shorter and lighter per rank so the order is visible without reading.
- **Sound:** whoosh on the card, tick on each new row.
- **Do not:** start a ranking at "second". If the speaker says "second" without "first", no card is made.

### 6. number

- **Trigger:** digits (`3`, `100%`, `2.5`) or number words (two, ten, hundred, dua, seratus). The word "one" is ignored because it is almost always a pronoun.
- **Merge:** numbers in a sentence that starts within 3.5 s of an open number card join that card, up to three.
- **Look:** panel with a small caps label (BY THE NUMBERS), each number huge in the accent color with the next content word as its label. Values over 3 count up in ten steps over 450 ms.
- **Motion:** punch zoom at 60% of the level's zoom amount.
- **Sound:** pop, then tick for each merged number.
- **Memory:** every number shown is remembered for the callback beat.

### 7. callback

- **Trigger:** a sentence containing "number" plus one of back, remember, start, again, earlier, kembali, tadi, and at least one remembered number.
- **Look:** the number card layout labeled BACK TO THE START with up to three earlier numbers.
- **Why:** it shows the edit follows the whole video.
- **Exception:** callbacks ignore the breathing-room gap.

### 8. question

- **Trigger:** a sentence ending in "?" with nine words or fewer.
- **Look:** accent pill with the question, zooming in from 55%.
- **Motion:** gentle ease-in zoom at 50% of the level amount.

### 9. word

- **Trigger:** a sentence of one to three words with at least one content word of four or more letters. Filler sentences ("That's it", "Thanks", "Bye") are skipped.
- **Look:** the phrase (or its longest word if the phrase is over 12 characters) in huge accent letters with a thick stroke, scaling from 40% with blur to 112% to 100%, and an underline that grows from the center.
- **Motion:** full punch zoom. At level 81+, a white flash hit.

### 10. nothing (the default)

- **Trigger:** everything else.
- **Look:** captions only. On long sentences (five words or more) a slow drift zoom is added every few sentences so the shot is never frozen.
- **Why:** restraint is what makes the other beats land. The planner keeps at least 38% of runtime card-free by dropping the weakest beats; the QA gate `breathing_room` fails below 35%.

---

### Global limits

| Limit | Formula (L = level 1-100) |
|---|---|
| Pause removal threshold | 0.95 - 0.65 x L/100 seconds |
| Card ceiling | 10 x L/100 cards per minute (hook and CTA are free) |
| Minimum gap between cards | max(2.0, 11 - 9 x L/100) seconds |
| Zoom amount | 1 + 0.22 x L/100 |
| Grade strength | 0.25 + 0.75 x L/100 |

### Adding a beat type by hand

1. Copy an existing card object in `edl.json`.
2. Change `type` to one of: hook, number, callback, ranking, quote, question, versus, word, cta.
3. Set `start` to the trigger word's `s` from `words`, and `end` 1.6 to 4.2 s later.
4. Make sure it does not overlap the previous or next card.
5. Render again.

---

# Part 14. edit-levels.md

## Edit levels 1 to 100

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

One number controls the whole edit. Switches change at tier borders. Continuous values change smoothly inside a tier.

### Tier switches

| Setting | Clean 1-20 | Social 21-40 | Creator 41-60 | Pro 61-80 | Showrunner 81-100 |
|---|---|---|---|---|---|
| Caption style | plain | chunk | highlight | pop | kinetic |
| Words per caption | 7 | 4 | 3 | 3 | 3 |
| Hook title | no | yes | yes | yes | yes |
| Zooms | no | yes | yes | yes | yes |
| Music bed | no | yes | yes | yes | yes |
| Sound effects | no | no | yes | yes | yes |
| Ranking cards | no | yes | yes | yes | yes |
| Word cards | no | no | yes | yes | yes |
| Callbacks | no | no | yes | yes | yes |
| Progress bar | no | no | no | yes | yes |
| Film grain on cinema/noir | no | no | no | yes | yes |
| Flash hits | no | no | no | no | yes |

### Continuous values at sample levels

| Level | Pause cut above | Cards/min ceiling | Min gap between cards | Zoom | Grade strength |
|---|---|---|---|---|---|
| 1 | 0.94 s | 0.1 | 10.9 s | 1.002 | 0.26 |
| 10 | 0.89 s | 1.0 | 10.1 s | 1.022 | 0.33 |
| 25 | 0.79 s | 2.5 | 8.75 s | 1.055 | 0.44 |
| 50 | 0.63 s | 5.0 | 6.5 s | 1.11 | 0.63 |
| 60 | 0.56 s | 6.0 | 5.6 s | 1.132 | 0.70 |
| 75 | 0.46 s | 7.5 | 4.25 s | 1.165 | 0.81 |
| 85 | 0.40 s | 8.5 | 3.35 s | 1.187 | 0.89 |
| 100 | 0.30 s | 10.0 | 2.0 s | 1.22 | 1.00 |

### Picking a level for the user

| The user says | Level |
|---|---|
| "Just add subtitles" | 10 |
| "Clean it up, nothing flashy" | 20 |
| "For Instagram" / "for LinkedIn" | 35 to 50 |
| "Make it engaging" / "like a creator" | 55 to 65 |
| "Like MrBeast" / "super dynamic" / "viral" | 80 to 90 |
| "Maximum" / "go crazy" | 95 |
| Serious topic (grief, medical, legal) | 15 to 30, look `editorial` or `cinema`, no flashes |
| Tutorial with a screen recording | 30 to 45; heavy zoom fights the UI on screen |

### Caption styles

- **plain:** full phrase, white with dark stroke, 80 ms fade.
- **chunk:** short phrase pops from 88% to 100% scale.
- **highlight:** phrase stays; the spoken word turns accent color.
- **pop:** words appear as spoken; the current word pops from 108% (118% for keywords) and is accent colored.
- **kinetic:** pop, plus long keywords (7+ letters) flash above the caption in small spaced capitals.

---

# Part 15. color-and-cinematic.md

## Color, cinematic looks, and chroma key

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

The grade runs before zooms and captions, so graphics keep their exact colors.

### 1. Built-in grades (`--grade`)

`k` is the grade strength from the level (0.25 to 1.0).

| Grade | ffmpeg chain | Use for |
|---|---|---|
| clean | `eq=contrast=1+0.08k:saturation=1+0.1k` | anything; safest on skin |
| punchy | `eq=contrast=1+0.18k:saturation=1+0.3k:brightness=0.01,unsharp=5:5:0.6` | bright creator content, flat webcam footage |
| cinematic | `eq` slight desaturation + `colorbalance` (warm shadows-to-red, cool highlights-to-blue) + S-curve + `vignette` | stories, documentaries, dark rooms |
| warm | `eq` + `colortemperature` down to about 5300 K | interviews, lifestyle, editorial |
| mono | `hue=s=0`, contrast lift, vignette | drama, quotes, noir look |
| none | passthrough | footage that is already graded |

Each look in `presets/styles.json` has a default grade. `--grade` overrides it.

### 2. Reading the source before grading

Take three frames and look at them:

```bash
ffmpeg -i input.mp4 -vf "select='eq(n\,30)+eq(n\,300)+eq(n\,900)',scale=360:-1,tile=3x1" -frames:v 1 frames.jpg
```

| You see | Do this |
|---|---|
| Face darker than the wall | `--grade punchy`, and add `,eq=gamma=1.12` in a custom chain (section 5) |
| Orange or green skin already | `--grade clean` or `none`; strong grades make it worse |
| Blown-out window behind | `curves=all='0/0 0.7/0.62 1/0.9'` to pull highlights down |
| Noisy dark footage | add `hqdn3d=3:3:6:6` before the grade; skip grain |
| Blue daylight cast | `colortemperature=temperature=5600` (lower = warmer) |
| Tungsten orange cast | `colortemperature=temperature=7500` |

### 3. LUTs

```bash
$SC render input.mp4 work/edl.json -o out.mp4 --lut looks/teal_orange.cube --grade clean
```

- Only `.cube` 3D LUTs. The LUT is applied after the built-in grade, so use `--grade clean` or `none` to avoid stacking.
- Log footage (S-Log, C-Log, V-Log) needs its manufacturer's conversion LUT first, then a creative LUT. With `--lut` you can apply one; chain the second by hand (section 5).
- Only use LUTs the user supplies or that come with a license allowing use.

### 4. Cinematic checklist

A "cinematic" request usually means these, in this order of impact:

1. **Motion restraint.** Level 40 to 65. Drift zooms, fewer punch zooms, no flashes.
2. **Contrast curve.** S-curve with lifted blacks: `curves=all='0/0.03 0.25/0.22 0.75/0.8 1/0.97'`.
3. **Split tone.** Warm skin, cool shadows: `colorbalance=rs=0.05:bs=-0.05:rh=-0.03:bh=0.05`.
4. **Vignette.** `vignette=angle=PI/5`.
5. **Grain.** `noise=alls=6:allf=t` (automatic at level 61+ for cinema and noir).
6. **24 fps.** `--fps 24` for a film cadence. Not for fast-talking social clips.
7. **Letterbox** on 16:9 output only: add `drawbox=x=0:y=0:w=iw:h=ih*0.06:color=black:t=fill,drawbox=x=0:y=ih*0.94:w=iw:h=ih*0.06:color=black:t=fill` and raise `card_y` in `brand.json` so cards clear the bar. Never letterbox 9:16.
8. **Look:** `--style cinema`.

### 5. Custom chains

Edit `GRADES` in `scripts/splicecraft.py` or add an entry:

```python
GRADES["daylight_fix"] = "colortemperature=temperature=5600,eq=contrast={c}:gamma=1.08:saturation={s}"
```

Placeholders available: `{c}` `{c2}` `{s}` `{s2}` `{s3}` `{rs}` `{bs}` `{rh}` `{bh}` `{temp}`. Then pass `--grade daylight_fix`.

### 6. Chroma key (green or blue screen)

```bash
$SC render input.mp4 work/edl.json -o out.mp4 --key green --bg backgrounds/office.jpg
```

- `--key green`, `--key blue`, or an exact color `--key 0x3BB54A`.
- `--bg` can be an image (looped) or a video (looped). Without `--bg`, an animated gradient in the look's `bg_a` and `bg_b` colors is used.
- The chain is `chromakey=color:0.16:0.08` then `despill`, then overlay on the background.

Tuning when the edge looks wrong:

| Problem | Fix in `render()` chromakey values |
|---|---|
| Green halo around hair | raise similarity from 0.16 to 0.20 |
| Parts of the person disappear (green shirt, reflections) | lower similarity to 0.10; ask the user to avoid green clothes |
| Hard jagged edge | raise blend from 0.08 to 0.15 |
| Uneven screen lighting (dark corners) | sample the actual screen color: `ffmpeg -i in.mp4 -vf "crop=40:40:20:20,scale=1:1" -frames:v 1 -f rawvideo -pix_fmt rgb24 - \| xxd` and pass it as `--key 0xRRGGBB` |

Match the background to the subject: same light direction, similar brightness, slightly blurred (`boxblur=8`) so the speaker stays the sharpest thing in frame.

### 7. Reframing to vertical

The render scales to cover the target and center-crops. For an off-center speaker, crop first:

```bash
## speaker on the left third of a 1920x1080 clip
ffmpeg -i wide.mp4 -vf "crop=608:1080:260:0" -c:a copy left.mp4
```

Width for a 9:16 crop of 1080 px tall footage is 608 px. Change the third number to move the window.

---

# Part 16. audio.md

## Audio: voice, music, effects, loudness

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

### Signal chain (what `render` builds)

```
voice: select kept ranges -> highpass 75 Hz -> compressor 3:1 at -20 dB -> +2.5 dB at 3.2 kHz -> split
music: loop -> trim to length -> volume (--music-db, default -20 dB) -> sidechain compress keyed by voice
sfx:   synthesized wav (pop / tick / whoosh) -> -9 dB
mix:   amix (no auto-normalize) -> loudnorm I=-14 TP=-1.5 LRA=11 -> 48 kHz AAC 192 kbps
```

### Loudness targets

| Platform | Target | Notes |
|---|---|---|
| TikTok, Reels, Shorts | -14 LUFS, peak -1 dBTP | default |
| YouTube long form | -14 LUFS | same |
| Podcasts | -16 LUFS | change `I=-14` to `I=-16` in `render()` |

`qa` accepts -16.5 to -12.5 LUFS and a peak at or below -0.5 dBFS.

### Music

Allowed sources, in order of preference:

1. **Generated bed** (default at level 21+). `synth-music` renders a chord pad, soft kick, and hat with ffmpeg `aevalsrc`. No license needed. Moods: `bright` (major progression) and `moody` (minor). Tempo comes from the look (`bpm` in styles.json).
2. **The user's own file** with rights to use it: `--music song.mp3`.
3. Royalty-free libraries the user already has an account with. The agent must not download music itself.

Never rip songs from YouTube, TikTok, or Spotify. Platform content ID will mute or strike the post.

Standalone bed:

```bash
$SC synth-music -o bed.wav --seconds 90 --bpm 100 --mood bright
```

#### Choosing tempo

| Content | BPM |
|---|---|
| Calm explainer, cinema look | 80 to 90 |
| Standard creator talk | 95 to 105 |
| Hype, product launch, neon look | 115 to 125 |

#### Ducking

The sidechain compressor (threshold 0.03, ratio 8, attack 20 ms, release 350 ms) drops the music when the voice is present and lets it breathe in pauses. If the music pumps audibly, raise release to 500. If the voice still fights the music, lower `--music-db` to -24.

### Sound effects

Synthesized by the script, so there is nothing to license:

| Name | Sound | Used on |
|---|---|---|
| pop | 90 ms falling sine chirp | hook, number, quote, question, word, CTA |
| tick | 40 ms 1.8 kHz click | extra ranking rows, merged numbers |
| whoosh | 320 ms filtered noise swell, starts 180 ms before the card | ranking, versus |

Rules: an effect marks a visual change. No effect without a graphic. No more than one effect per second.

### Cleaning bad voice audio

Add to the voice chain in `render()` when needed:

| Problem | Filter |
|---|---|
| Constant hiss / fan | `afftdn=nf=-25` |
| Room echo | not fixable well in ffmpeg; lower music and accept it |
| Clicks, mouth noise | `adeclick` |
| Very quiet recording | the compressor plus loudnorm handles up to about 20 dB of gain |
| Hum at 50/60 Hz | `highpass=f=90` or `bandreject=f=50:w=5` |

### Voice pitch and speed (read before touching either)

The most common AI editing mistake with voices: the speaker comes out as a chipmunk (pitch too high) or a slow robot (pitch too low). Both break trust in the first second, and viewers swipe.

#### The default is: do not change pitch. Ever.

splicecraft never changes voice pitch unless `params.voice` in `edl.json` names an allowed reason. The render refuses anything else with an error. Pause removal cuts silence; it does not speed up or slow down speech.

#### Why it happens (so you can spot it)

| Cause | Result | Fix |
|---|---|---|
| Speeding audio with `asetrate` (or "speed" in an editor with pitch lock off) | chipmunk | use `atempo`, which stretches time and keeps pitch |
| Slowing audio with `asetrate` | deep, slow, robotic | use `atempo` |
| Treating 44.1 kHz audio as 48 kHz (or back) when muxing | pitch 1.5 semitones off, speech 9% fast or slow | resample with `aresample=48000`, never relabel the rate |
| A TTS voice rendered at one rate and played at another | high or low voice | check `ffprobe` sample rate of the TTS file |
| "Pitch correction" or "voice enhance" presets on already-good audio | robotic warble | turn them off |
| Formant-less pitch shift of more than about 2 semitones | cartoon or monster timbre | do not shift speech that far unless it is an intended effect |

#### Decision table: when pitch may change

| Situation | Allowed? | How | Limit |
|---|---|---|---|
| Normal talking head, tutorial, pitch, demo, podcast, story | **No** | nothing | 0 |
| User says "make it faster" | **Speed only, pitch unchanged** | cut more pauses first (raise the level); if still needed, `atempo` on voice *and* re-time video together outside splicecraft | 1.05-1.15x; above 1.25x speech sounds rushed |
| Source sounds wrong (chipmunk or slow) because of a sample-rate mismatch | Yes, to restore the original | `"voice": {"pitch_semitones": <measured>, "reason": "fix_wrong_sample_rate"}` | +/-2 semitones |
| User asks to disguise a voice (privacy, whistleblower, a minor) | Yes, if the user asked | `"reason": "anonymize_speaker"`, try -3 to -4 or +3 to +4 | +/-5; also blur the face, pitch alone is weak anonymization |
| A deliberate comedy or character voice the user asked for | Yes, on purpose only | `"reason": "character_effect"` | +/-12 |
| A sung or hummed line must match the music key | Yes | `"reason": "match_music_key"` | +/-1 |
| "Sound more confident / deeper" | **No** | better mic distance, EQ (low shelf +2 dB at 150 Hz), compression; already in the voice chain | 0 |
| "Sound younger / more energetic" | **No** | a faster music template and a higher edit level, not pitch | 0 |
| Music does not fit the voice | **No voice change** | pick another template (`$SC music pick`) | 0 |
| Audience is kids or older adults | **No** | caption size and pace via the brief | 0 |
| AI dubbing or TTS voice sounds off | **No shift** | regenerate the voice at the right sample rate | 0 |

If you are unsure, the answer is no.

#### How to set an allowed change

In `edl.json`:

```json
"params": { "voice": { "pitch_semitones": -1.5, "reason": "fix_wrong_sample_rate" } }
```

Semitones from a rate mismatch: `12 * log2(correct_rate / wrong_rate)`. Example: audio made at 44100 but played as 48000 sounds +1.47 semitones high, so set -1.47.

Render uses `asetrate` + `aresample` + a compensating `atempo`, so the pitch moves and the timing (and caption sync) does not.

#### Check by ear and by numbers

1. Listen to the first 5 seconds of the render next to the source. Same voice? Good.
2. `duration_match` in QA must pass: speed changes show up as duration drift.
3. Compare `ffprobe` of source and render: sample rate 48000 in the render is expected; the speech length between two words should match the transcript timing.

Sources (checked 2026-09-15): FFmpeg atempo vs asetrate explanations at https://dev.to/javidjamae/ffmpeg-atempo-filter-change-audio-speed-without-pitch-shift-3e6i and https://hhsprings.bitbucket.io/docs/programming/examples/ffmpeg/manipulating_audio/atempo_asetrate_aresample.html

---

# Part 17. baseline-teardown.md

## Baseline teardown: "Which AI edits better?"

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Source studied: a 107.6 second vertical video (1080x1920, 60 fps, AAC stereo, mean loudness -17.8 dB, peak -0.9 dB) from the withPT.ai account. One creator, one raw take, handed to two AI models with the same prompt. The frame is split: the top half is one model's edit, the bottom half is the other's, both playing in sync under a fixed header.

Method: frames sampled every 2 s into contact sheets, scene changes detected with ffmpeg `select=gt(scene,0.25)`, speech transcribed with Whisper large-v3 at word level. Timestamps below are from the source.

The footage belongs to its creator. This file describes it for study only; none of it is redistributed in this repository.

### 1. Layout

| Zone | Share of 1920 px height | Content |
|---|---|---|
| Header | ~15% | "Which AI edits better?" in heavy black sans, blue subline "Same Footage & Audio \| Zero Human Edits" |
| Top label | ~3% | model name with a small orange mark |
| Top pane | ~28% | 16:9 cutout of the take with model A's graphics |
| Bottom label | ~3% | model name with a small blue mark |
| Bottom pane | ~28% | same take with model B's graphics |
| Margins | ~23% | pale blue-white gradient, empty |

Both panes are 16:9 rectangles placed inside a 9:16 canvas. The speaker is filmed against a plain white wall, black cap and t-shirt, soft frontal light, no color grade.

### 2. Beat map (the script is a test of beat types)

The speaker announces each beat, then performs it. This is a clean catalogue of what an automated editor should handle.

| Time (s) | Speech | Beat type | Model A (orange, top) | Model B (blue, bottom) |
|---|---|---|---|---|
| 0.0-5.0 | "Let's see if Astra 6 or Fable 5.1 is better at video editing." | hook / versus | two name pills with a round VS badge | "THE SAME EDITING TEST" label, 6 vs 5.1 numerals |
| 5.0-6.0 | "Who do you think will win?" | question | none | none |
| 6.0-10.0 | "I gave it this raw video and a prompt to make edits. That's it." | setup | small UI screenshot card | "THE ENTIRE BRIEF" card with thumbnail |
| 10.0-15.0 | "Every graphic in this video was drawn by AI. Without me editing anything." | claim | none | "BUILT FROM CODE" line-drawing that morphs into a blob |
| 15.0-19.0 | "Every line in this video is a different job. Note how they render differently." | framing | none | none |
| 19.0-25.0 | "Here is a number: 1 recording. 2 models, 0 edits from me." | number | three chips pop in one by one: 1, 2, 0 with icons | "THE TEST, IN NUMBERS": 1 / 2 / 0 with labels and underline |
| 25.0-31.0 | "Here are two things to compare. A timeline editor moves pixels around. This one moves code." | comparison | dark timeline UI mock, then code panel | "TIMELINE -> PICTURE", then "CODE -> PICTURE" |
| 31.0-40.0 | "Here are three at once. Which is harder? Color, font, and timing. All pulled from one brand file." | trio | color swatch, "Aa" type card, timing card, joined by a line | "ONE SOURCE, THREE OUTPUTS" tree diagram |
| 38.0-43.0 | "Here's a quote. They say in life you miss 100% of the shots you don't take." | quote | quote card with typewriter text | "THE SHOT NEVER TAKEN": ball, hoop, 100% counter |
| 43.0-52.0 | "Here are captions. Every word I'm saying should land on the screen as I say it..." | captions | none extra | none extra |
| 52.0-58.5 | "Here's the before and after. The raw take on one side and the finished cut on the other." | before/after | desaturated left half with a wipe line and camera HUD | literal split: RAW and FINISHED side by side |
| 58.5-65.0 | "Here's a ranking. Speed first. Control second. And something something third." | ranking | numbered list card, rows added as spoken | "THE PRIORITY ORDER" bars shrinking per rank |
| 65.0-72.0 | "Here's a word worth zooming into. Anchored. Every graphic is tied to the one moment I say it." | word zoom | "Anchored" over a timeline ruler | "ONE WORD, ONE FRAME": ANCHORED over a waveform with playhead |
| 72.0-80.0 | "And here's the hardest one. Do nothing. Some sentences don't need a graphic..." | restraint | none | none |
| 80.0-89.0 | "Bring back the number from the start. If it remembers it, it was watching the whole video..." | callback | 1 / 2 / 0 chips return | "BACK TO THE START": 1 2 0 with a timeline scrubber |
| 89.6-96.4 | "Comment 'edit' and I'll send you the setup, including the prompt..." | CTA (comment) | comment box with "EDIT" and a prompt.md file card | "GET THE SAME SETUP": EDIT field and prompt.md |
| 96.6-102.5 | "And follow me because I keep putting these two head to head." | CTA (follow) | red "Following" pill | withPT.ai brand line |
| 102.8-104.6 | "That's it for now. Thanks. Bye." | outro | none | none |

Scene-change detection found almost no hard cuts: the edit is one continuous take with graphics layered on top. Pauses were not removed.

### 3. Captions

- Top pane: 3 to 4 word chunk in a small white rounded box, current word in blue. At phone size the box text is roughly 14 px tall. It is hard to read.
- Bottom pane: same chunking, black text on white box with the current word in blue, slightly larger.
- Both sit on the speaker's chest, below the chin. Good placement. Both are too small for the pane they live in.

### 4. What works (and what splicecraft copies)

1. The script is a checklist of beat types. That makes it a fair benchmark and a great template for a rule-based planner.
2. Graphics land on the trigger word, not before or after.
3. "Do nothing" is treated as a skill. Restraint is scored.
4. The callback proves the edit understood the whole video, not one line at a time.
5. Every card has a small caps label ("THE TEST, IN NUMBERS"). It tells the viewer what kind of information is coming before they read it.
6. Model B's cards use one consistent visual system: pale card, blue numerals, thin rules. It reads as designed, not assembled.

### 5. Weak spots (critical review of UI, UX, and design)

Rated by how much each costs a viewer on a phone.

1. **Two videos in one frame halves everything.** Each face occupies about 12% of the screen. Expressions, which are the reason to watch a talking head, are lost.
2. **The header wastes the prime real estate.** The top 15% of a vertical video is the first place the eye lands. It holds a static title for 107 seconds. After second 3 it carries no new information.
3. **16:9 panes inside 9:16.** Roughly a quarter of the canvas is empty gradient. Vertical footage cropped for vertical would have filled it.
4. **Top-pane graphics are too small to read.** The three-card "color, font, timing" beat and the prompt.md card have text under 10 px at phone size. A graphic you cannot read is decoration.
5. **Model B squeezes the speaker to the right.** Its cards take the left 60% of the pane, so the face sits at the edge and is sometimes cut off at the shoulder.
6. **No music, no sound design.** Card entrances are silent. Nothing marks the beats for someone half-watching.
7. **No grade.** White wall, flat light, neutral color. It looks like a webcam. A slight contrast lift and warmth would separate the speaker from the wall.
8. **No pause removal.** The take has dead air between sentences (6.5 s total at a 0.3 s threshold). On a 107 s short that is 6% of runtime doing nothing.
9. **The test never ends.** There is no verdict, score, or winner reveal. The hook asks "who do you think will win?" and the video never pays it off, which hurts retention at the end.
10. **Transcript placeholder left in.** "And something something third" is spoken filler that becomes a graphic ("Something something") in both edits. Neither model flagged it.
11. **Weak CTA hierarchy.** Two calls to action (comment, then follow) back to back. The comment CTA is stronger for reach; the follow pill competes with it.
12. **Split before/after inside a split screen.** Model B shows RAW and FINISHED side by side inside a half-height pane: four small faces at once. It is the hardest moment to read.
13. **Same end frame for both halves.** The last 3 seconds show no graphics on either pane. No end card, no loop point back to the start.

### 6. How splicecraft goes further

| Baseline gap | splicecraft behavior |
|---|---|
| Face is small | Full-frame 9:16 speaker, cards in the top third only |
| Tiny captions | 66-80 px captions on a 1920 grid, heavy weight, stroke and shadow, word-level pop |
| Dead air | Pause removal scaled by level |
| No sound | Generated music bed with sidechain ducking, pop / whoosh / tick effects on card entrances |
| Flat image | Five grades plus LUT support and film grain at Pro level and up |
| No motion on the speaker | Punch-in, ease-in, and drift zooms tied to beats |
| No green-screen path | Chroma key with despill over an image, video, or animated gradient |
| Loudness not managed | Voice chain (high-pass, compressor, presence EQ) and loudnorm to -14 LUFS |
| No quality gate | `qa` subcommand with nine pass/fail checks and a contact sheet |
| Fixed intensity | One dial from 1 to 100 |

### 7. Honest limits of the automated version

- The planner is rule-based. It will not draw bespoke illustrations like model B's basketball hoop. Custom illustrations need a motion tool (Remotion, After Effects) or a human.
- It does not track the face. Cards assume the face is in the middle third, which is true for most talking heads and false for some.
- Transcript mistakes become caption mistakes. Step 3 of SKILL.md asks the agent to read the transcript for this reason.

---

# Part 18. design-secrets-glass.md

## Design study 2: the frosted-glass edit

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Source studied: a 26.0 second vertical video (1080x1920, 30 fps) from the softgirlnocode account. Same format as the first baseline (two AI models edit one take, stacked), but a very different visual system. A woman speaks to camera in a bright apartment: grey wall, window, white chair, black top.

Transcript (Whisper large-v3):

| Time (s) | Speech |
|---|---|
| 0.0 | "For the past few months, I've been using AI to edit pretty much all my short form videos" |
| 4.3 | "from animating interfaces, adding graphic effects to creating spatial captions." |
| 9.3 | "It is honestly incredible." |
| 10.7 | "What blew me away is every time I ask it to create something and think it probably can't do it, it won't look good." |
| 16.0 | "And somehow it does it." |
| 17.2 | "What's required from you is just articulate what you want, because now you can create animations in minutes" |
| 20.9 | "that previously would have taken a highly skilled graphic designer hours to do." |

The footage belongs to its creator and is not redistributed here. Only the techniques are described.

### Why it looks expensive: 10 techniques

#### 1. Frosted glass cards instead of flat white cards

Cards are not painted on top of the video. They are windows into a blurred, brightened copy of the video behind them, with a faint white tint and a 1-2 px light hairline border. The room stays visible through the card, so the graphic feels like it lives inside the scene.

**In splicecraft:** `--style glass`, or `"glass": true` in `brand.json`. The renderer crops the zoomed frame under each card, applies `gblur` (sigma 34 on a 1920 grid) plus `eq=brightness=0.05:saturation=1.15`, cuts rounded corners with a `geq` alpha mask, fades it in and out with the card, and overlays it before the captions. `glass_alpha` (0 opaque to 255 clear, default 150) sets how much tint sits on top.

**Rule:** glass needs something behind it. On a plain white wall it reads as a grey box. Use it on footage with depth: windows, furniture, plants, city.

#### 2. Eyebrow labels

Every card starts with a tiny, widely spaced, all-caps label: "AND SOMEHOW...", "TIME TO CREATE", "EDIT TIMELINE", "PROOF · AI EDITED REELS". It tells the eye what kind of card this is before it reads the content. The first baseline does the same ("THE TEST, IN NUMBERS").

**In splicecraft:** the `label` field on every card, drawn at 30 px with 4 px letter spacing in the `muted` color.

#### 3. Headline with a full stop

"Minutes." with a period, set very large and heavy, then a thin rule under it. Punctuation on a one-word headline turns it into a statement. Variant in the other edit: "Minutes, not hours." with the second phrase in grey.

**In splicecraft:** `word` cards. If you edit `edl.json` by hand, add the period to `text`.

#### 4. Two-tone contrast headlines

"Minutes, not hours." puts the claim in the accent green and the rejected alternative in dark neutral. The eye reads the colored half first.

**How to do it by hand:** in the `.ass` file, wrap the second half in `{\1c&H6B645E&}`.

#### 5. Real interface mockups, not icons

Instead of an icon for "timeline", the card shows a small timeline: a title bar ("EDIT TIMELINE 00:00:21"), a playhead, and colored clip bars in soft pastels (sky, peach, lilac, mint, butter). A prompt box with a blinking cursor, then a green check pill "and it does it". The viewer recognizes a product UI, which is more convincing than a symbol.

**In splicecraft:** the ranking card's bars are the same idea (rows of rounded color bars). For full mockups, render a PNG in any design tool and overlay it (see "Image overlays" below).

#### 6. Layout reflow: the speaker makes room

On the "Minutes" beat the full-frame shot shrinks into a rounded card with a drop shadow and slides left while a panel slides in from the right. The speaker is still visible but the information gets half the frame. When the beat ends, the shot grows back.

**Recipe (manual, ffmpeg):**

```bash
## T0 = beat start, T1 = beat end, output 1080x1920
ffmpeg -i edited.mp4 -loop 1 -i panel.png -filter_complex "[0:v]split=3[full][small][blur];[small]scale=520:924,format=yuva420p,geq=lum='p(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='255*lte(hypot(max(0,abs(X-260)-228),max(0,abs(Y-462)-430)),32)'[card];[blur]gblur=sigma=40,eq=brightness=0.08[bg];[bg][card]overlay=x=40:y=480[a];[a][1:v]overlay=x=580:y=480:shortest=1[b];[full][b]overlay=enable='between(t,T0,T1)'[v]" -map "[v]" -map 0:a -c:a copy reflow.mp4
```

Replace `T0` and `T1` with numbers. Keep reflow to one or two beats per video; it is the strongest move you have.

#### 7. Spatial captions (text behind the person)

A big word ("bigger") sits behind the speaker's head: the person occludes the text. It needs a per-frame person mask.

**Honest limit:** ffmpeg alone cannot segment a person. Options: (a) shoot on a green screen and use `--key`, then burn the word into the background before overlaying the person; (b) run a segmentation model (MediaPipe Selfie Segmentation, rembg, or Robust Video Matting) to export a mask video, then composite `background -> word -> person`. splicecraft does not ship a model, to stay dependency-free.

#### 8. A color pulse on the emotional beat

On "and somehow it does it" the whole frame warms (orange-peach tint, lifted highlights) for about a second, then returns. It works like a sound cue for the eyes.

**In splicecraft:** at level 41+, every `word` and `question` card triggers a `colortemperature` pulse (down to about 5000 K) for up to 1.2 s.

#### 9. Muted captions that do not compete

Captions are small white sentence-case text on a dark translucent rounded pill, low on the frame. Because the cards carry the emphasis, the captions stay quiet.

**In splicecraft:** the `glass` look sets `caption_size` 64 and `caption_y` 1430. For a pill background, set level 21-40 (chunk style) and change the Caption style's `BorderStyle` from 1 to 3 in the `.ass` header (3 draws an opaque box using the outline color).

#### 10. A restrained palette

Warm grey room, black clothing, white glass, one saturated green for success states, pastels only inside mockups. The title uses a yellow italic highlight with an outline for the words "AI Model", the only loud element, and it is fixed at the top.

**In splicecraft:** `glass` look uses a green accent `#1E9E5A`, near-white card tint, warm grade.

### Weak spots in this video

1. Same split-screen problem as baseline 1: each face is small and the header plus model rows take about a third of the frame.
2. Glass cards on the top pane sit over a grey wall, so they read as grey boxes (see rule under technique 1).
3. The mockup text ("Create something...", timeline labels) is unreadable at phone size. It signals "UI" but cannot be read.
4. The model rows show "35mins & 7M token" vs "29mins & 12M token" in italic light grey. It is the most interesting data in the video and it is styled as fine print.
5. No hook card in the first 2 seconds; the first graphic arrives around 1.5-3 s.
6. The persistent line "comment 'vid' to get the full video" is the CTA for the whole video, set at body size with no contrast, below both panes.
7. It ends mid-thought at 26 s with no end card.

### Image overlays (for mockups you design elsewhere)

```bash
ffmpeg -i edited.mp4 -loop 1 -i mockup.png -filter_complex "[1:v]format=rgba,fade=t=in:st=12.0:d=0.25:alpha=1,fade=t=out:st=15.5:d=0.25:alpha=1[m];[0:v][m]overlay=x=(W-w)/2:y=260:enable='between(t,12,15.75)':shortest=1[v]" -map "[v]" -map 0:a -c:a copy out.mp4
```

Export the PNG at the final pixel size (for a 940 px wide card on 1080 output, export 940 px wide). Scaling a PNG up blurs it.

---

# Part 19. edl-schema.md

## edl.json schema

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

The edit decision list is plain JSON. `plan` writes it, `render` reads it. You can change anything between the two.

All times are in seconds on the **output** timeline (after pause removal), except `keep`, which is in **source** time.

```jsonc
{
  "version": 1,
  "params": {                 // from presets/levels.json + params_for(level)
    "level": 60, "tier": "Creator",
    "captions": "highlight",  // plain | chunk | highlight | pop | kinetic
    "caption_words": 3,
    "zoom": true, "sfx": true, "music": true,
    "hook_title": true, "progress": false, "flash": false,
    "word_zoom": true, "allow_ranking": true, "callbacks": true,
    "silence_gap": 0.56, "cards_per_min": 6.0, "min_card_gap": 5.6,
    "zoom_amount": 1.132, "grade_strength": 0.7
  },
  "theme": { "accent": "#FF5A1F", "...": "see presets/styles.json" },
  "keep": [[0.0, 4.93], [5.4, 9.1]],   // source ranges kept, in order
  "duration": 101.1,                  // output length
  "words": [ {"w": "Let's", "s": 0.1, "e": 0.32, "brk": false} ],
  "cards": [ /* see below */ ],
  "zooms": [ {"start": 20.0, "end": 21.2, "amount": 1.11, "ease": "punch"} ], // ease: punch | in | drift
  "sfx":   [ {"t": 20.0, "kind": "pop"} ],                                    // kind: pop | tick | whoosh
  "flashes": [ {"t": 64.8} ]
}
```

### Card shapes

```jsonc
{"type": "hook",     "start": 0.1,  "end": 4.3,  "label": "", "text": "Let's see who edits better"}
{"type": "number",   "start": 20.0, "end": 25.2, "label": "BY THE NUMBERS",
 "items": [{"value": "1", "label": "recording", "t": 20.0}, {"value": "2", "label": "models", "t": 22.2}]}
{"type": "callback", "start": 78.3, "end": 82.9, "label": "BACK TO THE START",
 "items": [{"value": "1", "label": "recording"}]}
{"type": "ranking",  "start": 57.7, "end": 62.4, "label": "RANKED",
 "items": [{"rank": 1, "text": "Speed", "t": 58.8}, {"rank": 2, "text": "Control", "t": 60.0}]}
{"type": "quote",    "start": 39.2, "end": 43.9, "label": "QUOTE", "text": "They say ..."}
{"type": "question", "start": 4.7,  "end": 6.3,  "label": "", "text": "Who will win?"}
{"type": "versus",   "start": 51.9, "end": 55.4, "label": "", "left": "BEFORE", "right": "AFTER"}
{"type": "word",     "start": 64.8, "end": 66.2, "label": "", "text": "ANCHORED"}
{"type": "cta",      "start": 95.7, "end": 100.0, "label": "", "text": "follow sentence"}
```

`items[].t` is when that item appears. Omit it to show all items at the card start.

### Limits the renderer assumes

- hook: up to 3 lines of about 18 characters.
- number and callback: up to 3 items.
- ranking: up to 5 rows, row text up to 22 characters.
- quote: up to 4 lines of about 24 characters.
- question: up to 30 characters.
- versus: up to 12 characters per side.
- word: up to 14 characters.

Longer text is truncated or runs off the card. Shorten it in the JSON.

### Validating after hand edits

```bash
python -c "import json;json.load(open('work/edl.json'))" && echo valid
```

Then run `render` and `qa`. The `no_card_overlap` gate catches cards whose times collide.

---

# Part 20. agent-prompts.md

## Prompts for different agents

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

The script makes the decisions, so output quality depends very little on which model runs it. What changes between agents is how they install the skill and how much hand-holding they need.

### Claude Code

Install once (either works):

```bash
npx skills add bryankwandou/splicecraft
## or
git clone https://github.com/bryankwandou/splicecraft ~/.claude/skills-src/splicecraft
cp -r ~/.claude/skills-src/splicecraft/skills/splicecraft ~/.claude/skills/
```

Prompt:

```
Use the splicecraft skill. Edit ./raw/take1.mp4. Ask me the intake questions first.
```

### OpenAI Codex CLI

```bash
git clone https://github.com/bryankwandou/splicecraft .splicecraft
```

Prompt:

```
Read .splicecraft/skills/splicecraft/SKILL.md completely, then follow it step by step to edit ./raw/take1.mp4.
Run every command it lists. Ask me the Step 1 questions before rendering.
```

Add to `AGENTS.md` to make it permanent:

```
When asked to edit a video, follow .splicecraft/skills/splicecraft/SKILL.md exactly.
```

### ChatGPT (chatgpt.com, with Code Interpreter / data analysis)

ChatGPT in the browser runs Python in a sandbox. That sandbox has no internet, usually has no ffmpeg with libass, and limits uploads to roughly 512 MB and runs to a few minutes. So ChatGPT is good at the thinking half (transcript review, genre, plan) and weak at the rendering half.

Split the work:

1. On your machine: `python splicecraft.py transcribe take.mp4 -o words.json`
2. Upload `words.json`, `splicecraft.py`, and the `presets/` folder (zip it) to ChatGPT.
3. Prompt:

```
Unzip presets.zip next to splicecraft.py. Then run, and paste the full output of each:
  python splicecraft.py detect words.json
  python splicecraft.py plan words.json -o edl.json --level 60 --style auto --genre auto
Read edl.json. List every card with type, start, end, text. Tell me if the detected genre is wrong
and which --genre you would use instead, with the keyword hits as evidence.
Do not render. Give me edl.json to download.
```

4. Back on your machine: `python splicecraft.py render take.mp4 edl.json -o edited.mp4 --size 1080x1920`, then `qa`.

If ChatGPT says ffmpeg is available and offers to render, let it try a 10 second test first (`ffmpeg -t 10`). Most sandboxes lack the `subtitles` filter, and the render fails without captions or cards.

Custom GPT: put the SKILL.md text in Instructions, attach `splicecraft.py`, `genres.json`, `styles.json`, `levels.json` as Knowledge, enable Code Interpreter. Same split applies.

### OpenAI Codex CLI and GPT models in any terminal agent

Codex runs on your machine, so it can do everything including render. See the Codex section above. GPT models follow numbered steps well but tend to "improve" commands by adding flags. Add: `Use only flags listed in SKILL.md. If unsure, run python splicecraft.py <command> --help.`

### Fable 5.1 (Claude Code, Claude desktop Code tab, or API agents)

Fable reads the whole skill folder and follows long instructions reliably, so give it the full job in one message and let it ask Step 1 questions:

```
Use the splicecraft skill on ./raw/take.mp4.
Run detect first and show me the genre ranking with keyword hits before asking the intake questions,
so my defaults match the video (hackathon demo, tutorial, launch, story, etc.).
Render at 1080x1920, run QA, fix anything that fails, and show me the contact sheet.
```

What Fable does well here: reading `edl.json` and hand-fixing a card whose text is wrong, rewriting a hook that starts with a greeting (beat-library.md, hook "Do not"), and reading the contact sheet image to catch cards covering the face.

What to forbid: long "creative" rewrites of the transcript. Add `Change spelling only, never wording or timestamps.`

Renders take minutes. In Claude Code, tell it to run render in the background so the session stays responsive.

### Gemini CLI

```bash
git clone https://github.com/bryankwandou/splicecraft .splicecraft
```

Add to `GEMINI.md`:

```
For any video editing request, read .splicecraft/skills/splicecraft/SKILL.md and follow the steps in order.
Do not skip Step 6 (QA). Do not invent command flags.
```

### Cursor, Windsurf, Cline

Put the repo in the project, then add a rule file (`.cursor/rules/splicecraft.mdc` or equivalent) containing the same two lines as the Gemini example.

### Small or cheap models

Smaller models drift when a task has many steps. Give them one step per message:

```
Message 1: Read SKILL.md Step 0 and run those checks. Report the output only.
Message 2: Ask me the Step 1 questions.
Message 3: Run Step 2 and Step 3. Show me the segments from words.json.
Message 4: Run Step 4 with --level <N> --style <look>. Paste the planner line and the list of cards.
Message 5: Run Step 5.
Message 6: Run Step 6 and paste the QA table.
```

Or skip the reasoning entirely and have them run the one-shot command:

```
Run exactly this and paste the output:
python .splicecraft/skills/splicecraft/scripts/splicecraft.py auto raw/take1.mp4 -d work --level 60 --style studio --size 1080x1920
```

### Things to forbid in the prompt if an agent misbehaves

- "Do not download music or fonts from the internet."
- "Do not overwrite the input file."
- "Do not change timestamps in words.json, only spelling."
- "If a command fails, paste the error and stop. Do not try random flags."

---

# Part 21. troubleshooting.md

## Troubleshooting

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

| Symptom | Cause | Fix |
|---|---|---|
| `ffmpeg not found on PATH` | not installed or terminal opened before install | install, then open a new terminal |
| `No such filter: 'subtitles'` | ffmpeg built without libass | install a full build (gyan.dev full on Windows, Homebrew or apt on Mac/Linux) |
| `No such filter: 'gradients'` | ffmpeg older than 6.1 | pass `--bg image.jpg` with `--key`, or upgrade ffmpeg |
| `HTTP Error 401` during transcribe | bad Groq key, often a hidden BOM or trailing newline | re-export `GROQ_API_KEY`; the script strips BOM but not wrong keys |
| `HTTP Error 413` | audio file too big for the API | `--engine local`, or cut the clip into parts |
| Captions in a different font than expected | family name not installed | `--fontsdir` plus exact family name; see captions.md |
| Captions show `{\...}` tags as text | a word in the transcript contains braces | the script replaces them; if you hand-edited, remove `{` `}` |
| Render stops with `Error reinitializing filters` | variable frame rate or rotation metadata | re-encode first: `ffmpeg -i in.mp4 -vf fps=30 -c:a aac fixed.mp4` |
| Audio drifts out of sync late in the video | variable frame rate phone footage | same re-encode as above |
| Output is shorter than expected | pause removal at a high level | lower the level or `plan --no-cut` |
| Words clipped at the start of a cut | speaker starts very softly | lower level by 10, which widens the pause threshold |
| Face covered by a card | speaker framed high | set `"card_y": 120` or move captions with `caption_y` in brand.json |
| Green edge around the person | chroma similarity too low | see color-and-cinematic.md section 6 |
| Render very slow | per-frame zoom scaling at 1080x1920 60 fps | `--fps 30 --preset veryfast` for drafts |
| `QA FAILED loudness` with own music | music master is very hot | `--music-db -24` |
| Planner makes 0 cards | level 1-20, or no triggers in speech | raise level; or add cards by hand (edl-schema.md) |
| Windows: `UnicodeEncodeError` | console code page | run `chcp 65001` first or use Windows Terminal |

---

# Part 22. Presets

## presets/levels.json

```json
{
  "note": "Edit level 1-100 is split into five tiers. Continuous values (silence gap, card density, zoom, grade strength) are interpolated inside splicecraft.py:params_for. Tier params below are switches.",
  "tiers": [
    {"name": "Clean",      "min": 1,  "max": 20,  "params": {"captions": "clean_accent", "caption_words": 7, "zoom": false, "sfx": false, "music": false, "hook_title": false, "progress": false, "flash": false, "word_zoom": false, "allow_ranking": false, "callbacks": false}},
    {"name": "Social",     "min": 21, "max": 40,  "params": {"captions": "chunk",     "caption_words": 4, "zoom": true,  "sfx": false, "music": true,  "hook_title": true,  "progress": false, "flash": false, "word_zoom": false, "allow_ranking": true,  "callbacks": false}},
    {"name": "Creator",    "min": 41, "max": 60,  "params": {"captions": "highlight", "caption_words": 3, "zoom": true,  "sfx": true,  "music": true,  "hook_title": true,  "progress": false, "flash": false, "word_zoom": true,  "allow_ranking": true,  "callbacks": true}},
    {"name": "Pro",        "min": 61, "max": 80,  "params": {"captions": "pop",       "caption_words": 3, "zoom": true,  "sfx": true,  "music": true,  "hook_title": true,  "progress": true,  "flash": false, "word_zoom": true,  "allow_ranking": true,  "callbacks": true}},
    {"name": "Showrunner", "min": 81, "max": 100, "params": {"captions": "kinetic",   "caption_words": 3, "zoom": true,  "sfx": true,  "music": true,  "hook_title": true,  "progress": true,  "flash": true,  "word_zoom": true,  "allow_ranking": true,  "callbacks": true}}
  ]
}
```

## presets/styles.json

```json
{
  "studio": {
    "accent": "#FF5A1F",
    "on_accent": "#FFFFFF",
    "card_bg": "#FFFFFF",
    "card_text": "#14161A",
    "muted": "#6B7280",
    "caption_text": "#FFFFFF",
    "caption_stroke": "#0B0C0F",
    "caption_size": 76,
    "caption_y": 1390,
    "card_y": 230,
    "grade": "punchy",
    "bpm": 100,
    "music_mood": "bright",
    "bg_a": "#FFE9DC",
    "bg_b": "#FFB38A",
    "cta_text": "Follow for part two"
  },
  "cinema": {
    "accent": "#E8C27A",
    "on_accent": "#101010",
    "card_bg": "#121417",
    "card_text": "#F4EFE6",
    "muted": "#9AA0A6",
    "caption_text": "#F4EFE6",
    "caption_stroke": "#000000",
    "caption_size": 66,
    "caption_y": 1420,
    "card_y": 250,
    "grade": "cinematic",
    "bpm": 84,
    "music_mood": "moody",
    "bg_a": "#0E1116",
    "bg_b": "#2A2F3A",
    "cta_text": "Follow for the next one",
    "caption_upper": false
  },
  "neon": {
    "accent": "#B6FF3B",
    "on_accent": "#0A0A0A",
    "card_bg": "#0A0A0A",
    "card_text": "#FFFFFF",
    "muted": "#8A8F98",
    "caption_text": "#FFFFFF",
    "caption_stroke": "#000000",
    "caption_size": 80,
    "caption_y": 1380,
    "card_y": 230,
    "grade": "punchy",
    "bpm": 118,
    "music_mood": "bright",
    "bg_a": "#050505",
    "bg_b": "#1B2A10",
    "cta_text": "FOLLOW FOR MORE",
    "caption_upper": true
  },
  "editorial": {
    "accent": "#1F5EFF",
    "on_accent": "#FFFFFF",
    "card_bg": "#F6F3EC",
    "card_text": "#111111",
    "muted": "#6E6A62",
    "caption_text": "#FFFFFF",
    "caption_stroke": "#111111",
    "caption_size": 70,
    "caption_y": 1400,
    "card_y": 240,
    "grade": "warm",
    "bpm": 92,
    "music_mood": "bright",
    "bg_a": "#F6F3EC",
    "bg_b": "#D9D2C3",
    "cta_text": "Follow for more tests"
  },
  "noir": {
    "accent": "#FF3355",
    "on_accent": "#FFFFFF",
    "card_bg": "#FFFFFF",
    "card_text": "#000000",
    "muted": "#555555",
    "caption_text": "#FFFFFF",
    "caption_stroke": "#000000",
    "caption_size": 74,
    "caption_y": 1400,
    "card_y": 240,
    "grade": "mono",
    "bpm": 88,
    "music_mood": "moody",
    "bg_a": "#000000",
    "bg_b": "#222222",
    "cta_text": "Follow"
  },
  "glass": {
    "accent": "#1E9E5A",
    "on_accent": "#FFFFFF",
    "card_bg": "#F4F6F5",
    "card_text": "#15201A",
    "muted": "#5E6B64",
    "caption_text": "#FFFFFF",
    "caption_stroke": "#1B1F1D",
    "caption_size": 64,
    "caption_y": 1430,
    "card_y": 250,
    "grade": "warm",
    "bpm": 92,
    "music_mood": "bright",
    "bg_a": "#EEF2EF",
    "bg_b": "#CFE3D6",
    "cta_text": "Comment VID for the full video",
    "glass": true,
    "glass_alpha": 150
  }
}
```

## presets/genres.json

```json
{
  "note": "Video genres the planner can detect from the transcript. keywords are scored per occurrence (English + Indonesian). style is the default look when --style auto; level_shift moves the requested level; params override the level's params; drop_beats removes card types that do not suit the genre; palettes are accent colors picked per video by --variant (or a hash of the transcript).",
  "genres": {
    "hackathon_demo": {
      "label": "Hackathon / product demo",
      "keywords": [
        "hackathon",
        "demo",
        "we built",
        "i built",
        "built",
        "prototype",
        "mvp",
        "judges",
        "submission",
        "track",
        "bounty",
        "solana",
        "onchain",
        "on-chain",
        "smart contract",
        "devnet",
        "mainnet",
        "wallet",
        "api",
        "github",
        "deploy",
        "deployed",
        "live",
        "dashboard",
        "users can",
        "problem",
        "solution",
        "team",
        "pitch",
        "hackaton",
        "kami membangun",
        "kami bikin",
        "juri",
        "solusi",
        "masalah",
        "tim"
      ],
      "style": "neon",
      "level_shift": 5,
      "params": {
        "cards_per_min_scale": 1.1,
        "flash": false
      },
      "drop_beats": [],
      "palettes": [
        "#C6FF3D",
        "#00E5FF",
        "#FF3DCB",
        "#7C5CFF",
        "#FFB800",
        "#14F195",
        "#FF5A1F",
        "#3DA5FF"
      ],
      "cta_text": "Try the live demo",
      "music_mood": "bright",
      "bpm": 112,
      "caption_modes": [
        "boxed",
        "pop",
        "kinetic"
      ]
    },
    "tutorial_docs": {
      "label": "Tutorial / documentation / walkthrough",
      "keywords": [
        "step",
        "steps",
        "click",
        "install",
        "open",
        "type",
        "run",
        "command",
        "settings",
        "configure",
        "setup",
        "set up",
        "folder",
        "file",
        "documentation",
        "docs",
        "tutorial",
        "how to",
        "guide",
        "next",
        "then",
        "select",
        "menu",
        "button",
        "langkah",
        "klik",
        "buka",
        "pasang",
        "jalankan",
        "pengaturan",
        "cara",
        "panduan",
        "dokumentasi",
        "pilih",
        "lalu",
        "kemudian"
      ],
      "style": "editorial",
      "level_shift": -15,
      "params": {
        "cards_per_min_scale": 0.8,
        "zoom_scale": 0.5,
        "flash": false
      },
      "drop_beats": [
        "word",
        "versus"
      ],
      "palettes": [
        "#1F5BFF",
        "#0F8A5F",
        "#B8410E",
        "#6D28D9",
        "#0E7490",
        "#BE185D",
        "#374151",
        "#A16207"
      ],
      "cta_text": "Full guide in the description",
      "music_mood": "moody",
      "bpm": 84,
      "caption_modes": [
        "clean_accent",
        "sweep",
        "highlight"
      ]
    },
    "product_launch": {
      "label": "Product launch / ad",
      "keywords": [
        "introducing",
        "launch",
        "new",
        "announce",
        "available",
        "price",
        "pricing",
        "free",
        "sign up",
        "waitlist",
        "feature",
        "features",
        "customers",
        "brand",
        "today",
        "limited",
        "discount",
        "order",
        "buy",
        "memperkenalkan",
        "peluncuran",
        "baru",
        "harga",
        "gratis",
        "fitur",
        "daftar",
        "beli",
        "promo"
      ],
      "style": "glass",
      "level_shift": 10,
      "params": {
        "cards_per_min_scale": 1.0
      },
      "drop_beats": [
        "callback"
      ],
      "palettes": [
        "#3DDC97",
        "#FF7AB6",
        "#FFD166",
        "#8EC5FF",
        "#FF8A5B",
        "#B794F6",
        "#5EEAD4",
        "#F5F5F5"
      ],
      "cta_text": "Link in bio",
      "music_mood": "bright",
      "bpm": 104,
      "caption_modes": [
        "bounce",
        "boxed",
        "pop"
      ]
    },
    "education_explainer": {
      "label": "Education / explainer / news",
      "keywords": [
        "why",
        "because",
        "means",
        "research",
        "study",
        "percent",
        "data",
        "history",
        "science",
        "fact",
        "facts",
        "explain",
        "reason",
        "actually",
        "study shows",
        "according",
        "kenapa",
        "karena",
        "artinya",
        "penelitian",
        "fakta",
        "sejarah",
        "data",
        "menurut",
        "persen"
      ],
      "style": "studio",
      "level_shift": 0,
      "params": {
        "cards_per_min_scale": 1.0
      },
      "drop_beats": [],
      "palettes": [
        "#FF5A1F",
        "#2563EB",
        "#16A34A",
        "#DB2777",
        "#9333EA",
        "#EA580C",
        "#0891B2",
        "#CA8A04"
      ],
      "cta_text": "Follow for part two",
      "music_mood": "bright",
      "bpm": 96,
      "caption_modes": [
        "highlight",
        "stack",
        "pop"
      ]
    },
    "story_vlog": {
      "label": "Story / vlog / personal",
      "keywords": [
        "i was",
        "my life",
        "felt",
        "feel",
        "life",
        "day",
        "yesterday",
        "story",
        "family",
        "friend",
        "love",
        "trip",
        "honestly",
        "aku",
        "gue",
        "cerita",
        "hidup",
        "hari",
        "kemarin",
        "rasanya",
        "keluarga",
        "teman",
        "jujur"
      ],
      "style": "cinema",
      "level_shift": -5,
      "params": {
        "cards_per_min_scale": 0.6,
        "flash": false
      },
      "drop_beats": [
        "ranking",
        "versus"
      ],
      "palettes": [
        "#E8B04A",
        "#D97757",
        "#C9A227",
        "#E07A5F",
        "#B5838D",
        "#81B29A",
        "#F2CC8F",
        "#CDB4DB"
      ],
      "cta_text": "Follow for the rest of the story",
      "music_mood": "moody",
      "bpm": 80,
      "caption_modes": [
        "sweep",
        "clean_accent",
        "highlight"
      ]
    },
    "sales_pitch": {
      "label": "Sales / business / finance tips",
      "keywords": [
        "money",
        "revenue",
        "profit",
        "clients",
        "business",
        "sales",
        "income",
        "growth",
        "marketing",
        "strategy",
        "mistake",
        "mistakes",
        "tips",
        "secret",
        "roi",
        "uang",
        "omzet",
        "untung",
        "klien",
        "bisnis",
        "penjualan",
        "strategi",
        "rahasia",
        "cuan"
      ],
      "style": "noir",
      "level_shift": 10,
      "params": {
        "cards_per_min_scale": 1.15
      },
      "drop_beats": [],
      "palettes": [
        "#E11D48",
        "#F59E0B",
        "#10B981",
        "#F43F5E",
        "#FACC15",
        "#22D3EE",
        "#FB7185",
        "#FFFFFF"
      ],
      "cta_text": "Comment GUIDE",
      "music_mood": "bright",
      "bpm": 100,
      "caption_modes": [
        "stack",
        "kinetic",
        "boxed"
      ]
    },
    "podcast_talk": {
      "label": "Podcast / interview / long talk",
      "keywords": [
        "podcast",
        "episode",
        "guest",
        "interview",
        "conversation",
        "question",
        "think",
        "opinion",
        "agree",
        "tamu",
        "obrolan",
        "episode",
        "pendapat",
        "setuju",
        "menurutku"
      ],
      "style": "cinema",
      "level_shift": -20,
      "params": {
        "cards_per_min_scale": 0.5,
        "zoom_scale": 0.6,
        "flash": false
      },
      "drop_beats": [
        "word"
      ],
      "palettes": [
        "#E8B04A",
        "#7DD3FC",
        "#F0ABFC",
        "#86EFAC",
        "#FCA5A5",
        "#FDE68A",
        "#C4B5FD",
        "#FDBA74"
      ],
      "cta_text": "Full episode on the channel",
      "music_mood": "moody",
      "bpm": 76,
      "caption_modes": [
        "sweep",
        "highlight",
        "clean_accent"
      ]
    },
    "ai_comparison": {
      "label": "AI / tool comparison (like the withpt.ai reference)",
      "keywords": [
        " vs ",
        "versus",
        "better",
        "compare",
        "comparison",
        "test",
        "tested",
        "benchmark",
        "winner",
        "won",
        "gpt",
        "chatgpt",
        "claude",
        "fable",
        "gemini",
        "astra",
        "model",
        "prompt",
        "agent",
        "ai",
        "lebih bagus",
        "bandingkan",
        "pemenang",
        "uji"
      ],
      "style": "studio",
      "level_shift": 5,
      "params": {
        "cards_per_min_scale": 1.1
      },
      "drop_beats": [],
      "palettes": [
        "#FF5A1F",
        "#10A37F",
        "#D97757",
        "#4285F4",
        "#8B5CF6",
        "#EC4899",
        "#14B8A6",
        "#F59E0B"
      ],
      "cta_text": "Which one wins? Comment below",
      "music_mood": "bright",
      "bpm": 104,
      "caption_modes": [
        "kinetic",
        "boxed",
        "stack"
      ]
    }
  },
  "variants": {
    "caption_size_scale": [
      0.92,
      1.0,
      1.08
    ],
    "card_y_offset": [
      -40,
      0,
      40
    ],
    "grade": [
      "style",
      "punchy",
      "warm",
      "cinematic",
      "clean"
    ]
  }
}
```

## presets/audience.json

```json
{
  "note": "Project brief -> edit decisions. Each field in brief.json picks one entry below; its effects are applied in order platform, market, age, stage, funnel, niche. level: added to the level. density: multiplies cards per minute. caption_scale: multiplies caption size. caption_modes: preferred caption styles (first that exists wins over the genre's). energy: music energy override. style: used when --style auto. Research date for platform numbers: 2026-09-15; see references/audience-and-market.md for sources.",
  "platform": {
    "tiktok":        {"size": "1080x1920", "ideal_seconds": [15, 45], "max_reach_seconds": 180, "level": 5,  "density": 1.0, "note": "completion rate is the heaviest signal; ~70% completion benchmark; search uses captions, on-screen text and transcript"},
    "reels":         {"size": "1080x1920", "ideal_seconds": [15, 60], "max_reach_seconds": 180, "level": 5,  "density": 1.0, "note": "shares and saves weigh above likes; Reels over 3 minutes stop being recommended to non-followers"},
    "shorts":        {"size": "1080x1920", "ideal_seconds": [30, 45], "max_reach_seconds": 180, "level": 0,  "density": 1.0, "note": "ranked on watch time per impression; ~65% average view duration gate under 30 s, ~50% above"},
    "linkedin":      {"size": "1080x1350", "ideal_seconds": [30, 90], "max_reach_seconds": 600, "level": -15, "density": 0.8, "caption_modes": ["clean_accent", "highlight"], "note": "professional feed, many watch muted at work; proof and clarity over hype"},
    "youtube_long":  {"size": "1920x1080", "ideal_seconds": [480, 900], "max_reach_seconds": 7200, "level": -20, "density": 0.5, "caption_modes": ["clean_accent", "sweep"], "note": "cards every few seconds tire a long viewer; chapters matter more"},
    "x_twitter":     {"size": "1080x1080", "ideal_seconds": [20, 60], "max_reach_seconds": 140, "level": 0, "density": 1.0, "note": "autoplay muted in feed; first frame must read as a claim"}
  },
  "market": {
    "b2c":       {"level": 5,   "density": 1.1, "cta": "follow", "note": "impulse and emotion; faster cuts, brighter look"},
    "b2b":       {"level": -10, "density": 0.85, "caption_modes": ["highlight", "stack", "clean_accent"], "style": "editorial", "cta": "book a demo", "note": "multi-stakeholder, 60-180 day cycles; proof, numbers, case studies"},
    "b2g":       {"level": -20, "density": 0.7, "caption_modes": ["clean_accent"], "style": "editorial", "cta": "download the brief", "note": "compliance and trust first; no hype language"},
    "investor":  {"level": -5,  "density": 1.0, "caption_modes": ["stack", "highlight"], "style": "cinema", "cta": "see the deck", "note": "market size, traction, team; every number on screen"},
    "creator":   {"level": 10,  "density": 1.15, "cta": "follow", "note": "personality-led; kinetic captions and word hits"},
    "nonprofit": {"level": -10, "density": 0.8, "caption_modes": ["sweep", "clean_accent"], "style": "cinema", "cta": "donate or share", "note": "story first, one clear ask"},
    "hackathon": {"level": 0,   "density": 1.1, "caption_modes": ["boxed", "highlight"], "style": "neon", "cta": "try the live demo", "note": "judges scan many videos; claim, demo, proof inside 60-120 s"}
  },
  "age": {
    "gen_z":      {"range": [13, 28], "level": 10,  "caption_scale": 1.0,  "caption_modes": ["kinetic", "bounce", "boxed"], "energy": "high", "note": "fast pattern changes, self-aware humor, native platform style"},
    "millennial": {"range": [29, 44], "level": 0,   "caption_scale": 1.0,  "caption_modes": ["pop", "highlight", "boxed"], "energy": "mid", "note": "value and credibility; how-to and story both work"},
    "gen_x":      {"range": [45, 60], "level": -10, "caption_scale": 1.08, "caption_modes": ["highlight", "clean_accent"], "energy": "mid", "note": "slower pace, larger text, clear benefit"},
    "boomer":     {"range": [61, 80], "level": -20, "caption_scale": 1.15, "caption_modes": ["clean_accent", "sweep"], "energy": "low", "note": "largest captions, fewest effects, no flashes"},
    "mixed":      {"range": [18, 65], "level": 0,   "caption_scale": 1.04, "note": "design for the oldest meaningful segment's readability"}
  },
  "stage": {
    "idea":       {"level": 0,   "grade": "clean",     "note": "pre-product: build in public, problem interviews, honest and scrappy"},
    "pre_revenue":{"level": 0,   "grade": "punchy",    "note": "prototype or hackathon: demo and proof beat polish"},
    "growth":     {"level": 5,   "grade": "punchy",    "note": "traction exists: social proof, case studies, offers"},
    "scale":      {"level": -5,  "grade": "cinematic", "note": "brand building: consistent look, fewer gimmicks"},
    "enterprise": {"level": -15, "grade": "clean",     "note": "brand safety and consistency; restraint signals quality"}
  },
  "funnel": {
    "awareness":     {"frameworks": ["HVC", "Curiosity Gap", "Myth vs Fact", "POV Scenario", "Endless Loop"], "cta": "follow", "note": "optimize completion and shares"},
    "consideration": {"frameworks": ["Comparison Breakdown", "What-Why-How", "Case Study", "Teardown"], "cta": "save this", "note": "optimize saves and profile visits"},
    "conversion":    {"frameworks": ["PAS", "AIDA", "4P", "PASTOR", "Hook-Story-Offer"], "cta": "link in bio", "note": "optimize clicks; one offer, one action"},
    "retention":     {"frameworks": ["Build in Public", "Q&A Escalation", "Challenge-Progress-Result"], "cta": "comment your question", "note": "optimize comments and repeat viewers"}
  },
  "niche": {
    "tech_ai":       {"style": "neon",      "moods": ["tech_pulse", "mysterious"],       "compliance": ""},
    "saas_b2b":      {"style": "editorial", "moods": ["corporate_clean", "confident"],   "compliance": ""},
    "web3_crypto":   {"style": "neon",      "moods": ["tech_pulse", "dark_tension"],     "compliance": "Not financial advice. Never promise returns. Many regions regulate crypto promotion."},
    "finance":       {"style": "noir",      "moods": ["confident", "corporate_clean"],   "compliance": "Not financial advice. Show risk. Regulated claims need a licensed review."},
    "health_fitness":{"style": "studio",    "moods": ["motivational", "uplifting"],      "compliance": "No medical claims or cure language. Results vary; say so."},
    "beauty_fashion":{"style": "glass",     "moods": ["bright_pop", "chill_lofi"],       "compliance": "Disclose paid partnerships and gifted products."},
    "food":          {"style": "studio",    "moods": ["sunny_acoustic", "playful"],      "compliance": ""},
    "travel":        {"style": "cinema",    "moods": ["sunny_acoustic", "hopeful"],      "compliance": ""},
    "education":     {"style": "studio",    "moods": ["corporate_clean", "hopeful"],     "compliance": "Cite sources for facts."},
    "gaming":        {"style": "neon",      "moods": ["tech_pulse", "playful"],          "compliance": "Game footage may be copyrighted; check the publisher's video policy."},
    "real_estate":   {"style": "cinema",    "moods": ["confident", "cinematic_epic"],    "compliance": "Housing ads have anti-discrimination rules in many regions."},
    "parenting":     {"style": "editorial", "moods": ["emotional", "calm_ambient"],      "compliance": "Children on camera: consent and privacy."},
    "religion":      {"style": "cinema",    "moods": ["hopeful", "calm_ambient"],        "compliance": "No rage bait. Respectful framing."},
    "local_business":{"style": "studio",    "moods": ["sunny_acoustic", "bright_pop"],   "compliance": "Prices and promos must be accurate on the date posted."},
    "automotive":    {"style": "noir",      "moods": ["cinematic_epic", "motivational"],      "compliance": ""},
    "career":        {"style": "editorial", "moods": ["confident", "motivational"],      "compliance": ""},
    "entertainment": {"style": "neon",      "moods": ["playful", "bright_pop"],          "compliance": "Clips from films, shows and songs are usually claimed."}
  },
  "funnel_defaults": {"view_to_profile": 0.01, "profile_to_click": 0.15, "click_to_buy": 0.02, "note": "Placeholder conversion assumptions for the revenue calculator. Replace with the user's own analytics; these are not benchmarks."}
}
```

## presets/music.json

```json
{
  "note": "Procedural, license-free background music. A template id is mood.key.drums.timbre.energy, e.g. tech_pulse.D.driving.pluck.high. Every template is synthesized by ffmpeg on the user's machine, so there is no copyright claim risk. Chords are semitone offsets from the key root. Drum patterns are 16 steps per bar (x = hit).",
  "keys": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
  "moods": {
    "uplifting":      {"bpm": 104, "chords": [[0,4,7],[7,11,14],[-3,0,4],[5,9,12]], "feel": "I-V-vi-IV, wins and reveals"},
    "bright_pop":     {"bpm": 112, "chords": [[0,4,7],[-3,0,4],[5,9,12],[7,11,14]], "feel": "I-vi-IV-V, lifestyle and launches"},
    "hopeful":        {"bpm": 96,  "chords": [[5,9,12],[0,4,7],[7,11,14],[-3,0,4]], "feel": "IV-I-V-vi, mission and impact"},
    "confident":      {"bpm": 100, "chords": [[-3,0,4],[5,9,12],[0,4,7],[7,11,14]], "feel": "vi-IV-I-V, pitches and tips"},
    "corporate_clean":{"bpm": 98,  "chords": [[0,4,7],[5,9,12],[-3,0,4],[7,11,14]], "feel": "I-IV-vi-V, explainers and B2B"},
    "playful":        {"bpm": 118, "chords": [[0,4,7],[2,5,9],[4,7,11],[5,9,12]], "feel": "I-ii-iii-IV, light and funny"},
    "calm_ambient":   {"bpm": 76,  "chords": [[0,4,7],[5,9,12],[-3,0,4],[5,9,12]], "feel": "I-IV-vi-IV, tutorials and talk"},
    "chill_lofi":     {"bpm": 84,  "chords": [[2,5,9],[7,11,14],[0,4,7],[-3,0,4]], "feel": "ii-V-I-vi, study, docs, vlogs"},
    "emotional":      {"bpm": 80,  "chords": [[0,4,7],[4,7,11],[5,9,12],[5,8,12]], "feel": "I-iii-IV-iv, stories and gratitude"},
    "tech_pulse":     {"bpm": 116, "chords": [[0,3,7],[-4,0,3],[3,7,10],[-2,2,5]], "feel": "i-VI-III-VII minor drive, demos and AI"},
    "cinematic_epic": {"bpm": 90,  "chords": [[0,3,7],[-4,0,3],[5,8,12],[-2,2,5]], "feel": "i-VI-iv-VII, trailers and big claims"},
    "dark_tension":   {"bpm": 94,  "chords": [[0,3,7],[1,5,8],[0,3,7],[-2,2,5]], "feel": "i-bII-i-VII, warnings, mistakes, noir"},
    "mysterious":     {"bpm": 86,  "chords": [[0,3,7],[3,7,10],[-2,2,5],[5,8,12]], "feel": "i-III-VII-iv, secrets and reveals"},
    "sunny_acoustic": {"bpm": 102, "chords": [[0,4,7],[7,11,14],[5,9,12],[0,4,7]], "feel": "I-V-IV-I, travel and food"},
    "motivational":   {"bpm": 108, "chords": [[-3,0,4],[7,11,14],[5,9,12],[0,4,7]], "feel": "vi-V-IV-I, fitness and growth"},
    "news_neutral":   {"bpm": 92,  "chords": [[0,4,7],[-3,0,4],[0,4,7],[5,9,12]], "feel": "I-vi-I-IV, reports and summaries"}
  },
  "drums": {
    "none":       {"kick": "................", "hat": "................", "clap": "................"},
    "soft_pulse": {"kick": "x.......x.......", "hat": "................", "clap": "................"},
    "four_floor": {"kick": "x...x...x...x...", "hat": "..x...x...x...x.", "clap": "....x.......x..."},
    "half_time":  {"kick": "x...............", "hat": "x.x.x.x.x.x.x.x.", "clap": "........x......."},
    "lofi":       {"kick": "x.....x...x.....", "hat": "..x...x...x...xx", "clap": "....x.......x..."},
    "trap":       {"kick": "x......x..x.....", "hat": "xxxxxxxxxxxxxxxx", "clap": "........x......."},
    "driving":    {"kick": "x.x.x.x.x.x.x.x.", "hat": ".x.x.x.x.x.x.x.x", "clap": "....x.......x..."},
    "broken":     {"kick": "x..x....x.x.....", "hat": "x.xx.x.xx.x.x.xx", "clap": "....x..x....x..."}
  },
  "timbres": {
    "sine":  "pure soft pad, never fights the voice",
    "warm":  "sine plus 2nd and 3rd harmonics, rounder",
    "organ": "drawbar-like 1st, 2nd and 4th harmonics",
    "pluck": "each beat re-attacks and decays, rhythmic"
  },
  "energy": {"low": 0.85, "mid": 1.0, "high": 1.15},
  "genre_match": {
    "hackathon_demo":      {"moods": ["tech_pulse", "confident", "uplifting", "motivational"], "drums": ["driving", "four_floor", "broken"], "timbres": ["pluck", "warm"], "energy": ["mid", "high"]},
    "tutorial_docs":       {"moods": ["calm_ambient", "chill_lofi", "corporate_clean"], "drums": ["none", "soft_pulse", "lofi"], "timbres": ["sine", "warm"], "energy": ["low"]},
    "product_launch":      {"moods": ["bright_pop", "uplifting", "sunny_acoustic", "playful"], "drums": ["four_floor", "driving", "half_time"], "timbres": ["pluck", "warm", "organ"], "energy": ["mid", "high"]},
    "education_explainer": {"moods": ["corporate_clean", "hopeful", "news_neutral", "mysterious"], "drums": ["soft_pulse", "lofi", "half_time"], "timbres": ["warm", "sine", "pluck"], "energy": ["low", "mid"]},
    "story_vlog":          {"moods": ["emotional", "hopeful", "chill_lofi", "sunny_acoustic"], "drums": ["none", "soft_pulse", "lofi"], "timbres": ["warm", "sine", "pluck"], "energy": ["low", "mid"]},
    "sales_pitch":         {"moods": ["confident", "motivational", "dark_tension", "cinematic_epic"], "drums": ["trap", "driving", "half_time"], "timbres": ["pluck", "organ", "warm"], "energy": ["mid", "high"]},
    "podcast_talk":        {"moods": ["calm_ambient", "chill_lofi", "news_neutral"], "drums": ["none", "soft_pulse"], "timbres": ["sine", "warm"], "energy": ["low"]},
    "ai_comparison":       {"moods": ["tech_pulse", "mysterious", "confident", "playful"], "drums": ["broken", "driving", "trap", "half_time"], "timbres": ["pluck", "warm"], "energy": ["mid", "high"]}
  },
  "style_default": {"studio": "bright_pop", "cinema": "cinematic_epic", "neon": "tech_pulse", "editorial": "calm_ambient", "noir": "dark_tension", "glass": "chill_lofi"}
}
```

## presets/content.json

```json
{
 "note": "Script library for the script command. frameworks: 100 content structures. hooks: 200 named opening techniques; risky ones manipulate emotion and may only be used with a true claim. genre_scripts: which frameworks, hooks and beat order suit each genre.",
 "frameworks": [
  {
   "category": "conversion",
   "name": "AIDA",
   "steps": [
    "Attention",
    "Interest",
    "Desire",
    "Action"
   ]
  },
  {
   "category": "conversion",
   "name": "PAS",
   "steps": [
    "Problem",
    "Agitate",
    "Solution"
   ]
  },
  {
   "category": "conversion",
   "name": "BAB",
   "steps": [
    "Before",
    "After",
    "Bridge"
   ]
  },
  {
   "category": "conversion",
   "name": "FAB",
   "steps": [
    "Features",
    "Advantages",
    "Benefits"
   ]
  },
  {
   "category": "conversion",
   "name": "4P",
   "steps": [
    "Promise",
    "Picture",
    "Proof",
    "Push"
   ]
  },
  {
   "category": "conversion",
   "name": "4C",
   "steps": [
    "Clear",
    "Concise",
    "Compelling",
    "Credible"
   ]
  },
  {
   "category": "conversion",
   "name": "4U",
   "steps": [
    "Useful",
    "Urgent",
    "Unique",
    "Ultra-specific"
   ]
  },
  {
   "category": "conversion",
   "name": "ACCA",
   "steps": [
    "Awareness",
    "Comprehension",
    "Conviction",
    "Action"
   ]
  },
  {
   "category": "conversion",
   "name": "AIDA-C",
   "steps": [
    "Attention",
    "Interest",
    "Desire",
    "Action",
    "Conviction"
   ]
  },
  {
   "category": "conversion",
   "name": "PASTOR",
   "steps": [
    "Problem",
    "Amplify",
    "Story",
    "Transformation",
    "Offer",
    "Response"
   ]
  },
  {
   "category": "conversion",
   "name": "QUEST",
   "steps": [
    "Qualify",
    "Understand",
    "Educate",
    "Stimulate",
    "Transition"
   ]
  },
  {
   "category": "conversion",
   "name": "SLAP",
   "steps": [
    "Stop",
    "Look",
    "Act",
    "Purchase"
   ]
  },
  {
   "category": "conversion",
   "name": "AIDCA",
   "steps": [
    "Attention",
    "Interest",
    "Desire",
    "Conviction",
    "Action"
   ]
  },
  {
   "category": "conversion",
   "name": "AICPB",
   "steps": [
    "Attention",
    "Interest",
    "Concern",
    "Proof",
    "Benefit"
   ]
  },
  {
   "category": "conversion",
   "name": "PASPP",
   "steps": [
    "Problem",
    "Agitate",
    "Solution",
    "Proof",
    "Pitch"
   ]
  },
  {
   "category": "story",
   "name": "Hero's Journey",
   "steps": [
    "Status quo",
    "Call to adventure",
    "Conflict",
    "Transformation",
    "Return"
   ]
  },
  {
   "category": "story",
   "name": "Pixar Pitch",
   "steps": [
    "Once upon a time",
    "Every day",
    "One day",
    "Because of that",
    "Until finally"
   ]
  },
  {
   "category": "story",
   "name": "Sparkline",
   "steps": [
    "What is",
    "What could be",
    "Contrast",
    "Call to action"
   ]
  },
  {
   "category": "story",
   "name": "Freytag Pyramid",
   "steps": [
    "Exposition",
    "Inciting incident",
    "Rising action",
    "Climax",
    "Resolution"
   ]
  },
  {
   "category": "story",
   "name": "Star-Chain-Hook",
   "steps": [
    "Star hook",
    "Chain of facts",
    "Hook CTA"
   ]
  },
  {
   "category": "story",
   "name": "Three-Act",
   "steps": [
    "Setup",
    "Confrontation",
    "Resolution"
   ]
  },
  {
   "category": "story",
   "name": "Hook-Story-Offer",
   "steps": [
    "Emotional hook",
    "Personal story",
    "Offer"
   ]
  },
  {
   "category": "story",
   "name": "PASS",
   "steps": [
    "Problem",
    "Agitate",
    "Story",
    "Solution"
   ]
  },
  {
   "category": "story",
   "name": "SOAR",
   "steps": [
    "Situation",
    "Obstacle",
    "Action",
    "Result"
   ]
  },
  {
   "category": "story",
   "name": "Mystery Box",
   "steps": [
    "Teasing question",
    "Deepen the problem",
    "Unexpected resolution"
   ]
  },
  {
   "category": "story",
   "name": "Underdog Arc",
   "steps": [
    "Humble start",
    "Big obstacle",
    "Failure",
    "Win"
   ]
  },
  {
   "category": "story",
   "name": "Vulnerability-First",
   "steps": [
    "Honest confession",
    "Background",
    "Lesson",
    "Solution"
   ]
  },
  {
   "category": "story",
   "name": "Inverted Pyramid",
   "steps": [
    "Climax first",
    "Supporting context",
    "Conclusion"
   ]
  },
  {
   "category": "story",
   "name": "Before-Epiphany-After",
   "steps": [
    "Old problem",
    "Sudden realization",
    "New result"
   ]
  },
  {
   "category": "story",
   "name": "Parallel Lives",
   "steps": [
    "Two choices",
    "Consequences",
    "Direction"
   ]
  },
  {
   "category": "short",
   "name": "HVC",
   "steps": [
    "3-second hook",
    "Value drop",
    "Immediate CTA"
   ]
  },
  {
   "category": "short",
   "name": "Pattern Disrupt-Context-Payoff",
   "steps": [
    "Surprising visual",
    "Short context",
    "Payoff"
   ]
  },
  {
   "category": "short",
   "name": "Contrarian-Proof-Twist",
   "steps": [
    "Controversial claim",
    "Proof",
    "Twist ending"
   ]
  },
  {
   "category": "short",
   "name": "GRWM Storytime",
   "steps": [
    "Visual activity",
    "Story narration",
    "Main message"
   ]
  },
  {
   "category": "short",
   "name": "POV Scenario",
   "steps": [
    "Relatable situation",
    "Realistic reaction",
    "Punchline"
   ]
  },
  {
   "category": "short",
   "name": "Stop and Show",
   "steps": [
    "Physical demo first",
    "Short steps",
    "Final result"
   ]
  },
  {
   "category": "short",
   "name": "Open Loop-Fulfillment",
   "steps": [
    "Hanging question",
    "Visual teaser",
    "Answer at the end"
   ]
  },
  {
   "category": "short",
   "name": "B-Roll Text Hook",
   "steps": [
    "Aesthetic visual",
    "On-screen claim",
    "Detailed voiceover"
   ]
  },
  {
   "category": "short",
   "name": "Mistake-Fix",
   "steps": [
    "Stop doing X",
    "Why it fails",
    "Do Y"
   ]
  },
  {
   "category": "short",
   "name": "Tension-Resolution Loop",
   "steps": [
    "Awkward question",
    "Escalate tension",
    "Satisfying answer"
   ]
  },
  {
   "category": "short",
   "name": "Myth vs Fact",
   "steps": [
    "Common belief",
    "Myth broken",
    "Actual fact"
   ]
  },
  {
   "category": "short",
   "name": "Secret Unlocked",
   "steps": [
    "Rarely covered topic",
    "Secret steps",
    "Save this video"
   ]
  },
  {
   "category": "short",
   "name": "3-Second Visual Shock",
   "steps": [
    "Unusual action",
    "Logical explanation",
    "Practical advice"
   ]
  },
  {
   "category": "short",
   "name": "Before/After Transition",
   "steps": [
    "Bad state",
    "Fast transition",
    "Perfect result"
   ]
  },
  {
   "category": "short",
   "name": "Endless Loop",
   "steps": [
    "Hook",
    "Fast body",
    "Ending that flows into second one"
   ]
  },
  {
   "category": "education",
   "name": "What-Why-How",
   "steps": [
    "Definition",
    "Why it matters",
    "How to do it"
   ]
  },
  {
   "category": "education",
   "name": "ELUM",
   "steps": [
    "Entertain",
    "Learn",
    "Understand",
    "Master"
   ]
  },
  {
   "category": "education",
   "name": "Teardown",
   "steps": [
    "Success case",
    "Mechanism",
    "Key lesson"
   ]
  },
  {
   "category": "education",
   "name": "PAE",
   "steps": [
    "Problem statement",
    "Root cause",
    "Action steps"
   ]
  },
  {
   "category": "education",
   "name": "Rule of 3",
   "steps": [
    "Hook",
    "Three pillars",
    "Short conclusion"
   ]
  },
  {
   "category": "education",
   "name": "FAA",
   "steps": [
    "Complex framework",
    "Simple analogy",
    "Everyday use"
   ]
  },
  {
   "category": "education",
   "name": "Jargon-Buster",
   "steps": [
    "Technical term",
    "Very simple explanation",
    "Real example"
   ]
  },
  {
   "category": "education",
   "name": "CSR",
   "steps": [
    "Context",
    "Solution",
    "Result data"
   ]
  },
  {
   "category": "education",
   "name": "STAR",
   "steps": [
    "Situation",
    "Task",
    "Action",
    "Result"
   ]
  },
  {
   "category": "education",
   "name": "5W1H",
   "steps": [
    "What",
    "Why",
    "Who",
    "Where",
    "When",
    "How"
   ]
  },
  {
   "category": "education",
   "name": "Checklist",
   "steps": [
    "Show the gap",
    "Full checklist",
    "Summary"
   ]
  },
  {
   "category": "education",
   "name": "Comparison Breakdown",
   "steps": [
    "X vs Y",
    "Pros and cons",
    "Final pick"
   ]
  },
  {
   "category": "education",
   "name": "Resource Stack",
   "steps": [
    "Best tools",
    "Specific use",
    "Top pick"
   ]
  },
  {
   "category": "education",
   "name": "Case Study",
   "steps": [
    "Starting challenge",
    "Execution",
    "Measured result"
   ]
  },
  {
   "category": "education",
   "name": "Trend-Insight-Prediction",
   "steps": [
    "Current trend",
    "Hidden data",
    "Prediction"
   ]
  },
  {
   "category": "psychology",
   "name": "FOMO",
   "steps": [
    "Scarcity",
    "Cost of missing out",
    "Instant action"
   ]
  },
  {
   "category": "psychology",
   "name": "Social Proof Stack",
   "steps": [
    "Bold claim",
    "Real testimony",
    "Statistic",
    "Join"
   ]
  },
  {
   "category": "psychology",
   "name": "Us vs Them",
   "steps": [
    "Common enemy",
    "Different position",
    "Unite the audience"
   ]
  },
  {
   "category": "psychology",
   "name": "Unpopular Opinion",
   "steps": [
    "Against the grain",
    "Logical argument",
    "Invite debate"
   ]
  },
  {
   "category": "psychology",
   "name": "Identity Shift",
   "steps": [
    "Name profile X",
    "Challenge old mindset",
    "Become Y"
   ]
  },
  {
   "category": "psychology",
   "name": "Confession-Transformation",
   "steps": [
    "Past regret",
    "Lesson",
    "Change guide"
   ]
  },
  {
   "category": "psychology",
   "name": "Curiosity Gap",
   "steps": [
    "Puzzle",
    "Build curiosity",
    "Answer"
   ]
  },
  {
   "category": "psychology",
   "name": "Expectation vs Reality",
   "steps": [
    "Common expectation",
    "Reality",
    "Tactic"
   ]
  },
  {
   "category": "psychology",
   "name": "Friction Reduction",
   "steps": [
    "Heavy task",
    "One-minute trick",
    "Quick win"
   ]
  },
  {
   "category": "psychology",
   "name": "Fear-Relief-Reward",
   "steps": [
    "Hidden risk",
    "Protection",
    "Quick reward"
   ]
  },
  {
   "category": "psychology",
   "name": "Status Elevator",
   "steps": [
    "Credibility-killing mistake",
    "High-value alternative",
    "Level-up step"
   ]
  },
  {
   "category": "psychology",
   "name": "Shocking Stat-Insight",
   "steps": [
    "Shocking number",
    "Reason behind it",
    "How to use it"
   ]
  },
  {
   "category": "psychology",
   "name": "Rejection to Triumph",
   "steps": [
    "Early doubt",
    "Proof steps",
    "Evidence of success"
   ]
  },
  {
   "category": "psychology",
   "name": "Paradox Breakdown",
   "steps": [
    "Contradiction",
    "Underlying logic",
    "Smart use"
   ]
  },
  {
   "category": "psychology",
   "name": "Trojan Horse",
   "steps": [
    "Humor or meme",
    "Smooth transition",
    "High-value lesson"
   ]
  },
  {
   "category": "community",
   "name": "Crowdsourced Question",
   "steps": [
    "Audience dilemma",
    "Best options",
    "Discuss in comments"
   ]
  },
  {
   "category": "community",
   "name": "A/B Poll",
   "steps": [
    "Option A vs B",
    "Quick comparison",
    "Vote"
   ]
  },
  {
   "category": "community",
   "name": "Challenge-Progress-Result",
   "steps": [
    "Recurring challenge",
    "Obstacles",
    "Transformation"
   ]
  },
  {
   "category": "community",
   "name": "Audit",
   "steps": [
    "Open review of audience work",
    "Concrete fixes"
   ]
  },
  {
   "category": "community",
   "name": "Build in Public",
   "steps": [
    "Project goal",
    "Honest update",
    "Lessons and results"
   ]
  },
  {
   "category": "community",
   "name": "Q&A Escalation",
   "steps": [
    "Simple question",
    "Deeper follow-up",
    "Complete answer"
   ]
  },
  {
   "category": "community",
   "name": "Tier List",
   "steps": [
    "S to F ranking",
    "Live evaluation",
    "Debate"
   ]
  },
  {
   "category": "community",
   "name": "Stitch/Duet Response",
   "steps": [
    "Popular clip",
    "Different take",
    "Evidence"
   ]
  },
  {
   "category": "community",
   "name": "Interactive Quiz",
   "steps": [
    "Case question",
    "Answer choices",
    "Explanation"
   ]
  },
  {
   "category": "community",
   "name": "Resource Swap",
   "steps": [
    "Comment keyword",
    "Auto delivery",
    "Engagement lift"
   ]
  },
  {
   "category": "ai",
   "name": "Prompt-to-Result",
   "steps": [
    "Prompt",
    "Raw AI output",
    "Human polish"
   ]
  },
  {
   "category": "ai",
   "name": "Hyper-Personalized Segment",
   "steps": [
    "Call out a profession",
    "Specific solution"
   ]
  },
  {
   "category": "ai",
   "name": "Spatial Visual Demo",
   "steps": [
    "3D or interactive view",
    "Main feature",
    "Direct access"
   ]
  },
  {
   "category": "ai",
   "name": "Deepfake vs Real",
   "steps": [
    "Visual test",
    "Technical tell",
    "Trust signal"
   ]
  },
  {
   "category": "ai",
   "name": "Data Narrative",
   "steps": [
    "Modern chart",
    "Simplified story",
    "Key conclusion"
   ]
  },
  {
   "category": "ai",
   "name": "Micro-SaaS Teardown",
   "steps": [
    "Tool architecture",
    "Revenue numbers",
    "Growth blueprint"
   ]
  },
  {
   "category": "ai",
   "name": "Automation Workflow",
   "steps": [
    "Trigger",
    "Automated flow",
    "Time saved"
   ]
  },
  {
   "category": "ai",
   "name": "Synthetic Persona Dialogue",
   "steps": [
    "Two opposing views",
    "Summary",
    "Synthesis"
   ]
  },
  {
   "category": "ai",
   "name": "Future-Proofing",
   "steps": [
    "Industry shift",
    "Relevant vs obsolete skills",
    "Action plan"
   ]
  },
  {
   "category": "ai",
   "name": "Zero-Click Value",
   "steps": [
    "Full value in the post",
    "No friction",
    "Follow"
   ]
  },
  {
   "category": "ai",
   "name": "Curation-Filter-Action",
   "steps": [
    "Information overload",
    "Top 1% filter",
    "Execution guide"
   ]
  },
  {
   "category": "ai",
   "name": "One-Prompt Solution",
   "steps": [
    "Pain point",
    "One prompt",
    "Result preview"
   ]
  },
  {
   "category": "ai",
   "name": "Algorithmic Insight",
   "steps": [
    "How the algorithm works now",
    "Strategy change",
    "Apply it"
   ]
  },
  {
   "category": "ai",
   "name": "Interactive Simulator",
   "steps": [
    "Input numbers",
    "Live projection",
    "Free trial"
   ]
  },
  {
   "category": "ai",
   "name": "Evergreen Engine",
   "steps": [
    "Timeless principle",
    "Modern tool",
    "Long-term guide"
   ]
  }
 ],
 "hooks": [
  {
   "category": "emotion",
   "name": "Rage Bait",
   "risky": true,
   "template": "{strong_claim}. Fight me in the comments."
  },
  {
   "category": "emotion",
   "name": "FOMO Trigger",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Shock Value",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Controversy Framing",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Curiosity Gap",
   "risky": false,
   "template": "Nobody tells you this about {topic}."
  },
  {
   "category": "emotion",
   "name": "Ego Trigger",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Nostalgia Bait",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Empathy Trap",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Guilt Hook",
   "risky": true,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Schadenfreude",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Insecurity Trigger",
   "risky": true,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Validation Seeking",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Outrage",
   "risky": true,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Paranoia Bait",
   "risky": true,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Secret Society Appeal",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Status Anxiety",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Revenge Narrative",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Identity Affirmation",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Misery Loves Company",
   "risky": false,
   "template": null
  },
  {
   "category": "emotion",
   "name": "Perceived Scarcity",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Pattern Interrupt",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Open Loop",
   "risky": false,
   "template": "By the end of this you'll know {payoff}. But first, {setup}."
  },
  {
   "category": "curiosity",
   "name": "Information Asymmetry",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Paradox",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Contrarian Statement",
   "risky": false,
   "template": "{common_belief} is wrong. Here's why."
  },
  {
   "category": "curiosity",
   "name": "Counter-Intuitive Claim",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Cliffhanger",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Myth-Busting",
   "risky": false,
   "template": "{myth}? That's a myth."
  },
  {
   "category": "curiosity",
   "name": "Trojan Horse",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "What-If",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Cognitive Dissonance",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Expectation Violation",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Secret Unlocking",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Unexpected Twist",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "The Glitch",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Mystery Box",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "The Loophole",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Zero-Context",
   "risky": false,
   "template": null
  },
  {
   "category": "curiosity",
   "name": "Unpopular Opinion",
   "risky": false,
   "template": "Unpopular opinion: {opinion}."
  },
  {
   "category": "curiosity",
   "name": "Confession",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Shortcut",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Negative Framing",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Mistake Highlight",
   "risky": false,
   "template": "The mistake that cost me {cost}."
  },
  {
   "category": "value",
   "name": "Stop Doing X",
   "risky": false,
   "template": "Stop {mistake} if you want {result}."
  },
  {
   "category": "value",
   "name": "Cheap vs Expensive",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Resource Stack",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Cheat Code",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Time-Saving Claim",
   "risky": false,
   "template": "This saves me {time} every {period}."
  },
  {
   "category": "value",
   "name": "Friction Reduction",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Authority Drop",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Teardown",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Instant Gratification",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Hack/Exploit",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Free Resource",
   "risky": false,
   "template": "Free {resource} that feels illegal to know about."
  },
  {
   "category": "value",
   "name": "Cost of Ignorance",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "The Audit",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Zero to Hero",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "The Blueprint",
   "risky": false,
   "template": null
  },
  {
   "category": "value",
   "name": "Risk Avoidance",
   "risky": false,
   "template": "Don't {action} until you check this."
  },
  {
   "category": "value",
   "name": "Efficiency Upgrade",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Text-over-Video",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Green Screen Reaction",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Micro-Movement Cut",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Visual Shock Drop",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "SFX Jump",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Whisper/ASMR",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Physical Demo First",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Extreme Close-up",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Reverse Progression",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "B-Roll Disconnect",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Fast Collage",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Prop Opening",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "On-Screen Countdown",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Mid-Action Start",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Silent Subtitles-Only",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Eye-Contact Stare",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Screen Recording Reveal",
   "risky": false,
   "template": "Watch this: {demo_action}."
  },
  {
   "category": "visual_audio",
   "name": "Motion Blur Transition",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Split-Screen Comparison",
   "risky": false,
   "template": null
  },
  {
   "category": "visual_audio",
   "name": "Text Deletion Animation",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Us vs Them",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Insider Knowledge",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Tribe Callout",
   "risky": false,
   "template": "If you're a {audience}, watch this before {deadline}."
  },
  {
   "category": "social",
   "name": "POV Relatable",
   "risky": false,
   "template": "POV: you {relatable_moment}."
  },
  {
   "category": "social",
   "name": "Calling Out Bad Advice",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Underdog",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Social Proof Stack",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Peer Pressure",
   "risky": true,
   "template": null
  },
  {
   "category": "social",
   "name": "Common Enemy",
   "risky": true,
   "template": null
  },
  {
   "category": "social",
   "name": "Taboo Subject",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Gatekeeping Callout",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Loyalty Test",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Industry Insider Confession",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Generational Divide",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Meme Hijack",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Community Challenge",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Tea Spilling",
   "risky": true,
   "template": null
  },
  {
   "category": "social",
   "name": "Vulnerability Opener",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Unfiltered Truth",
   "risky": false,
   "template": null
  },
  {
   "category": "social",
   "name": "Direct Call-Out",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "GRWM Storytime",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Day in the Life",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Inverted Pyramid",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Mid-Story Climax",
   "risky": false,
   "template": "{climax_moment}. Let me back up."
  },
  {
   "category": "story_format",
   "name": "Dramatic Monologue",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Simulated Conversation",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Mock Interview",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Voiceover Overlay",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Before/After Reveal",
   "risky": false,
   "template": "Before: {before}. After: {after}."
  },
  {
   "category": "story_format",
   "name": "Timeline Jump",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Result First",
   "risky": false,
   "template": "This is {result}. Here's how {subject} got there."
  },
  {
   "category": "story_format",
   "name": "Fail-to-Win Start",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Third-Person Narration",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Real-Time Reaction",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Unboxing Teaser",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Behind the Scenes",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Interrogation Format",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "News Anchor",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Documentary Style",
   "risky": false,
   "template": null
  },
  {
   "category": "story_format",
   "name": "Cinematic Cold Open",
   "risky": false,
   "template": "{sensory_line}."
  },
  {
   "category": "interactive",
   "name": "Poll",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Direct Question",
   "risky": false,
   "template": "Why does {problem} keep happening to you?"
  },
  {
   "category": "interactive",
   "name": "Quiz/Test",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "A/B Test",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Comment Trigger",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Stitch/Duet Setup",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Tier List Teaser",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Guess the Result",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Challenge Accepted",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Spot the Difference",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Fill in the Blank",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Crowdsourced Dilemma",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Dare/Bet",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Screenshot This",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Double-Tap Trick",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Tag a Friend",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Secret Code",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Live Demo Ask",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Rating Scale",
   "risky": false,
   "template": null
  },
  {
   "category": "interactive",
   "name": "Debate Trigger",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "AI vs Human",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Stat Bomb",
   "risky": false,
   "template": "{stat}. And almost nobody talks about it."
  },
  {
   "category": "data_ai",
   "name": "Algorithm Exposure",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Prompt Reveal",
   "risky": false,
   "template": "One prompt turned {input} into {output}."
  },
  {
   "category": "data_ai",
   "name": "Automation Showdown",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Future Prediction",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Data Leak Framing",
   "risky": true,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Tool Stack Reveal",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Workflow Shortcut",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Synthetic Reveal",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Benchmark Comparison",
   "risky": false,
   "template": "I gave {a} and {b} the same task. One of them failed."
  },
  {
   "category": "data_ai",
   "name": "Code Teardown",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Tech Replacement Threat",
   "risky": true,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Zero-Click Value",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Automated Result Showcase",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Industry Obsolescence",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "AI Tool War",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Hyper-Personalization",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Privacy Warning",
   "risky": false,
   "template": null
  },
  {
   "category": "data_ai",
   "name": "Old Tech vs New",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Urgency Trigger",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Price Shock",
   "risky": true,
   "template": null
  },
  {
   "category": "sales",
   "name": "Guarantee First",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Offer Stack",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Freebie Bait",
   "risky": true,
   "template": null
  },
  {
   "category": "sales",
   "name": "Risk-Free Pitch",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "VIP Exclusive",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Price vs Value",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Direct Problem Pitch",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Limited Edition",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Comparison Matrix",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "ROI First",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Hard Truth Sell",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Discontinuation Warning",
   "risky": true,
   "template": null
  },
  {
   "category": "sales",
   "name": "Case Study Teaser",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Transformation Pitch",
   "risky": false,
   "template": "From {before} to {after} in {time}."
  },
  {
   "category": "sales",
   "name": "Unfair Advantage",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Competitor Flaw",
   "risky": true,
   "template": null
  },
  {
   "category": "sales",
   "name": "Pain-Point Amplification",
   "risky": false,
   "template": null
  },
  {
   "category": "sales",
   "name": "Guarantee Challenge",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Meta-Hook",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Anti-Hook",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Fake-Out",
   "risky": true,
   "template": null
  },
  {
   "category": "meta",
   "name": "Overly Honest",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Whispered Secret",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Chaotic Energy",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Awkward Silence",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Breaking Character",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Glitch in the Matrix",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Subverted Expectation",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Infinite Loop",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Multimodal Teaser",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Hyper-Specific Persona",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Raw Footage Drop",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Self-Deprecating",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Absurdist",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Context Collapse",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Accidental Reveal",
   "risky": true,
   "template": null
  },
  {
   "category": "meta",
   "name": "Fast-Forward Teaser",
   "risky": false,
   "template": null
  },
  {
   "category": "meta",
   "name": "Silence-to-Noise Spike",
   "risky": false,
   "template": null
  }
 ],
 "genre_scripts": {
  "hackathon_demo": {
   "frameworks": [
    "PAS",
    "STAR",
    "CSR",
    "Stop and Show",
    "Build in Public",
    "Rule of 3"
   ],
   "hooks": [
    "Result First",
    "Screen Recording Reveal",
    "Stat Bomb",
    "Direct Question",
    "Before/After Reveal"
   ],
   "beats": [
    "hook",
    "problem",
    "why_now",
    "solution_demo",
    "proof",
    "how_it_works",
    "impact",
    "closing",
    "cta"
   ]
  },
  "tutorial_docs": {
   "frameworks": [
    "What-Why-How",
    "Checklist",
    "PAE",
    "Jargon-Buster",
    "Friction Reduction"
   ],
   "hooks": [
    "Time-Saving Claim",
    "Stop Doing X",
    "Screen Recording Reveal",
    "Mistake Highlight",
    "Free Resource"
   ],
   "beats": [
    "hook",
    "outcome_preview",
    "requirements",
    "step_1",
    "step_2",
    "step_3",
    "common_mistake",
    "recap",
    "cta"
   ]
  },
  "product_launch": {
   "frameworks": [
    "AIDA",
    "BAB",
    "FAB",
    "4P",
    "PASTOR"
   ],
   "hooks": [
    "Before/After Reveal",
    "Transformation Pitch",
    "Tribe Callout",
    "Result First",
    "Curiosity Gap"
   ],
   "beats": [
    "hook",
    "relatable_pain",
    "tension",
    "reveal",
    "benefits",
    "proof",
    "offer",
    "closing",
    "cta"
   ]
  },
  "education_explainer": {
   "frameworks": [
    "What-Why-How",
    "Myth vs Fact",
    "Shocking Stat-Insight",
    "5W1H",
    "Curiosity Gap"
   ],
   "hooks": [
    "Curiosity Gap",
    "Myth-Busting",
    "Stat Bomb",
    "Direct Question",
    "Contrarian Statement"
   ],
   "beats": [
    "hook",
    "why_care",
    "fact_1",
    "fact_2",
    "twist",
    "takeaway",
    "closing",
    "cta"
   ]
  },
  "story_vlog": {
   "frameworks": [
    "Pixar Pitch",
    "Before-Epiphany-After",
    "Vulnerability-First",
    "Three-Act",
    "Underdog Arc"
   ],
   "hooks": [
    "Mid-Story Climax",
    "Cinematic Cold Open",
    "POV Relatable",
    "Confession",
    "Open Loop"
   ],
   "beats": [
    "hook",
    "setting",
    "relatable",
    "conflict",
    "tension",
    "turning_point",
    "lesson",
    "closing",
    "cta"
   ]
  },
  "sales_pitch": {
   "frameworks": [
    "PAS",
    "PASTOR",
    "Hook-Story-Offer",
    "Fear-Relief-Reward",
    "Social Proof Stack"
   ],
   "hooks": [
    "Mistake Highlight",
    "Stop Doing X",
    "Stat Bomb",
    "Unpopular Opinion",
    "Risk Avoidance"
   ],
   "beats": [
    "hook",
    "problem",
    "agitate",
    "story",
    "solution",
    "proof",
    "offer",
    "urgency",
    "cta"
   ]
  },
  "podcast_talk": {
   "frameworks": [
    "Inverted Pyramid",
    "Q&A Escalation",
    "Unpopular Opinion",
    "Synthetic Persona Dialogue"
   ],
   "hooks": [
    "Mid-Story Climax",
    "Unpopular Opinion",
    "Direct Question",
    "Open Loop"
   ],
   "beats": [
    "hook",
    "guest_or_context",
    "question",
    "answer",
    "surprise",
    "takeaway",
    "cta"
   ]
  },
  "ai_comparison": {
   "frameworks": [
    "Comparison Breakdown",
    "Prompt-to-Result",
    "Tension-Resolution Loop",
    "Tier List",
    "Open Loop-Fulfillment"
   ],
   "hooks": [
    "Benchmark Comparison",
    "Prompt Reveal",
    "Open Loop",
    "Result First",
    "Unpopular Opinion"
   ],
   "beats": [
    "hook",
    "rules_of_test",
    "contender_a",
    "contender_b",
    "tension",
    "verdict",
    "why",
    "cta"
   ]
  }
 },
 "beat_guide": {
  "hook": "0-3 s. One sentence. Make a claim, show a result, or ask a question the viewer needs answered. No greeting, no name.",
  "outcome_preview": "Show the finished result for 1-2 s so the viewer knows the payoff.",
  "requirements": "What the viewer needs before starting. One line.",
  "step_1": "One action per step. Say the button or command out loud.",
  "step_2": "Same.",
  "step_3": "Same.",
  "common_mistake": "The error most people hit and the fix.",
  "recap": "Three steps in one sentence.",
  "problem": "The pain, concrete: who, what breaks, what it costs.",
  "why_now": "Why this matters today (a trend, a cost, a deadline). Real, checkable.",
  "solution_demo": "Show the product working on screen. Say what the viewer is looking at.",
  "proof": "Numbers, a live link, a user quote, a benchmark. Only true ones.",
  "how_it_works": "One sentence of architecture judges can repeat.",
  "impact": "Who benefits and by how much.",
  "relatable_pain": "A moment the audience has lived ('you open the app and...').",
  "tension": "Raise the stakes: what happens if nothing changes, or which side is losing.",
  "reveal": "Name the product or answer. Land it on a beat.",
  "benefits": "Outcomes, not features. Max three.",
  "offer": "Price, access, bonus. Plain.",
  "urgency": "A real deadline or limit. Never invent scarcity.",
  "why_care": "Why this fact changes something for the viewer.",
  "fact_1": "One fact with a source.",
  "fact_2": "A second fact that builds on the first.",
  "twist": "The part that contradicts what the viewer assumed.",
  "takeaway": "What to do or remember.",
  "setting": "Where and when, in one image.",
  "relatable": "The feeling the viewer shares.",
  "conflict": "What went wrong.",
  "turning_point": "The moment things changed.",
  "lesson": "What it taught you, stated simply.",
  "agitate": "Make the cost of the problem vivid.",
  "story": "A short personal or customer story.",
  "solution": "The fix, framed as the bridge.",
  "guest_or_context": "Who is talking and why they are worth hearing.",
  "question": "The sharpest question of the episode.",
  "answer": "The best 20 seconds of the answer.",
  "surprise": "The unexpected line.",
  "rules_of_test": "Same prompt, same task, how it is scored.",
  "contender_a": "Result A, shown.",
  "contender_b": "Result B, shown.",
  "verdict": "Say who won. Always answer the hook.",
  "why": "The reason it won.",
  "closing": "One line that ties back to the hook (callback).",
  "cta": "One action only: follow, comment a keyword, try the link, or watch part two.",
  "market_size": "TAM > SAM > SOM in one breath, then why you can win the SOM first. Numbers only if sourced."
 }
}
```

