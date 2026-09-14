# edl.json schema

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

## Card shapes

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

## Limits the renderer assumes

- hook: up to 3 lines of about 18 characters.
- number and callback: up to 3 items.
- ranking: up to 5 rows, row text up to 22 characters.
- quote: up to 4 lines of about 24 characters.
- question: up to 30 characters.
- versus: up to 12 characters per side.
- word: up to 14 characters.

Longer text is truncated or runs off the card. Shorten it in the JSON.

## Validating after hand edits

```bash
python -c "import json;json.load(open('work/edl.json'))" && echo valid
```

Then run `render` and `qa`. The `no_card_overlap` gate catches cards whose times collide.
