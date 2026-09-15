# Beat library

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

A beat is one sentence and the treatment it gets. The planner (`plan` in `scripts/splicecraft.py`) checks beats in the order listed. The first match wins. A sentence that matches nothing gets captions only.

All positions use a 1080 x 1920 design grid and are scaled to the output size. Cards live in the top third (y 230 to about 600). Captions live at y 1390. The face is assumed to sit between y 600 and y 1300.

Card timing rule for every type: `start` = the first word of the trigger, `end` = sentence end + 0.6 s, clamped to between 1.6 s and 4.2 s after start.

---

## 1. hook

- **Trigger:** the first sentence of the video. Level 21 and up.
- **Look:** panel across the top, sentence split into up to three lines, words fade in 70 ms apart, keywords (6+ letters or numbers) in the accent color.
- **Motion:** panel rises 40 px with a 92% to 100% scale. Video eases in to the level's zoom amount over the first 2 s.
- **Sound:** pop.
- **Why:** the first second decides whether the viewer stays. A title that builds word by word gives the eye something to track while the voice starts.
- **Do not:** use the hook card for a greeting ("Hi guys"). If the first sentence is a greeting, delete the hook card in `edl.json` and make the second sentence the hook by changing its start and text.

## 2. cta

- **Trigger:** a sentence in the last 40% of the video containing follow, subscribe, or ikuti. Used once.
- **Look:** accent pill in the card zone at the top (y card_y + 40); the bottom ~400 px is covered by platform buttons and captions with `cta_text` from the theme.
- **Variant:** "comment WORD" becomes a question pill reading `Comment WORD`.
- **Do not:** show two CTAs back to back. The planner keeps only the first follow sentence.

## 3. quote

- **Trigger:** "they say", "quote", "said", "kata orang", "pepatah". If the trigger sentence has four words or fewer ("Here's a quote."), the next sentence becomes the quote.
- **Look:** panel with a large accent opening quote mark and the sentence revealed character by character (ASS `\kf` karaoke with transparent secondary color).
- **Timing:** reveal takes about 30 ms per character, never longer than the sentence.
- **Do not:** quote a sentence longer than about 90 characters; it becomes a wall of text. Shorten the text field in `edl.json` and keep the meaning.

## 4. versus (before and after)

- **Trigger:** the phrase "before and after" (or "sebelum dan sesudah").
- **Look:** two panels, BEFORE and AFTER, with a round accent VS badge that scales from 0 to 115% to 100%.
- **Sound:** whoosh.

## 5. ranking

- **Trigger:** ordinal words: first, second, third, fourth, fifth (pertama, kedua, ketiga...). A ranking starts at "first". Each next ordinal within 6 s appends a row to the same card.
- **Look:** numbered rows; each bar wipes in from the left over 420 ms. Bars get shorter and lighter per rank so the order is visible without reading.
- **Sound:** whoosh on the card, tick on each new row.
- **Do not:** start a ranking at "second". If the speaker says "second" without "first", no card is made.

## 6. number

- **Trigger:** digits (`3`, `100%`, `2.5`) or number words (two, ten, hundred, dua, seratus). The word "one" is ignored because it is almost always a pronoun.
- **Merge:** numbers in a sentence that starts within 3.5 s of an open number card join that card, up to three.
- **Look:** panel with a small caps label (BY THE NUMBERS), each number huge in the accent color with the next content word as its label. Values over 3 count up in ten steps over 450 ms.
- **Motion:** punch zoom at 60% of the level's zoom amount.
- **Sound:** pop, then tick for each merged number.
- **Memory:** every number shown is remembered for the callback beat.

## 7. callback

- **Trigger:** a sentence containing "number" plus one of back, remember, start, again, earlier, kembali, tadi, and at least one remembered number.
- **Look:** the number card layout labeled BACK TO THE START with up to three earlier numbers.
- **Why:** it shows the edit follows the whole video.
- **Exception:** callbacks ignore the breathing-room gap.

## 8. question

- **Trigger:** a sentence ending in "?" with nine words or fewer.
- **Look:** accent pill with the question, zooming in from 55%.
- **Motion:** gentle ease-in zoom at 50% of the level amount.

## 9. word

- **Trigger:** a sentence of one to three words with at least one content word of four or more letters. Filler sentences ("That's it", "Thanks", "Bye") are skipped.
- **Look:** the phrase (or its longest word if the phrase is over 12 characters) in huge accent letters with a thick stroke, scaling from 40% with blur to 112% to 100%, and an underline that grows from the center.
- **Motion:** full punch zoom. At level 81+, a white flash hit.

## 10. nothing (the default)

- **Trigger:** everything else.
- **Look:** captions only. On long sentences (five words or more) a slow drift zoom is added every few sentences so the shot is never frozen.
- **Why:** restraint is what makes the other beats land. The planner keeps at least 38% of runtime card-free by dropping the weakest beats; the QA gate `breathing_room` fails below 35%.

---

## Global limits

| Limit | Formula (L = level 1-100) |
|---|---|
| Pause removal threshold | 0.95 - 0.65 x L/100 seconds |
| Card ceiling | 10 x L/100 cards per minute (hook and CTA are free) |
| Minimum gap between cards | max(2.0, 11 - 9 x L/100) seconds |
| Zoom amount | 1 + 0.22 x L/100 |
| Grade strength | 0.25 + 0.75 x L/100 |

## Adding a beat type by hand

1. Copy an existing card object in `edl.json`.
2. Change `type` to one of: hook, number, callback, ranking, quote, question, versus, word, cta.
3. Set `start` to the trigger word's `s` from `words`, and `end` 1.6 to 4.2 s later.
4. Make sure it does not overlap the previous or next card.
5. Render again.
