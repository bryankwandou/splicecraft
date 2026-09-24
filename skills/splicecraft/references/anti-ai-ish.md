# Anti AI-ish: the rejection list

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Why this file exists:** community users complained that SpliceCraft's scripts and edits still *"berasa AI"*. This is the gate that catches it. Run it before delivering anything.
> **Editable:** every rule below carries its evidence. If you disagree with a rule, change it — but replace the evidence too. `<!-- journal -->` notes mark which rules are measured and which are judgement.

"AI-ish" is not a vibe. It is a short list of specific, nameable habits. Each one below is a habit, the reason it reads as machine-made, and the fix.

Two sources feed this file:
1. The course's own *"Contoh yang Salah"* and *"Yang Banyak Orang Lakukan"* slides (`kadev-personal-branding.md` §9.3, §8.1).
2. **Measurement of 82 real, well-performing reference videos** in `E:\Download\CONTOH INSPIRASI TEKNIK NGOTEN DAN EDITING VIDEO` — see `viral-edit-teardown.md` for the full numbers.

---

## A. The one that matters most

> **A script with no personal story is AI-ish, and no amount of editing fixes it.**

Element 5 of the 6 Script Hack Elements is *Personal Opinion / Story*. It is the only element a language model cannot supply, because it requires having lived something. Everything else in this file is secondary to it.

**The test:** point at the sentence in the script that could only have been written by this specific person. If you cannot find one, the script is AI-ish regardless of how good the hooks are.

**The rule for the agent:** if the user cannot give you a real story, a real number, or a real opinion — **stop and ask**. Do not write a plausible-sounding one. An invented anecdote is the worst possible failure here, because it is both AI-ish *and* dishonest.

---

## B. Script-level tells

### B1. The opening sentence

| ❌ Reject | Why | ✅ Instead |
|---|---|---|
| *"Halo guys, balik lagi di channel aku"* | 2 seconds of nothing. The viewer gives you 8. | Start on the hook. No greeting at all. |
| *"Di video kali ini aku akan membahas tentang…"* | Announcing the video instead of starting it. The single most AI-ish sentence in Indonesian video. | The hook *is* the first sentence. |
| *"Pernahkah kamu bertanya-tanya…"* | Formal register nobody speaks in. | *"Pernah gak sih kamu…"* |
| *"Sebelum kita mulai, jangan lupa follow"* | CTA before value. Trains people to scroll. | CTA at the end, once. |

**Measured:** in the reference set the opening shot is **held** — median 2.22 s in cut-driven videos, which is 1.58× a typical shot in the same video. There is no greeting because the held shot is spending its time on the hook itself, not on a wind-up. See §C2.

### B2. Vagueness where a number belongs

| ❌ | ✅ |
|---|---|
| "beberapa cara" | "3 cara" |
| "cukup lama" | "4 tahun" |
| "banyak orang" | "7 dari 10 orang" |
| "hasilnya lumayan" | "12 juta di bulan pertama" |

Vagueness is what a model produces when it does not know the fact. It is also what a person produces when they are hiding that they do not know. Both read the same. **If the number is not known, do not gesture at it — cut the claim.**

Every example in the source PDF uses **3, 4, or 5**. Odd, small, specific.

### B3. Register drift into formal Indonesian

The source material is written in casual Indonesian and so is the market. Formal Indonesian in a TikTok script is a machine tell.

| ❌ Formal | ✅ Spoken |
|---|---|
| Anda | kamu / lu / kalian |
| tidak | gak / nggak |
| sangat penting | penting banget |
| melakukan | ngelakuin |
| memberikan | ngasih |
| oleh karena itu | makanya |
| dapat meningkatkan | bisa naikin |

Exception: a B2B or LinkedIn brief may legitimately want formal register. The brief decides. The *default* is spoken.

**"Kalian" → "kamu" / "kita".** Kadev's rule for spoken scripts (`kadev-live-mentoring.md` §8.2): *kalian* sounds like a teacher addressing a class, and a Gen Z viewer feels judged. Speak to one person. *Kalian* is acceptable only when an older speaker deliberately addresses a younger group.

### B4. LLM sentence architecture

These are structural, not lexical, and they survive translation — which is why they are the hardest to spot.

