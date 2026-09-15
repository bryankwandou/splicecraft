# Prompts for different agents

> **Published:** 2026-09-15 · **Last reviewed:** 2026-09-15
> **Agent check:** compare this date with today. If more than 6 months have passed, or a platform, model, or tool named here has changed, research the current facts on the web before relying on them, tell the user what changed, and update this file.

The script makes the decisions, so output quality depends very little on which model runs it. What changes between agents is how they install the skill and how much hand-holding they need.

## Claude Code

Install once (either works):

```bash
npx skills add bryankwandou/splicecraft
# or
git clone https://github.com/bryankwandou/splicecraft ~/.claude/skills-src/splicecraft
cp -r ~/.claude/skills-src/splicecraft/skills/splicecraft ~/.claude/skills/
```

Prompt:

```
Use the splicecraft skill. Edit ./raw/take1.mp4. Ask me the intake questions first.
```

## OpenAI Codex CLI

```bash
git clone https://github.com/bryankwandou/splicecraft .splicecraft
```

Prompt:

```
Read .splicecraft/skills/splicecraft/SKILL.md completely, then follow it step by step to edit ./raw/take1.mp4.
Run every command it lists. Ask me the Step 1 questions before rendering.
```

Add to `AGENTS.md` to make it permanent:

```
When asked to edit a video, follow .splicecraft/skills/splicecraft/SKILL.md exactly.
```

## ChatGPT (chatgpt.com, with Code Interpreter / data analysis)

ChatGPT in the browser runs Python in a sandbox. That sandbox has no internet, usually has no ffmpeg with libass, and limits uploads to roughly 512 MB and runs to a few minutes. So ChatGPT is good at the thinking half (transcript review, genre, plan) and weak at the rendering half.

Split the work:

1. On your machine: `python splicecraft.py transcribe take.mp4 -o words.json`
2. Upload `words.json`, `splicecraft.py`, and the `presets/` folder (zip it) to ChatGPT.
3. Prompt:

```
Unzip presets.zip next to splicecraft.py. Then run, and paste the full output of each:
  python splicecraft.py detect words.json
  python splicecraft.py plan words.json -o edl.json --level 60 --style auto --genre auto
Read edl.json. List every card with type, start, end, text. Tell me if the detected genre is wrong
and which --genre you would use instead, with the keyword hits as evidence.
Do not render. Give me edl.json to download.
```

4. Back on your machine: `python splicecraft.py render take.mp4 edl.json -o edited.mp4 --size 1080x1920`, then `qa`.

If ChatGPT says ffmpeg is available and offers to render, let it try a 10 second test first (`ffmpeg -t 10`). Most sandboxes lack the `subtitles` filter, and the render fails without captions or cards.

Custom GPT: put the SKILL.md text in Instructions, attach `splicecraft.py`, `genres.json`, `styles.json`, `levels.json` as Knowledge, enable Code Interpreter. Same split applies.

## OpenAI Codex CLI and GPT models in any terminal agent

Codex runs on your machine, so it can do everything including render. See the Codex section above. GPT models follow numbered steps well but tend to "improve" commands by adding flags. Add: `Use only flags listed in SKILL.md. If unsure, run python splicecraft.py <command> --help.`

## Fable 5.1 (Claude Code, Claude desktop Code tab, or API agents)

Fable reads the whole skill folder and follows long instructions reliably, so give it the full job in one message and let it ask Step 1 questions:

```
Use the splicecraft skill on ./raw/take.mp4.
Run detect first and show me the genre ranking with keyword hits before asking the intake questions,
so my defaults match the video (hackathon demo, tutorial, launch, story, etc.).
Render at 1080x1920, run QA, fix anything that fails, and show me the contact sheet.
```

What Fable does well here: reading `edl.json` and hand-fixing a card whose text is wrong, rewriting a hook that starts with a greeting (beat-library.md, hook "Do not"), and reading the contact sheet image to catch cards covering the face.

What to forbid: long "creative" rewrites of the transcript. Add `Change spelling only, never wording or timestamps.`

Renders take minutes. In Claude Code, tell it to run render in the background so the session stays responsive.

## Gemini CLI

```bash
git clone https://github.com/bryankwandou/splicecraft .splicecraft
```

Add to `GEMINI.md`:

```
For any video editing request, read .splicecraft/skills/splicecraft/SKILL.md and follow the steps in order.
Do not skip Step 6 (QA). Do not invent command flags.
```

## Cursor, Windsurf, Cline

Put the repo in the project, then add a rule file (`.cursor/rules/splicecraft.mdc` or equivalent) containing the same two lines as the Gemini example.

## Small or cheap models

Smaller models drift when a task has many steps. Give them one step per message:

```
Message 1: Read SKILL.md Step 0 and run those checks. Report the output only.
Message 2: Ask me the Step 1 questions.
Message 3: Run Step 2 and Step 3. Show me the segments from words.json.
Message 4: Run Step 4 with --level <N> --style <look>. Paste the planner line and the list of cards.
Message 5: Run Step 5.
Message 6: Run Step 6 and paste the QA table.
```

Or skip the reasoning entirely and have them run the one-shot command:

```
Run exactly this and paste the output:
python .splicecraft/skills/splicecraft/scripts/splicecraft.py auto raw/take1.mp4 -d work --level 60 --style studio --size 1080x1920
```

## Things to forbid in the prompt if an agent misbehaves

- "Do not download music or fonts from the internet."
- "Do not overwrite the input file."
- "Do not change timestamps in words.json, only spelling."
- "If a command fails, paste the error and stop. Do not try random flags."
