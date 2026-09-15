---
name: splicecraft
description: Edit a raw talking-head or face-to-camera video into a finished short with word-synced captions, animated info cards, punch-in zooms, a color grade, chroma key, music with ducking, and sound effects. Use when the user gives a video file and asks to "edit this video", "add subtitles/captions", "make it look professional", "add music", "make it cinematic", "remove the green screen", "turn this into a reel/short/TikTok", or wants an edit at a chosen intensity from 1 to 100. Runs locally with ffmpeg and Python; no paid editor needed.
license: MIT
---

> **MEGA-SKILL.md** · SKILL.md + 14 references + presets in one file.
> **Published:** 2026-09-15 · built from commit `3f5ced9` · rebuild with `python tools/build_mega.py`, never edit by hand.
> **Agent check:** compare the published date with today. If more than 6 months have passed, re-research platform algorithms, lengths, safe zones, demographics and model names on the web before relying on them, tell the user what changed, and update the source files.

## Contents

- Part 1. Main procedure (SKILL.md)
- Part 2. script-and-marketing.md
- Part 3. audience-and-market.md
- Part 4. captions.md
- Part 5. genres-and-variants.md
- Part 6. music-guide.md
- Part 7. beat-library.md
- Part 8. edit-levels.md
- Part 9. color-and-cinematic.md
- Part 10. audio.md
- Part 11. baseline-teardown.md
- Part 12. design-secrets-glass.md
- Part 13. edl-schema.md
- Part 14. agent-prompts.md
- Part 15. troubleshooting.md
- Part 16. Presets (levels, styles, genres, music)

When this file says `references/<name>.md`, that section is included below under the same name.

# Part 1. Main procedure

# splicecraft

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this skill.


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
```

---

## Step 0.5. Brief and script (when the video is not filmed yet, or the user wants strategy)

1. Write `brief.json` with the user: platform, market, age, stage, funnel, niche, and if relevant TAM/SAM/SOM, price, revenue target. Field list and effects: `references/audience-and-market.md`. Run `$SC brief brief.json` and show the checks and revenue math. Never present the placeholder conversion rates as facts.
2. Generate the script skeleton: `$SC script "<topic>" --genre <genre> --seconds <n> --brief brief.json --language <en|id> -o script.md`.
3. Fill the "Your line" column with the user. Use only facts the user confirms. Risky hooks only with a provable claim (`references/script-and-marketing.md`).
4. Give the user the script, titles, description and hashtags. Then the video gets filmed and you continue at Step 1 with `--brief brief.json` on every plan.

If the footage already exists, skip to Step 1 but still ask for the brief fields in question 1c.

## Hard rules (apply to every step)

1. **Never change voice pitch.** No chipmunk, no robot. Only `references/audio.md` 'Voice pitch and speed' can allow it, and only for its listed reasons.
2. **Never invent facts** in scripts, cards, titles or descriptions. Numbers must come from the user or a cited source.
3. **Never use music, fonts, or footage the user has no rights to.**
4. **Check dates.** If this skill's Published date is more than 6 months old, research platform facts again before advising on strategy.

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

# Part 2. script-and-marketing.md

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

# Part 3. audience-and-market.md

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

# Part 4. captions.md

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

# Part 5. genres-and-variants.md

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

# Part 6. music-guide.md

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

# Part 7. beat-library.md

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

# Part 8. edit-levels.md

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

# Part 9. color-and-cinematic.md

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

# Part 10. audio.md

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

# Part 11. baseline-teardown.md

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

# Part 12. design-secrets-glass.md

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

# Part 13. edl-schema.md

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

# Part 14. agent-prompts.md

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

# Part 15. troubleshooting.md

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

# Part 16. Presets

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

