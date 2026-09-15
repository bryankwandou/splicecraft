# Script, hooks, and platform strategy

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

Before the camera rolls, the script decides most of the edit. The planner can only animate what the speaker says: a number becomes a count-up, "first, second, third" becomes a ranking, a one-word sentence becomes a word hit. A flat script gives a flat edit at any level.

## The generator

```bash
$SC script "refund bond for online sellers" --genre hackathon_demo --seconds 60 --brief brief.json -o script.md
$SC script "cara pakai AI untuk edit video" --genre tutorial_docs --seconds 40 --language id
$SC library frameworks                       # all 100 structures
$SC library hooks --category curiosity       # 200 named hooks, risky ones flagged
```

`script` writes a timed skeleton: three hook options, every beat with its time window and word budget (2.6 words per second in English, 2.3 in Indonesian), retention rules, six titles, a description template, hashtags, and the exact render command. Your agent (or you) fills the "Your line" column. The generator does not invent facts; lines stay blank until someone who knows the project writes them.

## The anatomy every short needs

| Part | Seconds (45 s video) | Job | Test |
|---|---|---|---|
| Hook | 0-3 | stop the scroll | Would a stranger need the next sentence? |
| Context / why | 3-8 | tell them why they should care | Does it name who this is for? |
| Relatable | 5-12 | "that's me" moment | Is it a moment, not a category? |
| Tension | 8-20 | stakes, conflict, or an open loop | What happens if nothing changes? |
| Value / fact / demo | 12-35 | the payoff, with a number or a visual every 3-5 s | Is there proof? |
| Twist or verdict | 30-38 | answer the hook | Did you actually answer it? |
| Closing | 38-42 | callback to the hook, so the replay loops | Does the last line echo the first? |
| CTA | 42-45 | one action | Is there only one? |

## How to write a line the planner can edit well

- **Numbers out loud.** "Three minutes, two mistakes, zero edits" gives three count-ups. "A few minutes" gives nothing.
- **Ordinals for lists.** "First... second... third..." builds a ranking card.
- **Short sentences.** One idea per sentence. A 1-3 word sentence ("Rhythm.") becomes a giant word hit.
- **Say "before and after" or "versus"** when comparing: a head-to-head card appears.
- **Quote a line.** "They say..." gives a typewriter quote card.
- **Callbacks.** "Remember those numbers from the start?" brings the number card back.
- **Name the viewer.** "If you sell online..." is a tribe callout and raises completion for that group.
- **No greeting.** "Hi guys, welcome back" is 2 seconds of scroll bait. Start on the hook.

## 100 content structures (grouped)

Full list with steps: `$SC library frameworks` (source of truth: `presets/content.json`).

| Group | Count | Use when | Examples |
|---|---|---|---|
| conversion | 15 | selling, launches, sign-ups | AIDA, PAS, BAB, FAB, 4P, 4U, ACCA, PASTOR, QUEST, SLAP |
| story | 15 | founders, vlogs, nonprofits, brand | Hero's Journey, Pixar Pitch, Sparkline, Three-Act, SOAR, Mystery Box, Underdog, Inverted Pyramid |
| short | 15 | TikTok, Reels, Shorts | HVC, Pattern Disrupt, Contrarian-Proof-Twist, POV, Stop and Show, Open Loop, Mistake-Fix, Myth vs Fact, Endless Loop |
| education | 15 | tutorials, docs, explainers | What-Why-How, Rule of 3, Jargon-Buster, STAR, 5W1H, Checklist, Comparison Breakdown, Case Study |
| psychology | 15 | growth and reach | FOMO, Social Proof Stack, Us vs Them, Identity Shift, Curiosity Gap, Expectation vs Reality, Trojan Horse |
| community | 10 | comments and repeat viewers | Poll, Build in Public, Tier List, Stitch/Duet, Quiz, Resource Swap |
| ai | 15 | AI, SaaS, data | Prompt-to-Result, Automation Workflow, Micro-SaaS Teardown, Data Narrative, One-Prompt Solution |

## 200 hooks (grouped)

`$SC library hooks` lists all 200 by name. Ten groups of twenty: emotion, curiosity, value, visual_audio, social, story_format, interactive, data_ai, sales, meta. Twenty-four have fill-in templates the script generator uses.

