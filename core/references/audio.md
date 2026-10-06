# Audio: voice, music, effects, loudness

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

## Signal chain (what `render` builds)

```
voice: select kept ranges -> highpass 75 Hz -> compressor 3:1 at -20 dB -> +2.5 dB at 3.2 kHz -> split
music: loop -> trim to length -> volume (--music-db, default -20 dB) -> sidechain compress keyed by voice
sfx:   synthesized wav (pop / tick / whoosh) -> -9 dB
mix:   amix (no auto-normalize) -> loudnorm I=-14 TP=-1.5 LRA=11 -> 48 kHz AAC 192 kbps
```

## Loudness targets

| Platform | Target | Notes |
|---|---|---|
| TikTok, Reels, Shorts | -14 LUFS, peak -1 dBTP | default |
| YouTube long form | -14 LUFS | same |
| Podcasts | -16 LUFS | change `I=-14` to `I=-16` in `render()` |

`qa` accepts -16.5 to -12.5 LUFS and a peak at or below -0.5 dBFS.

## Music

Allowed sources, in order of preference:

1. **Generated bed** (default at level 21+). `synth-music` renders a chord pad, soft kick, and hat with ffmpeg `aevalsrc`. No license needed. Moods: `bright` (major progression) and `moody` (minor). Tempo comes from the look (`bpm` in styles.json).
2. **The user's own file** with rights to use it: `--music song.mp3`.
3. Royalty-free libraries the user already has an account with. The agent must not download music itself.

Never rip songs from YouTube, TikTok, or Spotify. Platform content ID will mute or strike the post.

Standalone bed:

```bash
$SC synth-music -o bed.wav --seconds 90 --bpm 100 --mood bright
```

### Choosing tempo

| Content | BPM |
|---|---|
| Calm explainer, cinema look | 80 to 90 |
| Standard creator talk | 95 to 105 |
| Hype, product launch, neon look | 115 to 125 |

### Ducking

The sidechain compressor (threshold 0.03, ratio 8, attack 20 ms, release 350 ms) drops the music when the voice is present and lets it breathe in pauses. If the music pumps audibly, raise release to 500. If the voice still fights the music, lower `--music-db` to -24.

## Sound effects

Synthesized by the script, so there is nothing to license:

| Name | Sound | Used on |
|---|---|---|
| pop | 90 ms falling sine chirp | hook, number, quote, question, word, CTA |
| tick | 40 ms 1.8 kHz click | extra ranking rows, merged numbers |
| whoosh | 320 ms filtered noise swell, starts 180 ms before the card | ranking, versus |

Rules: an effect marks a visual change. No effect without a graphic. No more than one effect per second.

## Cleaning bad voice audio

Add to the voice chain in `render()` when needed:

| Problem | Filter |
|---|---|
| Constant hiss / fan | `afftdn=nf=-25` |
| Room echo | not fixable well in ffmpeg; lower music and accept it |
| Clicks, mouth noise | `adeclick` |
| Very quiet recording | the compressor plus loudnorm handles up to about 20 dB of gain |
| Hum at 50/60 Hz | `highpass=f=90` or `bandreject=f=50:w=5` |

## Voice pitch and speed (read before touching either)

The most common AI editing mistake with voices: the speaker comes out as a chipmunk (pitch too high) or a slow robot (pitch too low). Both break trust in the first second, and viewers swipe.

### The default is: do not change pitch. Ever.

splicecraft never changes voice pitch unless `params.voice` in `edl.json` names an allowed reason. The render refuses anything else with an error. Pause removal cuts silence; it does not speed up or slow down speech.

### Why it happens (so you can spot it)

| Cause | Result | Fix |
|---|---|---|
| Speeding audio with `asetrate` (or "speed" in an editor with pitch lock off) | chipmunk | use `atempo`, which stretches time and keeps pitch |
| Slowing audio with `asetrate` | deep, slow, robotic | use `atempo` |
| Treating 44.1 kHz audio as 48 kHz (or back) when muxing | pitch 1.5 semitones off, speech 9% fast or slow | resample with `aresample=48000`, never relabel the rate |
| A TTS voice rendered at one rate and played at another | high or low voice | check `ffprobe` sample rate of the TTS file |
| "Pitch correction" or "voice enhance" presets on already-good audio | robotic warble | turn them off |
| Formant-less pitch shift of more than about 2 semitones | cartoon or monster timbre | do not shift speech that far unless it is an intended effect |

### Decision table: when pitch may change

| Situation | Allowed? | How | Limit |
|---|---|---|---|
| Normal talking head, tutorial, pitch, demo, podcast, story | **No** | nothing | 0 |
| User says "make it faster" | **Speed only, pitch unchanged** | cut more pauses first (raise the level); if still needed, `atempo` on voice *and* re-time video together outside splicecraft | 1.05-1.15x; above 1.25x speech sounds rushed |
| Source sounds wrong (chipmunk or slow) because of a sample-rate mismatch | Yes, to restore the original | `"voice": {"pitch_semitones": <measured>, "reason": "fix_wrong_sample_rate"}` | +/-2 semitones |
| User asks to disguise a voice (privacy, whistleblower, a minor) | Yes, if the user asked | `"reason": "anonymize_speaker"`, try -3 to -4 or +3 to +4 | +/-5; also blur the face, pitch alone is weak anonymization |
| A deliberate comedy or character voice the user asked for | Yes, on purpose only | `"reason": "character_effect"` | +/-12 |
| A sung or hummed line must match the music key | Yes | `"reason": "match_music_key"` | +/-1 |
| "Sound more confident / deeper" | **No** | better mic distance, EQ (low shelf +2 dB at 150 Hz), compression; already in the voice chain | 0 |
| "Sound younger / more energetic" | **No** | a faster music template and a higher edit level, not pitch | 0 |
| Music does not fit the voice | **No voice change** | pick another template (`$SC music pick`) | 0 |
| Audience is kids or older adults | **No** | caption size and pace via the brief | 0 |
| AI dubbing or TTS voice sounds off | **No shift** | regenerate the voice at the right sample rate | 0 |

If you are unsure, the answer is no.

### How to set an allowed change

In `edl.json`:

```json
"params": { "voice": { "pitch_semitones": -1.5, "reason": "fix_wrong_sample_rate" } }
```

Semitones from a rate mismatch: `12 * log2(correct_rate / wrong_rate)`. Example: audio made at 44100 but played as 48000 sounds +1.47 semitones high, so set -1.47.

Render uses `asetrate` + `aresample` + a compensating `atempo`, so the pitch moves and the timing (and caption sync) does not.

### Check by ear and by numbers

1. Listen to the first 5 seconds of the render next to the source. Same voice? Good.
2. `duration_match` in QA must pass: speed changes show up as duration drift.
3. Compare `ffprobe` of source and render: sample rate 48000 in the render is expected; the speech length between two words should match the transcript timing.

Sources (checked 2026-09-15): FFmpeg atempo vs asetrate explanations at https://dev.to/javidjamae/ffmpeg-atempo-filter-change-audio-speed-without-pitch-shift-3e6i and https://hhsprings.bitbucket.io/docs/programming/examples/ffmpeg/manipulating_audio/atempo_asetrate_aresample.html
