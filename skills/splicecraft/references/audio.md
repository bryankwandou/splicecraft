# Audio: voice, music, effects, loudness

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
