# Genres, auto style, and variants

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

The same editing model runs for every look. What changes per video is decided from the transcript.

## Three layers

| Layer | Decides | Where |
|---|---|---|
| Edit model | cuts, beat detection, card timing, zooms, sound effects, breathing room, QA | `plan` in `scripts/splicecraft.py` (identical for every style) |
| Genre | level shift, card density, zoom strength, which beat types are dropped, default style, CTA text, music tempo | `presets/genres.json` |
| Look | colors, grade, caption size, card height, caption style | `presets/styles.json` plus the per-video variant |

The test `test_same_edit_model_for_every_style` proves layer one: for the same transcript and level, all six styles produce byte-identical `keep`, `cards`, `zooms`, `sfx`, and `words`. Only `theme` differs.

## Genre detection

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

## Using it

```bash
# detect genre, pick style from genre, vary the look per video
$SC plan work/words.json -o work/edl.json --level 60 --style auto --genre auto

# force a genre but keep your own style
$SC plan work/words.json -o work/edl.json --level 60 --style cinema --genre hackathon_demo

# pick a specific look (0-359); same number always gives the same look
$SC plan work/words.json -o work/edl.json --genre auto --style auto --variant 42
```

Without `--variant`, the variant is a hash of the transcript, so the same video always gets the same look and different videos get different ones.

`--genre none` (the default) keeps the old behavior: exact level, exact style colors.

## How many options

```bash
$SC options
```

Computed from the preset files, not typed in:

- 8 accent palettes x 3 caption sizes x 3 card heights x 5 grades = **360 variants** per genre and style
- 8 genres x 6 styles x 360 variants x 100 levels x 3 aspect ratios = **5,184,000 combinations**

Honest note: many neighboring combinations look alike (level 61 vs 62). The meaningful distinct looks are the 8 x 6 x 360 = 17,280 genre/style/variant setups.

## Adding a genre

1. Copy a block in `presets/genres.json` and rename it.
2. Add 15 or more keywords a speaker in that genre actually says, in each language you support.
3. Add two sample scripts to `tests/fixtures/genre_scripts.json`.
4. Run `python -m unittest discover tests`. The detection test must still pass for every genre.

## Proof

- `tests/test_plan.py`: `test_detects_every_genre_in_english_and_indonesian` (16 scripts, 8 genres, 2 languages), `test_same_edit_model_for_every_style`, `test_genre_changes_the_edit`, `test_variants_are_deterministic_and_distinct`.
- A per-genre rendered image matrix was attempted and failed on this machine (ffmpeg `drawtext` crashed without a fontconfig file); it is not included rather than faked.
