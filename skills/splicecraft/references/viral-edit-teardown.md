# Viral edit teardown: what 82 reference videos actually do

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Corpus:** all 82 `.mp4` files in `E:\Download\CONTOH INSPIRASI TEKNIK NGOTEN DAN EDITING VIDEO` — reference videos the user collected as examples of viral, well-made Indonesian short-form content. Creators: `bahasvideo`, `fitrisitisalma`, and `kadafidevayana` (the bulk).
> **Editable:** every number here is reproducible with the commands in §1. If you re-measure, update the numbers *and* the date.

## Why this file exists, and an honest note on method

The user asked SpliceCraft to learn editing, opening and closing technique from these videos so community users stop reporting that edits feel AI-ish.

Claude cannot watch video. So rather than guess at "technique" and dress the guess up as analysis, every file was **measured** with `ffprobe` and `ffmpeg` scene detection. What follows is what the measurements support, and nothing more. Where a claim is inference rather than measurement, it says so.

This turned out to matter: the measurements **contradicted** two things that seemed obviously true before the data came in. Both are documented in §6 rather than quietly dropped.

---

## 1. Method, so you can reproduce or challenge it

```bash
# per-file: dimensions, fps, duration
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate \
  -show_entries format=duration -of csv=p=0 "$f"

# per-file: scene-cut timestamps
ffmpeg -hide_banner -nostats -i "$f" \
  -vf "scale=160:-2,select='gt(scene,0.3)',showinfo" -f null - 2>&1 \
  | grep -o "pts_time:[0-9.]*" | cut -d: -f2
```

Downscaling to 160 px wide before scene detection makes the pass fast and does not meaningfully change cut detection.

**Known limits of this method, stated up front:**

- **Threshold 0.3 is conventional but untuned.** It under-counts cuts between visually similar shots — two angles of the same person against the same wall read as one continuous shot. So the "single-take" bucket in §3 may be slightly overstated. The bimodality is far too strong to be a threshold artifact, but the exact bucket sizes are soft.
- **A scene cut is not the only kind of edit.** Speed ramps, zooms, caption changes, and overlay animations are all editing and none of them register here. A video with zero scene cuts is not necessarily an unedited video.
- **53 of 82 files are 540×960** — re-compressed downloads, not masters. Fine for cut detection; useless for any conclusion about grading, grain, or colour.
- **No audio or transcript analysis.** No transcription backend was available this session. Music, loudness, ducking, and anything about what is *said* are unmeasured.

<!-- journal: raw per-file data lived in the session scratchpad and was not committed - it is ~82 lines of timestamps and regenerating it takes about 12 minutes. If you need it, re-run the commands above. -->

---

## 2. The corpus at a glance

| | |
|---|---|
| Files | 82 |
| Resolution | 540×960 (53), 1080×1920 (27), 360×640 (2) — **all 9:16 vertical, no exceptions** |
| Frame rate | 30 fps (80), 60 fps (2) |
| Duration | min 12.7 s · p25 22.2 s · **median 37.5 s** · p75 66.0 s · max 132.8 s |

**Duration is bimodal.** This is the first of three bimodal findings and they all point the same way.

| Bucket | Count |
|---|---|
| 10-20 s | 14 |
| **20-30 s** | **24** ← cluster |
| 30-45 s | 10 |
| 45-60 s | 9 |
| **60-90 s** | **17** ← cluster |
| > 90 s | 8 |

Two clusters — a quick hit at 20-30 s and a full story at 60-90 s — with a visible dip at 30-60 s between them.

**What follows:** pick which of the two jobs you are doing before you write. Landing at 50 s is usually what happens when nobody decided. See `kadev-script-formulas.md` §8 for the matching word budgets.

---

## 3. The headline finding: real edits are bimodal, AI-ish edits are uniform

Average shot length (ASL = duration ÷ number of shots) across all 82:

| | ASL |
|---|---|
| min | 0.54 s |
| p25 | 1.87 s |
| median | 3.23 s |
| p75 | 11.63 s |
| max | 46.35 s |

That p25-to-p75 spread — 1.87 s to 11.63 s — is not a distribution around a centre. It is two populations:

| Mode | ASL | Videos | Share | What it is |
|---|---|---|---|---|
| **Cut-driven** | 0.5 - 2.5 s | 32 | 39% | b-roll, voiceover, documentation, list content, jedag-jedug |
| *(dead zone)* | 2.5 - 8 s | 27 | 33% | mixed or transitional |
| **Single-take** | 8 s to no cuts | 23 | 28% | talking head, straight to camera |

