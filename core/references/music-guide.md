# Background music guide

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Music is picked automatically, but you can override every part. Three routes, in order of safety:

1. **Built-in templates** (default): 18,432 license-free beds synthesized by ffmpeg on the user's machine. No copyright claims possible.
2. **A library track the user owns or licensed**: `--music song.mp3`.
3. **A track the user found online**: only from the license-clear sources listed below, and only after reading that track's license.

Never download music from YouTube videos, TikTok sounds, or Spotify for a published edit. Platforms mute or claim it.

## Template ids

A template id is `mood.key.drums.timbre.energy`, for example `tech_pulse.D.driving.pluck.high`.

| Part | Options | Count |
|---|---|---|
| mood | uplifting, bright_pop, hopeful, confident, corporate_clean, playful, calm_ambient, chill_lofi, emotional, tech_pulse, cinematic_epic, dark_tension, mysterious, sunny_acoustic, motivational, news_neutral | 16 |
| key | C to B | 12 |
| drums | none, soft_pulse, four_floor, half_time, lofi, trap, driving, broken | 8 |
| timbre | sine, warm, organ, pluck | 4 |
| energy | low (x0.85 tempo), mid, high (x1.15 tempo) | 3 |

16 x 12 x 8 x 4 x 3 = **18,432 templates**. Check with `$SC music count`.

Honest limit: these are simple synth beds (pad, bass, drums). They sit well under a voice. They are not produced songs with melodies and vocals. For a music-led edit with no voice, use route 2.

## Commands

```bash
$SC music count                                   # how many templates, total and per genre
$SC music list --genre hackathon_demo --limit 30  # sample the ids that fit a genre
$SC music pick work/words.json                    # detect genre + speech pace, return one id and the reason
$SC music render tech_pulse.D.driving.pluck.high --seconds 30 -o preview.wav   # listen before rendering video
```

`plan` stores the pick in `edl.json` under `theme.music_template` and `params.music_pick`. `render` synthesizes it. To change it, edit `theme.music_template` in `edl.json` and render again.

## How the match is made

1. **Genre** (from `detect`) limits moods, drums, timbres and energy to ones that suit it (table below).
2. **Speaking pace**: words per minute. Under 130 = low energy, 130 to 170 = mid, above 170 = high. A fast talker over a slow bed feels sluggish; a calm talker over a fast bed feels anxious.
3. **Variant seed** (the same `--variant` as the look) picks inside the allowed set, so the same video always gets the same track and different videos get different ones.

| Genre | Moods | Drums | Timbres | Energy | Templates |
|---|---|---|---|---|---|
| hackathon_demo | tech_pulse, confident, uplifting, motivational | driving, four_floor, broken | pluck, warm | mid, high | 576 |
| tutorial_docs | calm_ambient, chill_lofi, corporate_clean | none, soft_pulse, lofi | sine, warm | low | 216 |
| product_launch | bright_pop, uplifting, sunny_acoustic, playful | four_floor, driving, half_time | pluck, warm, organ | mid, high | 864 |
| education_explainer | corporate_clean, hopeful, news_neutral, mysterious | soft_pulse, lofi, half_time | warm, sine, pluck | low, mid | 864 |
| story_vlog | emotional, hopeful, chill_lofi, sunny_acoustic | none, soft_pulse, lofi | warm, sine, pluck | low, mid | 864 |
| sales_pitch | confident, motivational, dark_tension, cinematic_epic | trap, driving, half_time | pluck, organ, warm | mid, high | 864 |
| podcast_talk | calm_ambient, chill_lofi, news_neutral | none, soft_pulse | sine, warm | low | 144 |
| ai_comparison | tech_pulse, mysterious, confident, playful | broken, driving, trap, half_time | pluck, warm | mid, high | 768 |

"100% match" is not something any rule can promise; taste is involved. What the rules do guarantee: the tempo family fits the pace, the mood fits the genre, and the ducking keeps the voice on top. Always listen to the preview.

## Mood cheat sheet (when choosing by hand)

| If the video says... | Mood | Why |
|---|---|---|
| "we built", "it works", results | tech_pulse, confident | minor drive sounds like momentum without being cheesy |
| "step one", "click", "open" | calm_ambient, chill_lofi | nothing competes with instructions |
| "introducing", "today we launch" | bright_pop, uplifting | major, four-on-the-floor lifts the reveal |
| "why", "research", "the reason" | corporate_clean, mysterious | neutral, or curious for reveals |
| "I felt", "my family", "honestly" | emotional, hopeful | iv minor chord gives the bittersweet turn |
| "the mistake", "the secret", money | dark_tension, confident | tension sells the problem, confidence sells the fix |
| comparisons, "which is better" | tech_pulse, playful | playful keeps a versus light; tech for AI |
| travel, food, day in the life | sunny_acoustic | bright, simple I-V-IV |

## Mixing rules (already applied by render)

- Music sits at `--music-db` (default -20 dB) under the voice and is ducked by sidechain compression whenever the voice speaks.
- Final mix normalized to -14 LUFS, true peak under -1 dBFS.
- 1.2 s fade in, 1.5 s fade out.
- Tutorials and podcasts: consider `--music-db -26`. Launches and hackathon demos: `-18`.
- No music under a quote card with a sad or serious line: set `params.music` to false in `edl.json` if the whole video is serious.

## Syncing cuts to the beat

The template tempo is in the render log (`133 bpm`). One beat = 60 / bpm seconds. Cards and zooms feel intentional when their `start` lands within 80 ms of a beat. To snap by hand in `edl.json`: `start = round(start / beat) * beat`. Do not snap captions; they follow speech.

## License-clear sources for real tracks (route 3)

Read each track's license page before use. Terms change.

| Source | Typical license | Watch out for |
|---|---|---|
| YouTube Audio Library (Studio > Audio Library) | free for YouTube; many need attribution | some tracks say "attribution required"; use outside YouTube may not be covered |
| Pixabay Music | Pixabay Content License, no attribution | a few tracks are Content ID registered; keep the license certificate |
| Uppbeat | free tier with credit, paid without | free tier needs the credit line in the description |
| Free Music Archive | varies per track (CC BY, CC BY-NC, ...) | NC means no commercial use: no ads, no sponsored posts |
| Incompetech (Kevin MacLeod) | CC BY 4.0 | attribution required in the exact format given |
| Artlist, Epidemic Sound, Musicbed | paid subscription | license covers the subscriber's channels only, while subscribed at publish time |

Search phrases that find beds that work under speech: `<mood> background no vocals`, `<mood> corporate underscore`, `lofi instrumental loop`, `minimal tech pulse`. Pick tracks without vocals and without a busy melody in the 1 to 4 kHz range, where speech lives.
