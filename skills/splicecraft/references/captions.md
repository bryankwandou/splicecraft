# Captions

Captions are rendered as an Advanced SubStation Alpha (`.ass`) file and burned in with libass. The `.ass` file is saved next to the output (`edited.ass`) so it can be inspected or edited and re-burned.

## Typography rules

1. **Size:** 66 to 80 px on a 1920 px tall frame. That is 3.4% to 4.2% of height. Smaller is unreadable on a phone; larger covers the face.
2. **Weight:** heavy. Default fonts are Segoe UI Black (Windows), Helvetica Neue (macOS), DejaVu Sans (Linux). Override with `--font-bold "Montserrat ExtraBold" --fontsdir ./fonts`.
3. **Contrast:** light text, 7 px dark stroke, 3 px shadow. Readable over white walls and dark rooms alike.
4. **Length:** three words at level 41+, four at 21-40, seven at 1-20. Break early at commas and sentence ends.
5. **Position:** centered at y 1390. Clear of the face above and of the TikTok/Reels caption and button zone below (bottom 320 px and right 140 px).
6. **Timing:** a caption appears on its first word's start and leaves 0.25 s after its last word, or when the next one starts.
7. **Accent:** one accent color for the spoken word and keywords. Never more than two colors in a caption.
8. **Case:** sentence case by default. All caps only in the `neon` look, where the font is set wide.

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
