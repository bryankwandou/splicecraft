# SpliceCraft journal

Why things are the way they are, what was measured versus guessed, and what to fix next. Every reference file in `skills/splicecraft/references/` also carries inline `<!-- journal -->` notes at the paragraph level; this file is the session-level record.

Newest entry first.

---

## 2026-09-24: all videos transcribed; mentoring layer added; spoken-grammar measured

### Transcription (open item 1 from 2026-09-23, closed)
- **Kadev folder:** 49 video files, 4 of them byte-identical duplicates, so **45 unique**, and all 45 are transcribed. The 38 lessons and short videos ran locally (faster-whisper `small`, int8, CPU). The 7 long VIP mentoring recordings (1h40–2h15 each) went to **Groq whisper-large-v3**. Each one took 2–4 minutes on Groq, against 1–5 hours locally.
- **Reference folder:** 80 of 82 transcribed. 76 have 15+ words of speech. The rest are music-only.
- `tools/transcribe_groq.py` now cuts audio into **20-minute chunks** before upload, because Groq rejects files over 25 MB and a 2-hour mp3 at 32 kbps is about 29 MB. Segment timestamps are offset per chunk. It needs `GROQ_API_KEY` set in the environment. The key is never written to the repo.
- Two local workers had been started on the same folder by accident. One was killed.
- Local faster-whisper **looped for hours** on two lessons, `(3.2 6)` at 19,967 s and `(4 2) (1)` at 14,072 s, even with the time-budget guard. The guard checks elapsed time between segments, not inside a hung segment. For long files, use Groq.

### New: `references/kadev-live-mentoring.md` (~580 lines)
It's built from transcripts, not slides, and has 14 sections: the 16 formats, PAS + Storytelling Arc with worked sales scripts, a table of 14 real account diagnoses, attention economy / six emotions / thesis+arguments / outer-inner circle, TOFU-MOFU-BOFU and test→win→replicate, Trial Reels and Link Reels, "the niche is you" plus six income streams, the Art of Yapping, lesson-only additions (success vs failure, LinkedIn, the CapCut order), Rich's 10k-in-3-weeks experiment, business branding and archetypes, networking, the anatomy of a viral format (with an SFX map), and agent rules. The provenance table maps each section to its recording.

**Tensions recorded, not hidden:**
- *Superniche* (slides §6.2) vs *"niche itu gak penting, kamu nichenya"* (Dec 2025 mentoring). Reconciled in §7.1: keep an umbrella (a message plus 1–2 pillars) and a specific audience, define yourself by the message rather than a topic label, and always include a story pillar.
- 80/15/5 (slides) vs **50/50 outer/inner circle** (Oct 2025). They measure different things. Explained in §4.4.
- Slide order of the six hack elements vs Nadif's spoken order. Same six, and the slide says order doesn't matter. No change.
- Unsourced statistics are flagged in place: 75% of UMKM failing by year 3, "7 of 10 HR" background checks, and the earlier 74/63/62% from 2026-09-23.

### New: spoken grammar of the reference corpus (`viral-edit-teardown.md` §9)
The skill measured how the 82 references **cut**, but not what they **say**. Now measured across 76 transcripts:
- **0 of 76** open with a greeting. **0 of 76** close with a summary or *"semoga bermanfaat"*.
- 36% address *kamu* in the first sentence, 36% open on an *Ini… / Kalau… / Pakai…* frame, and 24% have a number in the first 20 words.
- The close has two parts: **one** engagement move (26% comment keyword → DM, 22% question), then a **fixed brand tagline** (46% ask for a follow, 37% for a repost).
- Caveat stated in the file: this corpus is essentially one creator's style.

**This contradicted the site checker**, which flagged any script with 2+ distinct CTA words, so Kadev's own sign-off failed it. The checker now counts *engagement moves* (keyword→DM, question, save, tag-a-friend) and flags 2+ moves or 4+ CTA words. `anti-ai-ish.md` §B5 got the same refinement.

