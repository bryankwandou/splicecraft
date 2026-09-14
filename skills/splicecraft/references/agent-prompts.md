# Prompts for different agents

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