### Risky hooks: rules

Sixteen hooks are flagged `risky` (rage bait, outrage, paranoia bait, guilt, insecurity, data-leak framing, replacement threat, price shock, fake-out, accidental reveal, competitor flaw, tea spilling, common enemy, peer pressure, freebie bait, discontinuation warning). They work by pushing an emotion, and they backfire when the claim is not true.

An agent using this skill must:

1. Use a risky hook only when the claim is true and the video proves it.
2. Never invent scarcity, deadlines, leaks, or quotes.
3. Never target a real private person, a protected group, or health or money fears with false claims.
4. Prefer a curiosity or value hook with the same payoff when unsure. They hold up better over time.

Platforms penalize misleading content and engagement bait in their community guidelines, and a fooled viewer does not follow.

## Titles, descriptions, hashtags, on-screen text

- **Title / first caption line:** the searchable phrase people type, plus the payoff. "Edit a video with AI in 60 seconds" beats "My new workflow!!".
- **Say the keyword in the first sentence** too. Short-video platforms use captions, on-screen text, and the spoken transcript for search.
- **Description:** line 1 is the hook and payoff (it shows before "more"), line 2 a concrete detail, line 3 the CTA, line 4 hashtags.
- **Hashtags:** 3 to 5. One broad, two niche, one branded. Walls of tags do not help.
- **On-screen hook text** in the first frame, because many people start muted. The hook card does this automatically at level 21+.
- **Cover frame:** the frame with the hook card and a clear face. `sheet.jpg` shows candidates.

## Platform strategy (researched 2026-09-15; re-check before relying on it)

| Signal | TikTok | Instagram Reels | YouTube Shorts |
|---|---|---|---|
| Strongest ranking signal | watch time and completion | completion; shares and saves above likes; skip rate added | watch time per impression (not swipe rate) |
| Completion bar people cite | around 70% | completion is the most weighted metric | ~65% average view duration under 30 s, ~50% for longer |
| Sweet spot length | 15-30 s for highest completion | under 3 min for non-follower reach (max 20 min) | 30-45 s |
| Discovery | small test audience (hundreds), then wider pools; search is a major channel | shares to DMs | watch-time driven feed |

What follows from that, and what the planner does about it:

- **Cut dead air.** Pause removal is the cheapest completion gain. Every level removes pauses; higher levels remove more.
- **Loop the ending.** A closing line that calls back to the hook invites a replay (rewatch and loop rate are ranking signals).
- **Captions always.** Captioned videos are reported to get more watch time and completion. The exact "85% watch muted" figure is widely repeated but traces to a 2016 publisher claim; do not quote it as fact.
- **Earn shares and saves.** Checklists, numbers, and "save this" CTAs in consideration content. `funnel: consideration` in the brief sets this.
- **Post natively per platform.** Size and safe zones differ; see `references/audience-and-market.md`.

Nothing guarantees the For You page. The algorithm tests every video on a small audience first; the edit's job is to win that test.

## Sources

Checked 2026-09-15. Treat blog summaries as second-hand; platform pages change without notice.

- Hootsuite, How the TikTok algorithm works in 2026: https://blog.hootsuite.com/tiktok-algorithm/
- Darkroom, TikTok Algorithm 2026: https://www.darkroomagency.com/observatory/tiktok-algorithm-guide-2026-everything-we-know-about-how-videos-are-ranked
- Betterview, TikTok's 70% completion rate: https://betterview.nl/en/blog/tiktok-completion-rate-70-procent-2026
- Socialync, YouTube Shorts algorithm 2026: https://www.socialync.io/blog/youtube-shorts-algorithm-2026
- InstantDM, Instagram Reels reach 20 minutes: https://instantdm.com/blog/instagram-reels-reach-20-minutes-the-2026-limit-explained
- Fastlane, The Instagram Reels algorithm in 2026: https://www.usefastlane.ai/blog/instagram-reels-algorithm-2026
- Kapwing, Short-form video statistics 2026: https://www.kapwing.com/resources/short-form-video-statistics-tiktok-reels-and-shorts-by-the-numbers-in-2026/
- Vidico, 60+ short-form video statistics (notes the origin of the 85% muted claim): https://vidico.com/news/short-form-video-statistics/
