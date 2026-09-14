# Design study 2: the frosted-glass edit

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

## Why it looks expensive: 10 techniques

### 1. Frosted glass cards instead of flat white cards

Cards are not painted on top of the video. They are windows into a blurred, brightened copy of the video behind them, with a faint white tint and a 1-2 px light hairline border. The room stays visible through the card, so the graphic feels like it lives inside the scene.

**In splicecraft:** `--style glass`, or `"glass": true` in `brand.json`. The renderer crops the zoomed frame under each card, applies `gblur` (sigma 34 on a 1920 grid) plus `eq=brightness=0.05:saturation=1.15`, cuts rounded corners with a `geq` alpha mask, fades it in and out with the card, and overlays it before the captions. `glass_alpha` (0 opaque to 255 clear, default 150) sets how much tint sits on top.

**Rule:** glass needs something behind it. On a plain white wall it reads as a grey box. Use it on footage with depth: windows, furniture, plants, city.

### 2. Eyebrow labels

Every card starts with a tiny, widely spaced, all-caps label: "AND SOMEHOW...", "TIME TO CREATE", "EDIT TIMELINE", "PROOF · AI EDITED REELS". It tells the eye what kind of card this is before it reads the content. The first baseline does the same ("THE TEST, IN NUMBERS").

**In splicecraft:** the `label` field on every card, drawn at 30 px with 4 px letter spacing in the `muted` color.

### 3. Headline with a full stop

"Minutes." with a period, set very large and heavy, then a thin rule under it. Punctuation on a one-word headline turns it into a statement. Variant in the other edit: "Minutes, not hours." with the second phrase in grey.

**In splicecraft:** `word` cards. If you edit `edl.json` by hand, add the period to `text`.

### 4. Two-tone contrast headlines

"Minutes, not hours." puts the claim in the accent green and the rejected alternative in dark neutral. The eye reads the colored half first.

**How to do it by hand:** in the `.ass` file, wrap the second half in `{\1c&H6B645E&}`.

### 5. Real interface mockups, not icons

Instead of an icon for "timeline", the card shows a small timeline: a title bar ("EDIT TIMELINE 00:00:21"), a playhead, and colored clip bars in soft pastels (sky, peach, lilac, mint, butter). A prompt box with a blinking cursor, then a green check pill "and it does it". The viewer recognizes a product UI, which is more convincing than a symbol.

**In splicecraft:** the ranking card's bars are the same idea (rows of rounded color bars). For full mockups, render a PNG in any design tool and overlay it (see "Image overlays" below).

### 6. Layout reflow: the speaker makes room

On the "Minutes" beat the full-frame shot shrinks into a rounded card with a drop shadow and slides left while a panel slides in from the right. The speaker is still visible but the information gets half the frame. When the beat ends, the shot grows back.

**Recipe (manual, ffmpeg):**

```bash
# T0 = beat start, T1 = beat end, output 1080x1920
ffmpeg -i edited.mp4 -loop 1 -i panel.png -filter_complex "[0:v]split=3[full][small][blur];[small]scale=520:924,format=yuva420p,geq=lum='p(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='255*lte(hypot(max(0,abs(X-260)-228),max(0,abs(Y-462)-430)),32)'[card];[blur]gblur=sigma=40,eq=brightness=0.08[bg];[bg][card]overlay=x=40:y=480[a];[a][1:v]overlay=x=580:y=480:shortest=1[b];[full][b]overlay=enable='between(t,T0,T1)'[v]" -map "[v]" -map 0:a -c:a copy reflow.mp4
```

Replace `T0` and `T1` with numbers. Keep reflow to one or two beats per video; it is the strongest move you have.

### 7. Spatial captions (text behind the person)

A big word ("bigger") sits behind the speaker's head: the person occludes the text. It needs a per-frame person mask.

**Honest limit:** ffmpeg alone cannot segment a person. Options: (a) shoot on a green screen and use `--key`, then burn the word into the background before overlaying the person; (b) run a segmentation model (MediaPipe Selfie Segmentation, rembg, or Robust Video Matting) to export a mask video, then composite `background -> word -> person`. splicecraft does not ship a model, to stay dependency-free.

### 8. A color pulse on the emotional beat

On "and somehow it does it" the whole frame warms (orange-peach tint, lifted highlights) for about a second, then returns. It works like a sound cue for the eyes.

**In splicecraft:** at level 41+, every `word` and `question` card triggers a `colortemperature` pulse (down to about 5000 K) for up to 1.2 s.

### 9. Muted captions that do not compete

Captions are small white sentence-case text on a dark translucent rounded pill, low on the frame. Because the cards carry the emphasis, the captions stay quiet.

**In splicecraft:** the `glass` look sets `caption_size` 64 and `caption_y` 1430. For a pill background, set level 21-40 (chunk style) and change the Caption style's `BorderStyle` from 1 to 3 in the `.ass` header (3 draws an opaque box using the outline color).

### 10. A restrained palette

Warm grey room, black clothing, white glass, one saturated green for success states, pastels only inside mockups. The title uses a yellow italic highlight with an outline for the words "AI Model", the only loud element, and it is fixed at the top.

**In splicecraft:** `glass` look uses a green accent `#1E9E5A`, near-white card tint, warm grade.

## Weak spots in this video

1. Same split-screen problem as baseline 1: each face is small and the header plus model rows take about a third of the frame.
2. Glass cards on the top pane sit over a grey wall, so they read as grey boxes (see rule under technique 1).
3. The mockup text ("Create something...", timeline labels) is unreadable at phone size. It signals "UI" but cannot be read.
4. The model rows show "35mins & 7M token" vs "29mins & 12M token" in italic light grey. It is the most interesting data in the video and it is styled as fine print.
5. No hook card in the first 2 seconds; the first graphic arrives around 1.5-3 s.
6. The persistent line "comment 'vid' to get the full video" is the CTA for the whole video, set at body size with no contrast, below both panes.
7. It ends mid-thought at 26 s with no end card.

## Image overlays (for mockups you design elsewhere)

```bash
ffmpeg -i edited.mp4 -loop 1 -i mockup.png -filter_complex "[1:v]format=rgba,fade=t=in:st=12.0:d=0.25:alpha=1,fade=t=out:st=15.5:d=0.25:alpha=1[m];[0:v][m]overlay=x=(W-w)/2:y=260:enable='between(t,12,15.75)':shortest=1[v]" -map "[v]" -map 0:a -c:a copy out.mp4
```

Export the PNG at the final pixel size (for a 940 px wide card on 1080 output, export 940 px wide). Scaling a PNG up blurs it.
