---
name: sc-edit
description: Edit raw talking-head phone clips into a finished vertical short in ONE pass - full-screen footage with the framing changing every few seconds, a big opening title, word-by-word captions, and the script's on-screen text and props as slates and sheets (never on the face). Use when the user hands over raw clips or a source video and wants it edited. Not for scripts (/sc-script), branding strategy (/sc-personalbranding) or animated product demos (/sc-demo).
---

# /sc-edit

One job: raw clips in, one finished MP4 out, right the first time.

The rule this skill exists for: **the user sees one render, and it is the good one.**

How it stays right even when you are a small or careless model: every judgement that can go wrong
(which word Whisper misheard, which take is the retake, what a card may say, whether a card rendered)
is made by the tool, not by you. Your job is to run the steps in order, write the title and pick the
card moments, and obey lint. **You never report a check you did not do.** "Looks fine" is not a check;
the report quotes what each cell of the cards image shows.

Tools live in `core/scripts/` (paths relative to the splicecraft repo). `S=core/scripts/studio.py`,
`SC=core/scripts/splicecraft.py`. Work in one folder per video. Python output through `timeout` or a pipe
can vanish on Windows; redirect to a file (`> log.txt 2>&1`) and read the file.

## 0. Find the script (naskah)

Look in the folder the clips came from and its parent for the script of THIS video: `SKRIP-*`, `BACA-*`,
`naskah*`, `script*`, `*.md`/`*.txt` with the spoken lines. A pack often has two versions of the same video
(a monolog table and a read-aloud version); take both. The script is the source of truth for names,
institutions, numbers and every word on a card. If there truly is none, ask once; if the user says there
is none, set `"script": false` and every card must quote the transcript.

## 1. Join and look

```
python $S join clip1.mp4 clip2.mp4 ... -o work/source.mp4      # order = story order; ask if unclear
python $S track work/source.mp4 -o work/face.json
```

If the tracker log says `PRODUCTION FAULT: the top of the frame cuts the head`, tell the user in one line
(it is their footage, not the edit) and carry on.

## 2. Transcribe, then align to the script

```
python $SC transcribe work/source.mp4 -o work/words.json --engine local --language id
python $S align --words work/words.json --script <script1> [<script2>] --edl work/edl.json
```

