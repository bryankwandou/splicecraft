# Content memory: the ledger

> **Published:** 2026-09-23 · **Last reviewed:** 2026-09-23
> **Tool:** `scripts/ledger.py` (standard library only, Python 3.9+)
> **Store:** `~/.splicecraft/ledger.json` on the user's own machine. Nothing is uploaded anywhere.

## Why this exists

An AI asked for "ide konten personal branding" produces roughly the same twelve ideas every time it is asked. One user, over one month, ends up with an account that says one thing twelve ways. The course diagnoses inconsistency as the killer; the modern failure is the opposite — **sameness**.

The ledger is the fix: a local, permanent, user-owned record of every script, niche, hook and theme already produced, which the agent is required to consult *before* writing and required to update *after* producing.

It also solves a second problem. A user comes back three weeks later in a fresh conversation. The agent has no memory of the previous session. The ledger is that memory, and it lives on the user's disk rather than in a chat log.

---

## The contract

Two obligations, both mandatory, both wired into `SKILL.md`:

1. **Before writing any script or idea list** → `ledger check`. Exit code 2 means do not write it.
2. **After producing anything** → `ledger add`. Idea, script, or finished video — log it with its angle.

An agent that skips step 2 breaks the tool for every future session. Logging is not optional bookkeeping; it is the product.

---

## Setup

```bash
LEDGER="python <skill-folder>/scripts/ledger.py"
$LEDGER init
```

Prints the store path. Run once per machine. If it already exists, it says so and does nothing.

To keep the ledger somewhere else (a synced folder, a project directory):

```bash
$LEDGER --store "D:/brand/ledger.json" init
# or, for the whole session:
export SPLICECRAFT_LEDGER="D:/brand/ledger.json"
```

---

## Checking before you write

```bash
$LEDGER check "3 cara stop prokrastinasi buat mahasiswa" --theme prokrastinasi
```

```
checking: "3 cara stop prokrastinasi buat mahasiswa prokrastinasi"
against 14 entries

  BLOCK   71%  478aac15  2026-08-02  3 langkah biar gak prokrastinasi lagi
              angle: pakai timer fisik bukan app
  warn    48%  1dd93368  2026-07-19  kenapa to-do list kamu gak kepake
           9%  9f10ac22  2026-07-05  cerita gue gagal 4 tahun bikin konten

VERDICT: too close. Do not write this.
```

| Exit code | Meaning | What the agent does |
|---|---|---|
| 0, score < 45% | clear | write it |
| 0, score 45-61% | adjacent | allowed, but the agent must **say out loud what is new about it**. If it cannot, treat as a repeat. |
| **2**, score ≥ 62% | collision | **do not write it.** Change the angle, the pillar, or the audience segment. |

Useful flags: `--niche` restricts the comparison to one superniche first (falls back to everything if that niche is empty); `--json` for machine-readable output; `--hook` and `--angle` sharpen the probe.

### How the score works

Two scores are computed and **the stronger wins**:

- **Topic-level** — topic + themes only, scaled to 0.92. Catches "you already covered this subject" even when the hook and angle differ. Because it is capped below 1.0, a pure subject repeat lands in WARN, not BLOCK: reusing a subject with a genuinely new angle is allowed, it just has to be declared.
- **Full-text** — topic, themes, hook, angle and premise together. Catches an actual rewrite, which blocks.

Each score blends unigram **overlap** (`|A∩B| / min(|A|,|B|)`) at 65% with bigram **Jaccard** at 35%. Overlap rather than Jaccard on unigrams because Jaccard punishes the short side — a five-word topic compared against a fully-filled entry scored low purely because the union was large, which let real repeats read as "clear". Bigrams stay Jaccard because they measure shared *phrasing*, where union size is meaningful, and phrasing is what separates "same subject, new angle" from "same script, reworded".

Indonesian and English stopwords are removed, plus words that appear in nearly every content brief (`konten`, `video`, `tiktok`, `script`, `tips`) and therefore carry no signal. A light Indonesian stemmer collapses `mengedit` / `editing` / `edit`.

<!-- journal: thresholds WARN_AT=0.45 / BLOCK_AT=0.62 were set by hand against a small set of constructed cases (a near-duplicate, a verbatim rewrite, an unrelated topic) and verified to give warn/block/clear respectively. They are not tuned against real user data because none exists yet. Expect to revisit once a real ledger has ~50 entries. Both constants are at the top of ledger.py and are meant to be edited. -->

---

## Logging after you produce