Full ASL histogram: `<1 s` (3), `1-1.5 s` (5), `1.5-2.5 s` (24), `2.5-4 s` (10), `4-8 s` (17), `>8 s` (23).

**Six videos have zero scene cuts at all**, running 18.7 s, 29.5 s, 43.6 s and 46.3 s among others. They are in a folder the user collected as examples of good work. They are not under-edited — they are a different grammar: one take, one person, captions, nothing else.

Length correlates with mode, and not in the direction most people assume:

| | Median ASL |
|---|---|
| Videos under 30 s | 3.97 s |
| Videos 60 s and over | **2.00 s** |

**Longer videos cut faster.** A 90-second video earns its length by moving; a 20-second video can hold a single shot because it is over before attention runs out.

### Why this is the anti-AI-ish rule

The failure is not "too many cuts" or "too few". It is **landing in the middle by default** — a cut every 3-4 seconds for the whole runtime regardless of what is being said. Nobody chooses that rhythm. It is what you get when a tool applies a uniform rule to non-uniform material.

**The rule:** choose the mode before planning the edit, and commit to it.

- Talking head, one location, personal story → **single-take mode**. Cuts only where a sentence is removed. Zero cuts is a legitimate outcome.
- Voiceover over b-roll, a numbered list, a tutorial → **cut-driven mode**. Typical shot 1.3-2 s, and it *stays* there.

Never average the two.

---

## 4. Openings — measured

Restricting to the 32 cut-driven videos, since a single-take video has no opening cut by definition:

| | Time to first cut |
|---|---|
| p25 | 0.80 s |
| **median** | **2.22 s** |
| p75 | 4.00 s |

Across all 76 videos that have any cuts at all, the median is 4.33 s — pulled up by the single-take group.

### The counterintuitive part

Cuts falling in the first 3 seconds, compared against what that video's own average cut rate would predict:

> **median 0.75×** — the opening cuts **slower** than the video's own baseline.

And the first shot compared to a typical shot in the same video:

> **first shot = 1.58× the median shot length.** In 56% of cut-driven videos the opening shot is more than 1.2× a typical one.

In absolute terms: first shot **2.22 s** median, against a typical shot of **1.32 s**.

**The hook is held, not chopped.** This is the opposite of the "chop the first three seconds to grab attention" instinct. The opening shot stays on screen long enough for a person to read the on-screen hook and hear the spoken one — and *then* the video starts moving.

**What follows for the edit:**
1. Give the hook shot roughly **1.5× your typical shot length**. Do not cut into it to seem energetic.
2. Something should still *change* early — a zoom, a card, a movement. Held is not the same as static.
3. The hook is spoken **and** on screen simultaneously. Many viewers start muted, and 8 seconds is the whole budget (`kadev-personal-branding.md` §7.1).
4. No logo animation, no intro card. The corpus has none.

---

## 5. Closings — measured, and the strongest finding in the file

Gap from the last scene cut to the end of the video:

| | All 76 with cuts | Cut-driven 32 |
|---|---|---|
| p25 | 2.21 s | 1.15 s |
| **median** | **3.56 s** | **3.16 s** |
| p75 | 4.33 s | 4.09 s |

Cuts in the final 3 seconds versus the video's own baseline rate:

> **median 0.21×** — the closing cuts at roughly **one fifth** of the video's normal rate.

Last shot versus a typical shot in the same video:

> **last shot = 2.42× the median shot length.**
> **24 of 32 cut-driven videos (75%)** hold their final shot more than 1.2× longer than a typical one.

In absolute terms: last shot **3.16 s** median, against a typical shot of **1.32 s**.

**The ending is a landing, not a stop.** The final line is delivered on one held shot, with the cutting essentially switched off. This is consistent across three quarters of the corpus — the most consistent single behaviour measured.

**What follows for the edit:**
1. Give the closing line its own shot and **hold it ~2.4× your typical shot length** — around 3 seconds in a fast edit.
2. Stop cutting entirely for the last ~3 s. No flourish, no rapid montage over the CTA.
3. That held shot is where the Storytelling Hack's beat ⑤ lands — the line that reverses the opening (`kadev-script-formulas.md` §3). It needs room to be heard, because it is what makes the video loop.

### The shape, in one line

> **Hold the open · chop the middle · hold the close.**
> 1.58× — 1.0× — 2.42×

