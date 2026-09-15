---
name: splicecraft
description: Edit a raw talking-head or face-to-camera video into a finished short with word-synced captions, animated info cards, punch-in zooms, a color grade, chroma key, music with ducking, and sound effects. Use when the user gives a video file and asks to "edit this video", "add subtitles/captions", "make it look professional", "add music", "make it cinematic", "remove the green screen", "turn this into a reel/short/TikTok", or wants an edit at a chosen intensity from 1 to 100. Runs locally with ffmpeg and Python; no paid editor needed.
license: MIT
---

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