### New rules wired in
- `anti-ai-ish.md` §B3: **"kalian" → "kamu/kita"** (Art of Yapping: Gen Z hears *kalian* as being lectured). Also added to the site checker, along with a *welcome back / izinin aku* rule.
- `SKILL.md` 0.5b now requires a **source for the idea**, a **format** and a **funnel stage** before writing. 0.5d adds PAS for selling scripts and thesis+arguments for opinion scripts. 0.5f logs `--format --funnel --source`.
- `ledger.py`: new fields `funnel` (tofu/mofu/bofu, validated) and `source`, plus a named `FORMATS` list (free text still accepted, with a warning). `stats` shows format and funnel mix. `suggest` lists untried formats and warns when none of the recent pieces is TOFU. `add` nudges for `--source` when it's missing. `§` was removed from CLI output because the Windows console mangles it.
- Site: branding tabs **PAS**, **Funnel** and **16 formats** added. Hack element 5 relabelled "Opinion / story" to match the slide.

### Verified
- `python tests/test_plan.py` → OK. `test_every_doc_is_dated` first failed on the new file, and a `Published:` line was added.
- Ledger exercised: `add` with and without `--source`, an unknown format warns, `stats` shows FORMAT and FUNNEL, `suggest` lists untried formats, `edit --set funnel=tofu` writes the value.
- Playwright against a local server: tells 8 → 0 on the human sample, ledger 90/33/0%, 6 hack cards, range slider, Indonesian toggle, no horizontal scroll at 375 px, no JS errors.

### Not done, and why
- **Nothing was pushed or deployed this session.** The course folder contains `Copyright - Hak Cipta © 2025 Kadev Academy.docx`: *"Dilarang keras untuk menduplikasi, mendistribusikan… Produk ini hanya untuk penggunaan pribadi pembeli yang sah."* The GitHub repo is **public**, and commit `ad2b9f3` already published `site/MEGA-SKILL.md` with the Kadev extracts, served at splicecraft.vercel.app/MEGA-SKILL.md. Publishing more of it needs the owner's decision. Options are listed in the chat record for 2026-09-24.
- Not every one of the 38 lesson transcripts was read line by line against the slides. Lessons that looked slide-only by title were spot-checked (1.3, 3.1.2, 3.1.6, 3.2.6) and confirmed to narrate the slides, with the additions captured in §9. The rest are in `transcripts/kadev/` for anyone who wants to check.
- The ledger thresholds still haven't been tuned against a real 50+ entry ledger.

### Open items
1. Owner decision on public vs private for the Kadev-derived material (see above).
2. Tune `WARN_AT`/`BLOCK_AT` against a real ledger.
3. Wire `ledger check` into `splicecraft.py script` so an agent can't skip it.
4. Series awareness in `ledger check`: currently a planned part 2 is flagged like a repeat.

---


## 2026-09-23 (later) — cold-agent test with Sonnet and Haiku; offline transcription started

### Test
Sonnet and Haiku were each given only the skill folder (no JOURNAL, no MEGA-SKILL, no chat context) and five scenarios: a bare "bikinin script" request, a follow-up with real facts, a repeat request, an editing question, and a quiz.

| | Sonnet | Haiku |
|---|---|---|
| S1 stops and asks for premis / real story instead of inventing one | yes | yes |
| S2 script passes the anti-AI-ish gate, logged to ledger | yes | yes |
| S3 repeat request blocked | **yes, exit 2 (67%)** | **no — "clear" 44%** |
| S4 single-take talking head advice | correct | applied cut-driven ratios to a single-take video |
| S5 quiz | all correct | all correct; one overclaim ("the middle is death") |

### Bug found: the ledger depended on how the agent phrased things
Haiku logged the topic as *"Dokumentasi naik IPK pakai Pomodoro"* and checked *"jadwal belajar pomodoro buat naikin IPK mahasiswa"* without `--theme`. Same video, scored 44%. Sonnet happened to reuse the words and pass themes, so it blocked. A safety check that works only for the careful agent is not a safety check.