That is the measured grammar of this corpus. It is also, usefully, the exact shape a uniform automatic cutter will never produce.

---

## 6. Two things I got wrong, corrected

Both of these were written into `anti-ai-ish.md` before the timestamp measurement finished, on the strength of general short-form convention. Both were wrong for this corpus and have been corrected there. Recording them here because the wrong versions are widely believed.

**Wrong: "the first cut lands a median of 1.2 s in."**
That figure was the **p25**, misread as the median. The actual median is **2.22 s** for cut-driven videos and 4.33 s across the corpus. More importantly, the direction was wrong — openings cut *slower* than baseline (0.75×), not faster.

**Wrong: "ends on the last word, no tail — do not add a 2-second tail."**
The opposite is true here. The median final shot runs **3.16 s** and is **2.42× longer** than a typical shot, in 75% of cut-driven videos. The "tail" is not dead air; it is the held landing the closing line is delivered on. Cutting it off truncates the beat that makes the video loop.

The general advice these came from is not nonsense — it is aimed at padded, dead-air endings. But applied to this style it removes the single most consistent thing the corpus does.

---

## 7. What is *not* measured, and must not be asserted

Be honest with users about the boundary. The following were **not** measured and any claim about them is opinion:

- **Music** — presence, genre, loudness, ducking behaviour. No audio analysis was run.
- **Captions** — style, position, karaoke timing, font. Not detectable from scene cuts.
- **Zooms, speed ramps, transitions** — invisible to scene detection. The claim in `anti-ai-ish.md` §C4 that "cuts are hard cuts and flashy transitions appear at topic changes" is **inference from the ASL distribution, not measurement.** Flagged as such there.
- **Colour, grading, lighting** — most files are re-compressed 540×960; no valid conclusions available.
- **What is actually said** — no transcripts. Everything about script content comes from the Kadev course material, not from these videos.
- **Whether these videos actually performed well.** They are in a folder the user labelled as inspiring and viral. No view counts, no engagement data. Treat the corpus as "what this creator considers good", which is a real signal, not as verified top performers.

---

## 8. Applying it

| Decision | Setting |
|---|---|
| Aspect ratio | 9:16, always. 100% of the corpus. |
| Duration | 20-30 s **or** 60-90 s. Decide which. |
| Mode | cut-driven (ASL 1.3-2 s) **or** single-take (few cuts to none). Decide which. Never average. |
| Opening shot | ~1.5× your typical shot. Hold the hook. |
| Middle | stay in your chosen mode |
| Closing shot | ~2.4× your typical shot, ~3 s. Stop cutting. |
| Tail | keep it — it is the landing, not dead air |
| Longer video | cut *faster*, not slower |

Wired into `SKILL.md` Step 4 (mode choice) and `anti-ai-ish.md` §C (the gate).

## 9. What they *say*: openings and closings from the transcripts

§§2–8 measure the cutting. This section measures the words. All 80 reference videos were transcribed (faster-whisper `small`, `transcripts/reference/`). **76** have enough speech to count, i.e. 15+ words. Almost all are Kadafi Devayana's own shorts, so this describes **one successful creator's spoken grammar**, not Indonesian short-form in general. Median script length is **112 words** (p25 61, p75 200).

### 9.1 Counts

| Pattern | Videos | Share |
|---|---|---|
| Opens with a greeting (*halo, hai, balik lagi*) in the first 5 words | **0** | **0%** |
| Opens by announcing the video (*"di video ini…"*) | 2 | 3%. Both are tutorials, one of them by a different creator |
| First sentence addresses the viewer (*kamu / lu*) | 27 | 36% |
| A number in the first 20 words | 18 | 24% |
| Opens with *Ini… / Kalau… / Pakai…* (a demonstrative or conditional frame) | 27 | 36% |
| Closes by summarising (*jadi itulah, semoga bermanfaat, demikian*) | **0** | **0%** |
| Closes with a comment keyword → DM (*"ketik X, nanti aku kirim lewat DM"*) | 20 | 26% |
| Closes with an answerable question (*sepakat gak?, komen di bawah*) | 17 | 22% |
| Asks for a follow | 35 | 46% |
| Asks for a repost or share | 28 | 37% |

Counted with keyword regexes over the plain transcripts. Whisper mangles the sign-off (*"lipos kalau bermanfaat"* = *"repost kalau bermanfaat"*), so the regex accepts the common mishearings. Treat the counts as ±2.

