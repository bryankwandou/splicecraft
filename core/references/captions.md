# Captions

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Captions are rendered as an Advanced SubStation Alpha (`.ass`) file and burned in with libass. The `.ass` file is saved next to the output (`edited.ass`) so it can be inspected or edited and re-burned.

## Typography rules

1. **Size:** 66 to 80 px on a 1920 px tall frame. That is 3.4% to 4.2% of height. Smaller is unreadable on a phone; larger covers the face.
2. **Weight:** heavy. Default fonts are Segoe UI Black (Windows), Helvetica Neue (macOS), DejaVu Sans (Linux). Override with `--font-bold "Montserrat ExtraBold" --fontsdir ./fonts`.
3. **Contrast:** light text, 7 px dark stroke, 3 px shadow. Readable over white walls and dark rooms alike.
4. **Length:** three words at level 41+, four at 21-40, seven at 1-20. Break early at commas and sentence ends.
5. **Position:** centered at y 1390. Clear of the face above and of the platform caption and button zone below (about the bottom 400 px and the right 140-180 px on 1080x1920, per 2026 safe-zone guides).
6. **Timing:** a caption appears on its first word's start and leaves 0.25 s after its last word, or when the next one starts.
7. **Accent:** one accent color for the spoken word and keywords. Never more than two colors in a caption.
8. **Case:** sentence case by default. All caps only in the `neon` look, where the font is set wide.

## Creative caption styles (never flat)

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

### Rules that make captions look designed

1. **One accent, one base.** Accent on keywords (6+ letters or numbers) and the spoken word. Never a rainbow.
2. **Three words per line is the default.** A line should be read in under a second.
3. **Motion under 200 ms.** Captions follow speech; a slow animation lags behind the voice.
4. **Keywords decide emphasis, not position.** The planner highlights numbers and long content words, the words people remember.
5. **Match the style to the audience.** Kinetic and bounce for Gen Z; highlight and clean_accent for Gen X and B2B. The brief does this.
6. **Stay in the safe zone.** Captions sit at y 1390, above the platform UI in the bottom ~400 px.
7. **Pair with cards, don't compete.** When a card is on screen, captions stay; the card lives in the top third.
8. **Say what the caption should show.** Spoken numbers, names and short punchy sentences give captions something to emphasize. See `references/script-and-marketing.md`.

### Known limits

- `boxed` estimates word width from the character count (0.5 x font size per character). Very wide or very narrow fonts shift the pill slightly; pass a font close to the default or check `sheet.jpg`.
- `sweep` relies on libass karaoke (`\kf`); some very old ffmpeg builds ignore it and show the fill color at once.
- Word-level styles need spaces between words. For Chinese and Japanese use `clean_accent` or `chunk`.

## Fonts on other machines

libass looks up fonts by family name. If the name is not installed, it falls back silently and the look changes. To make renders identical everywhere:

1. Put the `.ttf` or `.otf` files in a folder.
2. Pass `--fontsdir that/folder --font-bold "Exact Family Name"`.
3. Find the family name with `fc-list : family` (Linux/macOS) or by opening the font file on Windows.

Use fonts with a license that allows video embedding (for example anything on Google Fonts under OFL).

## Right-to-left and non-Latin scripts

libass shapes Arabic, Hebrew, Devanagari, Thai, and CJK when a font covering the script is available. Pass a suitable font, for example `--font-bold "Noto Sans Arabic"`. Word-pop styles assume spaces between words; for Chinese and Japanese use level 21-40 (chunk style).

## Editing a caption by hand

1. Open `edited.ass`.
2. Find the `Dialogue:` line with the wrong text. Fix the text only, not the `{...}` tags.
3. Re-burn without re-planning:

```bash
ffmpeg -i input_after_cuts.mp4 -vf "subtitles=edited.ass" -c:a copy fixed.mp4
```

Easier: fix the word in `edl.json` under `words` and run `render` again.

## Exporting an SRT for platforms that take sidecar captions

```bash
ffmpeg -i edited.ass edited.srt
```
