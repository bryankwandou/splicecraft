# Troubleshooting

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