### 9.2 The opening shapes that recur

Verbatim, lightly cleaned of transcription errors. Each is a **template**. Reusing the wording word-for-word is the fastest way to sound like a copy.

| Shape | Example |
|---|---|
| **Ini X, dan ini Y. Apa bedanya, dan kamu yang mana?** | *"Ini pencitraan, dan ini personal branding. Apa bedanya, dan kamu yang mana?"* (also: konten vs personal branding, bakat vs skill, hiburan vs edukasi, cringe vs yang ngatain cringe) |
| **The ladder**: *Kalau kamu A → B. Kalau A + C → D. …* | *"Kalau kamu ngonten, orang bakal notice kamu. Kalau ditambah niche, orang bakal kenal kamu. Kalau ada formula dan scripting, orang bakal follow kamu…"* |
| **Chant / repetition** (7–15 s shorts) | *"Sehari sekali. Seminggu sekali. Sebulan sekali."* Or one line said four times with rising energy |
| **Tunjuk list** | *"Pakai sound ini kalau konten kamu emotional. Pakai sound ini kalau edukasi…"* |
| **"Aku mau kamu nonton ini."** | Show a clip first, then *"Menurut kamu ada yang aneh? Ada."* |
| **A contrarian claim** | *"Jangan bangun followers, tapi bangun trust."* / *"Kalau aku lebih pilih bangun trust daripada sekadar viral."* |
| **A stranger's result** | *"Ada penjual kambing di Jawa Timur, followersnya tembus 100.000 cuma dalam 3 hari."* |
| **A famous-brand anomaly** | *"Ada brand yang logonya nempel di ketiak pemain World Cup 2026."* / *"Marvel dibangun dari nol banget."* |
| **Before → after** | *"Dulu kontenku sering sepi kayak gini. Sekarang bisa viral kayak gini."* |
| **The objection, in the viewer's voice** | *"Aku gak punya penghasilan karena susah cari kerja. Aku gak bisa investasi karena gajiku kecil."* |
| **A quiz with a wrong answer** | *"Juara 3 Piala Dunia 2018? Nggak inget kan? Aku nyebut Inggris juga kamu pasti percaya."* |

What's absent is as useful as what's there: no greeting, no *"pernahkah kamu"*, no *"di video kali ini aku akan…"*, and no statement of what the video is about.

### 9.3 The closing is two parts

The corpus shows a stable two-part close:

1. **One engagement move**, which is the real CTA. Either a comment keyword that triggers a DM freebie (*"Ketik SOUND, nanti aku kirim list lengkapnya lewat DM"*) or a question with two defensible answers (*"Viral dulu atau cuan dulu? Yuk diskusi di komen."*, *"Sepakat gak?"*).
2. **A fixed brand tagline**, the same words in every video: *"Repost kalau bermanfaat, dan follow untuk tips personal branding dan konten lainnya."* Sometimes it's an identity line instead: *"Aku Kadafi Devayana, teman kamu buat upgrade konten dan personal branding tiap hari."*

Part 2 has two asks (repost and follow), but it doesn't work as a stack of CTAs. It's a **signature**, recognisable because it never changes, and it tells the viewer the topic to follow for. The fault `anti-ai-ish.md` §B5 names (*"like, comment, share, save, dan follow!"*) is different: five **new** asks invented for this video, none of them tied to a topic.

**For the agent:** write exactly one engagement move per script. If the user has a fixed tagline, append it unchanged. If they don't, help them write one **once** and store it in the ledger's `notes` of their first entry. Never generate a fresh multi-ask sign-off per video.

### 9.4 What this adds to the gate
- Greeting in the first sentence: **reject**. 0 of 76 do it.
- Summary close: **reject**. 0 of 76 do it.
- Two or more *different* engagement moves (a keyword **and** a question **and** "save"): **reject**.
- No number, no *kamu*, no contrast frame and no named stranger in the first sentence: **warn**. The hook has none of the recurring shapes.

<!-- journal 2026-09-24: §9 added from transcripts. Before this, the skill knew how the corpus cuts but not what it says. The two-part close contradicted the site checker, which flagged any script with 2+ CTA words; the checker was changed to count *engagement moves*, not words. Caveat kept in the text: this is essentially one creator's style. -->

---

## Reproducing

Re-run §1 over the folder. Roughly 12 minutes for 82 files on the machine this was measured on. If you change the scene threshold, say so here and re-state every number that moves.