```bash
$LEDGER add "3 cara stop prokrastinasi buat mahasiswa" \
  --niche "produktivitas mahasiswa" \
  --pillar educate \
  --hook-template 11 \
  --hook "Ini adalah 3 langkah untuk stop prokrastinasi" \
  --angle "pakai timer fisik, bukan aplikasi" \
  --theme prokrastinasi --theme mahasiswa \
  --premise "dari mahasiswa yang selalu telat jadi yang selesai duluan" \
  --platform tiktok --format talking_head --seconds 32 \
  --script-path work/script.md --video-path work/edited.mp4 \
  --status published
```

Every field except the topic is optional, but the ones that matter most for future de-duplication are **`--angle`** and **`--theme`**. The angle is the sentence that answers *"what made this one different?"* — without it, the ledger can tell you that you covered a subject but not how.

`add` always reports the nearest existing entry. Logging a near-duplicate is permitted — the user may have decided it is fine — but it is never silent.

### Fields

| Field | What goes in it |
|---|---|
| `topic` | what it was about, in the user's own words |
| `niche` | the superniche it serves |
| `pillar` | `educate` / `inspiration` / `entertaining` / `promotion` |
| `hook` | the actual hook line used |
| `hook_template` | which of the 20 templates (`kadev-script-formulas.md` §4) |
| `angle` | **what made this one different** |
| `themes` | repeatable tags |
| `premise` | the premis this serves (`kadev-personal-branding.md` §2.4) |
| `platform`, `format`, `seconds` | production facts |
| `script_path`, `video_path` | where the artifacts live |
| `status` | `idea` / `scripted` / `filmed` / `produced` / `published` |
| `performance` | reserved; fill later by hand with views, saves, comments |
| `notes` | anything |

Log at `--status idea` too. A rejected idea is worth remembering — it stops the agent proposing it again next month.

---

## Reading the ledger back

```bash
$LEDGER list --limit 20              # recent, newest first
$LEDGER list --pillar educate        # filter
$LEDGER stats                        # pillar balance, niche mix, hook fatigue, cadence
$LEDGER themes                       # everything covered, ranked
$LEDGER suggest                      # what is under-used and due next
$LEDGER show <id>                    # one entry in full
$LEDGER export --format md --out ledger.md
$LEDGER export --format csv --out ledger.csv
```

`stats` is the one to run at the start of a strategy conversation:

```
PILLAR BALANCE
  educate          9    64%  ###############
  inspiration      3    21%  #####
  entertaining     1     7%  ##
  promotion        1     7%  ##

NICHE MIX  (target 80 / 15 / 5 - superniche / adjacent / personal)
  personal branding             11    79%
  self development               2    14%
  kehidupan personal             1     7%

HOOK TEMPLATES USED
  #11       4  <- leaning on this
  #2        3
  #7        2

CADENCE  2026-07-05 -> 2026-09-14  (71 days)
  1.4 pieces per week
  last entry was 9 days ago
```

That readout answers, with evidence: is the 80/15/5 ratio holding? Is the account a pillar monoculture? Is the same hook template being reused until it burns out? Has the user actually stopped posting?

`suggest` turns the same data into a recommendation — which pillar is due, which hook templates are fatigued, and the last five topics so the agent does not circle back.

---

## Editing and correcting

The store is plain JSON, indented, UTF-8. The user can open it in any editor. From the CLI:

```bash
$LEDGER edit 478aac15 --set status=published --set "notes=did 40k views"
$LEDGER edit 478aac15 --set "themes=prokrastinasi,mahasiswa,produktivitas"
$LEDGER remove 478aac15
```

IDs are matched by prefix — the first 8 characters shown in `list` are enough.

If the file is hand-edited into invalid JSON, every command fails with a message naming the file and the parse error rather than silently starting over. Writes go to a temp file and are then moved into place, so an interrupted write cannot truncate an existing ledger.

---

## Privacy

- The ledger never leaves the machine. There is no network code in `ledger.py`.
- It is a plain file the user owns, can read, can back up, can delete.
- It records what the user made. If a topic is sensitive, they can `remove` it or edit the file directly.
- Do not copy ledger contents into anything that gets published.

---

## Limits

- Similarity is lexical, not semantic. *"cara berhenti menunda pekerjaan"* and *"stop prokrastinasi"* mean the same thing but share no tokens, and the ledger will not catch it. The `--theme` tags exist to bridge this — **tag consistently and the gap mostly closes.**
- One ledger per machine by default. A user running several brands should use `--store` per brand, or `SPLICECRAFT_LEDGER` per session.
- Performance data is not collected automatically. The `performance` field is there to be filled in by hand.
- The thresholds are hand-set, not learned. See the journal note above.

<!-- journal: the lexical-vs-semantic limit is the known weak point. An embedding-based check would fix it but would need either a model download or a network call, and this skill is deliberately offline and stdlib-only. If that constraint is ever relaxed, this is the first thing to upgrade. Until then, the --theme discipline is what carries it, which is why SKILL.md tells the agent to always pass themes. -->