- **Adjective triads.** *"efektif, efisien, dan optimal"*. Real speech uses one adjective, or none.
- **Balanced antithesis.** *"Bukan hanya X, tetapi juga Y."* Occasionally fine. Twice in one script is a tell.
- **The summarising close.** *"Jadi, itulah beberapa tips yang bisa kamu terapkan."* Nobody says this out loud. Real closes reverse the opening instead (see §C3).
- **Uniform sentence length.** Every sentence 12-18 words. Real speech alternates: a long one, then three words.
- **Hedging stacks.** *"mungkin bisa jadi salah satu cara yang cukup membantu"*. Four hedges, zero claims.
- **Listing without ranking.** Five items of equal weight and no opinion about which matters. The source material always says *"nomer 3 paling penting!"*

<!-- journal: B4 is judgement, not measurement — derived from reading the source scripts against typical LLM output, not from a corpus study. It is the least evidenced section here and the most likely to need revision. If someone later transcribes the 82 reference videos, this section should be rewritten against that data. -->

### B5. The CTA

| ❌ | Why | ✅ |
|---|---|---|
| *"Semoga bermanfaat ya!"* | a sign-off, not a call to action | ask something answerable |
| *"Jangan lupa like, comment, share, save, dan follow!"* | five asks = zero asks | one ask |
| *"Follow untuk konten menarik lainnya"* | no reason given | *"Follow kalau kamu lagi bangun personal branding dari nol"* — names the tribe |

The course's own model CTA: *"Menurut kalian gimana? Kira-kira mic profesional bisa diganti sama AI ini? Beri tahu pendapat kalian di kolom komentar."* — a real question, with two defensible answers.

Element 6 is **Interactions**. A CTA that cannot be answered in a comment is not a CTA.

**Measured refinement (transcripts, `viral-edit-teardown.md` §9.3):** the reference corpus closes in two parts: **one** engagement move (a comment keyword → DM, or an answerable question), then a **fixed brand tagline** that is identical in every video (*"Repost kalau bermanfaat, dan follow untuk tips personal branding dan konten lainnya"*). The tagline is a signature, not a stack. What stays forbidden is several *different* asks written fresh for this video. 0 of 76 reference videos end on *"semoga bermanfaat"* or a summary.

---

## C. Edit-level tells

This section is measured. All numbers come from the 82-video reference set; method and full distribution in `viral-edit-teardown.md`.

### C1. Uniform cutting is the giveaway

The single clearest finding from the measurement:

> **Real edits are bimodal. AI-ish edits are uniform.**

| Mode | Average shot length | Share of the 82 videos | What it is |
|---|---|---|---|
| **Cut-driven** | 0.5 - 2.5 s | 32 videos (39%) | b-roll, documentation, voiceover, jedag-jedug |
| *(the dead zone)* | 2.5 - 8 s | 27 videos (33%) | mixed / transitional |
| **Single-take** | 8 s - no cuts at all | 23 videos (28%) | talking head, straight to camera |

**Six of the 82 videos have zero scene cuts across 18-46 seconds.** They perform. They are not under-edited — they are a different grammar: one take, one person, captions and nothing else.

The AI-ish failure is landing in the middle by default: a cut every 3-4 seconds for the whole video, regardless of what is being said. That is the rhythm nobody chooses on purpose. It is the rhythm you get when a tool applies a uniform rule.

**The rule:** decide which mode the video is in *before* planning the edit, and commit.
- Talking head, one location, personal story → **single-take mode**. Cuts only where a sentence is removed. Possibly zero cuts.
- Voiceover over b-roll, a list, a tutorial → **cut-driven mode**. Median shot 1.5-2 s, and it stays there.

Never average the two.

<!-- journal: measured 2026-09-23 with ffmpeg scene detection (scale=160, select='gt(scene,0.3)') over all 82 files. Threshold 0.3 is conventional but not tuned; it will under-count cuts between visually similar shots (e.g. two angles of the same person against the same wall), so the single-take bucket may be slightly overstated. The bimodality is far too strong to be a threshold artifact. Raw per-file data in the session scratchpad, not committed. -->

### C2. Openings

Measured on the reference set — and this one is **counterintuitive**, so read it before applying the usual advice:

- Median time to the **first cut** in cut-driven videos: **2.22 s** (p25 0.80 s, p75 4.00 s).
- Cuts landing in the first 3 s, against that video's own average rate: **0.75×**. The opening cuts **slower** than the video's baseline.
- The **first shot is 1.58× longer** than a typical shot in the same video. 56% of cut-driven videos hold it more than 1.2× as long.
- Median video length: **37.5 s**, bimodal — a cluster at **20-30 s** (24 videos) and a second at **60-90 s** (17 videos), with a dip between.

> **The hook is held, not chopped.**

This contradicts the common "chop the first three seconds to grab attention" instinct. The opening shot stays up long enough to read the on-screen hook and hear the spoken one, *then* the video starts moving.

**What this means for the opening:**
1. Give the hook shot about **1.5× your typical shot length**. Do not cut into it to seem energetic.
2. Something should still *change* early — a zoom, a card, a movement. Held is not the same as static.
3. The hook is *spoken* and *on screen* simultaneously. Many viewers start muted.
4. No logo animation. No "intro". The reference set has none.

### C3. Closings

The course's Storytelling Hack beat ⑤ is *"Wrap It Up with a Relatable Message"* — and in the worked example, beat ⑤ **reverses** beat ①:

> ① *"Networking itu gila, bisa bikin kita sukses dan kaya raya"*
> ⑤ *"networking bukan seberapa banyak orang yang kamu kenal, tapi seberapa banyak orang yang pengen kenal kamu."*

That reversal is what makes a short loop: the viewer re-watches to check whether the opening already contained the ending. Rewatch and loop rate are ranking signals on every platform.

**Measured — and this is the most consistent single behaviour in the whole corpus:**

- Gap from the **last cut to the end**: median **3.16 s** in cut-driven videos.
- Cuts in the final 3 s against that video's own rate: **0.21×**. The closing cuts at about **one fifth** of normal.
- The **last shot is 2.42× longer** than a typical shot. **24 of 32 cut-driven videos (75%)** hold it more than 1.2× as long.

> **The ending is a landing, not a stop.**

The closing line gets its own held shot with the cutting switched off. That held shot is where beat ⑤ lands, and it needs room to be heard — it is what makes the video loop.

| ❌ AI-ish close | ✅ |
|---|---|
| summarises what was just said | reverses or reframes the opening claim |
| trails off | lands on a short sentence |
| stacks five CTAs | one question |
| keeps cutting over the CTA | stops cutting for the last ~3 s |
| hard-stops on the last syllable | holds the final shot ~2.4× a typical shot |

**Correction.** An earlier draft of this file said *"do not add a 2-second tail; the video ends on the last syllable."* The measurement says the opposite, and it has been corrected here. That advice is aimed at padded dead-air endings, which is a real fault — but in this style the held final shot is not dead air, it is the beat the closing line is delivered on. Cutting it off removes the loop. Full numbers and the correction record: `viral-edit-teardown.md` §5-6.

### C4. Over-editing

Straight from the course's *"Contoh yang Salah"*:

> 🚫 **Editing Berlebihan / Minim Editing**
> - Terlalu banyak efek & transition, bikin pusing
> - Nggak ada subtitle, orang nggak ngerti kalau nonton tanpa suara
> - Musik terlalu kencang sampai nutupin suara

SpliceCraft's existing guards already encode this and they should not be relaxed:
- **breathing_room** gate: at least 35% of runtime with no card on screen.
- **no_card_overlap**: never two cards at once.
- **card_density** ceiling per level.
- Music sits under the voice; if you can hear music over a word, it is too loud.

Add one rule: **transitions are not decoration.** Use them at moments of *topic change*, not between every shot.

<!-- journal: the transition rule is INFERENCE, not measurement. Scene detection cannot see transitions, speed ramps or zooms - it only reports cuts. The rule is derived from the ASL distribution plus the course's own "terlalu banyak efek & transition, bikin pusing" slide. Do not present it to a user as measured. See viral-edit-teardown.md §7. -->

### C5. Production faults that no edit repairs

From *"Contoh yang Salah"* — check these on the source file before planning anything:

| Fault | Check |
|---|---|
| **Cahaya buruk** — video gelap, wajah nggak kelihatan; backlight parah, muka jadi siluet | look at the contact sheet |
| **Suara nggak jelas** — noise (angin, kendaraan, orang ngobrol); ngomong terlalu pelan / jauh dari mic | listen; check the transcript's confidence |
| **Format salah** — horizontal footage for TikTok/Reels (terpotong); vertical for long YouTube | `$SC probe` reports orientation |
| **Mata nggak fokus** — ngeliatin layar HP, bukan kamera | visible on the sheet |
| **Kamera terlalu rendah** — double chin | visible on the sheet |

If one of these is present, **say so plainly and recommend a reshoot.** Silently "fixing" bad footage with heavy grading and zooms is itself an AI-ish move — it produces a video that looks processed rather than shot.

---

## D. Content-level tells

### D1. Repetition across the account

This is why the content ledger exists (`content-memory.md`).

The failure: an AI asked for "content ideas about personal branding" produces the same twelve ideas every time. Over a month that becomes an account that says one thing twelve ways. The course names the symptom — *"orang gak inget dan gak percaya sama kamu"* — but blames inconsistency; the modern version of the problem is the opposite, **sameness**.

**Rule:** run `ledger check` before writing. Exit code 2 means do not write it.

### D2. Writing to "everyone"

> **Niche bukan topik, tapi siapa secara spesifik.**

A script addressed to "content creators" is AI-ish. A script addressed to *"editor pemula yang baru pake CapCut dan videonya masih sepi"* is not. The 4K Method (`kadev-personal-branding.md` §6.6) exists to produce that sentence.

### D3. Pillar monoculture

Four pillars: Educate, Inspiration, Entertaining, Promotion. An account that is 100% Educate reads like a knowledge base, not a person. `ledger stats` shows the balance; `ledger suggest` names what is due.

Same for the **80/15/5** ratio — superniche / adjacent / personal life. *"Bahas yang lain agar terlihat manusiawi."*

### D4. Borrowed authority

*"Cuma bilang 'Saya bisa ini, saya jago itu' tanpa bukti nyata"* · *"Upload sertifikat doang tanpa konteks"* · *"Pamer doang tanpa value"*.

The fix from the same slide: **tunjukin proses kerja, bukan cuma hasil akhir.** Process footage is inherently un-fakeable, which is exactly why it reads as human.

---

## E. The gate

Run this before delivering. Any ❌ blocks delivery until fixed or explicitly waived by the user.

```
SCRIPT
  [ ] there is a sentence only this person could have written   (§A)
  [ ] no greeting, no "di video kali ini"                        (§B1)
  [ ] every vague quantity is either a real number or cut        (§B2)
  [ ] register is spoken Indonesian, unless the brief says else  (§B3)
  [ ] no adjective triads, no summarising close                  (§B4)
  [ ] exactly one CTA, and it is answerable                      (§B5)
  [ ] every factual claim confirmed by the user                  (§A)

EDIT
  [ ] mode chosen on purpose: cut-driven OR single-take          (§C1)
  [ ] shot rhythm stays in that mode, no drift to the middle     (§C1)
  [ ] opening shot HELD ~1.5x a typical shot                     (§C2)
  [ ] hook is spoken AND on screen                               (§C2)
  [ ] closing reverses the opening                               (§C3)
  [ ] final shot HELD ~2.4x a typical shot, cutting stops        (§C3)
  [ ] 9:16 vertical                                              (teardown §2)
  [ ] duration is 20-30 s OR 60-90 s on purpose                  (teardown §2)
  [ ] QA gates pass: breathing_room, no_card_overlap, density    (§C4)
  [ ] production faults named honestly, not hidden               (§C5)

CONTENT
  [ ] ledger check run, exit code 0                              (§D1)
  [ ] audience named as a specific WHO                           (§D2)
  [ ] pillar chosen, and not the same as the last three          (§D3)
  [ ] claims backed by process, not assertion                    (§D4)
```

---

## F. What this file does not claim

- These rules are tuned for **Indonesian short-form video** for a personal brand. A B2B English explainer wants different defaults; use `script-and-marketing.md`.
- The C-section numbers describe **82 videos from one reference folder**, most of them from a single creator. They are a strong signal about *this* style, not a universal law of short video. Treat them as "what good looks like in this lane."
- Nothing here guarantees reach. It removes the specific failure the community named. That is all.
