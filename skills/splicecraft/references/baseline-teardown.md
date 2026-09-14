# Baseline teardown: "Which AI edits better?"

Source studied: a 107.6 second vertical video (1080x1920, 60 fps, AAC stereo, mean loudness -17.8 dB, peak -0.9 dB) from the withPT.ai account. One creator, one raw take, handed to two AI models with the same prompt. The frame is split: the top half is one model's edit, the bottom half is the other's, both playing in sync under a fixed header.

Method: frames sampled every 2 s into contact sheets, scene changes detected with ffmpeg `select=gt(scene,0.25)`, speech transcribed with Whisper large-v3 at word level. Timestamps below are from the source.

The footage belongs to its creator. This file describes it for study only; none of it is redistributed in this repository.

## 1. Layout

| Zone | Share of 1920 px height | Content |
|---|---|---|
| Header | ~15% | "Which AI edits better?" in heavy black sans, blue subline "Same Footage & Audio \| Zero Human Edits" |
| Top label | ~3% | model name with a small orange mark |
| Top pane | ~28% | 16:9 cutout of the take with model A's graphics |
| Bottom label | ~3% | model name with a small blue mark |
| Bottom pane | ~28% | same take with model B's graphics |
| Margins | ~23% | pale blue-white gradient, empty |

Both panes are 16:9 rectangles placed inside a 9:16 canvas. The speaker is filmed against a plain white wall, black cap and t-shirt, soft frontal light, no color grade.

## 2. Beat map (the script is a test of beat types)

The speaker announces each beat, then performs it. This is a clean catalogue of what an automated editor should handle.

| Time (s) | Speech | Beat type | Model A (orange, top) | Model B (blue, bottom) |
|---|---|---|---|---|
| 0.0-5.0 | "Let's see if Astra 6 or Fable 5.1 is better at video editing." | hook / versus | two name pills with a round VS badge | "THE SAME EDITING TEST" label, 6 vs 5.1 numerals |
| 5.0-6.0 | "Who do you think will win?" | question | none | none |
| 6.0-10.0 | "I gave it this raw video and a prompt to make edits. That's it." | setup | small UI screenshot card | "THE ENTIRE BRIEF" card with thumbnail |
| 10.0-15.0 | "Every graphic in this video was drawn by AI. Without me editing anything." | claim | none | "BUILT FROM CODE" line-drawing that morphs into a blob |
| 15.0-19.0 | "Every line in this video is a different job. Note how they render differently." | framing | none | none |
| 19.0-25.0 | "Here is a number: 1 recording. 2 models, 0 edits from me." | number | three chips pop in one by one: 1, 2, 0 with icons | "THE TEST, IN NUMBERS": 1 / 2 / 0 with labels and underline |
| 25.0-31.0 | "Here are two things to compare. A timeline editor moves pixels around. This one moves code." | comparison | dark timeline UI mock, then code panel | "TIMELINE -> PICTURE", then "CODE -> PICTURE" |
| 31.0-40.0 | "Here are three at once. Which is harder? Color, font, and timing. All pulled from one brand file." | trio | color swatch, "Aa" type card, timing card, joined by a line | "ONE SOURCE, THREE OUTPUTS" tree diagram |
| 38.0-43.0 | "Here's a quote. They say in life you miss 100% of the shots you don't take." | quote | quote card with typewriter text | "THE SHOT NEVER TAKEN": ball, hoop, 100% counter |
| 43.0-52.0 | "Here are captions. Every word I'm saying should land on the screen as I say it..." | captions | none extra | none extra |
| 52.0-58.5 | "Here's the before and after. The raw take on one side and the finished cut on the other." | before/after | desaturated left half with a wipe line and camera HUD | literal split: RAW and FINISHED side by side |
| 58.5-65.0 | "Here's a ranking. Speed first. Control second. And something something third." | ranking | numbered list card, rows added as spoken | "THE PRIORITY ORDER" bars shrinking per rank |
| 65.0-72.0 | "Here's a word worth zooming into. Anchored. Every graphic is tied to the one moment I say it." | word zoom | "Anchored" over a timeline ruler | "ONE WORD, ONE FRAME": ANCHORED over a waveform with playhead |
| 72.0-80.0 | "And here's the hardest one. Do nothing. Some sentences don't need a graphic..." | restraint | none | none |
| 80.0-89.0 | "Bring back the number from the start. If it remembers it, it was watching the whole video..." | callback | 1 / 2 / 0 chips return | "BACK TO THE START": 1 2 0 with a timeline scrubber |
| 89.6-96.4 | "Comment 'edit' and I'll send you the setup, including the prompt..." | CTA (comment) | comment box with "EDIT" and a prompt.md file card | "GET THE SAME SETUP": EDIT field and prompt.md |
| 96.6-102.5 | "And follow me because I keep putting these two head to head." | CTA (follow) | red "Following" pill | withPT.ai brand line |
| 102.8-104.6 | "That's it for now. Thanks. Bye." | outro | none | none |