Fix: `theme_coverage()` in `ledger.py` — the stored entry's theme tags are matched against the probe text itself. All of 3+ tags hit → 0.90 (block); 2 of 3 → 0.60 (warn); a single tag → 0.30, so one broad tag like "mahasiswa" cannot block everything. Verified: Haiku's repeat → exit 2; "pomodoro buat freelancer desain" → exit 0; Sonnet store still exit 2; `tests/test_plan.py` OK.

### Doc fixes from the critiques
- SKILL.md 0.5a: always pass `--theme` on `check`; a blocked idea is still logged `--status idea` (Sonnet found this only in a different section).
- SKILL.md Step 4: the 1.58×/2.42× ratios are for cut-driven mode; do not add cuts to a talking head to manufacture the shape (Haiku's error).
- kadev-personal-branding.md: jump table at the top so small models read one section, not 1,000 lines (Sonnet's cost complaint).

### Not fixed, noted
- Step 1's genre detection needs a transcript before the transcription step (Sonnet: circular for small models).
- No worked example of 0.5c revenue math.

### Transcription
The main gap from the entry below is being closed offline: `tools/transcribe_local.py` (faster-whisper `small`, int8, CPU, no API, resumable, skips byte-identical duplicates) runs over the 82 reference videos, 36 lessons and 13 mentoring recordings (not 2 — the folder holds 13). About 27 h of unique audio at ~1.9× realtime. Output in `transcripts/`. Reconciliation into the theory files follows when it finishes.

---

## 2026-09-23 — Kadev Academy extraction, anti-AI-ish gate, content ledger

### What was asked

Four things:
1. Extract *all* of `E:\Download\kadev academy` into executable skill documentation, with complete personal-branding theory.
2. Also extract `E:\Download\SLIDE PPT KADEV` — noted by the user as containing the more complete core material than the videos.
3. Learn editing, opening and closing technique from `E:\Download\CONTOH INSPIRASI TEKNIK NGOTEN DAN EDITING VIDEO`, so community users stop reporting that scripts and edits feel AI-ish.
4. Give SpliceCraft a persistent local memory of scripts, niches and themes already produced, so the AI stops repeating itself.

### What was added

| File | What it is |
|---|---|
| `references/kadev-personal-branding.md` | the full theory: 6-chapter curriculum, Ikigai, Johari, SWOT→Premis→PMF, Perception/Persona, Circle of Control, Golden Circle, Opportunity Mapping, superniche, 80/15/5, Perfect Niche, 4K Method, Sweet Spot, First Impression, Brand Pillar, Hirarki Konten, documentation, survival, evaluation, monetisation, PING, LinkedIn |
| `references/kadev-script-formulas.md` | 20 hooks, 6 Script Hack Elements, Storytelling Hack, Hook/Body/CTA, Content Idea Framework, length budgets, writing pass |
| `references/anti-ai-ish.md` | the rejection list and the delivery gate |
| `references/viral-edit-teardown.md` | measurements from all 82 reference videos |
| `references/content-memory.md` | how the ledger works |
| `scripts/ledger.py` | the ledger tool |
| `JOURNAL.md` | this file |

`SKILL.md` was rewired so the ledger check and the anti-AI-ish gate are mandatory steps rather than optional reading.

### What was actually extracted, and what was not

**Fully extracted.** All 64 slide screens in `SLIDE PPT KADEV`, read individually. Each screen holds roughly 6 slides, so this is on the order of 380 slides. This was the highest-yield source by a wide margin and the user was right that it is more complete than the videos — several core frameworks (**Premis / Personal Market Fit**, the **4K Method**, the **6 Script Hack Elements**, **80/15/5**, **Perfect Niche**, **Money Making Potential**, the **superniche ladder**) appear *only* in the slides and in none of the PDFs.

**Fully extracted.** The text-bearing PDFs in `kadev academy`:
- `02 - Personal Branding Mengubahmu eBook.pdf` — 100 pp
- `04 - Content Creator Strategy.pdf` — 53 pp
- `03 - Content Cheat (Hook Writing).pdf` — 9 pp, all 20 hooks verbatim
- `06 - Content Creator Blueprint.pdf` — 8 pp
- plus the CV / cover-letter / student-leadership PDFs, which are out of scope for a video skill and were read but not incorporated

**Not extracted — and this is the main gap.** The 37 lesson videos and 2 live-mentoring recordings in `kadev academy` contributed only their filenames, which fixed the chapter ordering. No transcription backend was available: `GROQ_API_KEY` was unset and `faster-whisper` was not installed. The slides and PDFs are the author's own written version of the same lessons, so the loss is smaller than it looks, but it is real.

> **Next session, if a transcription key exists:** run over `E:\Download\kadev academy\*.mp4`. Prioritise the two live-mentoring files — `22 Juli 2026 - Topik Format Winning` and `27 Agustus 2026 - Formula Script Viral & Jualan` — because their titles suggest material that is in neither the slides nor the PDFs. Then reconcile against `kadev-personal-branding.md` and `kadev-script-formulas.md`.

**Four PDFs are link-only landing pages** with no content: `01 - Viral Script Generator`, `05 - 100+ Template Portfolio`, `07 - Personal Branding Builder V1`, `08 - Linkedin Post Generator`. Each is a cover plus a "Klik Disini" link to kadevacademy.com. Nothing was lost by not following the links, but note that the *Viral Script Generator* behind that link is likely a real tool worth looking at.

### The reference videos were measured, not watched

82 videos. Claude cannot watch video, so instead of guessing at "editing technique", the files were measured directly with `ffprobe` and `ffmpeg` scene detection. Method and full numbers are in `viral-edit-teardown.md`.

The finding that changed the design:

> **Real edits are bimodal. AI-ish edits are uniform.**

Average shot length across the 82 splits into a fast cluster (0.5–2.5 s, 39% of videos) and a slow cluster (8 s to literally zero cuts, 28%), with a thinner middle. Six videos have **no scene cuts at all** across 18–46 seconds and work fine. The AI-ish failure is defaulting to the middle — a cut every 3–4 seconds regardless of content — which is the rhythm nobody chooses deliberately.

Duration is bimodal too: a cluster at 20–30 s and a second at 60–90 s, dipping in between. Median 37.5 s.

This is now rule §C1 of `anti-ai-ish.md` and it is the most defensible thing in the whole delivery, because it is measured rather than asserted.

### The openings and closings measurement — and two claims I got wrong

A second pass extracted every cut *timestamp*, not just the count, which made opening and closing behaviour measurable. The result contradicted two things I had already written into `anti-ai-ish.md` on the strength of general short-form convention. Both were wrong for this corpus, both are corrected there, and the correction is recorded in `viral-edit-teardown.md` §6.

**Wrong claim 1: "the first cut lands a median of 1.2 s in."** That number was the **p25**, misread as the median. The real median is **2.22 s** for cut-driven videos, 4.33 s across the corpus. And the direction was backwards: cuts in the first 3 s land at **0.75×** the video's own average rate. Openings cut *slower*, not faster. The first shot is **1.58×** a typical shot.

**Wrong claim 2: "ends on the last word, no tail — do not add a 2-second tail."** The opposite. Median final shot is **3.16 s**, which is **2.42× a typical shot**, and **24 of 32** cut-driven videos (75%) hold it more than 1.2× as long. Cuts in the last 3 s run at **0.21×** — cutting essentially stops. The tail is not dead air; it is the held landing the closing line is delivered on, and it is what makes the video loop.

The measured grammar is:

> **Hold the open (1.58×) · chop the middle (1.32 s typical) · hold the close (2.42×).**

Which is, usefully, the exact shape a uniform automatic cutter will never produce. This is now in `SKILL.md` Step 4 and `anti-ai-ish.md` §C2-C3.

Worth recording plainly: the wrong versions were written from general convention *before* the data arrived, and they sounded right. The 1.2 s figure in particular came from misreading a quartile. Both would have made SpliceCraft's edits worse in a specific, measurable way — trimming the held ending removes the single most consistent behaviour in the corpus.

**Caveats on the measurement**, stated plainly: scene threshold 0.3 is conventional but untuned, and it will under-count cuts between visually similar shots — two angles of the same person against the same wall read as one shot. So the single-take bucket may be slightly overstated. The bimodality is far too strong to be a threshold artifact. Also: 53 of the 82 files are 540×960, i.e. re-compressed downloads rather than masters, which does not affect cut detection but does mean no useful conclusions about grading or grain.

### Decisions worth recording

**The theory file is long and stays long.** `kadev-personal-branding.md` is ~1,100 lines. The temptation is to compress it into a cheat sheet. Resisted: the user asked for *selengkap mungkin*, and the premis examples in §2.4 in particular lose their usefulness when paraphrased — their value is in the exact shape of the sentences. If it ever must be trimmed, cut §13.3 (LinkedIn) first; it is the least relevant to video.

**Indonesian was kept verbatim.** Hooks, premis examples, 4K sweet spots and quotes are reproduced in the original casual Indonesian. Translating them into formal Indonesian or English would destroy the register, and register is half of what makes a script not read as machine-written. This is stated explicitly at the top of `kadev-script-formulas.md`.

**Hook/Body/CTA was demoted, not deleted.** One slide marks it with a red ❌ and says *"jangan gunakan ini doang"* — "don't use only this". It is a necessary skeleton, not a sufficient structure. The two frameworks layered on top are the 6 Script Hack Elements (what must be present) and the Storytelling Hack (what order it moves in).

**Element 5 — Personal Opinion / Story — was promoted to the top rule.** It is the only one of the six an LLM cannot supply, because it requires having lived something. `anti-ai-ish.md` §A makes it rule zero, and `SKILL.md` makes "stop and ask rather than invent a story" a hard rule. This is the single highest-leverage change in the delivery.

**The beat→element mapping table is inference, not source.** The two frameworks appear on adjacent slides and one slide shows both diagrams stacked, so they are clearly meant to be used together — but the explicit mapping and the second-column timings in `kadev-script-formulas.md` §3.2 are mine. Flagged inline so a future editor does not mistake it for the author's.

**The ledger is stdlib-only and offline.** Matches the existing `splicecraft.py` constraint. The cost is that similarity is lexical, not semantic: *"cara berhenti menunda pekerjaan"* and *"stop prokrastinasi"* mean the same thing and share no tokens. The `--theme` tags bridge this, which is why `SKILL.md` tells the agent to always pass themes. An embedding check would fix it properly and is the first thing to upgrade if the offline constraint is ever relaxed.

### A bug found and fixed during the build

The ledger's first similarity implementation used Jaccard on both unigrams and bigrams, weighted toward bigrams. It was tested against a constructed near-duplicate:

- stored: *"3 cara stop prokrastinasi buat mahasiswa"*
- probe: *"3 langkah biar gak prokrastinasi lagi untuk mahasiswa"*

These are plainly the same video. It scored **25% — "clear"**. A false negative on exactly the case the tool exists to catch.

Two causes. Jaccard punishes the short side: a five-word probe compared against an entry that also carries a hook, an angle and themes scores low purely because the union is large. And the distinctive angle string (*"pakai timer fisik bukan app"*) diluted the topic collision.

Fixed by (a) switching unigrams to the overlap coefficient `|A∩B| / min(|A|,|B|)`, which asks "is the smaller of these already contained in the other?", and (b) scoring topic-level and full-text separately and taking the **max** rather than a blend, so a strong subject collision cannot be averaged away by a distinctive angle. Re-tested: near-duplicate → BLOCK, verbatim rewrite → BLOCK, unrelated topic → CLEAR, exit codes 2/2/0.

Worth recording because the original approach looked reasonable and was silently wrong.

### A second bug: `edit --set` accepted anything

`cmd_edit` wrote whatever key it was given straight onto the entry. `--set video-path=x` (hyphen, matching the CLI flag name rather than the JSON field) silently created a junk `video-path` key while the real `video_path` stayed stale. The command printed "updated" and had done nothing useful. Found while writing the Step 7 example in `SKILL.md`, where I made exactly that typo.

Fixed with an `EDITABLE_FIELDS` allowlist that rejects unknown keys and names the valid ones, plus validation for `pillar` (must be one of the four) and `seconds` (must parse as a number). All three now exit 1 with a message instead of corrupting the entry.

### Other things fixed in passing

- Em-dashes and middots in `ledger.py`'s printed output rendered as `?` on the Windows console (cp1252). Replaced with ASCII in printed strings only; source comments keep their typography.
- `ledger themes` showed both `prokrastinasi` and `prokrastinas` — the crude stemmer strips a trailing `i`. Stemming is now off for the themes display and on for scoring, which is the right split.
- `kamu` and `setiap` appeared twice in the `STOPWORDS` set. Harmless in a set, but flagged by the linter; deduplicated. 158 stopwords.

### Verified

21 of 21 checks pass. `ledger.py` parses (AST) and every subcommand was exercised end to end:

- `init`, `add`, `list`, `list --json`, `list --pillar`, `show`, `stats`, `themes`, `suggest`, `export --format md`, `export --format csv`, `remove`
- `check` in all three verdicts with the correct exit codes: near-duplicate → 2, verbatim rewrite → 2, unrelated topic → 0
- `edit --set` with a valid field → 0 and the value actually written; with a hyphen typo, a bad pillar, and a non-numeric `seconds` → all rejected with exit 1
- `show` with a missing id → exit 1; a hand-corrupted JSON store → exit 1 with a message naming the file, not a silent reset

- The existing suite still passes: `python tests/test_plan.py` → **26 tests, OK**. `splicecraft.py` was not modified, but the suite was run to confirm nothing regressed.
- `MEGA-SKILL.md` regenerated with `python tools/build_mega.py` → 7,098 lines, 302 KB, 19 references. Both copies (root and `site/`) verified identical, and the five new references verified present inside the bundle.

### One more change: bundle ordering

`tools/build_mega.py` auto-appends any reference not listed in `ORDER`, so the five new files would have landed at the very end, after the codec notes. Moved them to the front of `ORDER` instead — `anti-ai-ish.md` first, then the two Kadev files, the teardown, and the ledger guide. A reader who stops partway through the bundle should have read the layer that decides whether the script is any good, not the troubleshooting appendix.

### Not verified

- The ledger has never been run against a real ledger with 50+ entries. `WARN_AT = 0.45` and `BLOCK_AT = 0.62` are hand-set against three constructed cases. Both constants sit at the top of `ledger.py` and are meant to be edited once real data exists.
- No end-to-end run of the full pipeline (brief → script → film → edit → QA → ledger) was performed this session; the existing `splicecraft.py` was not modified and its own tests were not re-run.
- The `74% / 63% / 62%` statistics quoted on one Kadev slide have **no named source on the slide**. Flagged in `kadev-personal-branding.md` §1.4 as the weakest claim in the file. Do not present them to a user as sourced fact.

### Open items, roughly in priority order

1. Transcribe the 37 lesson videos and 2 live-mentoring recordings; reconcile.
2. Re-tune the ledger thresholds against a real ledger.
3. Wire `ledger check` into `splicecraft.py script` directly, so the check cannot be skipped by an agent that ignores `SKILL.md`.
4. Consider a `--themes-suggest` that proposes tags from existing entries, to keep tagging consistent — the lexical limit rests entirely on tag discipline.
5. Re-measure the reference videos with a lower scene threshold (0.2) to test the single-take bucket.
6. `anti-ai-ish.md` §B4 (LLM sentence architecture) is judgement, not measurement. It is the least evidenced section and should be rewritten against transcripts when they exist.

---

## Older entries

### 2026-09-15 — initial publication

SpliceCraft published with `SKILL.md`, 15 reference files, `splicecraft.py`, preset libraries, demo assets and the site. See git history from `3f72d03` backwards. No journal was kept before this date; this file starts here.