`align` records the script in edl.json and prints what the tool will do with it: caption corrections by word
position (Whisper's misheard names), retake cuts, and greetings / sign-offs outside the script. It tries the
other script versions next to the one you gave and uses whichever the speaker actually followed. **You write
none of this**: lint and render recompute it from the script every time, so keep `"script"` as align wrote it
(point it at the pack's files, do not copy them) and do not add `fix`, `fix_at` or `drop`. If align exits
with `no script matches this speech`, stop and ask the user for the right script; do not guess.

## 3. Plan: the script writes the cards

```
python $S plan --words work/words.json --script <script1> [<script2>] --edl work/edl.json > work/plan.txt 2>&1
```

When the pack has a script table (`Ucapan | Visual | Teks layar`), `plan` writes the whole edl: title, every
on-screen text of the table, every prop the Visual column shows (SID card, keys, ball, whistle, book: drawn
as icons because talking-head footage has no insert shots), the `Overlay:` notes of the read-aloud version,
the line that must stick, a term being named, a spoken number, the closing card (theme + event) and the
pack's brand colours. Each card sits on the word it names. **Do not rewrite it.** Read `plan.txt`: one line
per card. `NOT PLACED` means the script asks for something the speaker never said; tell the user in one
line. Lint fails if a card the script asks for is missing, so deleting one costs a render.

Go to step 4. Write cards by hand (below) only when `plan` says there is no script table.

### Writing cards by hand (no script table)

Read the transcript next to the script, only to find the 2-4 moments that deserve a card: a term being
defined, a number, a list said out loud, the line the script marks as the one that must stick.
Add to the edl align wrote (keep its `script`):

```json
{
  "title": "Reksa Dana: Patungan yang Diawasi",
  "subtitle": "Modal kecil, dikelola manajer investasi",
  "theme": "paper",
  "overlays": [
    {"type": "term", "at": 12.4, "until": 17.0, "eyebrow": "Istilah", "title": "NAB",
     "body": "Nilai Aktiva Bersih per unit"},
    {"type": "list", "at": 40.2, "until": 50.0, "title": "Cek dulu", "marker": "check", "items": [
      {"text": "Terdaftar di OJK", "at": 41.0}, {"text": "Ada bank kustodian", "at": 44.5}]}
  ],
  "endcard": {"lines": ["Mulai dari yang kecil", "Cek izinnya dulu"], "hold": 2.4}
}
```

- **Card text comes from the script**: its on-screen text column (`Teks layar`, `Overlay:`) first, else its
  spoken lines. Lint rejects any card word that is not in the script. Do not explain a term from your own
  knowledge; if the script does not define it, the card only names it.
- A card appears **on the word**: `at` is the `s` (source seconds, from words.json) of the word the card names,
  and a list item's `at` is the `s` of the word that item names. Lint rejects a term, stat or list item that
  is on screen while its word is not being said. The tool remaps every time through the cuts; never compute
  output times yourself.
- Pick the type by what is said: a term being defined -> `term` with `title` = the term exactly as the script
  writes it (`Kliring`, `SID`) and `body` = its meaning from the script; several things named in a row
  (`BEI ... IDClear ... KSEI`) -> one `list` or `flow` with an item per thing, not a row of chips; a number ->
  `stat`; the line the script says must stick -> `quote`. `chip` is only a small corner label.
- `title` <= 44 chars, says what the viewer gets. `subtitle` is the promise in plain words.
- Themes: `paper` (neutral), `red` (Indonesian civic / finance), `night` (dark footage, tech).
- Level 1 budget: at most one card per ~20 s, one on screen at a time, each >= 2.5 s. Captions carry the rest.
- Card text is the key phrase, not the sentence. A card never repeats the caption word for word.

Fields each type shows. Any other field is ignored, and lint says so (a `cta` given `title` renders empty):

| type | fields |
| --- | --- |
| `term` | `title` (required), `eyebrow`, `body` |
| `stat` | `value` (required, counts up), `suffix`, `label`, `eyebrow` |
| `list`, `flow` | `items` (required: `{"text", "at", "sub"}`), `title`, `eyebrow`; list also `marker: "check"` |
| `quote` | `text` (required), `by` |
| `compare` | `left`, `right` (each `{"eyebrow","title","body"}`), `highlight: "left"|"right"` |
| `chip`, `question`, `cta` | `text` (required) |
| `word` | `text` (required), `lead` |
| `props` | `items` (required: `{"icon", "text", "sub", "at"}`): objects put on the table one by one |
| `prop` | `icon` (required), `text`, `from: "envelope"` (the card rises out of an envelope) |
| `endcard` | `lines` (required), `eyebrow`, `icon`, `hold` |

Icons: `sid`, `envelope`, `key`, `door`, `house`, `ball`, `whistle`, `book`, `shield`, `phone`, `check`.
`term`, `stat`, `word`, `quote`, `list` take `"icons": [{"icon": "door", "at": 39.9}, ...]` (a row on top,
each on its word); list/flow/props items take `"icon"`.

Layout (default `"layout": "full"`): the footage fills the screen and the framing changes every cut and at
least every 2.6 s (wide / medium / tight, each with a slow 105% push), the title opens the video big over the
first 2.4 s, and each card opens as a 1.3 s full-screen slate (giant icon + its words) and then sits in a sheet
over the bottom of the footage. Props fall in big and shrink into their tile. You set none of this; lint fails
when the picture holds still too long or slates pass the pack's 30% cover limit. `"slate": 0.8` shortens one
card's slate, `"slate": false` skips it. `"layout": "inset"` is the old framed look (speaker in a box on a
canvas, title on top); only use it when the user asks for it.

Inset layout only: `"mode": "takeover"` covers the inset (big list/stat); `"place": "left"|"right"|"lower"|"top"|"table"`.
`"hold": [[a, b]]` keeps the pauses of a line the script says not to cut. `"punch": 1.0` turns off the
punch-in on jump cuts; `"grade": "none"` turns off the light colour correction.

## 4. Lint, then render a draft

The end card is added after the last word (2.6 s); it never covers speech. The pack's rules (duration
window, share of animation) are read from its guide and checked by lint.

```
python $S lint work/source.mp4 --words work/words.json --face work/face.json --edl work/edl.json > work/lint.txt 2>&1
python $S render work/source.mp4 --words work/words.json --face work/face.json --edl work/edl.json -o out/draft.mp4 > work/render.txt 2>&1
```

Run render in the **foreground** and wait for it (80 s of video takes about 1-3 minutes). Never run it in the
background, never start a second render while one runs (the tool refuses), and never judge progress by file
size: the output file appears only when the render is complete, and its log's last line starts with `wrote`.
A draft is about 2-3 MB.

Lint checks, in the browser and against the script: card words not in the script, names/numbers in the
title not in the script, retakes still in the cut, empty cards and ignored fields, face overlap, overflow,
time overlap, too short, caption length. Render refuses to run with lint problems. Fix the edl, never the
tool, and never `force`.

Renders are `draft` (480p, 24 fps) by default: the draft is for judging the edit, not the picture. Only
when the user has approved the draft, render the same edl once more with `--quality final` (1080p, 30 fps).

## 5. Look before you hand over

```
python $S cards out/draft.mp4                  # -> out/draft.cards.jpg, one cell per card
python $SC sheet out/draft.mp4 out/sheet.jpg
```

Open `draft.cards.jpg` (Read the image). Under each cell is what the edl says the card is. For every cell,
write one line in your report: what you see, and whether it matches the label. A cell with no card, an
empty card, a card on the face or a card that differs from its label is a failed render: find the step
below, fix it, render again, and say in the report that it took two renders and why.

| What you see | Go back to |
| --- | --- |
| no card / empty card in a cell | 3: wrong fields for that type (see table) |
| a card on the face, or cut by the inset edge | 3: shorten text, `place`, or `takeover` |
| wrong word in a caption | 2: script missing or wrong; rerun align with the right script |
| a stumble / repeated sentence | 2: rerun align (it finds retakes); tell the user if it did not |
| head too high/low in a shot | 1: check face.json for that shot (borrowed or weak detection) |

Hand the user: the draft, the cards image, the sheet, one line per card from the cards image, the number
of renders, and one line on anything that is their footage's fault.