Scene-change detection found almost no hard cuts: the edit is one continuous take with graphics layered on top. Pauses were not removed.

## 3. Captions

- Top pane: 3 to 4 word chunk in a small white rounded box, current word in blue. At phone size the box text is roughly 14 px tall. It is hard to read.
- Bottom pane: same chunking, black text on white box with the current word in blue, slightly larger.
- Both sit on the speaker's chest, below the chin. Good placement. Both are too small for the pane they live in.

## 4. What works (and what splicecraft copies)

1. The script is a checklist of beat types. That makes it a fair benchmark and a great template for a rule-based planner.
2. Graphics land on the trigger word, not before or after.
3. "Do nothing" is treated as a skill. Restraint is scored.
4. The callback proves the edit understood the whole video, not one line at a time.
5. Every card has a small caps label ("THE TEST, IN NUMBERS"). It tells the viewer what kind of information is coming before they read it.
6. Model B's cards use one consistent visual system: pale card, blue numerals, thin rules. It reads as designed, not assembled.

## 5. Weak spots (critical review of UI, UX, and design)

Rated by how much each costs a viewer on a phone.

1. **Two videos in one frame halves everything.** Each face occupies about 12% of the screen. Expressions, which are the reason to watch a talking head, are lost.
2. **The header wastes the prime real estate.** The top 15% of a vertical video is the first place the eye lands. It holds a static title for 107 seconds. After second 3 it carries no new information.
3. **16:9 panes inside 9:16.** Roughly a quarter of the canvas is empty gradient. Vertical footage cropped for vertical would have filled it.
4. **Top-pane graphics are too small to read.** The three-card "color, font, timing" beat and the prompt.md card have text under 10 px at phone size. A graphic you cannot read is decoration.
5. **Model B squeezes the speaker to the right.** Its cards take the left 60% of the pane, so the face sits at the edge and is sometimes cut off at the shoulder.
6. **No music, no sound design.** Card entrances are silent. Nothing marks the beats for someone half-watching.
7. **No grade.** White wall, flat light, neutral color. It looks like a webcam. A slight contrast lift and warmth would separate the speaker from the wall.
8. **No pause removal.** The take has dead air between sentences (6.5 s total at a 0.3 s threshold). On a 107 s short that is 6% of runtime doing nothing.
9. **The test never ends.** There is no verdict, score, or winner reveal. The hook asks "who do you think will win?" and the video never pays it off, which hurts retention at the end.
10. **Transcript placeholder left in.** "And something something third" is spoken filler that becomes a graphic ("Something something") in both edits. Neither model flagged it.
11. **Weak CTA hierarchy.** Two calls to action (comment, then follow) back to back. The comment CTA is stronger for reach; the follow pill competes with it.
12. **Split before/after inside a split screen.** Model B shows RAW and FINISHED side by side inside a half-height pane: four small faces at once. It is the hardest moment to read.
13. **Same end frame for both halves.** The last 3 seconds show no graphics on either pane. No end card, no loop point back to the start.

## 6. How splicecraft goes further

| Baseline gap | splicecraft behavior |
|---|---|
| Face is small | Full-frame 9:16 speaker, cards in the top third only |
| Tiny captions | 66-80 px captions on a 1920 grid, heavy weight, stroke and shadow, word-level pop |
| Dead air | Pause removal scaled by level |
| No sound | Generated music bed with sidechain ducking, pop / whoosh / tick effects on card entrances |
| Flat image | Five grades plus LUT support and film grain at Pro level and up |
| No motion on the speaker | Punch-in, ease-in, and drift zooms tied to beats |
| No green-screen path | Chroma key with despill over an image, video, or animated gradient |
| Loudness not managed | Voice chain (high-pass, compressor, presence EQ) and loudnorm to -14 LUFS |
| No quality gate | `qa` subcommand with nine pass/fail checks and a contact sheet |
| Fixed intensity | One dial from 1 to 100 |

## 7. Honest limits of the automated version

- The planner is rule-based. It will not draw bespoke illustrations like model B's basketball hoop. Custom illustrations need a motion tool (Remotion, After Effects) or a human.
- It does not track the face. Cards assume the face is in the middle third, which is true for most talking heads and false for some.
- Transcript mistakes become caption mistakes. Step 3 of SKILL.md asks the agent to read the transcript for this reason.
