---
name: splicecraft
description: Edit a raw talking-head or face-to-camera video into a finished short with word-synced captions, animated info cards, punch-in zooms, a color grade, chroma key, music with ducking, and sound effects — and write the script and personal-branding strategy behind it. Use when the user gives a video file and asks to "edit this video", "add subtitles/captions", "make it look professional", "add music", "make it cinematic", "remove the green screen", "turn this into a reel/short/TikTok", or wants an edit at a chosen intensity from 1 to 100. Also use when the user asks for a content script, a hook, a content plan, a niche, or personal branding strategy, or complains that a script or edit "feels AI" / "masih AI-ish". Keeps a local ledger of everything already made so it never repeats a theme. Runs locally with ffmpeg and Python; no paid editor needed.
license: MIT
---

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
| **Premis** — one paragraph turning a weakness into a message | `references/academy-personal-branding.md` §2.4 |
| **Superniche** — named as a *who*, not a topic | §6.2. *"Niche bukan topik, tapi siapa secara spesifik."* |
| **4K** — Keresahan / Kebutuhan / Keinginan / Kebiasaan of that person | §6.6 |
| **Pillar** — Educate / Inspiration / Entertaining / Promotion | §8.2 |

| **Source of the idea** — a question someone asked, a repeated complaint, a misconception, something the user saw | `references/academy-live-mentoring.md` §2.3. An idea with no source is an invented idea. |
| **Format** — one of the 15 named formats; if there is no winner yet, test several | `academy-live-mentoring.md` §1, §5.3 |
| **Funnel stage** — TOFU (tahu) / MOFU (mau) / BOFU (beli) | §5.1. A small account starts at TOFU. |

If the user cannot answer these, walk them through the frameworks. Do not guess on their behalf.

**0.5c — Brief.** Write `brief.json` with the user: platform, market, age, stage, funnel, niche, and if relevant TAM/SAM/SOM, price, revenue target. Field list and effects: `references/audience-and-market.md`. Run `$SC brief brief.json` and show the checks and revenue math. Never present the placeholder conversion rates as facts.

**0.5d — Write.** Generate the skeleton: `$SC script "<topic>" --genre <genre> --seconds <n> --brief brief.json --language <en|id> -o script.md`. Then fill it using:

- **Hook** — one of the 20 templates, brackets filled from the real 4K answers: `references/academy-script-formulas.md` §4
- **Elements** — all 6 Script Hack Elements present: §2
- **Beats** — 5-beat Storytelling Hack, where beat ⑤ reverses beat ①: §3
- **Length** — pick 20-30 s *or* 60-90 s deliberately, not 50 s by accident: §8
- **Selling?** Use Problem → Agitation → Solution with **one** benefit per video; agitation may not be skipped: `references/academy-live-mentoring.md` §2
- **Opinion or education?** Write the thesis in one sentence and its 3-4 sourced arguments before any hook: `academy-live-mentoring.md` §4.3

Fill the "Your line" column *with* the user. Use only facts the user confirms.

**0.5e — Gate.** Run the full checklist in `references/anti-ai-ish.md` §E before handing anything over.

**0.5f — Log it.**

```bash
$LEDGER add "<topic>" --niche "<superniche>" --pillar <pillar> \
  --hook-template <1-20> --angle "<what made THIS one different>" \
  --format <format> --funnel <tofu|mofu|bofu> --source "<where the idea came from>" \n  --theme <tag> --theme <tag> --status scripted --script-path script.md
```

**0.5g — Plan the next 30 days (daily content planner).** Once the premis, niche and 4K keresahan are known, build the calendar instead of writing one-offs:

```bash
$LEDGER plan --days 30 --per-week 5 --niche "<superniche>" --goal "<the transformation>"   --problem "<keresahan 1>; <keresahan 2>; <keresahan 3>" --platform tiktok --followers <n>   [--winner-format <format that already won>] [--start YYYY-MM-DD] [--dry-run]
$LEDGER today                 # what to post today, and anything overdue
$LEDGER done <id> --metric views=1200 --metric saves=40
$LEDGER reflect --answer 1="..." --answer 3="..."   # Refleksi Mingguan, 6 questions
$LEDGER export-plan --out plan.csv                  # the 30-day tracker layout, opens in Excel/Sheets
```

What `plan` decides: pillar rotation (educate-heavy, one promotion a week), the 80/15/5 superniche / adjacent / personal mix, funnel stage (accounts under 1,000 followers get mostly TOFU), format (untried formats first; with `--winner-format`, ~80% winner + 20% testing), and an angle from the Content Idea Framework per problem. Every day is checked against what was already **made** and saved as `status=planned`, so later checks know those themes are taken. The topics are **seeds**: before scripting one, still get the real story, number and opinion from the user.

**Auto-logging.** `splicecraft.py script`, `render` and `auto` write to the ledger by themselves (reusing the planned entry when the topic matches). The agent no longer has to remember. Set `SPLICECRAFT_NO_LOG=1` to turn it off for a test run. Still run `$LEDGER add` with the full fields (pillar, hook template, themes) when you have them: the auto entry only knows the topic, status and file path.

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

The held final shot is where the closing line lands — the one that reverses the opening (`references/academy-script-formulas.md` §3). Do not trim it off as dead air; it is the beat that makes the video loop. Full numbers, method and limits: `references/viral-edit-teardown.md`.

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

**Strategy, script, and the anti-AI-ish gate** (the SpliceCraft Academy body of work, Indonesian market):

- The full personal branding theory — Ikigai, Johari, SWOT → **Premis** → Personal Market Fit, Perception vs Persona, Circle of Control, Golden Circle, Opportunity Mapping, the **superniche ladder**, **80/15/5**, Perfect Niche, the **4K Method**, Sweet Spot, First Impression, the four **Brand Pillars**, Hirarki Konten, self-documentation, survival, evaluation, monetisation, PING, LinkedIn: `references/academy-personal-branding.md`
- Writing the script — the **20 hooks**, the **6 Script Hack Elements**, the **5-beat Storytelling Hack**, Hook/Body/CTA, the Content Idea Framework, length budgets: `references/academy-script-formulas.md`
- **The rejection list and the delivery gate** — what "AI-ish" actually means, rule by rule, with the evidence behind each: `references/anti-ai-ish.md`
- What 82 reference videos measurably do — cut rates, the bimodal finding, opening and closing shape, method and limits: `references/viral-edit-teardown.md`
- What the live mentoring recordings add — the **16 formats**, **PAS** selling scripts, the **Storytelling Arc**, attention economy and the six emotions, thesis + arguments, outer/inner circle, **TOFU/MOFU/BOFU**, test → win → replicate, **Trial Reels** and **Link Reels**, and a table of real account diagnoses: `references/academy-live-mentoring.md`
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
